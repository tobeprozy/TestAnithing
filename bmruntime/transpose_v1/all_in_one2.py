def export_onnx():
    import torch
    import torch.onnx
    # 定义自定义的PyTorch模型类
    class Model(torch.nn.Module):
        def __init__(self):
            super(Model, self).__init__()

        def forward(self, x):
            # 执行多维转置操作
            # 这里假设我们要从 (2, 0, 1) 转置到 (0, 2, 1)
            return x.permute(1, 0, 2)  # 此处根据需要修改维度顺序

    # 实例化模型
    model = Model()

    # 创建一个输入张量，这里假设是三维的
    x = torch.randn(2, 3, 4, dtype=torch.float32)

    # 设置模型为评估模式
    model.eval()

    # 设置导出的模型路径和文件名
    model_path = "multi_dim_transpose.onnx"

    # 导出模型
    torch.onnx.export(model,
                      x,                   # 模型输入
                      model_path,          # 模型保存路径
                      export_params=True,  # 带上模型参数
                      opset_version=11,    # ONNX版本，使用11以支持更多功能
                      do_constant_folding=True,  # 是否执行常量折叠优化
                      input_names=['input'],    # 输入名
                      output_names=['output'],    # 输出名
                      dynamic_axes={'input': {0: 'n', 1: 'h', 2: 'w'},
                                    'output': {0: 'n', 1: 'h', 2: 'w'}})  # 动态轴

    print(f"Model has been exported to {model_path}.")


# def mlir():
#     model_transform.py \
#         --model_name matmul \
#         --model_def ../model.onnx \
#         --input_shapes [[1,1000,1000],[1,1000,1000]] \
#         --mlir matmul.mlir \
#         --dynamic_inputs input0,input1 

#     model_deploy.py \
#         --mlir matmul.mlir \
#         --quantize F32 \
#         --chip bm1684x \
#         --model matmul.bmodel \
#         --dynamic
#     return None
def runtime_onnx():

    import onnxruntime
    import numpy as np

    # 1.加载ONNX模型
    session = onnxruntime.InferenceSession("multi_dim_transpose.onnx")

    # 2.获取模型的输入输出信息
    input_names = session.get_inputs()
    output_names = session.get_outputs()

    # 3.准备输入数据
    x0 = np.ones((3,4,5),dtype=np.float32)
    input_dict = {input_names[0].name: x0}

    # 4.推理
    outputs = session.run(None, input_dict)

    # 5.输出结果
    print(outputs[0])

def runtime_sail():

    import sophon.sail as sail
    import numpy as np

    # 1.加载bmodel
    dev_id=0
    net = sail.Engine("./datasets/multi_dim_transpose.bmodel", 
                      dev_id, sail.IOMode.SYSIO)
    
    # 2.获取模型的输入信息
    graph_name = net.get_graph_names()[0]
    input_names = net.get_input_names(graph_name)
    output_names = net.get_output_names(graph_name)

    # 3.准备输入数据
    x0 = np.ones((3,4, 5))
    input_dict = {input_names[0].name: x0}
    # np.savez('input_data.npz', input_data=input_dict)

    # 4.推理
    outputs = net.process(graph_name, input_dict)

    # 5.输出结果
    print(outputs[output_names[0]])
    

def main(args):

    import time
    import torch
    import numpy as np
    import sophon.sail as sail

    net = sail.Engine(args.bmodel, args.dev_id, sail.IOMode.SYSIO)
    graph_name = net.get_graph_names()[0]
    input_names = net.get_input_names(graph_name)

    input1_name = net.get_input_names(graph_name)[0]
    output_names = net.get_output_names(graph_name)[0]

    input1_shape = net.get_input_shape(graph_name, input1_name)
    output_shape = net.get_output_shape(graph_name, output_names)


    x0 = 2* np.ones((3,4,5))
    
    input_dict = {input_names[0]: x0}

    np.savez('input_data.npz', input_data=input_dict)

    start=time.time()
    outputs = net.process(graph_name, input_dict)
    end=time.time()
    print('bmodel rum time:', end-start)

    print(outputs[output_names])

    
    x0 = torch.tensor(x0)
    start=time.time()
    torch_out = x0.permute(x0)
    end=time.time()
    print('torch rum time:', end-start)

    print('torch_out:', torch_out)
    print('bmodel_out:', outputs[output_names])

    runtime_onnx()



def argsparser():
    import argparse
    parser = argparse.ArgumentParser(prog=__file__)
    parser.add_argument('--bmodel', type=str, default='./datasets/matmul.bmodel', help='path of bmodel')
    parser.add_argument('--dev_id', type=int, default=0, help='dev id')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    # export_onnx()
    runtime_onnx()
    # args = argsparser()
    # main(args)
    
    # print('all done.')
