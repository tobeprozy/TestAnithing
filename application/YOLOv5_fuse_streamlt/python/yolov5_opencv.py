#===----------------------------------------------------------------------===#
#
# Copyright (C) 2022 Sophgo Technologies Inc.  All rights reserved.
#
# SOPHON-DEMO is licensed under the 2-Clause BSD License except for the
# third-party components.
#
#===----------------------------------------------------------------------===#
import os
import json
import time
import cv2
import argparse
import numpy as np
import sophon.sail as sail
from utils import COLORS, COCO_CLASSES
import logging
import ast
logging.basicConfig(level=logging.INFO)
# sail.set_print_flag(1)

class YOLOv5:
    def __init__(self, args):
        # load bmodel
        self.net = sail.Engine(args.bmodel, args.dev_id, sail.IOMode.SYSIO)
        logging.info("load {} success!".format(args.bmodel))
        self.graph_name = self.net.get_graph_names()[0]
        self.input_name = self.net.get_input_names(self.graph_name)[0]
        self.output_names = self.net.get_output_names(self.graph_name)
        self.input_shape = self.net.get_input_shape(self.graph_name, self.input_name)
        if len(self.output_names) not in [1]:
            raise ValueError('only suport 1 or 3 outputs, but got {} outputs bmodel'.format(len(self.output_names)))

        #模型输入是[1, 640, 640, 3]
        self.batch_size = self.input_shape[0]
        self.net_h = self.input_shape[1]
        self.net_w = self.input_shape[2]

    
    def init(self):
        self.preprocess_time = 0.0
        self.inference_time = 0.0
        self.postprocess_time = 0.0
            
    def prepare_data(self, ori_img):
        """
        pre-processing
        Args:
            img: numpy.ndarray -- (h,w,3)

        Returns: (3,h,w) numpy.ndarray after pre-processing

        """
        letterbox_img, ratio, (tx1, ty1) = self.letterbox(
            ori_img,
            new_shape=(self.net_h, self.net_w),
            color=(114, 114, 114),
            auto=False,
            scaleFill=False,
            scaleup=True,
            stride=32
        )
        return letterbox_img, ratio, (tx1, ty1) 
    
    def letterbox(self, im, new_shape=(640, 640), color=(114, 114, 114), auto=False, scaleFill=False, scaleup=True, stride=32):
        # Resize and pad image while meeting stride-multiple constraints
        shape = im.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:  # only scale down, do not scale up (for better val mAP)
            r = min(r, 1.0)

        # Compute padding
        ratio = r, r  # width, height ratios
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
        if auto:  # minimum rectangle
            dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
        elif scaleFill:  # stretch
            dw, dh = 0.0, 0.0
            new_unpad = (new_shape[1], new_shape[0])
            ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

        dw /= 2  # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
        return im, ratio, (dw, dh)
    
    def predict(self, input_img, img_num):
        input_data = {self.input_name: input_img}
        outputs = self.net.process(self.graph_name, input_data)

        out = {}
        for name in outputs.keys():
            out_keys = list(outputs.keys())
            ord = []
            for n in self.output_names:
                for i, k in enumerate(out_keys):
                    if n == k:
                        ord.append(i)
                        break
            out = [outputs[out_keys[i]][:img_num] for i in ord]
        return out

    def get_results(self, output, img_num: int, ratio_list, txy_list):
        res = np.array(output[0][0][0])
        results = [[] for _ in range(img_num)]

        for row in res:
            image_index = int(row[0])
            results[image_index].append(row.tolist())  

        for i in range(img_num):
            results[i] = np.array(results[i])
            for item in results[i]:
                x1, y1, x2, y2 = item[3:] 
                item[-4] = int((x1 - x2/2 - txy_list[i][0]) / ratio_list[i][0])  
                item[-3] = int((y1 - y2/2 - txy_list[i][1]) / ratio_list[i][1])  
                item[-2] = int((x1 + x2/2 - txy_list[i][0]) / ratio_list[i][0])  
                item[-1] = int((y1 + y2/2 - txy_list[i][1]) / ratio_list[i][1])

        results = np.array([np.array(x) for x in results], dtype=object) 
        return results
    
    def __call__(self, img_list):
        img_num = len(img_list)
        ori_size_list = []
        ori_w_list = []
        ori_h_list = []
        preprocessed_img_list = []
        ratio_list = []
        txy_list = []
        for ori_img in img_list:
            ori_h, ori_w = ori_img.shape[:2]
            ori_size_list.append((ori_w, ori_h))
            ori_w_list.append(ori_w)
            ori_h_list.append(ori_h)
            start_time = time.time()
            preprocessed_img, ratio, (tx1, ty1) = self.prepare_data(ori_img)
            self.preprocess_time += time.time() - start_time
            preprocessed_img_list.append(preprocessed_img)
            ratio_list.append(ratio)
            txy_list.append([tx1, ty1])
        
        if img_num == self.batch_size:
            input_img = np.stack(preprocessed_img_list)
        else:
            input_img = np.zeros(self.input_shape, dtype='float32')
            input_img[:img_num] = np.stack(preprocessed_img_list)
            
        start_time = time.time()
        outputs = self.predict(input_img, img_num)
        self.inference_time += time.time() - start_time

        start_time = time.time()
        results = self.get_results(outputs, img_num, ratio_list, txy_list)
        self.postprocess_time += time.time() - start_time


        return results

