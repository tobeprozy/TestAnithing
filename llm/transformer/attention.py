import torch
import torch.nn as nn


class MultiHeadAttention(nn.Module):
    def __init__(self, hidden_size, num_heads):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_heads=num_heads
        self.head_dim=hidden_size//num_heads
        
        self.Wq=nn.Linear(hidden_size,hidden_size)
        self.Wk=nn.Linear(hidden_size,hidden_size)
        self.Wv=nn.Linear(hidden_size,hidden_size)
        self.Wo=nn.linear(hidden_size,hidden_size)
        
    def forward(self,hidden_state,attention_mask=None):
        bs=hidden_state.shape[0]
        seq_len=hidden_state.shape[1]
        
        query=self.Wq(hidden_state)
        key=self.Wk(hidden_state)
        value=self.Wv(hidden_state)

        query=query.view(bs,seq_len,self.num_heads,self.head_dim).transpose(1,2)    # (bs,num_heads,seq_len,head_dim)
        key=key.view(bs,seq_len,self.num_heads,self.head_dim).transpose(1,2) # (bs,num_heads,seq_len,head_dim)
        value=value.view(bs,seq_len,self.num_heads,self.head_dim).transpose(1,2) # (bs,num_heads,seq_len,head_dim)
        
        attention_scores=torch.matmul(query,key.tranpose(-1,-2))/(self.head_dim**0.5) # (bs,num_heads,seq_len,seq_len)
        
        if attention_mask is not None:
            attention_scores=attention_scores+attention_mask
            
        attention_probs=nn.functional.softmax(attention_scores,dim=-1) # (bs,num_heads,seq_len,seq_len)
        
        attention_output=torch.matmul(attention_probs,value) # (bs,num_heads,seq_len,head_dim)
        
        attention_output=attention_output.transpose(1,2).continguous().view(bs,seq_len,self.hidden_size) # (bs,seq_len,hidden_size)
        
        attention_output=self.Wo(attention_output)
        
        return attention_output
        

class MLP(nn.Module):
    def __init__(self,hidden_size,intermediate_size):
        super().__init__()
        self.fc1=nn.Linear(hidden_size,intermediate_size)
        self.fc2=nn.Linear(hidden_size,intermediate_size)
        
        self.down_proj=nn.Linear(intermediate_size,hidden_size)
        
    def forward(self,hidden_state):
        a1=self.fc1(hidden_state)
        a2=self.fc2(hidden_state)
        a2=nn.functional.silu(a2)
        
        return self.down_proj(a2+a1)  
    
    
if __name__ == "__main__":
    vocab_size=1000
    hidden_size=128
    num_heads=8
    embed_tokens = nn.Embedding(vocab_size, hidden_size)