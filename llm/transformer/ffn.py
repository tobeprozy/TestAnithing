import torch
import torch.nn as nn
import torch.nn.functional as F

class ResNetBlockFNN(nn.module):
    def __init__(self,input_dim):
        super().__init__()
        
        self.fc1=nn.Linear(input_dim,input_dim)
        self.fc2=nn.Linear(input_dim,input_dim) 
        
    def forward(self,x):
        hidden_state=self.fc1(x)
        hidden_state=F.relu(hidden_state)
        output=self.fc2(hidden_state)
        
        output=output+x
        return output
        
        
class TransformerFFN(nn.Module):
    def __init__(self,hidden_size,intermediate_size):
        super().__init()
        
        self.fc1=nn.Linear(hidden_size,intermediate_size)
        self.fc2=nn.Linear(intermediate_size,hidden_size)
        
    def forward(self,x):
        hidden_state=self.fc1(x)  # first fully connected layer

        hidden_state=F.gelu(hidden_state)  # GELU activation function
        output=self.fc2(hidden_state)  # second fully connected layer
        
        output=output+x  # residual connection
        return output
    
    
    
def layer_norm(input_tensor):
    # 手写layer norm
    # input_tensor: (batch_size,seq_len,hidden_size)
    # mean
    mean=input_tensor.mean(dim=-1,keepdim=True)
    # std
    std=input_tensor.std(dim=-1,keepdim=True)
    # normalize
    normalized_tensor=(input_tensor-mean)/std
    
    return normalized_tensor
    