from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
import torch
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 禁用 tokenizers 并行警告
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 1. 检查并配置量化
if torch.cuda.is_available():
    logger.info("检测到 GPU 支持，启用 QLoRA 4-bit 量化")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=False
    )
    device_map = "auto"
else:
    logger.warning("未检测到 GPU 支持，使用标准 LoRA（非量化）")
    bnb_config = None
    device_map = None
    # 强制使用 CPU
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    torch.cuda.is_available = lambda: False

# 2. 加载模型和分词器
model_name = "Qwen/Qwen1.5-0.5B"
logger.info(f"加载模型: {model_name}")
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 设置 pad_token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# 加载模型
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map=device_map,
    trust_remote_code=True
)

# 3. 准备模型用于 k-bit 训练
if bnb_config:
    logger.info("准备模型用于 k-bit 训练")
    model = prepare_model_for_kbit_training(model)

# 4. 配置 LoRA
logger.info("配置 LoRA 适配器")
lora_config = LoraConfig(
    r=8,  # LoRA 秩
    lora_alpha=32,  # LoRA alpha
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # 目标模块
    lora_dropout=0.1,  # Dropout 率
    bias="none",  # 不添加偏置
    task_type="CAUSAL_LM"  # 因果语言模型任务
)
model = get_peft_model(model, lora_config)

# 打印可训练参数
model.print_trainable_parameters()

# 5. 加载数据集
logger.info("加载数据集")
dataset = load_dataset("Abirate/english_quotes", split="train[:50]")  # 使用小样本

# 6. 数据处理函数
def tokenize_function(examples):
    # 添加 EOS 标记
    texts = [text + tokenizer.eos_token for text in examples["quote"]]
    
    # 对文本进行分词
    tokenized = tokenizer(
        texts,
        padding="max_length",  # 填充到相同长度
        truncation=True,  # 截断超过最大长度的序列
        max_length=64,  # 最大序列长度
        return_tensors="pt"  # 返回 PyTorch 张量
    )
    
    # 创建标签 - 将输入序列作为标签
    tokenized["labels"] = tokenized["input_ids"].clone()
    
    # 转换为列表格式以避免兼容性问题
    return {
        "input_ids": tokenized["input_ids"].tolist(),
        "attention_mask": tokenized["attention_mask"].tolist(),
        "labels": tokenized["labels"].tolist()
    }

logger.info("处理数据集...")
tokenized_dataset = dataset.map(tokenize_function, batched=True)

# 设置数据集格式为 PyTorch 张量
tokenized_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])

# 7. 训练配置
training_args = TrainingArguments(
    output_dir="./qlora_ft",
    per_device_train_batch_size=2,  # 批大小
    num_train_epochs=1,  # 训练轮数
    learning_rate=3e-4,  # 学习率
    optim="paged_adamw_8bit" if torch.cuda.is_available() else "adamw_torch",  # 优化器选择
    logging_steps=5,  # 日志记录间隔
    report_to="none",  # 不报告到任何平台
    save_strategy="no",  # 不保存检查点
    fp16=torch.cuda.is_available(),  # 根据 GPU 可用性启用 FP16
    bf16=False,  # 禁用 BF16
    gradient_accumulation_steps=4,  # 梯度累积
    remove_unused_columns=False,  # 防止数据集列丢失
    use_cpu=not torch.cuda.is_available(),  # 明确使用 CPU 如果没有 GPU
    disable_tqdm=True  # 禁用进度条以减少开销
)

# 8. 创建 Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

# 9. 开始训练
logger.info("开始 QLoRA 微调...")
trainer.train()
logger.info("QLoRA 微调完成!")

# 10. 保存适配器
output_dir = "./qlora_adapter"
os.makedirs(output_dir, exist_ok=True)
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
logger.info(f"适配器已保存到 {output_dir}")