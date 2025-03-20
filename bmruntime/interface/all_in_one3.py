    import torch
    import torch.onnx
import numpy as np
import time
import argparse
import os
import onnxruntime
import sophon.sail as sail
import sys

# 新增导入语句 - 根据实际安装情况可能需要调整
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("警告: TensorFlow未安装，TensorFlow推理将被禁用")

try:
    import tensorrt as trt
    import pycuda.autoinit
    import pycuda.driver as cuda
    TENSORRT_AVAILABLE = True
except ImportError:
    TENSORRT_AVAILABLE = False
    print("警告: TensorRT或CUDA未安装，TensorRT推理将被禁用")

try:
    from openvino.runtime import Core
    OPENVINO_AVAILABLE = True
except ImportError:
    OPENVINO_AVAILABLE = False
    print("警告: OpenVINO未安装，OpenVINO推理将被禁用")

try:
    import paddle
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    print("警告: PaddlePaddle未安装，PaddlePaddle推理将被禁用")

try:
    import ncnn
    NCNN_AVAILABLE = True
except ImportError:
    NCNN_AVAILABLE = False
    print("警告: NCNN未安装，NCNN推理将被禁用")


def export_onnx(onnx_path="matmul.onnx", batch_size=1, dim1=32, dim2=160, dim3=10):
    """
    导出简单的矩阵乘法模型为ONNX格式。
    
    参数:
        onnx_path: 保存ONNX模型的路径
        batch_size: 输入张量的批次大小
        dim1, dim2, dim3: 矩阵乘法的维度
    """
    # 定义自定义PyTorch模型类
    class MatMulModel(torch.nn.Module):
        def __init__(self):
            super().__init__()

        def forward(self, x0, x1):
            return torch.matmul(x0, x1)

    # 创建指定维度的随机张量
    x0 = torch.randn(batch_size, dim1, dim2)
    x1 = torch.randn(batch_size, dim2, dim3)

    # 初始化模型
    model = MatMulModel()

    # 导出模型为ONNX格式
    torch.onnx.export(
        model,
        (x0, x1),
        onnx_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input0', 'input1'],
        output_names=['output'],
        dynamic_axes={
            'input0': {0: 'batch_size', 1: 'x0_dim_1', 2: 'x0_dim_2'},
                                     'input1': {0: 'batch_size', 1: 'x1_dim_1', 2: 'x1_dim_2'},
            'output': {0: 'batch_size', 1: 'output_dim_1', 2: 'output_dim_2'}
        }
    )
    print(f"ONNX模型已导出到 {onnx_path}")
    return True


def convert_to_tensorrt(onnx_path, trt_path, precision="FP32"):
    """
    将ONNX模型转换为TensorRT引擎。
    
    参数:
        onnx_path: ONNX模型路径
        trt_path: 保存TensorRT引擎的路径
        precision: 精度模式，可选"FP32"、"FP16"或"INT8"
    """
    if not TENSORRT_AVAILABLE:
        raise ImportError("TensorRT未安装，无法转换模型")
    
    # 创建TensorRT logger、builder和网络
    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)
    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    
    # 解析ONNX模型
    parser = trt.OnnxParser(network, logger)
    with open(onnx_path, 'rb') as model:
        if not parser.parse(model.read()):
            for error in range(parser.num_errors):
                print(f"TensorRT ONNX解析错误: {parser.get_error(error)}")
            return False
    
    # 配置builder
    config = builder.create_builder_config()
    config.max_workspace_size = 1 << 30  # 1 GB
    
    # 设置精度模式
    if precision == "FP16" and builder.platform_has_fast_fp16:
        config.set_flag(trt.BuilderFlag.FP16)
    elif precision == "INT8" and builder.platform_has_fast_int8:
        config.set_flag(trt.BuilderFlag.INT8)
    
    # 构建和保存引擎
    serialized_engine = builder.build_serialized_network(network, config)
    with open(trt_path, "wb") as f:
        f.write(serialized_engine)
    
    print(f"TensorRT引擎已导出到 {trt_path}")
    return True


def convert_to_openvino(onnx_path, ir_path):
    """
    将ONNX模型转换为OpenVINO IR格式。
    
    参数:
        onnx_path: ONNX模型路径
        ir_path: 保存OpenVINO IR的路径前缀（不包括扩展名）
    """
    if not OPENVINO_AVAILABLE:
        raise ImportError("OpenVINO未安装，无法转换模型")
    
    try:
        from openvino.tools import mo
        mo.convert_model(onnx_path, output_model=ir_path)
        print(f"OpenVINO IR模型已导出到 {ir_path}")
        return True
    except Exception as e:
        print(f"OpenVINO模型转换失败: {e}")
        return False


