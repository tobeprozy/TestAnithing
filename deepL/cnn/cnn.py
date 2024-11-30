import torch
import torch.nn as nn
import numpy as np

class Net(nn.module):
    def __init__(self):
        super(Net,self).__init__()
        self.conv1=nn.sequential(
            nn.conv2D(1,64,kernal_size=3,padding=1),
            nn.ReLU(),
            nn.con2D(64,128,kernal_size=3,padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernal_size=3, stride=2)
        )
        self.dense=nn.sequential(
            nn.Linear(128*14*14,1024),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(1024,10)
        )
    def forward(self,x):
        layer1=self.conv1(x)
        layer1=layer1.view(-1,128*14*14) # 
        out=self.dense(layer1)
        return out



import torchvision
train_dataset=torchvision.datasets.NMIST(root="Data",train=True,transform=torchvision.transforms.ToTensor(),download=True)
test_dataset=torchvision.datasets.NMIST(root="Data",train=False,transform=torchvision.transforms.ToTensor(),download=True)

train_loader=torch.utils.data.DataLoader(dataset=train_dataset,batch_size=100,shuffle=True)
test_loader=torch.utils.data.DataLoader(dataset=test_dataset,batch_size=100,shuffle=False)

device=torch.device("cuda" if torch.cuda.is_available() else "cpu")


net=Net().to(device)
criterion=nn.CrossEntropyLoss()
optimizer=torch.optim.Adam(net.parameters(),lr=0.001)
# print(net)

import tqdm
num_epochs=5
for epoch in tqdm(range(num_epochs)):
    for idx,(images,labels) in enumerate(train_loader):
        images=images.to(device)
        lables=labels.to(device)
        preds=net(images)
        
        loss=criterion(preds,labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if idx%100==0:
            print(f"Epoch:{epoch},Loss:{loss.item()}")
            
with torch.no_grad():
    total=0
    correct=0
    for idx,(images,labels) in enumerate(test_loader):
        images=images.to(device)
        labels=labels.to(device)
        preds=net(images)
        _,predicted=torch.max(preds.data,1)
        
        total+=labels.size(0)
        correct+=(predicted==labels).sum().item()

    print(f"Accuracy:{correct/total}")
        