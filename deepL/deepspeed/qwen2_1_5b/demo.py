import os
import torch
import deepspeed
import argparse
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    DataCollatorForLanguageModeling,
    Trainer
)
from datasets import load_dataset
from peft import LoraConfig, get_peft_model

# 1. 参数配置
def parse_args():
    parser = argparse.ArgumentParser(description="Qwen2 1.5B DeepSpeed 训练程序")
    
    # 模型参数
    parser.add_argument('--model_name', type=str, default="Qwen/Qwen1.5-1.8B", 
                        help='模型名称或路径')
    parser.add_argument('--dataset_name', type=str, default="wikitext", 
                        help='数据集名称')
    parser.add_argument('--dataset_config', type=str, default="wikitext-103-raw-v1", 
                        help='数据集配置')
    
    # 训练参数
    parser.add_argument('--epochs', type=int, default=1, help='训练轮数')
    parser.add_argument('--batch_size', type=int, default=4, help='批大小')
    parser.add_argument('--seq_length', type=int, default=512, help='序列长度')
    parser.add_argument('--learning_rate', type=float, default=2e-5, help='学习率')
    
    # DeepSpeed 参数
    parser.add_argument('--deepspeed', action='store_true', help='启用DeepSpeed')
    parser.add_argument('--deepspeed_config', type=str, default='ds_config.json', 
                        help='DeepSpeed配置文件路径')
    parser.add_argument('--local_rank', type=int, default=-1, help='本地排名')
    
    # LoRA 参数
    parser.add_argument('--use_lora', action='store_true', help='使用LoRA')
    parser.add_argument('--lora_rank', type=int, default=8, help='LoRA秩')
    parser.add_argument('--lora_alpha', type=int, default=32, help='LoRA alpha')
    parser.add_argument('--lora_dropout', type=float, default=0.1, help='LoRA dropout')
    
    # 输出参数
    parser.add_argument('--output_dir', type=str, default='./qwen_output', 
                        help='输出目录')
    
    return parser.parse_args()

# 2. 加载模型和分词器
def load_model_and_tokenizer(args):
    # 加载分词器
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    # 加载模型
    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        trust_remote_code=True
    )
    
    # 应用LoRA
    if args.use_lora:
        lora_config = LoraConfig(
            r=args.lora_rank,
            lora_alpha=args.lora_alpha,
            lora_dropout=args.lora_dropout,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            task_type="CAUSAL_LM"
        )
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()
    
    return model, tokenizer

# 3. 加载和预处理数据集
def load_and_preprocess_data(args, tokenizer):
    # 加载数据集
    dataset = load_dataset(args.dataset_name, args.dataset_config)
    
    # 预处理函数
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            max_length=args.seq_length,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )
    
    # 应用分词
    tokenized_datasets = dataset.map(
        tokenize_function,
        batched=True,
        num_proc=4,
        remove_columns=["text"]
    )
    
    return tokenized_datasets

# 4. 配置DeepSpeed训练
def configure_deepspeed_trainer(args, model, tokenizer, tokenized_datasets):
    # 数据整理器
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # 训练参数
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        save_strategy="epoch",
        evaluation_strategy="epoch",
        report_to="none",
        bf16=torch.cuda.is_bf16_supported(),
        fp16=not torch.cuda.is_bf16_supported(),
        deepspeed=args.deepspeed_config if args.deepspeed else None
    )
    
    # 创建Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"] if "validation" in tokenized_datasets else None,
        data_collator=data_collator,
        tokenizer=tokenizer
    )
    
    return trainer

# 5. 主函数
def main():
    args = parse_args()
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 加载模型和分词器
    print("加载模型和分词器...")
    model, tokenizer = load_model_and_tokenizer(args)
    
    # 加载和预处理数据
    print("加载和预处理数据集...")
    tokenized_datasets = load_and_preprocess_data(args, tokenizer)
    
    # 配置训练器
    print("配置训练器...")
    trainer = configure_deepspeed_trainer(args, model, tokenizer, tokenized_datasets)
    
    # 开始训练
    print("开始训练...")
    trainer.train()
    
    # 保存最终模型
    print("保存模型...")
    trainer.save_model(os.path.join(args.output_dir, "final_model"))
    
    # 保存分词器
    tokenizer.save_pretrained(os.path.join(args.output_dir, "final_model"))
    
    print("训练完成!")

if __name__ == "__main__":
    main()
