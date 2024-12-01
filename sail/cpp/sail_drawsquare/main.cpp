
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

//接口没加，跑不了
int main(int argc, char *argv[]){

    cout<<"nihao!!"<<endl;

    string img_file="zidane.jpg";
    int dev_id=0;

    auto handle = sail::Handle(dev_id);
    sail::Bmcv bmcv(handle);

    sail::BMImage bmimg;
    sail::Decoder decoder((const string)img_file, true, dev_id);
    int ret = decoder.read(handle, bmimg);
    // bmcv.imwrite("bmimg.jpg",bmimg.data());
    
    std::tuple<int, int, int> color = std::make_tuple(255, 0, 0); // 红色
    bmcv_point_t coord = {300, 300};
    ret=bm_image_is_attached(bmimg.data());
    bmcv_image_draw_point(handle.data(), bmimg.data(), 1, &coord, 10, 255, 0, 0);

    bmcv.drawsquare(bmimg.data(),300,300,10,color);
    bmcv.imwrite("bmimg.jpg",bmimg.data());
}