def convert_to_paddle(onnx_path, paddle_path):
    """
    将ONNX模型转换为PaddlePaddle模型。
    
    参数:
        onnx_path: ONNX模型路径
        paddle_path: 保存PaddlePaddle模型的路径
    """
    if not PADDLE_AVAILABLE:
        raise ImportError("PaddlePaddle未安装，无法转换模型")
    
    try:
        import paddle2onnx
        paddle2onnx.export(
            onnx_path,
            paddle_path,
            opset_version=11,
            enable_onnx_checker=True
        )
        print(f"PaddlePaddle模型已导出到 {paddle_path}")
        return True
    except Exception as e:
        print(f"PaddlePaddle模型转换失败: {e}")
        return False


def convert_to_ncnn(onnx_path, param_path, bin_path):
    """
    将ONNX模型转换为NCNN模型。
    
    参数:
        onnx_path: ONNX模型路径
        param_path: 保存NCNN参数文件的路径
        bin_path: 保存NCNN权重文件的路径
    """
    if not NCNN_AVAILABLE:
        raise ImportError("NCNN未安装，无法转换模型")
    
    try:
        import onnx
        from onnx2ncnn import onnx2ncnn
        
        # 加载ONNX模型
        onnx_model = onnx.load(onnx_path)
        
        # 使用onnx2ncnn工具转换模型
        # 注意：在某些环境中可能需要单独安装onnx2ncnn工具
        # 这里使用命令行方式执行，实际使用时可能需要调整
        import subprocess
        cmd = f"onnx2ncnn {onnx_path} {param_path} {bin_path}"
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode == 0:
            print(f"NCNN模型已导出到 {param_path} 和 {bin_path}")
            return True
        else:
            print(f"NCNN模型转换失败: {result.stderr.decode()}")
            return False
    except Exception as e:
        print(f"NCNN模型转换失败: {e}")
        
        # 替代方案：如果onnx2ncnn工具不可用，提供使用NCNN的Python API的方法
        try:
            import onnx
            from ncnn.model_zoo.translator import onnx2ncnn
            
            onnx_model = onnx.load(onnx_path)
            onnx2ncnn(onnx_model, param_path, bin_path)
            print(f"NCNN模型已导出到 {param_path} 和 {bin_path}")
            return True
        except Exception as e2:
            print(f"NCNN模型转换替代方案也失败: {e2}")
            return False


def run_pytorch_inference(x0, x1):
    """
    使用PyTorch运行推理。
    
    参数:
        x0, x1: 输入的NumPy数组
        
    返回:
        output: PyTorch推理结果和执行时间
    """
    # 将NumPy数组转换为PyTorch张量
    x0_tensor = torch.tensor(x0)
    x1_tensor = torch.tensor(x1)
    
    # 运行推理并测量时间
    start = time.time()
    output = torch.matmul(x0_tensor, x1_tensor)
    end = time.time()
    inference_time = end - start
    
    return output.numpy(), inference_time


def run_onnx_inference(onnx_path="matmul.onnx", x0, x1):
    """
    使用ONNX Runtime运行推理。
    
    参数:
        onnx_path: ONNX模型的路径
        x0, x1: 输入的NumPy数组
        
    返回:
        output: ONNX Runtime推理结果和执行时间
    """
    # 确保输入为float32类型以适配ONNX Runtime
    x0 = x0.astype(np.float32)
    x1 = x1.astype(np.float32)
    
    # 加载ONNX模型
    session = onnxruntime.InferenceSession(onnx_path)
    
    # 获取输入名称
    input_names = [input.name for input in session.get_inputs()]
    
    # 准备输入字典
    input_dict = {input_names[0]: x0, input_names[1]: x1}
    
    # 运行推理并测量时间
    start = time.time()
    outputs = session.run(None, input_dict)
    end = time.time()
    inference_time = end - start
    
    return outputs[0], inference_time

