import sophon.sail as sail
import numpy as np

dev_id=0
handle=sail.Handle(dev_id)
bmcv=sail.Bmcv(handle)

decoder = sail.Decoder("test.jpg", True, 0)
bimg = sail.BMImage()
ret = decoder.read(handle, bimg)

encode_img=bmcv.imencode(".jpg",bimg)

yuv420_img = sail.BMImage(handle, bimg.height(), bimg.width(),
                                          sail.Format.FORMAT_YUV420P, sail.DATA_TYPE_EXT_1N_BYTE)
bmcv.convert_format(bimg, yuv420_img)

imgyuv420= yuv420_img.asmat()

print("all down")