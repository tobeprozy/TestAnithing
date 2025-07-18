import torch
from transformers import AutoModelForCausalLM

num_threads=16
device = torch.device("cpu")

if device == "cpu":
    dtype = torch.float
    torch.set_num_threads(num_threads)
else:
    dtype = torch.bfloat16

# load model
model_path = "Qwen2-7B-Instruct"
origin_model = AutoModelForCausalLM.from_pretrained(
    model_path, trust_remote_code=True, torch_dtype=dtype,
    attn_implementation="eager"
).eval().to(device)

for param in origin_model.parameters():
    param.requires_grad = False

print(origin_model)

# 统计每一层的计算量和通信量


import numpy as np

a16_ratio = 2
w8a16_ratio =  1.
w4a16_ratio = 0.5469

ddr_util = 1.
mac_util = 0.5 # 目前一般能达到50%的利用率
p2p_util = 1.
pcie_avg_ms = 0.1 # ms


def count_embedding_weights(hidden_size, vocab_size):
    num_weights = hidden_size * vocab_size
    return num_weights

# y=Wx+b
# 乘法运算量：m×n（每个输入神经元与权重相乘）
# 加法运算量：m×n（累加m个乘积结果）
# 偏置加法：n（每个输出神经元加一个偏置）
# 总FLOPs‌ = 2×m×n + n ≈ 2mn
def compute_lm_head_flops(hidden_size, vocab_size):
    flops = hidden_size * vocab_size * 2 
    return flops

def count_lm_head_weights(hidden_size, vocab_size):
    num_weights = hidden_size * vocab_size
    return num_weights
    
# 统计block的计算量  
def compute_block_flops(query_len, key_len, hidden_size, inter_size, num_attn_heads, num_kv_heads):
    num_qo_mm = 2 
    num_kv_mm = 2
    num_attn_mm = 2
    num_mlp_mm = 3
    
    head_dim = hidden_size / num_attn_heads
    kv_dim = head_dim * num_kv_heads
    
    kv_flops = query_len * hidden_size * kv_dim * 2 * num_kv_mm # 表示计算key和value的计算量,涉及Wk,Wv
    qo_flops = query_len * hidden_size * hidden_size * 2 * num_qo_mm # 表示query和最后多头output的计算量，涉及Wq,Wo
    attn_flops = query_len * key_len * hidden_size * 2 * num_attn_mm # 表示attention的计算量,即softmax(QK^T)V的计算量
    mlp_flops = query_len * hidden_size * inter_size * 2 * num_mlp_mm # 表示mlp的计算量，包括3个linear，涉及gate_proj、up_proj、down_proj
    
    total_flops = kv_flops + qo_flops + attn_flops + mlp_flops
    return total_flops

# 统计block的权重
def count_block_mm_weights(hidden_size, inter_size, num_attn_heads, num_kv_heads):
    num_qo_mm = 2 # 2个矩阵乘法
    num_kv_mm = 2 # 2个矩阵乘法
    num_mlp_mm = 3 # 3个矩阵乘法
    
    head_dim = hidden_size / num_attn_heads # 每个head的维度
    kv_dim = head_dim * num_kv_heads # kv的维度
    
    num_qo_weights = hidden_size * hidden_size * num_qo_mm # qo的权重
    num_kv_weights = hidden_size * kv_dim * num_kv_mm # kv的权重
    num_mlp_weights = hidden_size * inter_size * num_mlp_mm # mlp的权重
    
    num_weights = num_qo_weights + num_kv_weights + num_mlp_weights # 所有block的权重
    return num_weights # 返回所有block的权重

# 
def count_block_gather_weights(max_seq_len, hidden_size, num_attn_heads):
    head_dim = hidden_size / num_attn_heads # 每个head的维度
    num_weights = max_seq_len * head_dim * 2 # cos, sin table
    return num_weights # 返回cos, sin table的权重

# 统计kv cache的权重
def count_kv_cache(seq_len, hidden_size, num_layers, num_attn_heads, num_kv_heads):
    head_dim = hidden_size / num_attn_heads # 每个head的维度
    kv_dim = head_dim * num_kv_heads # kv的维度
    
    num_kv_cache = 2 * seq_len * kv_dim * num_layers # kv cache的权重
    return num_kv_cache # 返回kv cache的权重

# 统计prefill的计算时间
def get_prefill_compute_time(total_flops, num_device, tpu_freq=1000):
    tpu_peak_flops = 16384 * num_device * tpu_freq / 1000 # 峰值计算量
    
    compute_time = total_flops / 1e9 / tpu_peak_flops / mac_util # 计算时间
    return compute_time

def get_prefill_allreduce_time(seq_len, hidden_size, num_layers, num_device, tpu_freq=1000):
    p2p_bw = p2p_speed # p2p带宽
    s2l_bw = s2l_speed * tpu_freq / 1000 # s2l带宽
    l2s_bw = l2s_speed * tpu_freq / 1000 # l2s带宽
    bf16_size = 2 # bf16的size
    ring_data_ratio = (num_device - 1) * 2 / num_device # 环形数据比例
    size = seq_len * hidden_size * bf16_size * ring_data_ratio * num_layers * 2 # 数据量
    
    p2p_time = size / p2p_bw / p2p_util # p2p时间
    add_time = (size * 2 / s2l_bw + size / l2s_bw) / ddr_util # add时间
    allreduce_time = p2p_time + add_time # 总时间
    return allreduce_time # 返回总时间