def run_sail_inference(sail_path="matmul.bmodel", x0, x1):

    import sophon.sail as sail
    import numpy as np

    # 1.加载bmodel
    dev_id=0
    net = sail.Engine(sail_path,dev_id, sail.IOMode.SYSIO)
    
    # 2.获取模型的输入信息
    graph_name = net.get_graph_names()[0]
    input_names = net.get_input_names(graph_name)
    output_names = net.get_output_names(graph_name)

    # 3.准备输入数据
    x0 = np.ones((1,1000, 1000))
    x1 = 2*np.ones((1,1000,1000))
    input_dict = {input_names[0].name: x0,
                   input_names[1].name: x1}
    # np.savez('input_data.npz', input_data=input_dict)

    # 4.推理
    outputs = net.process(graph_name, input_dict)

    # 5.输出结果
    print(outputs[output_names[0]])
    
    
def run_tensorrt_inference(trt_path="matmul.trt", x0, x1):
    """
    使用TensorRT运行推理。
    
    参数:
        trt_path: TensorRT引擎路径
        x0, x1: 输入的NumPy数组
        
    返回:
        output: TensorRT推理结果和执行时间
    """
    if not TENSORRT_AVAILABLE:
        raise ImportError("TensorRT未安装，无法进行推理")
    
    # 确保输入为float32类型
    x0 = x0.astype(np.float32)
    x1 = x1.astype(np.float32)
    
    # 加载TensorRT引擎
    logger = trt.Logger(trt.Logger.WARNING)
    with open(trt_path, "rb") as f, trt.Runtime(logger) as runtime:
        engine = runtime.deserialize_cuda_engine(f.read())
    
    # 创建执行上下文
    context = engine.create_execution_context()
    
    # 分配GPU内存
    d_x0 = cuda.mem_alloc(x0.nbytes)
    d_x1 = cuda.mem_alloc(x1.nbytes)
    d_output = cuda.mem_alloc(x0.shape[0] * x0.shape[1] * x1.shape[2] * 4)  # 假设输出是float32，每个元素4字节
    
    # 将数据复制到GPU
    cuda.memcpy_htod(d_x0, x0)
    cuda.memcpy_htod(d_x1, x1)
    
    # 运行推理
    bindings = [int(d_x0), int(d_x1), int(d_output)]
    start = time.time()
    context.execute_v2(bindings)
    end = time.time()
    
    # 将结果从GPU复制回来
    output = np.zeros((x0.shape[0], x0.shape[1], x1.shape[2]), dtype=np.float32)
    cuda.memcpy_dtoh(output, d_output)
    
    inference_time = end - start
    return output, inference_time


def run_openvino_inference(ir_path="matmul.xml", x0, x1):
    """
    使用OpenVINO运行推理。
    
    参数:
        ir_path: OpenVINO IR模型路径（XML文件）
        x0, x1: 输入的NumPy数组
        
    返回:
        output: OpenVINO推理结果和执行时间
    """
    if not OPENVINO_AVAILABLE:
        raise ImportError("OpenVINO未安装，无法进行推理")
    
    # 确保输入为float32类型
    x0 = x0.astype(np.float32)
    x1 = x1.astype(np.float32)
    
    # 加载模型
    core = Core()
    model = core.read_model(ir_path)
    compiled_model = core.compile_model(model)
    
    # 获取输入和输出信息
    input_names = [node.get_any_name() for node in model.inputs]
    output_name = compiled_model.outputs[0]
    
    # 准备输入字典
    input_dict = {input_names[0]: x0, input_names[1]: x1}

    # 运行推理并测量时间
    start = time.time()
    output = compiled_model(input_dict)[output_name]
    end = time.time()
    inference_time = end - start
    
    return output, inference_time


def run_paddle_inference(paddle_path="matmul_paddle", x0, x1):
    """
    使用PaddlePaddle运行推理。
    
    参数:
        paddle_path: PaddlePaddle模型路径
        x0, x1: 输入的NumPy数组
        
    返回:
        output: PaddlePaddle推理结果和执行时间
    """
    if not PADDLE_AVAILABLE:
        raise ImportError("PaddlePaddle未安装，无法进行推理")
    
    # 确保输入为float32类型
    x0 = x0.astype(np.float32)
    x1 = x1.astype(np.float32)
    
    # 加载模型
    model = paddle.jit.load(paddle_path)
    
    # 转换为Paddle张量
    paddle_x0 = paddle.to_tensor(x0)
    paddle_x1 = paddle.to_tensor(x1)
    
    # 运行推理并测量时间
    start = time.time()
    output = model(paddle_x0, paddle_x1)
    end = time.time()
    inference_time = end - start
    
    return output.numpy(), inference_time


