import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
import torch

num_epochs=30
batch_size=100
learning_rate=0.001

transform=transforms.Compose(
    [
        transforms.Pad(4),
        transforms.RandomHorizontalFlip(),
        transforms.RandomCrop(32),
        transforms.ToTensor(),
    ]
)


train_dataset=torchvision.datasets.CIFAR10(root="Data",train=True,transform=transform,download=True)
test_dataset=torchvision.datasets.CIFAR10(root="Data",train=False,transform=transforms.ToTensor(),download=True)

train_loader=torch.utils.data.DataLoader(dataset=train_dataset,batch_size=batch_size,shuffle=True)
test_loader=torch.utils.data.DataLoader(dataset=test_dataset,batch_size=batch_size,shuffle=False)

device=torch.device("cuda" if torch.cuda.is_available() else "cpu")

class ResidualBlock(nn.Module):
    def __init__(self,in_channels,out_channels,stride,downsample=None):
        super(ResidualBlock,self).__init__()
        self.conv1=nn.Conv2d(in_channels,out_channels,kernal_size=3,stride=stride,padding=1)
        self.batchnorm1=nn.BatchNorm2d(out_channels)
        self.relu=nn.ReLU()
        self.conv2=nn.Conv2d(out_channels,out_channels,kernal_size=3,stride=1,padding=1)
        self.batchnorm2=nn.BatchNorm2d(out_channels)
        self.downsample=downsample
    def forward(self,x):
        residual=x
        out=self.conv1(x)
        out=self.batchnorm1(out)
        out=self.relu(out)
        out=self.conv2(out)
        out=self.batchnorm2(out)
        if self.downsample:
            residual=self.downsample(x)
        out+=residual
        out=self.relu(out)
        return out
        
class ResNet(nn.Module):
    def __init__(self,block,num_classes=10):
        super(ResNet,self).__init__()
        self.in_channels=16
        
        self.conv1=nn.conv2D(3,16,kernal_size=3,stride=1,padding=1)
        self.batchnorm1=nn.BatchNorm2d(16)
        self.relu=nn.ReLU()
        
        self.res_block1=self.make_layer(block,16,1)
        self.res_block2=self.make_layer(block,16,1)
        self.res_block3=self.make_layer(block,32,2)
        self.res_block4=self.make_layer(block,32,1)
        self.res_block5=self.make_layer(block,64,2)
        self.res_block6=self.make_layer(block,64,1)

        self.avg_pool=nn.AvgPool2d(8)
        self.fc=nn.Linear(64,num_classes)
        
        
    def make_layer(self,block,out_channels,stride=1):
        downsample=None
        if stride!=1 or self.in_channels!=out_channels:
            downsample=nn.Sequential(
                nn.Conv2d(self.in_channels,out_channels,kernal_size=3,stride=stride,padding=1),
                nn.BatchNorm2d(out_channels)
            )
        out_layer=block(self.in_channels,out_channels,stride,downsample)
        self.in_channels=out_channels
        return out_layer
    
    def forwoard(self,x):
        out=self.conv1(x)
        out=self.batchnorm1(out)
        out=self.relu(out)
        out=self.res_block1(out)
        out=self.res_block2(out)
        out=self.res_block3(out)
        out=self.res_block4(out)
        out=self.res_block5(out)
        out=self.res_block6(out)    
        out=self.avg_pool(out)
        out=out.view(out.size(0),-1)
        out=self.fc(out)
        return out
    
    
reset=ResNet(ResidualBlock).to(device)
criterion=nn.CrossEntropyLoss()
optimizer=torch.optim.Adam(reset.parameters(),lr=learning_rate)

def update_lr(optimizer,lr):
    for param_group in optimizer.param_groups:
        param_group['lr']=lr
        
total_step=len(train_loader)
cur_lr=learning_rate

for epoch in range(num_epochs):
    for idx,(images,labels) in enumerate(train_loader):
        images=images.to(device)
        labels=labels.to(device)
        preds=reset(images)
        
        loss=criterion(preds,labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if (idx+1)%100==0:
            print("Epoch:[{}/{}], Step[{}/{}], Loss:{:.4f}".format(epoch+1,num_epochs,idx+1,total_step,loss.item()))
            
    # Decay learning rate
    if epoch%20==0:
        cur_lr/=3
        update_lr(optimizer,cur_lr)            
            
            
with torch.no_grad():
    correct=0
    total=0
    for images,labels in test_loader:
        images=images.to(device)
        labels=labels.to(device)
        preds=reset(images)
        _,predicted=torch.max(preds.data,1)
        total+=labels.size(0)
        correct+=(predicted==labels).sum().item()
    print("Accuracy of the model on the test images: {} %".format(100*correct/total))