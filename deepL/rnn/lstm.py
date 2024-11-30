import torch.nn as nn
import torch



class LSTM(nn.Module):
    def __init__(self,input_size,hidden_size):
        super(LSTM,self).__init__()
        self.rnn=nn.LSTM(input_size,hidden_size)
        self.fc=nn.Linear(hidden_size,1)

    def forward(self,x):
        x=x[:,:,None]
        x,_ = self.rnn(x)
        x = self.fc(x)
        x = x[:, :, 0]
        
        return x
    
lstm=LSTM(input_size=1,hidden_size=5)


from pandas_datareader import wb

countries = ['BR','CA','CN','FR','DE','IN','IL','JP','SA','GB','US']
data = wb.download(indicator='NY.GDP.PCAP.KD',country=countries,start=1970,end=2018)
df = data.unstack().T
df.index = df.index.droplevel(0)

df_scaled = df/df.max()

years = df_scaled.index
train_seq_len=sum((years>=1971) & (years<=2000))
test_seq_len=sum(years>=2001)
print("len of train_seq_len:{} len of test_seq_len:{}",train_seq_len,test_seq_len)

inputs=torch.tensor(df_scaled.iloc[:-1].values,dtype=torch.float32)
labels=torch.tensor(df_scaled.iloc[1:].values,dtype=torch.float32)

criterion=nn.MSELoss()
optimizer=torch.optim.Adam(lstm.parameters(),lr=0.01)
train_loss_list,test_loss_list=[],[]

for step in range(10001):
    preds=lstm(inputs)
    train_preds=preds[:train_seq_len]
    test_preds=preds[train_seq_len:]
    train_loss=criterion(train_preds,labels[:train_seq_len])
    
    optimizer.zero_grad()
    train_loss.backward()
    optimizer.step()
    
    test_preds=preds[train_seq_len:]
    test_loss=criterion(test_preds,labels[train_seq_len:])
    
    train_loss_list.append(train_loss)
    test_loss_list.append(test_loss)
    
    if step%500==0:
        print(f"Step:{step},Train Loss:{train_loss},Test Loss:{test_loss}")
        
import matplotlib.pyplot as plt
plt.plot(train_loss_list,label='Train Loss')
plt.plot(test_loss_list,label='Test Loss')
plt.legend()
plt.show()


from IPython.display import display
import pandas as pd
preds=lstm(inputs)
df_pred_scaled=pd.DataFrame(preds.detach().numpy(),index=df_scaled.index[1:],columns=df_scaled.columns)
df_pred=df_pred_scaled*df.loc['2000']
display(df_pred.loc['2001':])