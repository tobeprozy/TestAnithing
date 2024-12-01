import sophon.sail as sail
import threading
import queue
import os
import time
import json
import argparse
import numpy as np
import sophon.sail as sail
from postprocess_numpy import PostProcess
from utils import COLORS
import logging
logging.basicConfig(level=logging.INFO)
# sail.set_print_flag(1)
import datetime


class YOLOv5:
    def __init__(self, args):
        # load bmodel
        self.net = sail.Engine(args.bmodel, args.dev_id, sail.IOMode.SYSO)
        logging.debug("load {} success!".format(args.bmodel))
        # self.handle = self.net.get_handle()
        self.handle = sail.Handle(args.dev_id)
        self.bmcv = sail.Bmcv(self.handle)
        self.graph_name = self.net.get_graph_names()[0]
        
        # get input
        self.input_name = self.net.get_input_names(self.graph_name)[0]
        self.input_dtype= self.net.get_input_dtype(self.graph_name, self.input_name)
        self.img_dtype = self.bmcv.get_bm_image_data_format(self.input_dtype)
        self.input_scale = self.net.get_input_scale(self.graph_name, self.input_name)
        self.input_shape = self.net.get_input_shape(self.graph_name, self.input_name)
        self.input_shapes = {self.input_name: self.input_shape}
        
        # get output
        self.output_names = self.net.get_output_names(self.graph_name)
        if len(self.output_names) not in [1, 3]:
            raise ValueError('only suport 1 or 3 outputs, but got {} outputs bmodel'.format(len(self.output_names)))
        
        self.output_tensors = {}
        self.output_scales = {}
        self.output_shapes = []
        for output_name in self.output_names:
            output_shape = self.net.get_output_shape(self.graph_name, output_name)
            output_dtype = self.net.get_output_dtype(self.graph_name, output_name)
            output_scale = self.net.get_output_scale(self.graph_name, output_name)
            output = sail.Tensor(self.handle, output_shape, output_dtype, True, True)
            self.output_tensors[output_name] = output
            self.output_scales[output_name] = output_scale
            self.output_shapes.append(output_shape)
        
        # check batch size 
        self.batch_size = self.input_shape[0]
        support_batch_size = [1, 2, 3, 4, 8, 16, 32, 64, 128, 256]
        if self.batch_size not in support_batch_size:
            raise ValueError('batch_size must be {} for bmcv, but got {}'.format(support_batch_size, self.batch_size))
        self.net_h = self.input_shape[2]
        self.net_w = self.input_shape[3]
        
        # init preprocess
        self.use_resize_padding = True
        self.use_vpp = False
        self.ab = [x * self.input_scale / 255.  for x in [1, 0, 1, 0, 1, 0]]
        
        # init postprocess
        self.conf_thresh = args.conf_thresh
        self.nms_thresh = args.nms_thresh
        if 'use_cpu_opt' in getattr(args, '__dict__', {}):
            self.use_cpu_opt = args.use_cpu_opt
        else:
            self.use_cpu_opt = False
        
        self.agnostic = False
        self.multi_label = True
        self.max_det = 1000
        self.postprocess = PostProcess(
            conf_thresh=self.conf_thresh,
            nms_thresh=self.nms_thresh,
            agnostic=self.agnostic,
            multi_label=self.multi_label,
            max_det=self.max_det,
        )
        
        # init time
        self.preprocess_time = 0.0
        self.inference_time = 0.0
        self.postprocess_time = 0.0

    def init(self):
        self.preprocess_time = 0.0
        self.inference_time = 0.0
        self.postprocess_time = 0.0
        
    def preprocess_bmcv(self, input_bmimg):
        rgb_planar_img = sail.BMImage(self.handle, input_bmimg.height(), input_bmimg.width(),
                                          sail.Format.FORMAT_RGB_PLANAR, sail.DATA_TYPE_EXT_1N_BYTE)
        self.bmcv.convert_format(input_bmimg, rgb_planar_img)
        resized_img_rgb, ratio, txy = self.resize_bmcv(rgb_planar_img)
        preprocessed_bmimg = sail.BMImage(self.handle, self.net_h, self.net_w, sail.Format.FORMAT_RGB_PLANAR, self.img_dtype)
        self.bmcv.convert_to(resized_img_rgb, preprocessed_bmimg, ((self.ab[0], self.ab[1]), \
                                                                 (self.ab[2], self.ab[3]), \
                                                                 (self.ab[4], self.ab[5])))
        return preprocessed_bmimg, ratio, txy

    def resize_bmcv(self, bmimg):
        """
        resize for single sail.BMImage
        :param bmimg:
        :return: a resize image of sail.BMImage
        """
        img_w = bmimg.width()
        img_h = bmimg.height()
        if self.use_resize_padding:
            r_w = self.net_w / img_w
            r_h = self.net_h / img_h
            if r_h > r_w:
                tw = self.net_w
                th = int(r_w * img_h)
                tx1 = tx2 = 0
                ty1 = int((self.net_h - th) / 2)
                ty2 = self.net_h - th - ty1
            else:
                tw = int(r_h * img_w)
                th = self.net_h
                tx1 = int((self.net_w - tw) / 2)
                tx2 = self.net_w - tw - tx1
                ty1 = ty2 = 0

            ratio = (min(r_w, r_h), min(r_w, r_h))
            txy = (tx1, ty1)
            attr = sail.PaddingAtrr()
            attr.set_stx(tx1)
            attr.set_sty(ty1)
            attr.set_w(tw)
            attr.set_h(th)
            attr.set_r(114)
            attr.set_g(114)
            attr.set_b(114)
            
            preprocess_fn = self.bmcv.vpp_crop_and_resize_padding if self.use_vpp else self.bmcv.crop_and_resize_padding
            resized_img_rgb = preprocess_fn(bmimg, 0, 0, img_w, img_h, self.net_w, self.net_h, attr)
        else:
            r_w = self.net_w / img_w
            r_h = self.net_h / img_h
            ratio = (r_w, r_h)
            txy = (0, 0)
            preprocess_fn = self.bmcv.vpp_resize if self.use_vpp else self.bmcv.resize
            resized_img_rgb = preprocess_fn(bmimg, self.net_w, self.net_h)
        return resized_img_rgb, ratio, txy
    
    def predict(self, input_tensor, img_num):
        """
        ensure output order: loc_data, conf_preds, mask_data, proto_data
        Args:
            input_tensor:
        Returns:
        """
        input_tensors = {self.input_name: input_tensor} 
        self.net.process(self.graph_name, input_tensors, self.input_shapes, self.output_tensors)
        if self.use_cpu_opt:
            out = self.output_tensors
        else:
            outputs_dict = {}
            for name in self.output_names:
                # outputs_dict[name] = self.output_tensors[name].asnumpy()[:img_num] * self.output_scales[name]
                outputs_dict[name] = self.output_tensors[name].asnumpy()[:img_num]
            # resort
            out_keys = list(outputs_dict.keys())
            ord = []
            for n in self.output_names:
                for i, k in enumerate(out_keys):
                    if n in k:
                        ord.append(i)
                        break
            out = [outputs_dict[out_keys[i]] for i in ord]
        return out

    def __call__(self, bmimg_list):
        img_num = len(bmimg_list)
        ori_size_list = []
        ori_w_list = []
        ori_h_list = []
        ratio_list = []
        txy_list = []
        if self.batch_size == 1:
            ori_h, ori_w =  bmimg_list[0].height(), bmimg_list[0].width()
            ori_size_list.append((ori_w, ori_h))
            ori_w_list.append(ori_w)
            ori_h_list.append(ori_h)
            start_time = time.time()      
            preprocessed_bmimg, ratio, txy = self.preprocess_bmcv(bmimg_list[0])
            self.preprocess_time += time.time() - start_time
            ratio_list.append(ratio)
            txy_list.append(txy)
            
            input_tensor = sail.Tensor(self.handle, self.input_shape, self.input_dtype,  False, False)
            self.bmcv.bm_image_to_tensor(preprocessed_bmimg, input_tensor)
                
        else:
            BMImageArray = eval('sail.BMImageArray{}D'.format(self.batch_size))
            bmimgs = BMImageArray()
            for i in range(img_num):
                ori_h, ori_w =  bmimg_list[i].height(), bmimg_list[i].width()
                ori_size_list.append((ori_w, ori_h))
                ori_w_list.append(ori_w)
                ori_h_list.append(ori_h)
                start_time = time.time()
                preprocessed_bmimg, ratio, txy  = self.preprocess_bmcv(bmimg_list[i])
                self.preprocess_time += time.time() - start_time
                ratio_list.append(ratio)
                txy_list.append(txy)
                bmimgs[i] = preprocessed_bmimg.data()
            input_tensor = sail.Tensor(self.handle, self.input_shape, self.input_dtype,  False, False)
            self.bmcv.bm_image_to_tensor(bmimgs, input_tensor)
            
        start_time = time.time()
        outputs = self.predict(input_tensor, img_num)
        self.inference_time += time.time() - start_time
        
        start_time = time.time()
        if self.use_cpu_opt:
            self.cpu_opt_process = sail.algo_yolov5_post_cpu_opt(self.output_shapes, self.net_w, self.net_h)
            results = self.cpu_opt_process.process(outputs, ori_w_list, ori_h_list, [self.conf_thresh]*self.batch_size, [self.nms_thresh]*self.batch_size, self.use_resize_padding, self.multi_label)
            results = [np.array(result) for result in results]
        else:
            results = self.postprocess(outputs, ori_size_list, ratio_list, txy_list)
        self.postprocess_time += time.time() - start_time

        return results

