

import cv2
import numpy as np
import logging
logging.basicConfig(level=logging.INFO)
import time
import os
from queue import Queue
import base64
import json
import argparse

queue_max_size=10
my_queue = Queue(maxsize=queue_max_size)
def put_element(queue, element):
    if queue.qsize() >= queue_max_size:
        queue.get()  # 如果队列已满，移除最早放入的元素
    queue.put(element)  # 向队列中放入新元素 


def main(args):
    output_dir = "results"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output_img_dir = os.path.join(output_dir, 'images')
    if not os.path.exists(output_img_dir):
        os.mkdir(output_img_dir) 

    filepath = args.img
    result_jsons=[]
    for i in range(10): 
        result=[]
        start =time.time() 
        src_img = cv2.imdecode(np.fromfile(filepath, dtype=np.uint8), -1) 
        end = time.time()
        str="frame_id: %d, imdecodetime: %.6f"%(i, end-start)
        result.append(str)

        # save image  
        start =time.time()
        filename="frame_%d.jpg"%(i)
        cv2.imwrite(os.path.join(output_img_dir, filename), src_img)
        end = time.time()
        str="frame_id: %d, save time: %.6f"%(i, end-start)
        result.append(str)

        start =time.time()
        _, encoded_image = cv2.imencode('.jpg', src_img)
        base64_image = base64.b64encode(encoded_image).decode('utf-8')
        end = time.time()
        str="frame_id: %d, encode time: %.6f"%(i, end-start)
        result.append(str)
        put_element(my_queue, [i, base64_image])
        result_jsons.append(result)
        print("frame_id %d done"%(i))
    # save result
    json_name = "python_result.json"
    with open(os.path.join(output_dir, json_name), 'w') as jf:
        # json.dump(results_list, jf)
        json.dump(result_jsons, jf, indent=4, ensure_ascii=False)
    logging.info("result saved in {}".format(os.path.join(output_dir, json_name)))
def argsparser():
    parser = argparse.ArgumentParser(prog=__file__)
    parser.add_argument('--img', type=str, default='yuv420.jpg', help='path of input, must be image directory')
    args = parser.parse_args()
    return args

def create_task():
    print("===============")
    print("TEST")
    print("===============")
    args = argsparser()
    main(args)

def get_result():
    data=[]
    print("=========================")
    print("get_result!!!")
    while not my_queue.empty():
        print("getting!!!")
        element = my_queue.get()
        result = {}
        result['frame_id'] = element[0]
        result['jpg_base64'] = element[1]
        data.append(result)
    return data


if __name__ == '__main__':
    args = argsparser()
    main(args)
