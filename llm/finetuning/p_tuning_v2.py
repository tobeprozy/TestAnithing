from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import PromptTuningConfig, get_peft_model
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
    
# 添加P-Tuning V2
prompt_config = PromptTuningConfig(
    task_type="CAUSAL_LM",
    num_virtual_tokens=20,  # 提示令牌数量
    prompt_tuning_init_text="Classify if the tweet is a complaint or not:",
)
model = get_peft_model(model, prompt_config)

# 数据集
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

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# 训练配置
training_args = TrainingArguments(
    output_dir="./p_tuning_ft",
    per_device_train_batch_size=4,
    num_train_epochs=1,
    learning_rate=3e-4,
    logging_steps=10,
    report_to="none"
)

# 训练
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

print("开始P-Tuning V2微调...")
trainer.train()
print("P-Tuning V2微调完成！")