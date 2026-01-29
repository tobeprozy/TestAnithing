from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PromptTuningConfig, TaskType, get_peft_model,PromptTuningInit


tokenizer = AutoTokenizer.from_pretrained("Langboat/bloom-1b4-zh")

model = AutoModelForCausalLM.from_pretrained("Langboat/bloom-1b4-zh", low_cpu_mem_usage=True)
print(model)
# 设置 Prompt-Tuning
# Soft Prompt
# config = PromptTuningConfig(task_type=TaskType.CAUSAL_LM, num_virtual_tokens=10) # soft_prompt会随机初始化
# Hard Prompt
config = PromptTuningConfig(task_type = TaskType.CAUSAL_LM,
                            prompt_tuning_init = PromptTuningInit.TEXT,
                            prompt_tuning_init_text = "下面是一段人与机器人的对话。", # 设置hard_prompt的具体内容
                            num_virtual_tokens = len(tokenizer("下面是一段人与机器人的对话。")["input_ids"]),
                            tokenizer_name_or_path = "Langboat/bloom-1b4-zh")
model = get_peft_model(model, config) # 生成Prompt-Tuning对应的model
print(model)
print(model.print_trainable_parameters())