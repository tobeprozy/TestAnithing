from transformers import BertTokenizer, BertModel
import torch

# 初始化分词器和模型
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# 编码文本
text = "Here is some text to encode"
encoded_input = tokenizer(text, return_tensors='pt')

# 生成文本的隐藏状态
with torch.no_grad():
    output = model(**encoded_input)

# 获取编码的最后一层的输出
last_hidden_states = output.last_hidden_state

print(last_hidden_states)

