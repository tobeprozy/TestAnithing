import threading
import os
import argparse
import sophon.sail as sail
import time

# 处理每个视频流的线程函数
def get_img_enc(decoder,bmcv,ch_idx,is_save_jpeg,save_jpeg_path):
    i=0
    while True:
        time.sleep(0.1)  # 每隔100ms取一张图
        img = decoder.read(ch_idx)
        start=time.time()
        if is_save_jpeg:
            bmcv.imwrite(os.path.join(save_jpeg_path, f"chn_{ch_idx}_cnt_{i}.jpg"), img)
            print("imwrite success")
        else:  
            encode_img=bmcv.imencode(".jpg",img)
            print("encode success")
        end=time.time()
        i+=1
        cost_time=(end-start)*1000
        print(f"channel {ch_idx} get one frame, cost {cost_time} ms")


if __name__ == '__main__':

    parse = argparse.ArgumentParser(description="Demo for multi-channel decode")
    parse.add_argument('--dev_id', type=int, default=0, help='device id')
    parse.add_argument('--video_url', type=str, default="rtsp://admin:jdsm8888@27.151.43.4/Streaming/tracks/601?starttime=20240730T160518Z&endtime=20240730T161140Z", help='video url, can be rtsp, file path.')
    parse.add_argument('--is_local', type=bool, default=False, help='is local video')
    parse.add_argument('--read_timeout', type=int, default=5, help='read timeout')
    parse.add_argument('--channel_num', type = int, default = 2, help = 'channel number')
    parse.add_argument('--is_save_jpeg', type = bool, default = True, help = 'is save jpeg')
    args = parse.parse_args()

    # 准备输入
    rtsp_streams=[]
    for i in range(args.channel_num):
        rtsp_streams.append(args.video_url)

    # 是否将解码结果保存成本地图片
    is_save_jpeg = args.is_save_jpeg
    # 准备输出
    save_jpeg_path = "./multi-channel_decoded_images"
    if not os.path.exists(save_jpeg_path):
        os.mkdir(save_jpeg_path)
    handle = sail.Handle(args.dev_id)
    bmcv = sail.Bmcv(handle)

    # 初始化MultiDecoder
    decoder = sail.MultiDecoder(queue_size=10, tpu_id=args.dev_id, discard_mode=0)
    decoder.set_read_timeout(args.read_timeout)
     # 设置视频是否为本地视频。默认为False，即默认解码网络视频流。如果解码本地视频，需要设置为True，每路视频每秒固定解码25帧
    decoder.set_local_flag(args.is_local)
    # 本次测试的路数
    channel_num = args.channel_num

    # 向MultiDecoder添加channel
    ch_idx_list= []
    for i in range(channel_num):
        # 如果添加成功，则返回该通道的编号，从0开始
        ch_idx = decoder.add_channel(rtsp_streams[i], 0) # zero means no skip frame
        if (ch_idx >= 0):
            ch_idx_list.append(ch_idx)
            print(f"channel {ch_idx} is added")
        # 如果返回-1，说明添加失败
        else:
            print("add_channel failed")
            exit()
    
    # 创建并启动线程
    threads = []
    for i, ch_idx in enumerate(ch_idx_list):
        thread = threading.Thread(target=get_img_enc, args=(decoder,bmcv,ch_idx,is_save_jpeg,save_jpeg_path))
        thread.start()
        threads.append(thread)
        print(f"channel {ch_idx} is started")

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    print("All streams processed.")