def draw_numpy(image, boxes, masks=None, classes_ids=None, conf_scores=None, draw_thresh=None):
    for idx in range(len(boxes)):
        x1, y1, x2, y2 = boxes[idx, :].astype(np.int32).tolist()

        logging.debug("class id={}, score={}, (x1={},y1={},x2={},y2={})".format(classes_ids[idx],conf_scores[idx], x1, y1, x2, y2))
        if conf_scores[idx] < draw_thresh:
            continue
        if classes_ids is not None:
            color = COLORS[int(classes_ids[idx]) + 1]
        else:
            color = (0, 0, 255)

        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness=2)
        if classes_ids is not None and conf_scores is not None:
            classes_ids = classes_ids.astype(np.int8)
            cv2.putText(image, COCO_CLASSES[classes_ids[idx] + 1] + ':' + str(round(conf_scores[idx], 2)),
                        (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, thickness=2)
        if masks is not None:
            mask = masks[:, :, idx]
            image[mask] = image[mask] * 0.5 + np.array(color) * 0.5
    return image
   
                    
                        
from flask import Flask, request, jsonify
import base64
from PIL import Image
import io
import cv2
import numpy as np
def create_app(args,yolov5):
    app = Flask(__name__)

    @app.route('/push_data', methods=['POST'])
    def post_data():
        data = request.form
        id = data.get('id')
        image_base64 = data.get('image')

        # 解码Base64编码的图片数据
        image_data = base64.b64decode(image_base64)
        image_array = np.frombuffer(image_data, np.uint8)
        decoded_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        print("Received image with id: ", id)
        # 处理图片数据
        yolov5_results = yolov5([decoded_image])
        det = yolov5_results[0]
                        # save image
        res_img = draw_numpy(decoded_image, det[:,3:7], masks=None, classes_ids=det[:, 1], conf_scores=det[:, 2], draw_thresh=args.draw_thresh)

        # 使用YOLOv5对象进行进一步处理（假设有一个process方法）
        # result = g.yolov5.process(decoded_image)

        _, encoded_image = cv2.imencode('.jpg', res_img)
        image_base64 = base64.b64encode(encoded_image).decode('utf-8')  # 使用先前读取的文件内容

        print("Processed image with id: ", id)
        # 返回处理后的图片数据
        return jsonify({
            'frame_id': id,
            'jpg_base64': image_base64
        })

    return app

def argsparser():
    parser = argparse.ArgumentParser(prog=__file__)
    parser.add_argument('--input', type=str, default='../datasets/test', help='path of input')
    parser.add_argument('--bmodel', type=str, default='../models/BM1684X/yolov5s_v6.1_fuse_int8_1b.bmodel', help='path of bmodel')
    parser.add_argument('--dev_id', type=int, default=0, help='dev id')
    parser.add_argument('--draw_thresh', type=float, default=0.5, help='draw threshold')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = argsparser()
    yolov5 = YOLOv5(args)  # 初始化YOLOv5对象
    yolov5.init()
    print('all done.')
    app = create_app(args,yolov5)
    app.run(host='0.0.0.0', port=5000, debug=True)     

