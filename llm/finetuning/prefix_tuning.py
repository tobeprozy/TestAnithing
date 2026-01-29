from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import PrefixTuningConfig, get_peft_model
from datasets import load_dataset
import os
import torch
import numpy as np

# 禁用tokenizers并行警告
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 强制使用CPU
os.environ["CUDA_VISIBLE_DEVICES"] = ""
torch.cuda.is_available = lambda: False

model_name = "Qwen/Qwen1.5-0.5B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# 设置pad_token为eos_token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    
# 添加前缀微调
prefix_config = PrefixTuningConfig(
    task_type="CAUSAL_LM",
    num_virtual_tokens=10,  # 前缀令牌数量
    prefix_projection=False
)
model = get_peft_model(model, prefix_config)

# 数据集
dataset = load_dataset("Abirate/english_quotes", split="train[:50]")

# 修复的数据预处理函数 - 确保返回正确的数据类型
def tokenize_function(examples):
    # 添加EOS标记
    texts = [text + tokenizer.eos_token for text in examples["quote"]]
    
    # 对文本进行分词
    tokenized = tokenizer(
        texts,
        padding="max_length",
        truncation=True,
        max_length=64,
        return_tensors="np"  # 使用numpy数组而不是PyTorch张量
    )
    
    # 创建标签 - 将输入序列作为标签（用于语言建模）
    tokenized["labels"] = tokenized["input_ids"].copy()
    
    # 返回numpy数组格式
    return tokenized

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# 打印样本数据验证
print("样本数据验证:")
sample = tokenized_dataset[0]
print(f"Input IDs 类型: {type(sample['input_ids'])}")
print(f"Input IDs: {sample['input_ids'][:5]}... (共 {len(sample['input_ids'])} tokens)")
print(f"Labels 类型: {type(sample['labels'])}")
print(f"Labels: {sample['labels'][:5]}... (应与input_ids相同)")
print(f"Attention Mask 类型: {type(sample['attention_mask'])}")
print(f"Attention Mask: {sample['attention_mask'][:5]}...")

# 关键修复：将数据集转换为PyTorch格式
tokenized_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])

# 训练配置 - 针对CPU优化
training_args = TrainingArguments(
    output_dir="./prefix_ft",
    per_device_train_batch_size=2,  # 减小批大小以适应CPU
    num_train_epochs=1,
    learning_rate=2e-4,
    logging_steps=10,
    report_to="none",
    use_cpu=True,  # 使用新的use_cpu参数替代no_cuda
    fp16=False,    # 禁用FP16
    bf16=False,    # 禁用BF16
    optim="adamw_torch",  # 使用CPU优化的优化器
    remove_unused_columns=False,  # 防止数据集列丢失
    gradient_accumulation_steps=4  # 梯度累积以减少内存使用
)

# 训练
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)
print("开始前缀微调...")
trainer.train()
print("前缀微调完成！")