def get_decode_pcie_time(num_layers):
    pcie_ms = pcie_avg_ms * num_layers * 2 # pcie时间
    return pcie_ms # 返回pcie时间

def get_decode_allreduce_time(num_layers, num_device):
    time_per_allreduce = 0 # 每个allreduce的时间
    if num_device == 2:
        time_per_allreduce = 0.12 # 2个设备的时间
    elif num_device == 4:
        time_per_allreduce = 0.15 # 4个设备的时间
    elif num_device == 6:
        time_per_allreduce = 0.36 # old allreduce
    elif num_device == 8:
        time_per_allreduce = 0.2 # 8个设备的时间
    elif num_device == 1:
        return 0 # 1个设备的时间
    else:
        print(f"****** Do Not Support num_device = {num_device} **********")
        return -1 # 不支持的设备
    
    allreduce_ms = time_per_allreduce * num_layers * 2 # 总时间
    return allreduce_ms

def get_decode_load_weights_time(weight_bytes, num_device, tpu_freq=1000):
    s2l_bw = s2l_speed * tpu_freq / 1000 # s2l带宽
    
    load_weights_ms = weight_bytes / s2l_bw / num_device * 1000 / ddr_util # 加载权重时间
    return load_weights_ms

def get_decode_load_kv_cache_time(kv_cache_bytes, num_device, tpu_freq=1000):
    s2l_bw = s2l_speed * tpu_freq / 1000 # s2l带宽
    
    load_kv_cache_ms = kv_cache_bytes / s2l_bw / num_device * 1000 / ddr_util # 加载kv cache时间
    return load_kv_cache_ms

# 从模型结构里读取参数
seq_len = 8192
hidden_size = origin_model.config.hidden_size
inter_size = origin_model.config.intermediate_size
num_attn_heads = origin_model.config.num_attention_heads
num_kv_heads = origin_model.config.num_key_value_heads
num_layers = origin_model.config.num_hidden_layers
vocab_size = origin_model.config.vocab_size
ratio = w4a16_ratio

tpu_freq = 950
num_device = 1

p2p_speed = 3e9
s2l_speed = 200e9
l2s_speed = 120e9

lm_head_flops = compute_lm_head_flops(hidden_size, vocab_size)
block_flops = compute_block_flops(seq_len, seq_len, hidden_size, inter_size, num_attn_heads, num_kv_heads)

all_block_flops = block_flops * num_layers
total_flops = lm_head_flops + all_block_flops

embedding_weight_bytes = count_embedding_weights(hidden_size, vocab_size) * a16_ratio
lm_head_weight_bytes = count_lm_head_weights(hidden_size, vocab_size) * ratio
block_mm_weight_bytes = count_block_mm_weights(hidden_size, inter_size, num_attn_heads, num_kv_heads) * ratio
block_gather_weight_bytes = count_block_gather_weights(seq_len, hidden_size, num_attn_heads) * a16_ratio
mm_weight_bytes = lm_head_weight_bytes + block_mm_weight_bytes * num_layers

kv_cache_bytes = count_kv_cache(seq_len, hidden_size, num_layers, num_attn_heads, num_kv_heads) * a16_ratio

prefill_compute_time = get_prefill_compute_time(total_flops, num_device, tpu_freq)
prefill_allreduce_time = get_prefill_allreduce_time(seq_len, hidden_size, num_layers, num_device, tpu_freq)
decode_pcie_time = get_decode_pcie_time(num_layers)
decode_allreduce_time = get_decode_allreduce_time(num_layers, num_device)
decode_load_weights_time = get_decode_load_weights_time(mm_weight_bytes, num_device, tpu_freq)
decode_load_kv_cache_time = get_decode_load_kv_cache_time(kv_cache_bytes, num_device, tpu_freq)
total_prefill_time = prefill_compute_time + prefill_allreduce_time
total_decode_time = decode_pcie_time + decode_allreduce_time + decode_load_weights_time + decode_load_kv_cache_time
tps = 1000 / total_decode_time

print(f'## Qwen2-7B-W4A16-seq{seq_len}-{num_device}dev-{tpu_freq}MHz:')
print(f'### Basic Information')
print(f'embedding: {embedding_weight_bytes/2**20} MiB')
print(f'block_gather: {block_gather_weight_bytes/2**20} MiB')
print(f'lm_head: {lm_head_flops/1e9} GFLOPs, {lm_head_weight_bytes/2**20} MiB')
print(f'blocks: {block_flops/1e9} GFLOPs, {block_mm_weight_bytes/2**20} MiB')
print(f'all blocks: {all_block_flops/1e9} GFLOPs, {block_mm_weight_bytes*num_layers/2**20} MiB')
print(f'mm_weights: {mm_weight_bytes/2**20} MiB')
print(f'total flops: {total_flops/1e9} GFLOPs')
print(f'### Time Information')
print(f'prefill_time = {total_prefill_time} s')
print(f'decode_time = {total_decode_time} ms, Speed = {tps} token/s')