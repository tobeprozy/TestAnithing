from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import load_dataset
import os

# 禁用tokenizers并行警告
os.environ["TOKENIZERS_PARALLELISM"] = "false"

model_name = "Qwen/Qwen1.5-0.5B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# 设置pad_token为eos_token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# 使用小样本数据集
dataset = load_dataset("Abirate/english_quotes", split="train[:50]")

# 修复的数据预处理函数
def tokenize_function(examples):
    # 对文本进行分词
    tokenized = tokenizer(
        examples["quote"],
        padding="max_length",
        truncation=True,
        max_length=64,
        return_tensors="pt"
    )
    
    # 创建标签 - 将输入序列作为标签（用于语言建模）
    tokenized["labels"] = tokenized["input_ids"].clone()
    return tokenized

# 应用分词并创建标签
tokenized_dataset = dataset.map(tokenize_function, batched=True)

# 训练配置
training_args = TrainingArguments(
    output_dir="./full_ft",
    per_device_train_batch_size=4,
    num_train_epochs=1,
    learning_rate=5e-5,
    logging_steps=10,
    report_to="none",
    save_strategy="no",  # 禁用保存以加快速度
)

# 训练
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

print("开始全量微调...")
trainer.train()
print("全量微调完成!")