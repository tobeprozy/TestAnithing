import torch
import torchvision.models as models

def print_resnet_structure(resnet_type):
    """
    打印指定类型的 ResNet 模型结构。
    
    参数:
    resnet_type (str): 可以是 'resnet18', 'resnet34', 'resnet50', 'resnet101', 或 'resnet152'
    """
    # 根据类型获取 ResNet 模型
    if resnet_type == 'resnet18':
        model = models.resnet18(pretrained=True)
    elif resnet_type == 'resnet34':
        model = models.resnet34(pretrained=True)
    elif resnet_type == 'resnet50':
        model = models.resnet50(pretrained=True)
    elif resnet_type == 'resnet101':
        model = models.resnet101(pretrained=True)
    elif resnet_type == 'resnet152':
        model = models.resnet152(pretrained=True)
    else:
        print("Unsupported ResNet type. Please choose from 'resnet18', 'resnet34', 'resnet50', 'resnet101', or 'resnet152'.")
        return

    # 打印模型结构
    print(model)

# 示例：打印 ResNet-50 的结构
print_resnet_structure('resnet50')

