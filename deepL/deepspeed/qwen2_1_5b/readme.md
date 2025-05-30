pip install deepspeed transformers datasets peft torch
pip install cryptography==3.4.8

# 使用DeepSpeed训练（推荐）
deepspeed --num_gpus 4 demo.py \
  --deepspeed \
  --deepspeed_config ds_config.json \
  --model_name Qwen/Qwen1.5-0.5B \
  --dataset_name wikitext \
  --dataset_config wikitext-103-raw-v1 \
  --epochs 1 \
  --batch_size 4 \
  --seq_length 512 \
  --use_lora

# 纯CPU训练（仅用于测试）

python demo_cpu.py \
  --model_name Qwen/Qwen1.5-0.5B \
  --dataset_name wikitext \
  --dataset_config wikitext-103-raw-v1 \
  --epochs 1 \
  --batch_size 1 \
  --seq_length 128 \
  --gradient_accumulation_steps 4 \
  --output_dir ./qwen_output_cpu