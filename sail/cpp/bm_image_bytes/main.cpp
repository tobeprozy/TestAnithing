
#define USE_FFMPEG 1
#define USE_BMCV 1
#define USE_OPENCV 1

#include <cvwrapper.h>
#include <encoder.h>

#include "opencv2/opencv.hpp"
#include <stdio.h>
#include <iostream>
#include <string>
using namespace std;


int main(int argc, char *argv[]){

    string img_file="../1920x1080_yuvj420.jpg";
    int dev_id=0;
    // create handle
    auto handle = sail::Handle(dev_id);
    sail::Bmcv bmcv(handle);

    sail::BMImage img_input;
    sail::Decoder decoder((const string)img_file, true, dev_id);
    int ret = decoder.read(handle, img_input);

    bm_image frame;
    bm_image_create(handle.data(), img_input.height(), img_input.width(), FORMAT_YUV420P, DATA_TYPE_EXT_1N_BYTE, &frame);
    bmcv_image_storage_convert(handle.data(), 1, &img_input.data(), &frame);

    std::vector<unsigned char> byte_data;
    
    bmcv.bm_image_to_bytes(frame, byte_data);
    
    bmcv.imwrite("frame.jpg", frame);
    bm_image frame1;
    bm_image_create(handle.data(), img_input.height(), img_input.width(), FORMAT_YUV420P, DATA_TYPE_EXT_1N_BYTE, &frame1);

    bmcv.bytes_to_bm_image(byte_data,frame1);
    bmcv.imwrite("frame1.jpg", frame1);

}