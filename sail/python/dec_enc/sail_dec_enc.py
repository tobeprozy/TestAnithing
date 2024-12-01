import sophon.sail as sail
import argparse
import threading
import queue
import time
import os
import numpy as np

def decode_and_enqueue(handle, device_id, video_path, q, queue_lock):
    decoder = sail.Decoder(video_path, True, device_id)
    while True:
        frame_interval=0
        frame_counter=0s
        image = decoder.read(handle)
        fps=decoder.get_fps()
        if image is None:
            break
        with queue_lock:
            if (frame_counter % frame_interval == 0):
                try:
                    q.put_nowait(image)  # 确保使用正确的队列实例变量名
                except queue.Full:  # 正确捕获queue.Full异常
                    q.get_nowait()  # 如果队列满了，剔除最旧的数据
                    q.put_nowait(image)
            frame_counter += 1
        decoder.release()

def process_queue(queue_, bmcv, queue_id):
    i = 0
    while True:
        try: 
            img = queue_.get(timeout=1)
            # print(f"imwrite {i}, queue_id: {queue_id}")
            # bmcv.imwrite(f"./multi-channel_decoded_images/{queue_id}_{i}.jpg", img)
            print(f"imencode {i}, queue_id: {queue_id}")
            encode_img=bmcv.imencode(".jpg",img)
            print(encode_img)
            i += 1
        except queue.Empty:  # 注意这里的改动
            print("队列为空，等待图像...")
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--device_id", type=int, default=0, help="dev_id")
    parser.add_argument('--video_url', type=str, default="rtsp://admin:jdsm8888@27.151.43.4/Streaming/tracks/601?starttime=20240730T160518Z&endtime=20240730T161140Z", help='video url, can be rtsp, file path.')
    parser.add_argument("--num_queues", type=int, default=1, help="Number of queues")
    parser.add_argument("--max_queue_size", type=int, default=10, help="Maximum size of each queue")
    args = parser.parse_args()

    rtsp_streams=[]
    for i in range(args.num_queues):
        rtsp_streams.append(args.video_url)
    # 准备输出
    save_jpeg_path = "./multi-channel_decoded_images"
    if not os.path.exists(save_jpeg_path):
        os.mkdir(save_jpeg_path)

       
    handle = sail.Handle(args.device_id)
    bmcv = sail.Bmcv(handle)
    
    queues = [queue.Queue(maxsize=args.max_queue_size) for _ in range(args.num_queues)]
    queue_lock = threading.Lock()


    for i in range(args.num_queues):
        decode_thread = threading.Thread(target=decode_and_enqueue, args=(handle,args.device_id, rtsp_streams[i], queues[i], queue_lock))
        decode_thread.start()

        thread = threading.Thread(target=process_queue, args=(queues[i], bmcv,i))
        thread.start()
