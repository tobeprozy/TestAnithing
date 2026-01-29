import sophon.sail as sail
import numpy as np
import time

dev_id=0
handle=sail.Handle(dev_id)
bmcv=sail.Bmcv(handle)

decoder = sail.Decoder("1920x1080_yuvj420.jpg", True, 0)

bimg = sail.BMImage()
ret = decoder.read(handle, bimg)

yuv420_img = sail.BMImage(handle, bimg.height(), bimg.width(),
                                          sail.Format.FORMAT_YUV420P, sail.DATA_TYPE_EXT_1N_BYTE)
bmcv.convert_format(bimg, yuv420_img)
for i in range(100):
    # convert to bytes
    start =time.time()
    yuv420p_bytes=bmcv.bm_image_to_bytes(yuv420_img)
    end =time.time()
    print("bm_image_to_bytes convert time:",1000*(end-start),"ms")

    # print(len(yuv420p_bytes))


    # convert to bytes
    start =time.time()
    yuv420p_mat=yuv420_img.asmat().tobytes()
    end =time.time()
    print("yuv420_img.asmat().tobytes():",1000*(end-start),"ms")


    yuv420_img2 = sail.BMImage(handle, bimg.height(), bimg.width(),
                                            sail.Format.FORMAT_YUV420P, sail.DATA_TYPE_EXT_1N_BYTE)
    # convert to yuv420p
    
    start =time.time()
    bmcv.bytes_to_bm_image(yuv420p_bytes,yuv420_img2)
    end =time.time()
    print("bytes_to_bm_image:",1000*(end-start),"ms")

bmcv.imwrite("yuv420.jpg",yuv420_img2)

