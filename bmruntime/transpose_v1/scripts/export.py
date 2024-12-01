import torch
import torch.nn.functional as F
import numpy as np

class Model(torch.nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, mask_info, output1, rect, m_confThreshold):
        '''
            mask_info 1 * box_size * 32
            output1   1 * 32 * 160 * 160
            rect      1 * 6  --> x1,y1,x2,y2,origin_w,origin_h
            yoloboxs  1 * box_size * 4 --> x1,y1,x2,y2
            m_confThreshold   1 * 1
        '''
        ptotos = output1[0].view(32, -1)
 
        feature = torch.matmul(mask_info, ptotos)
        feature_uint8= torch.clamp(feature.mul(255).to(torch.uint8),min=0,max=255)
    
        return feature_uint8

mask_info=torch.rand(1,1,32)
output1=torch.rand(1,32,160,160)
rect = torch.tensor([[2,3,67,90,324,456]])
m_confThreshold = torch.tensor([[0.5]])

ret = {"mask_info":mask_info,"output1":output1,"rect":rect,"m_confThreshold":m_confThreshold}
model = Model()

torch.onnx.export(
    model,    
    (mask_info,output1,rect,m_confThreshold),
    "yolov8_int8_getmask_32.onnx",
    verbose=True, 
    input_names=["mask_info", "output1","rect","m_confThreshold"], 
    output_names=["output"], 
    opset_version=11,
    dynamic_axes={
        "mask_info": { 1:"num"},
        "output": {1:"num"}
    }
)