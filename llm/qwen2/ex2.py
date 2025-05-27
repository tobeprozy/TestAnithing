from transformers import pipeline

pipe = pipeline("text-generation", model="./Qwen2-7B-Instruct")
messages = [
        {"role": "user", "content": "Who are you? I"},
]
repose=pipe(messages)
print(repose)

import numpy as np 
import torch
# np.save("input_ids.npy", input_ids)
# np.save("hidden_states.npy", hidden_states)
hidden_states = np.load("hidden_states.npy")
input_ids = np.load("input_ids.npy")

oring_model = pipe.model
transformer = origin_model.model
layers = transformer.layers

class LmHead(torch.nn.Module):

    def __init__(self):
        super().__init__()

    def forward(self, hidden_states):
        hidden_states = transformer.norm(hidden_states)
        m_logits = origin_model.lm_head(hidden_states)
        return m_logits
    

class GreedyHead(torch.nn.Module):

    def __init__(self):
        super().__init__()

    def forward(self, m_logits):
        _, token = torch.topk(m_logits.float(), 1)
        return token
    
lm_head = LmHead()
greedy_head = GreedyHead()

m_logits = lm_head(hidden_states)
token = greedy_head(m_logits)
print(token)

