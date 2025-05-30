from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import IA3Config, get_peft_model
from datasets import load_dataset

model_name = "Qwen/Qwen1.5-0.5B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)


# 设置pad_token为eos_token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    
# 添加IA³
ia3_config = IA3Config(
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    feedforward_modules=["down_proj", "up_proj"],
)
model = get_peft_model(model, ia3_config)

# 数据集
dataset = load_dataset("Abirate/english_quotes", split="train[:50]")

# 数据处理
def tokenize_function(examples):
    return tokenizer(examples["quote"], padding="max_length", truncation=True, max_length=64)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# 训练配置
training_args = TrainingArguments(
    output_dir="./ia3_ft",
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

print("开始IA³微调...")
trainer.train()
print("IA³微调完成！")