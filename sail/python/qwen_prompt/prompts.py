from transformers import AutoTokenizer

# 任务长度列表
task_lengths = [6848, 6752, 6720, 6720, 6784, 6720, 6720, 6720, 8384, 8416, 6080, 6080, 928, 928, 192, 736]


# 初始化分词器
tokenizer_path = 'path_to_your_pretrained_model'  # 你的预训练模型路径
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True)
EOS = tokenizer.eos_token_id

# 读取文本文件
with open('performance_test_case.txt', 'r', encoding='utf-8') as file:
    text = file.read()

# 分词
tokens = tokenizer.encode(text)

# 生成prompts列表
prompts = []
for length in task_lengths:
    # 截取指定长度的tokens，确保不超出文件的tokens总长度
    prompt_tokens = tokens[:length] if length <= len(tokens) else tokens
    # 将tokens解码为文本
    prompt_text = tokenizer.decode(prompt_tokens, clean_up_tokenization_spaces=True)
    # 添加结束符，如果prompt不是以它结束的话
    if not prompt_text.endswith(tokenizer.decode([EOS])):
        prompt_text += tokenizer.decode([EOS])
    prompts.append(prompt_text)

# 现在prompts列表包含了不同长度的prompts文本
