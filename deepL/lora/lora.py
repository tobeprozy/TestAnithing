import torch
import torch.nn as nn
from peft import LoraConfig,get_peft_model


def export_onnx(model,input_shape,output_path):
    model.eval()
    dummy_input=torch.randn(input_shape)
    torch.onnx.export(model,dummy_input,output_path,input_names=["input"],output_names=["output"])


net=nn.Sequential(nn.Linear(20,20))

print(net)
# export_onnx(net,(1,20),"net.onnx")

config=LoraConfig(target_modules=['0'])
net_lora=get_peft_model(net,config)

# print(net)
# net = net_lora.merge_and_unload() # 拆除Lora
# print(net)

print(net_lora)
# export_onnx(net_lora,(1,20),"net_lora.onnx")