import cv2
import argparse

if __name__ == "__main__":
    paraser = argparse.ArgumentParser()
    paraser.add_argument('--input', type=str, default="rtsp://172.25.4.119:8554/1",help='input video file')
    paraser.add_argument('--output', type=str,default="rtsp://172.25.4.119:8554/2", help='output directory')
    args = paraser.parse_args()   
    
    cap = cv2.VideoCapture()
    if not cap.open(args.input):
        raise Exception("can not open the video")
    fourcc = cv2.VideoWriter_fourcc(*'h264')
    fps = cap.get(cv2.CAP_PROP_FPS)
    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    # print(fps, size)

    out = cv2.VideoWriter(args.output, fourcc, fps, size)
    
    end_flag=False
    count = 0
    while not end_flag:
        ret, frame = cap.read()
        if not ret or frame is None:
            end_flag = True
        else:
            print("write frame %d" % count)
            out.write(frame)
            count += 1
    cap.release()
    out.release()