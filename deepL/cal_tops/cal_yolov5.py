import torch 
from thop import profile
from ultralytics import YOLO
# Load a model
model = YOLO("yolov10s.pt")  # 载入预训练模型

# 获取底层的 PyTorch 模型
pytorch_model = model.model

# 确保模型处于评估模式
pytorch_model.eval()

# 创建输入张量
input_tensor = torch.randn(1, 3, 640, 640)  # 输入尺寸为 640x640

# 计算 FLOPs 和参数数量
flops, params = profile(pytorch_model, inputs=(input_tensor,), verbose=False)
print(f"FLOPs: {flops / 1e9:.2f} GFLOPs")
print(f"Parameters: {params / 1e6:.2f}M")



from torchinfo import summary
summary(model, input_size=(1, 3, 640, 640))



# FLOPs 的计算：
# 在深度学习中，FLOPs 通常是指模型在一次前向传播过程中需要执行的浮点运算次数。
# 例如，一个简单的卷积层的 FLOPs 可以通过以下公式计算：
# FLOPs = 2 × 输入通道数 ×(卷积核高度 × 卷积核宽度) × 输出通道数 × (输出高度 × 输出宽度)
# 这里的 2 表示每次卷积操作需要一次乘法和一次加法。
# FLOPs 的单位：
# FLOPs：浮点运算次数。
# GFLOPs：十亿次浮点运算（10^9 FLOPs）。
# TFLOPs：万亿次浮点运算（10^12 FLOPs）。