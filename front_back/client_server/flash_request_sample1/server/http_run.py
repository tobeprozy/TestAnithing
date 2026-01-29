from flask import Flask, request, Response
import logging
from server import create_task, get_result
import threading

import json
from flask import jsonify
import os
import subprocess
import time


# 创建Flask应用对象
app = Flask(__name__)

is_task_processing = False

@app.route('/create', methods=['POST'])
def handle_create_request():
    print("===============================")
    print("client posted a request!!!")
    print("===============================")
    global is_task_processing

    # 检查是否已经有任务在处理
    if is_task_processing:
        response_data = {'message': 'Task is already being processed'}
        return response_data, 400
        
    # 获取客户端发送的JSON数据
    request_data = request.get_json()
    
    if 'img_path' in request_data:
        img_path = request_data['img_path']
        # 创建一个线程来处理任务，并将rtsp_url传递给process_task函数
        thread = threading.Thread(target=process_task, daemon=True)
        thread.start()
        response_data = {'message': 'Task started'}
        is_task_processing = True
        return response_data, 200
    else:
        # 如果JSON数据中没有rtsp_url，则返回错误响应
        response_data = {'error': 'Missing dataset_pt'}
        return response_data, 400

def process_task():
    # 在这里执行耗时的任务
    create_task()
    # 处理完成后，可以在这里执行其他操作

@app.route('/eval', methods=['POST'])
def handle_eval_request():      
    # 获取客户端发送的JSON数据
    request_data = request.get_json()
    # 检查JSON数据中是否包含rtsp地址
    if 'eval' in request_data:
        res_name = "python_result.json"
        while True:
            result_files = os.listdir('results')
            if res_name in result_files:  # 检查res_name是否在文件列表中
                cmd = "echo handle_eval_request !!!!!"
                output_bytes = subprocess.check_output(cmd, shell=True)
                output_str = output_bytes.decode('utf-8')  # 转换为字符串
                response_data = {'output': output_str}
                return response_data, 200
            else:
                print("result json not exists, waiting....")
            time.sleep(1)
    else:
        # 如果JSON数据中没有rtsp_url，则返回错误响应
        response_data = {'error': 'Missing bmodel'}
        return response_data, 400


@app.route('/result', methods=['POST'])
def handle_result_request():
    # 处理结果请求
    print("===============================")
    print("client getting results!!!")
    print("===============================")
    result = get_result()
    json_data = json.dumps(result)
    def generate_chunks():
        chunk_size = 4096
        for i in range(0, len(json_data), chunk_size):
            yield json_data[i:i+chunk_size]
    response = Response(generate_chunks(), content_type='application/json')
    return response

if __name__ == '__main__':
    # 设置日志记录到文件
    logging.basicConfig(filename='app.log', level=logging.INFO)

    # 启动Flask应用，接收远程请求
    app.run(host='0.0.0.0', port=5000)
