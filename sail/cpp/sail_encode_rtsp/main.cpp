
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

    const char *inputFile = "/home/zhiyuanzhang/sophon/sophon_api_test/datasets/videos/dance_1080P.mp4";
    
    int dev_id=0;

    auto handle = sail::Handle(dev_id);
    sail::Bmcv bmcv(handle);

    
    sail::Decoder decoder((const string)inputFile, true, dev_id);


    string output="rtsp://127.0.0.1:8554/mystream";
    string enc_fmt="h264_bm";
    string pix_fmt="NV12";
    string enc_params="width=1920:height=1080:gop=32:gop_preset=3:framerate=25:bitrate=2000";

    sail::Encoder  encoder(output, handle,enc_fmt,pix_fmt,enc_params);

    while(true){
        sail::BMImage bmimg;
        int ret=decoder.read(handle, bmimg);
        
        sleep(0.01);
        cout<<bmimg.width()<<" "<<bmimg.height()<<endl;
        cout<<bmimg.format()<<endl;
        // bmcv.imwrite("bmimg.jpg",bmimg.data());

        ret =encoder.is_opened();
        
        ret=encoder.video_write(bmimg);
        
    }
    encoder.release();
    return 0;
}