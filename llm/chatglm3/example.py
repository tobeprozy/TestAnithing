# Load model directly
from transformers import AutoModel
model = AutoModel.from_pretrained("THUDM/chatglm3-6b", trust_remote_code=True)


# pip install protobuf transformers==4.30.2 cpm_kernels torch>=2.0 gradio mdtex2html sentencepiece accelerate
from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm3-6b", trust_remote_code=True)
model = AutoModel.from_pretrained("THUDM/chatglm3-6b", trust_remote_code=True).half().cuda()
model = model.eval()

response, history = model.chat(tokenizer, "你好", history=[])
response, history = model.chat(tokenizer, "晚上睡不着应该怎么办", history=history)