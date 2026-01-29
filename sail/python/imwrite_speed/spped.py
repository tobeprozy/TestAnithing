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
for i in range(1000):
   
    start =time.time()
    bmcv.imwrite("yuv420.jpg",yuv420_img)
    end =time.time()
    print("imwrite cost:",1000*(end-start),"ms")



