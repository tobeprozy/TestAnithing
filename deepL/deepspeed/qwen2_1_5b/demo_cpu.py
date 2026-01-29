import os
import torch
import argparse
import logging
import numpy as np
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    DataCollatorForLanguageModeling,
    Trainer
)
from datasets import load_dataset, Dataset
from typing import Dict, List, Any

# 禁用所有 GPU 相关操作
os.environ["CUDA_VISIBLE_DEVICES"] = ""
torch.cuda.is_available = lambda: False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 1. 参数配置
def parse_args():
    parser = argparse.ArgumentParser(description="Qwen2 1.5B CPU 训练程序")
    
    # 模型参数
    parser.add_argument('--model_name', type=str, default="Qwen/Qwen1.5-0.5B", 
                        help='模型名称或路径')
    parser.add_argument('--dataset_name', type=str, default="wikitext", 
                        help='数据集名称')
    parser.add_argument('--dataset_config', type=str, default="wikitext-103-raw-v1", 
                        help='数据集配置')
    
    # 训练参数
    parser.add_argument('--epochs', type=int, default=1, help='训练轮数')
    parser.add_argument('--batch_size', type=int, default=1, help='批大小')
    parser.add_argument('--seq_length', type=int, default=128, help='序列长度')
    parser.add_argument('--learning_rate', type=float, default=2e-5, help='学习率')
    parser.add_argument('--gradient_accumulation_steps', type=int, default=4, 
                        help='梯度累积步数')
    
    # 输出参数
    parser.add_argument('--output_dir', type=str, default='./qwen_output_cpu', 
                        help='输出目录')
    
    return parser.parse_args()

# 2. 加载模型和分词器
def load_model_and_tokenizer(args):
    logger.info("加载模型和分词器...")
    
    # 加载分词器
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # 加载模型 - 使用 float32 在 CPU 上训练
    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        torch_dtype=torch.float32,
        trust_remote_code=True
    )
    
    logger.info(f"模型 '{args.model_name}' 加载完成")
    logger.info(f"模型参数数量: {model.num_parameters():,}")
    return model, tokenizer

# 3. 自定义数据处理函数
def tokenize_function(examples: Dict[str, List[Any]], tokenizer, seq_length: int) -> Dict[str, List[Any]]:
    """自定义分词函数，确保返回统一长度的序列"""
    # 过滤空文本
    texts = [text for text in examples["text"] if text and text.strip()]
    if not texts:
        return {"input_ids": [], "attention_mask": []}
    
    # 分词
    tokenized = tokenizer(
        texts,
        max_length=seq_length,
        truncation=True,
        padding="max_length",  # 确保填充到固定长度
        return_tensors=None  # 返回字典而不是张量
    )
    
    return tokenized

# 4. 加载和预处理数据集
def load_and_preprocess_data(args, tokenizer):
    logger.info("加载和预处理数据集...")
    
    try:
        # 加载数据集
        dataset = load_dataset(args.dataset_name, args.dataset_config)
        logger.info(f"数据集 '{args.dataset_name}/{args.dataset_config}' 加载完成")
    except Exception as e:
        logger.error(f"加载数据集失败: {e}")
        raise
    
    # 获取CPU核心数用于并行处理
    num_proc = max(1, os.cpu_count() // 2)
    
    # 应用分词 - 使用自定义函数
    tokenized_datasets = dataset.map(
        lambda examples: tokenize_function(examples, tokenizer, args.seq_length),
        batched=True,
        num_proc=num_proc,
        remove_columns=["text"],
        desc="分词数据集"
    )
    
    # 过滤掉空样本
    tokenized_datasets = tokenized_datasets.filter(
        lambda example: len(example.get("input_ids", [])) > 0,
        num_proc=num_proc,
        desc="过滤空样本"
    )
    
    # 手动转换为PyTorch格式
    def convert_to_tensors(example):
        return {
            "input_ids": torch.tensor(example["input_ids"], dtype=torch.long),
            "attention_mask": torch.tensor(example["attention_mask"], dtype=torch.long)
        }
    
    tokenized_datasets = tokenized_datasets.map(
        convert_to_tensors,
        num_proc=num_proc,
        desc="转换为张量"
    )
    
    logger.info("数据集预处理完成")
    return tokenized_datasets

# 5. 配置训练器
def configure_trainer(args, model, tokenizer, tokenized_datasets):
    logger.info("配置训练器...")
    
    # 数据整理器
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # 训练参数 - 完全针对CPU优化
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        save_strategy="steps",
        save_steps=100,
        evaluation_strategy="no",  # CPU上禁用评估以节省时间
        report_to="none",
        no_cuda=True,  # 强制使用 CPU
        fp16=False,     # 在 CPU 上禁用 FP16
        bf16=False,     # 在 CPU 上禁用 BF16
        optim="adamw_torch",  # 使用CPU优化的优化器
        ddp_find_unused_parameters=False,
        remove_unused_columns=False,  # 防止数据集列丢失
        log_level="warning",  # 减少日志输出
        disable_tqdm=True    # 禁用进度条减少开销
    )
    
    # 创建Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        data_collator=data_collator,
        tokenizer=tokenizer
    )
    
    return trainer

# 6. 主函数
def main():
    args = parse_args()
    
    logger.info("="*50)
    logger.info(f"开始 Qwen2 CPU 训练")
    logger.info(f"模型: {args.model_name}")
    logger.info(f"数据集: {args.dataset_name}/{args.dataset_config}")
    logger.info(f"序列长度: {args.seq_length}")
    logger.info(f"批大小: {args.batch_size}")
    logger.info(f"梯度累积步数: {args.gradient_accumulation_steps}")
    logger.info(f"学习率: {args.learning_rate}")
    logger.info(f"输出目录: {args.output_dir}")
    logger.info("="*50)
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        # 加载模型和分词器
        model, tokenizer = load_model_and_tokenizer(args)
        
        # 加载和预处理数据
        tokenized_datasets = load_and_preprocess_data(args, tokenizer)
        
        # 配置训练器
        trainer = configure_trainer(args, model, tokenizer, tokenized_datasets)
        
        # 开始训练
        logger.info("开始训练...")
        trainer.train()
        
        # 保存最终模型
        logger.info("训练完成，保存模型...")
        model.save_pretrained(os.path.join(args.output_dir, "final_model"))
        tokenizer.save_pretrained(os.path.join(args.output_dir, "final_model"))
        
        logger.info(f"模型已保存到 {os.path.join(args.output_dir, 'final_model')}")
        logger.info("训练成功完成!")
        
    except Exception as e:
        logger.error(f"训练失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        logger.error("训练过程中断，请检查错误信息")

if __name__ == "__main__":
    main()