def draw_bmcv(bmcv, bmimg, boxes, classes_ids=None, conf_scores=None, save_path=""):
    img_bgr_planar = bmcv.convert_format(bmimg)
    thickness = 2
    for idx in range(len(boxes)):
        x1, y1, x2, y2 = boxes[idx, :].astype(np.int32).tolist()
        logging.debug("class id={}, score={}, (x1={},y1={},w={},h={})".format(int(classes_ids[idx]), conf_scores[idx], x1, y1, x2-x1, y2-y1))
        if conf_scores[idx] < 0.25:
            continue
        if classes_ids is not None:
            color = np.array(COLORS[int(classes_ids[idx]) + 1]).astype(np.uint8).tolist()
        else:
            color = (0, 0, 255)
        if (x2 - x1) <= thickness * 2 or (y2 - y1) <= thickness * 2:
            logging.info("width or height too small, this rect will not be drawed: (x1={},y1={},w={},h={})".format(x1, y1, x2-x1, y2-y1))
        else:
            bmcv.rectangle(img_bgr_planar, x1, y1, (x2 - x1), (y2 - y1), color, thickness)
    bmcv.imwrite(save_path, img_bgr_planar)


def decode_and_enqueue(device_id: int, video_path: str, queues: list, queue_lock: threading.Lock, max_queue_size: int):
    handle = sail.Handle(device_id)
    bmcv = sail.Bmcv(handle)
    decoder = sail.Decoder(video_path, True, device_id)
    
    while True:
        image = sail.BMImage()
        start_time = time.time()
        ret = decoder.read(handle, image)
        if ret:
            print("decode!!!!!", "image.width:", image.width(), "image.height:", image.height())
            continue
        with queue_lock:
            for q in queues:# 把这张图放入多个队列
                current_time = datetime.datetime.now()
                print(current_time,"decode!!!!!","image.width:",image.width(), "image.height:", image.height())
                try:
                    q.put_nowait(image)
                except queue.Full:
                    pass