def run_ncnn_inference(param_path, bin_path, x0, x1):
    """
    使用NCNN运行推理。
    
    参数:
        param_path: NCNN参数文件路径
        bin_path: NCNN权重文件路径
        x0, x1: 输入的NumPy数组
        
    返回:
        output: NCNN推理结果和执行时间
    """
    if not NCNN_AVAILABLE:
        raise ImportError("NCNN未安装，无法进行推理")
    
    # 确保输入为float32类型
    x0 = x0.astype(np.float32)
    x1 = x1.astype(np.float32)
    
    # 加载NCNN模型
    net = ncnn.Net()
    net.load_param(param_path)
    net.load_model(bin_path)
    
    # 创建NCNN推理器
    extractor = net.create_extractor()
    
    # 设置输入
    extractor.input("input0", ncnn.Mat(x0))
    extractor.input("input1", ncnn.Mat(x1))
    
    # 运行推理并测量时间
    start = time.time()
    ret, output = extractor.extract("output")
    end = time.time()
    inference_time = end - start
    
    # 将NCNN的Mat对象转换为NumPy数组
    output_np = np.array(output)
    
    # 重塑输出以匹配预期的形状
    output_np = output_np.reshape(x0.shape[0], x0.shape[1], x1.shape[2])
    
    return output_np, inference_time


def compare_frameworks(args):
    """
    比较PyTorch、ONNX Runtime、TensorRT、OpenVINO、PaddlePaddle和NCNN的推理性能。
    
    参数:
        args: 命令行参数
    """
    # 创建输入数据
    batch_size = args.batch_size
    dim1 = args.dim1
    dim2 = args.dim2
    
    x0 = args.factor1 * np.ones((batch_size, dim1, dim2))
    x1 = args.factor2 * np.ones((batch_size, dim2, dim1))
    
    # 如果需要，保存输入数据
    if args.save_inputs:
        input_dict = {'x0': x0, 'x1': x1}
        np.savez(args.save_inputs, **input_dict)
        print(f"输入数据已保存到 {args.save_inputs}")

    # 检查ONNX模型是否存在，如需要则创建
    if not os.path.exists(args.onnx_model) and args.export_onnx:
        export_onnx(args.onnx_model, batch_size, dim1, dim2, dim1)

    # 运行PyTorch推理
    torch_output, torch_time = run_pytorch_inference(x0, x1)
    print(f"\nPyTorch推理时间: {torch_time:.6f} 秒")
    
    # 如果启用，运行ONNX推理
    if args.run_onnx and os.path.exists(args.onnx_model):
        onnx_output, onnx_time = run_onnx_inference(args.onnx_model, x0, x1)
        print(f"ONNX Runtime推理时间: {onnx_time:.6f} 秒")
        print(f"ONNX vs PyTorch最大差异: {np.max(np.abs(onnx_output - torch_output)):.6f}")
    
    # 如果启用，转换为TensorRT并运行推理
    if args.run_tensorrt and TENSORRT_AVAILABLE:
        if not os.path.exists(args.trt_path) and args.export_tensorrt:
            convert_to_tensorrt(args.onnx_model, args.trt_path, args.precision)
        
        if os.path.exists(args.trt_path):
            trt_output, trt_time = run_tensorrt_inference(args.trt_path, x0, x1)
            print(f"TensorRT推理时间: {trt_time:.6f} 秒")
            print(f"TensorRT vs PyTorch最大差异: {np.max(np.abs(trt_output - torch_output)):.6f}")
    
    # 如果启用，转换为OpenVINO并运行推理
    if args.run_openvino and OPENVINO_AVAILABLE:
        if not os.path.exists(args.ir_path) and args.export_openvino:
            convert_to_openvino(args.onnx_model, args.ir_path)
        
        if os.path.exists(args.ir_path):
            openvino_output, openvino_time = run_openvino_inference(args.ir_path, x0, x1)
            print(f"OpenVINO推理时间: {openvino_time:.6f} 秒")
            print(f"OpenVINO vs PyTorch最大差异: {np.max(np.abs(openvino_output - torch_output)):.6f}")
    
    # 如果启用，转换为PaddlePaddle并运行推理
    if args.run_paddle and PADDLE_AVAILABLE:
        if not os.path.exists(args.paddle_path) and args.export_paddle:
            convert_to_paddle(args.onnx_model, args.paddle_path)
        
        if os.path.exists(args.paddle_path):
            paddle_output, paddle_time = run_paddle_inference(args.paddle_path, x0, x1)
            print(f"PaddlePaddle推理时间: {paddle_time:.6f} 秒")
            print(f"PaddlePaddle vs PyTorch最大差异: {np.max(np.abs(paddle_output - torch_output)):.6f}")
    
    # 如果启用，转换为NCNN并运行推理
    if args.run_ncnn and NCNN_AVAILABLE:
        if (not os.path.exists(args.ncnn_param) or not os.path.exists(args.ncnn_bin)) and args.export_ncnn:
            convert_to_ncnn(args.onnx_model, args.ncnn_param, args.ncnn_bin)
        
        if os.path.exists(args.ncnn_param) and os.path.exists(args.ncnn_bin):
            ncnn_output, ncnn_time = run_ncnn_inference(args.ncnn_param, args.ncnn_bin, x0, x1)
            print(f"NCNN推理时间: {ncnn_time:.6f} 秒")
            print(f"NCNN vs PyTorch最大差异: {np.max(np.abs(ncnn_output - torch_output)):.6f}")
    
    # 打印比较摘要
    print("\n推理时间比较:")
    print(f"PyTorch: {torch_time:.6f} 秒")
    
    frameworks_results = []
    
    if args.run_onnx and os.path.exists(args.onnx_model):
        speedup = torch_time/onnx_time
        print(f"ONNX Runtime: {onnx_time:.6f} 秒 (加速比: {speedup:.2f}倍)")
        frameworks_results.append(("ONNX Runtime", onnx_time, speedup))
    
    if args.run_tensorrt and os.path.exists(args.trt_path):
        speedup = torch_time/trt_time
        print(f"TensorRT: {trt_time:.6f} 秒 (加速比: {speedup:.2f}倍)")
        frameworks_results.append(("TensorRT", trt_time, speedup))
    
    if args.run_openvino and os.path.exists(args.ir_path):
        speedup = torch_time/openvino_time
        print(f"OpenVINO: {openvino_time:.6f} 秒 (加速比: {speedup:.2f}倍)")
        frameworks_results.append(("OpenVINO", openvino_time, speedup))
    
    if args.run_paddle and os.path.exists(args.paddle_path):
        speedup = torch_time/paddle_time
        print(f"PaddlePaddle: {paddle_time:.6f} 秒 (加速比: {speedup:.2f}倍)")
        frameworks_results.append(("PaddlePaddle", paddle_time, speedup))
    
    if args.run_ncnn and os.path.exists(args.ncnn_param) and os.path.exists(args.ncnn_bin):
        speedup = torch_time/ncnn_time
        print(f"NCNN: {ncnn_time:.6f} 秒 (加速比: {speedup:.2f}倍)")
        frameworks_results.append(("NCNN", ncnn_time, speedup))
    
    # 如果有超过一个框架被比较，打印排序后的结果
    if len(frameworks_results) > 1:
        sorted_results = sorted(frameworks_results, key=lambda x: x[1])
        fastest_framework = sorted_results[0][0]
        
        print("\n性能排名:")
        for i, (name, time, speedup) in enumerate(sorted_results, 1):
            print(f"{i}. {name}: {time:.6f} 秒 (加速比: {speedup:.2f}倍)")
        
        print(f"\n最快的框架是: {fastest_framework}，速度比PyTorch快 {sorted_results[0][2]:.2f} 倍")


