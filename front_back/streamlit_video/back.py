from flask import Flask, request, jsonify
import base64
from PIL import Image
import io
import cv2
import numpy as np

app = Flask(__name__)

@app.route('/push_data', methods=['POST'])
def push_data():
    data = request.form
    id = data.get('id')
    image_base64 = data.get('image')

    # 解码Base64编码的图片数据
    image_data = base64.b64decode(image_base64)
    image_array = np.frombuffer(image_data, np.uint8)
    decoded_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    gray_frame = cv2.cvtColor(decoded_image, cv2.COLOR_BGR2GRAY)

    print("Received image with id: ", id)
    # 处理图片数据

    print(gray_frame) 
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = 255  
    thickness = 2
    position = (10, 30)  # 文本位置，左上角

    # 在图像上绘制ID
    cv2.putText(gray_frame, f'ID: {id}', position, font, font_scale, color, thickness)

    
    _, encoded_image = cv2.imencode('.jpg', gray_frame)

    image_base64 = base64.b64encode(encoded_image).decode('utf-8')  # 使用先前读取的文件内容

    print("Processed image with id: ", id)
    # 返回处理后的图片数据
    return jsonify({
        'frame_id': id,
        'jpg_base64': image_base64
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)

