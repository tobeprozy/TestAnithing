# import sophon.sail as sail
 
# def main():
#     dev_id = 0
#     decformat = "h264"
#     h264_decoder = sail.Decoder_RawStream(dev_id, decformat)
 
#     handle = sail.Handle(dev_id)
#     bmcv = sail.Bmcv(handle)
 
#     # 读取H.264数据并处理图像
#     with open("20240702_150921_149369_6934-67356", "rb") as h264_file:
#         h264_data = h264_file.read()
#         image = sail.BMImage()  # 创建bm_image对象
#         continue_frame = True
#     while(True):
#         result = h264_decoder.read(h264_data,image, continue_frame)
        
#         if result == 0:
#             print("成功处理H.264数据。")
#         else:
#             print("处理H.264数据时出错。")
 
#         bmcv.imwrite("save_path.jpg", image)
 
# if __name__ == '__main__':
#     main()


# rgb_planar_img = sail.BMImage(handle, image.height(), image.width(),
#                                     sail.Format.FORMAT_RGB_PLANAR, sail.DATA_TYPE_EXT_1N_BYTE)
# bmcv.convert_format(image, rgb_planar_img)

# rgb_mat = rgb_planar_img.asmat()
# nv21_mat=image.asmat()
        

import threading
import sophon.sail as sail
import os

def decode_and_save(h264_decoder, h264_data,bmcv,save_dir):
    thread_id = threading.get_ident()

    image = sail.BMImage()  # 创建bm_image对象
    continue_frame = False
    frame_count = 0

    while True:
        result = h264_decoder.read(h264_data, image, continue_frame)
        
        if result == 0:
            print(f"Thread {thread_id}: 成功处理H.264数据。{frame_count}")
            frame_count += 1
            # save_path = os.path.join(save_dir, f"frame_{frame_count}.jpg")
            # bmcv.imwrite(save_path, image)
        else:
            print(f"Thread {thread_id}: 处理H.264数据时出错。")
            break

def main():
    dev_id_1 = 0
    decformat = "h264"
    h264_decoder = sail.Decoder_RawStream(dev_id_1, decformat)
    handle = sail.Handle(dev_id_1)
    bmcv = sail.Bmcv(handle)

    with open("20240702_150921_149369_6934-67356", "rb") as h264_file:
        h264_data = h264_file.read()

    # 创建线程列表
    threads = []

    # 创建并启动50个线程
    for i in range(50):
        save_dir = f"thread_{i}"
        os.makedirs(save_dir, exist_ok=True)
        thread = threading.Thread(target=decode_and_save, args=(h264_decoder, h264_data,bmcv,save_dir))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    main()