def process_queue(args,queue, queue_id):
    yolov5 = YOLOv5(args)
    while True:
        image = queue.get()
        if(image.width()==0 | image.height()==0):
            continue
        current_time = datetime.datetime.now()
        print(current_time,"process!!!!!","queue_id:", queue_id,"image.width:", image.width(), "image.height:", image.height())
        results = yolov5([image])

def main(args):
    queues = [queue.Queue(maxsize=args.max_queue_size) for _ in range(args.num_queues)]
    queue_lock = threading.Lock()

    decode_thread = threading.Thread(target=decode_and_enqueue, args=(args.dev_id, args.video_path, queues, queue_lock, args.max_queue_size))
    decode_thread.start()

    for i in range(args.num_queues):
        thread = threading.Thread(target=process_queue, args=(args,queues[i], i))
        thread.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=__file__)
    parser.add_argument('--dev_id', type=int, default=0, help='dev id')
    parser.add_argument("--num_queues", type=int, default=5, help="Number of queues")
    parser.add_argument("--max_queue_size", type=int, default=20, help="Maximum size of each queue")
    parser.add_argument('--video_path', type=str, default='../datasets/test_car_person_1080P.mp4', help='path of input')
    parser.add_argument('--bmodel', type=str, default='../models/BM1684/yolov5s_v6.1_3output_fp32_1b.bmodel', help='path of bmodel')
    parser.add_argument('--conf_thresh', type=float, default=0.001, help='confidence threshold')
    parser.add_argument('--nms_thresh', type=float, default=0.6, help='nms threshold')
    parser.add_argument('--use_cpu_opt', action="store_true", default=False, help='accelerate cpu postprocess')
    args = parser.parse_args()
    
    main(args)
# python3 python/yolov5_bmcv_mul.py --bmodel models/BM1684X/yolov5s_v6.1_3output_fp32_1b.bmodel --dev_id 0 --conf_thresh 0.5 --nms_thresh 0.5 --video_path datasets/test_car_person_1080P.mp4 --num_queues 5