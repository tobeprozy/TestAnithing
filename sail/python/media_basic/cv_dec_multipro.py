import cv2
from multiprocessing import Process
import os
import requests
import json

url_get_rtsp = 'http://aitest.qimiaowa.com:30356/ai-video-training/getVideoURL?videoId={}'
token_get_rtsp = '044fe1b9-478b-409f-b902-c0bd57fa645b'
headers = {"Token": token_get_rtsp}


video_ids = [581,581,121,121,600,600,675,675,612,612] # ,242,251,315,318

rtsp_streams=[]
for video_id in video_ids:
    url = ''
    url_request = url_get_rtsp.format(video_id)
    try:
        res = requests.get(url_request, headers=headers)
        res = json.loads(res.text)
        url = res['data']
        print('url:', url)
    except Exception as e:
        print(e)
    # rtsp_streams.append('rtsp://172.28.3.201:5544/vod/123/out264-20700.264')
    rtsp_streams.append(url)

# 输出目录
output_dir = 'results'

# 确保输出目录存在
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


# 处理每个视频流的线程函数
def process_stream(stream_index,frame_total):
    stream_url = rtsp_streams[stream_index]
    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        print(f"Failed to open stream: {stream_url}")
        return
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fps = cap.get(cv2.CAP_PROP_FPS)
    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    output_video_path = os.path.join(output_dir, 'output_' + os.path.basename(stream_url)+str(stream_index) + '.avi')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, size)

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 这里处理帧，例如保存或显示帧
        print(f"Decoding frame {frame_count} from stream {stream_url} _ {stream_index}")
        frame_count += 1
        out.write(frame)
        # 假设我们只处理前100帧
        if frame_count >= frame_total:
            break

    # 释放资源
    cap.release()
    print(f"Stream {stream_url} processing done.")

# 创建并启动线程
processes = []
frame_total = 1000

for i in range(len(rtsp_streams)):
    p = Process(target=process_stream, args=(i,frame_total))
    p.start()
    processes.append(p)

for p in processes:
    p.join()


print("All streams processed.")
