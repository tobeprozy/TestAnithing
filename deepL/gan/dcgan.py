import torch.nn as nn
import torch
import torchvision

train_dataset=torchvision.datasets.NMIST(root="Data",train=True,transform=torchvision.transforms.ToTensor(),download=True)
test_dataset=torchvision.datasets.NMIST(root="Data",train=False,transform=torchvision.transforms.ToTensor(),download=True)

train_loader=torch.utils.data.DataLoader(dataset=train_dataset,batch_size=100,shuffle=True)
test_loader=torch.utils.data.DataLoader(dataset=test_dataset,batch_size=100,shuffle=False)

dataset=torchvision.datasets.CIFAR10(root="Data",train=True,transform=torchvision.transforms.ToTensor(),download=True)
dataloader=torch.utils.data.DataLoader(dataset,batch_size=100,shuffle=True)

for idx,data in enumerate(dataloader):
    images,_=data
    
    batch_size=images.size(0)
    print("# {} has {} images".format(idx,batch_size))
    
    if idx%100==0:
        path="Data/CIFAR10_batch{:03d}.pt".format(idx)
        torchvision.utils.save_image(images,path,nornalize=True)
        
        

        
latent_size=64
n_channels=3
n_g_features=64

gnet=nn.Sequential(
    nn.ConvTranspose2d(latent_size,4*n_g_features,kernal_size=4,bias=False),
    nn.BatchNorm2d(4*n_g_features),
    nn.ReLU(),
    nn.ConvTranspose2d(4*n_g_features,2*n_g_features,kernal_size=4,stride=2,padding=1,bias=False),
    nn.BatchNorm2d(2*n_g_features),
    nn.ReLU(),
    nn.ConvTranspose2d(2*n_g_features,n_g_features,kernal_size=4,stride=2,padding=1,bias=False),
    nn.BatchNorm2d(n_g_features),
    nn.ReLU()
    nn.ConvTranspose2d(n_g_features,n_channels,kernal_size=4,stride=2,padding=1,bias=False),
    nn.Tanh()
)


n_d_features=64

dnet=nn.Sequential( 
    nn.Conv2d(n_channels,n_d_features,kernal_size=4,stride=2,padding=1),
    nn.LeakyReLU(0.2),
    nn.Conv2d(n_d_features,2*n_d_features,kernal_size=4,stride=2,padding=1,bias=False),
    nn.BatchNorm2d(2*n_d_features),
    nn.LeakyReLU(0.2),
    nn.Conv2d(2*n_d_features,4*n_d_features,kernal_size=4,stride=2,padding=1,bias=False),
    nn.BatchNorm2d(4*n_d_features),
    nn.LeakyReLU(0.2),
    nn.Conv2d(4*n_d_features,1,kernal_size=4,stride=2,padding=1)
)

import torch.nn.init as init
import torch.optim as optim

def weight_init(m):
    if type(m) in [nn.ConvTranspose2d,nn.Conv2d]:
        init.xavier_normal_(m.weight)
    elif type(m) == nn.BatchNorm2d:
        init.normal_(m.weight,1.0,0.02)
        init.constant_(m.bias,0)
        
gnet.apply(weight_init)
dnet.apply(weight_init)


criterion=nn.BCEWithLogitsLoss()

goptimizer_g=optim.Adam(gnet.parameters(),lr=0.0002,betas=(0.5,0.999))
doptimizer_d=optim.Adam(dnet.parameters(),lr=0.0002,betas=(0.5,0.999))

batch_size=64
noises=torch.randn(batch_size,latent_size,1,1)
epoch_num=10

for epoch in range(epoch_num):
    for idx,data in enumerate(dataloader):
        images,_=data

        batch_size=images.size(0)

        labels=torch.ones(batch_size)
        preds=dnet(images)
        outputs=preds.reshape(-1)
        
        d_loss_real=criterion(outputs,labels)
        d_mean_real=outputs.sigmoid().mean()
        
        noises=torch.randn(batch_size,latent_size,1,1)
        fake_images=gnet(noises)
        
        labels=torch.zeros(batch_size)
        preds=dnet(fake_images)
        outputs=preds.reshape(-1)

        d_loss_fake=criterion(outputs,labels)
        d_mean_fake=outputs.sigmoid().mean()

        d_loss=d_loss_real+d_loss_fake
        doptimizer_d.zero_grad()
        d_loss.backward()
        doptimizer_d.step()
        
        
        labels=torch.ones(batch_size)
        preds=dnet(fake_images)
        outputs=preds.reshape(-1)

        g_loss=criterion(outputs,labels)
        g_mean_fake=outputs.sigmoid().mean()

        goptimizer_g.zero_grad()
        g_loss.backward()
        goptimizer_g.step()
        
        print('[{}/{}]'.format(epoch,epoch_num)+'[{}/{}]'.format(idx,len(dataloader)))
        print('d_loss:{:g},g_loss:{:g}'.format(d_loss,g_loss))
        print('TPR:{:g},FPR:{:g}/{:g}'.format(d_mean_real,d_mean_fake,g_mean))

        if idx % 100 == 0:
            fake = gnet(noises)
            path = 'Data/images_epoch{:02d}_batch{:03d}.png'.format(epoch,idx)
            torchvision.utils.save_image(fake,path,normalize=True)