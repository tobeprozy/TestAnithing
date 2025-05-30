import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
import deepspeed
import argparse

# 1. 定义简单神经网络
class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, 3)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(16 * 13 * 13, 10)
    
    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = torch.flatten(x, 1)
        return self.fc1(x)

# 2. 准备数据集
def get_data():
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])
    
    train_set = torchvision.datasets.MNIST(
        root='./data', train=True, download=True, transform=transform)
    test_set = torchvision.datasets.MNIST(
        root='./data', train=False, download=True, transform=transform)
    
    return (
        torch.utils.data.DataLoader(train_set, batch_size=32, shuffle=True),
        torch.utils.data.DataLoader(test_set, batch_size=32, shuffle=False)
    )

# 3. 训练函数
def train(args):
    train_loader, _ = get_data()
    model = SimpleCNN()
    
    engine, _, _, _ = deepspeed.initialize(
        args=args,
        model=model,
        model_parameters=model.parameters()
    )
    
    for epoch in range(2):
        for i, (inputs, labels) in enumerate(train_loader):
            inputs = inputs.to(engine.device)
            labels = labels.to(engine.device)
            
            outputs = engine(inputs)
            loss = nn.CrossEntropyLoss()(outputs, labels)
            
            engine.backward(loss)
            engine.step()
            
            if i % 100 == 0:
                print(f'Epoch [{epoch+1}/2], Step [{i}], Loss: {loss.item():.4f}')
    
    engine.save_checkpoint('./output')
    print("训练完成，模型已保存")

# 4. 推理函数
def infer(args):
    _, test_loader = get_data()
    model = SimpleCNN()
    
    engine, _, _, _ = deepspeed.initialize(
        args=args,
        model=model,
        model_parameters=model.parameters()
    )
    
    engine.load_checkpoint('./output')
    engine.eval()
    
    correct = total = 0
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(engine.device)
            labels = labels.to(engine.device)
            
            outputs = engine(images)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    print(f'测试准确率: {100 * correct / total:.2f}%')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--deepspeed', action='store_true')
    parser.add_argument('--deepspeed_config', default='config.json')
    parser.add_argument('--local_rank', type=int, default=-1)
    parser.add_argument('--mode', choices=['train','infer'], default='train')
    
    args = parser.parse_args()
    
    if args.mode == 'train':
        train(args)
    else:
        infer(args)