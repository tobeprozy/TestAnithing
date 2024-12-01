import argparse
import numpy as np
import sophon.sail as sail
import torch
import torch.nn.functional as F
import numpy as np

def exportonnx():
    import torch
    import torch.onnx

    # 定义自定义的PyTorch模型类
    class Model(torch.nn.Module):
        def __init__(self):
            super().__init__()

        def forward(self, x0, x1):
            # 执行矩阵乘法
            x = torch.matmul(x0, x1)
            return x

    # 创建随机张量，这里假设第二和第三维度是动态的，可以根据需要调整
    x0 = torch.randn(1, 32, 160)
    x1 = torch.randn(1, 160, 10)  # 保持第一维度与x0的第三维度相同

    # 初始化模型
    model = Model()

    # 导出模型到ONNX格式
    # 注意：你必须提供保存ONNX模型的路径
    torch.onnx.export(model,               # 运行的模型
                      (x0, x1),            # 模型输入（或多个输入时的元组）
                      "model.onnx",        # 保存模型的位置
                      export_params=True,  # 将训练后的参数权重存储在模型文件中
                      opset_version=11,    # 要导出的ONNX版本
                      do_constant_folding=True,  # 是否执行常量折叠以优化
                      input_names=['input0', 'input1'],   # 模型的输入名
                      output_names=['output'],            # 模型的输出名
                      dynamic_axes={'input0': {0: 'batch_size', 1: 'x0_dim_1', 2: 'x0_dim_2'},
                                     'input1': {0: 'batch_size', 1: 'x1_dim_1', 2: 'x1_dim_2'},
                                     'output': {0: 'batch_size', 1: 'output_dim_1', 2: 'output_dim_2'}})

def mlir():
    # model_paraform.py \
    # --model_name matmul \
    # --model_def ../yolov8_getmask.onnx \
    # --input_shapes [[1,1000,1000],[1,1000,1000]] \
    # --mlir matmul.mlir \
    # --dynamic_inputs num 


    # model_deploy.py \
    #     --mlir matmul.mlir \
    #     --quantize F32 \
    #     --chip bm1684x \
    #     --model matmul.bmodel \
    #     --dynamic
    return None
def main(args):

    import time
   
    net = sail.Engine(args.bmodel, args.dev_id, sail.IOMode.SYSIO)
    graph_name = net.get_graph_names()[0]
    input1_name = net.get_input_names(graph_name)[0]
    input2_name = net.get_input_names(graph_name)[1]
    output_names = net.get_output_names(graph_name)[0]

    input1_shape = net.get_input_shape(graph_name, input1_name)
    input2_shape = net.get_input_shape(graph_name, input2_name)
    output_shape = net.get_output_shape(graph_name, output_names)


    x0 = 2* np.ones((1,180, 160))
    x1 = np.ones((1,2,180))
    
    input_data = {input1_name: x0,input2_name: x1}

    np.savez('input_data.npz', input_data=input_data)

    start=time.time()
    outputs = net.process(graph_name, input_data)
    end=time.time()
    print('bmodel rum time:', end-start)

    
    mask_info = torch.tensor(x0)
    ptotos = torch.tensor(x1)
    start=time.time()
    x = torch.matmul(mask_info, ptotos)
    end=time.time()
    print('torch rum time:', end-start)



def argsparser():
    parser = argparse.ArgumentParser(prog=__file__)
    parser.add_argument('--bmodel', type=str, default='matmul.bmodel', help='path of bmodel')
    parser.add_argument('--dev_id', type=int, default=0, help='dev id')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    # args = argsparser()
    # main(args)
    # exportonnx()
    print('all done.')
