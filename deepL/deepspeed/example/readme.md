
# DeepSpeed

DeepSpeed is a deep learning optimization library that makes distributed training easy, efficient, and effective. It achieves high performance by combining the best of both worlds: performance optimizations and model parallelism.

## Install
pip install deepspeed torch torchvision


# train 
```bash
deepspeed --num_gpus 0 demo.py \
  --deepspeed \
  --deepspeed_config config.json \
  --mode train
```

# infer 
```bash
deepspeed --num_gpus 0 demo.py \
  --deepspeed \
  --deepspeed_config config.json \
  --mode infer
```