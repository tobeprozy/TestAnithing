
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

    cout<<"nihao!!"<<endl;

    string img_file="rtsp://172.26.13.138:8554/stream0";
    int dev_id=0;

    auto handle = sail::Handle(dev_id);
    sail::Bmcv bmcv(handle);

    sail::BMImage bmimg;
    sail::Decoder decoder((const string)img_file, true, dev_id);
    int ret=0;
    while(ret==0){
        ret = decoder.read(handle, bmimg);
        bmcv.imwrite("bmimg.jpg",bmimg.data());
    }
    

    cv::Mat cvmat2;
    cvmat2=cv::imread(img_file);


}