def parse_args():
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description='比较不同框架间的推理性能')
    parser.add_argument('--onnx_model', type=str, default='matmul.onnx', help='ONNX模型的路径')
    parser.add_argument('--batch_size', type=int, default=1, help='批次大小')
    parser.add_argument('--dim1', type=int, default=1000, help='第一维度')
    parser.add_argument('--dim2', type=int, default=1000, help='第二维度')
    parser.add_argument('--factor1', type=float, default=2.0, help='第一个输入的系数')
    parser.add_argument('--factor2', type=float, default=1.0, help='第二个输入的系数')
    parser.add_argument('--export_onnx', action='store_true', help='导出模型到ONNX')
    parser.add_argument('--run_onnx', action='store_true', help='运行ONNX Runtime推理')
    parser.add_argument('--export_tensorrt', action='store_true', help='将ONNX模型转换为TensorRT')
    parser.add_argument('--run_tensorrt', action='store_true', help='运行TensorRT推理')
    parser.add_argument('--export_openvino', action='store_true', help='将ONNX模型转换为OpenVINO')
    parser.add_argument('--run_openvino', action='store_true', help='运行OpenVINO推理')
    parser.add_argument('--export_paddle', action='store_true', help='将ONNX模型转换为PaddlePaddle')
    parser.add_argument('--run_paddle', action='store_true', help='运行PaddlePaddle推理')
    parser.add_argument('--export_ncnn', action='store_true', help='将ONNX模型转换为NCNN')
    parser.add_argument('--run_ncnn', action='store_true', help='运行NCNN推理')
    parser.add_argument('--save_inputs', type=str, default='', help='保存输入数据的路径 (例如: "inputs.npz")')
    parser.add_argument('--trt_path', type=str, default='matmul.trt', help='TensorRT引擎路径')
    parser.add_argument('--precision', type=str, default='FP32', help='TensorRT精度模式')
    parser.add_argument('--ir_path', type=str, default='matmul.xml', help='OpenVINO IR路径前缀')
    parser.add_argument('--paddle_path', type=str, default='matmul_paddle', help='PaddlePaddle模型路径')
    parser.add_argument('--ncnn_param', type=str, default='matmul.param', help='NCNN参数文件路径')
    parser.add_argument('--ncnn_bin', type=str, default='matmul.bin', help='NCNN权重文件路径')
    return parser.parse_args()


