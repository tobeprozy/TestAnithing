import streamlit as st
import cv2
import numpy as np
import requests
from io import BytesIO
from PIL import Image
import tempfile
import base64
import sys
import time
import random

# 压缩图像函数
def compress_image(image, quality=20):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, img_encoded = cv2.imencode('.jpg', image, encode_param)
    img = cv2.imdecode(img_encoded, 1)
    return img

server_url = 'http://172.25.4.156:5000'


# 设置页面宽度
st.set_page_config(layout="wide")

# 左侧加载视频或图片或输入URL
st.sidebar.title("加载视频或图片")
file = st.sidebar.file_uploader("上传视频或图片文件", type=["mp4", "avi", "mov", "avi", "jpg", "png"])
url = st.sidebar.text_input("输入视频或图片URL")
enter=st.sidebar.button("开始")
# 右侧显示实时画面和后端处理结果
col1, col2 = st.columns(2)

# 显示实时画面
col1.title("实时画面")
video_placeholder = col1.empty()

# 显示后端处理后的图片结果
col2.title("后端处理结果")
image_placeholder = col2.empty()

print(file)
if enter:
    # 处理视频或图片
    if file is not None: 
        file_extension = file.name.split(".")[-1].lower()
        if file_extension in ["jpg", "jpeg", "png"]:
            # 处理图片           
            frame = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
            # gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            compressed_image1 = compress_image(frame)  # 假设这是您定义的压缩图像函数
            video_placeholder.image(compressed_image1,caption='origin Image.', channels="BGR")  # 假设这是显示图像的函数

            _, encoded_image = cv2.imencode('.jpg', frame)

            image_base64 = base64.b64encode(encoded_image).decode('utf-8')  # 使用先前读取的文件内容
            id = int(time.time() * 1000) + random.randint(0, 999)

            print(image_base64)
            # 将Base64编码的图片数据发送到后端处理
            response = requests.post(f'{server_url}/push_data', data={
                    'id': id,
                    'image': image_base64
            })

            # 检查响应
            print(response.text)

            # 显示后端处理后的图片
            if response.status_code == 200:
                result = response.json()
                img_name = result.get('frame_id')
                jpg_base64 = result.get('jpg_base64')
                if img_name and jpg_base64:
                    processed_image = base64.b64decode(jpg_base64)
                    image_placeholder.image(processed_image, caption='Processed Image.', use_column_width=True)
            else:
                st.error("后端处理出现问题，请重试或联系管理员")

                     
        elif file_extension in ["mp4", "avi", "mov"]:
            # 处理视频
            # 保存上传的视频文件到本地临时文件夹
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file.read())
                video_path = temp_file.name

            cap = cv2.VideoCapture(video_path)
            interval = 10
            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret or frame is None:
                    end_flag = True
                if frame_count % interval == 0:
                    # 在画面上进行后端处理，这里简单地将画面转为灰度图像
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    compressed_image1 = compress_image(frame)  # 压缩图像
                    compressed_image2 = compress_image(gray_frame)  # 压缩图像
          
                    video_placeholder.image(compressed_image1, channels="BGR")
                    image_placeholder.image(compressed_image2, channels="GRAY")

                frame_count += 1
    elif url:
        # 处理URL
            cap = cv2.VideoCapture(url)
            interval = 10
            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret or frame is None:
                    end_flag = True
                if frame_count % interval == 0:
                    # 在画面上进行后端处理，这里简单地将画面转为灰度图像
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    compressed_image1 = compress_image(frame)  # 压缩图像
                    compressed_image2 = compress_image(gray_frame)  # 压缩图像
          
                    video_placeholder.image(compressed_image1, channels="BGR")
                    image_placeholder.image(compressed_image2, channels="GRAY")
                            
                frame_count += 1
    else:
        st.warning("请上传视频或图片文件或输入视频或图片URL")

url="rtsp://172.28.3.201:5544/vod/123/out264-20700.264"

# streamlit run front.py