def print_usage_guide():
    """打印使用指南"""
    print("""
使用指南:
--------
这个脚本用于比较不同深度学习框架的矩阵乘法推理性能。
所有框架都基于同一个ONNX模型进行推理，确保比较的公平性。

基本用法:
python all_in_one3.py --export_onnx --run_onnx

更多选项:
* 改变矩阵维度：
  python all_in_one3.py --dim1 500 --dim2 500 --export_onnx --run_onnx

* 比较特定框架：
  python all_in_one3.py --run_onnx --run_tensorflow --export_onnx

* 同时比较所有可用框架：
  python all_in_one3.py --export_onnx

* 使用TensorRT：
  python all_in_one3.py --export_onnx --export_tensorrt --run_tensorrt

* 使用不同精度：
  python all_in_one3.py --export_onnx --export_tensorrt --run_tensorrt --precision FP16

* 保存输入数据：
  python all_in_one3.py --export_onnx --save_inputs inputs.npz

注意: 某些框架可能需要预先安装。如果缺少某个框架，脚本会自动跳过该框架的比较。
    """)


if __name__ == "__main__":
    # 检查是否有帮助标志
    if any(arg in sys.argv for arg in ['-h', '--help']):
        print_usage_guide()
        sys.exit(0)
    
    # 解析命令行参数
    args = parse_args()
    
    # 如果未指定任何框架，默认启用所有框架
    frameworks_to_run = [
        args.run_onnx, args.run_tensorrt, args.run_openvino, args.run_paddle, args.run_ncnn
    ]
    
    if not any(frameworks_to_run):
        available_frameworks = []
        args.run_onnx = True
        available_frameworks.append("ONNX Runtime")
        
        args.run_tensorrt = TENSORRT_AVAILABLE
        if args.run_tensorrt:
            available_frameworks.append("TensorRT")
        
        args.run_openvino = OPENVINO_AVAILABLE
        if args.run_openvino:
            available_frameworks.append("OpenVINO")
        
        args.run_paddle = PADDLE_AVAILABLE
        if args.run_paddle:
            available_frameworks.append("PaddlePaddle")
            
        args.run_ncnn = NCNN_AVAILABLE
        if args.run_ncnn:
            available_frameworks.append("NCNN")
        
        print(f"未指定框架，将使用所有可用框架: {', '.join(available_frameworks)}")
    
    try:
        # 确保需要的目录存在
        os.makedirs(os.path.dirname(args.onnx_model or "matmul.onnx"), exist_ok=True)
        if args.trt_path:
            os.makedirs(os.path.dirname(args.trt_path), exist_ok=True)
        if args.ir_path:
            os.makedirs(os.path.dirname(args.ir_path), exist_ok=True)
        if args.paddle_path:
            os.makedirs(os.path.dirname(args.paddle_path), exist_ok=True)
        if args.ncnn_param:
            os.makedirs(os.path.dirname(args.ncnn_param), exist_ok=True)
        if args.ncnn_bin:
            os.makedirs(os.path.dirname(args.ncnn_bin), exist_ok=True)
        
        # 运行比较
        compare_frameworks(args)
        print('\n比较完成。')
        print('使用 python all_in_one3.py --help 查看更多选项。')
    except Exception as e:
        print(f"运行时错误: {e}")
        import traceback
        traceback.print_exc()
