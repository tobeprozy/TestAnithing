#include "bmcv_api_ext.h"
#include "ff_video_decode.h"
extern "C"
{
    #include "libavcodec/avcodec.h"
    #include "libavformat/avformat.h"
}
#include <string>
#include <fstream>
#include <cassert>
#include <cstring>
#include <csignal>
#include <chrono>
#include <iomanip>
#include <iostream>
#include <sstream>

int quit_flag = 0;
void handler(int sig);
void write_frame(const AVFrame* frame, const std::string &prefix);

int main(int argc, char* argv[])
{
    const int devid = 0;
    // const std::string filename = "rtsp://admin:media266@172.26.13.175:554/Streaming/Channels/1";
    // const std::string prefix = "./results/";
    if (argc != 3)
    {
        std::cerr << "usage: `./test_latency [input_rtsp_url] [path_to_save_yuv]`" << std::endl;
        std::cerr << "example: `./test_latency rtsp://... ./results/`" << std::endl;
        exit(-1);
    }
    const std::string filename = argv[1];
    const std::string prefix = argv[2];

    VideoDec_FFMPEG reader;
    int ret = 0;
    int codec_name_flag = 0;
    std::string decoder_name = "";
    int output_format_mode = 100;
    int pre_allocation_frame = 5;
    int zero_copy = 0;
    int api_version = 1;
    ret = reader.openDec(filename.c_str(), codec_name_flag,
                            decoder_name.c_str(), output_format_mode,
                            pre_allocation_frame, devid,
                            zero_copy, api_version);
    if (ret < 0)
    {
        printf("open input media failed\n");
        exit(-1);
    }
    AVFrame *frame = nullptr;

    signal(SIGINT, handler);
    signal(SIGTERM, handler);

    while (!quit_flag)
    {

        frame = reader.grabFrame2();

        if(!frame)
        {
            printf("no frame!\n");
            break;
        }

        write_frame(frame, prefix);
    }
}

std::string getTime() {
  auto now = std::chrono::system_clock::now();
  auto now_time_t = std::chrono::system_clock::to_time_t(now);
  // 获取毫秒部分
  auto us = std::chrono::duration_cast<std::chrono::microseconds>(
                now.time_since_epoch()) % 1000000;
  // 格式化时间为年月日时分秒毫秒的形式
  std::tm tm = *std::localtime(&now_time_t);
  std::ostringstream oss;
  oss << std::put_time(&tm, "%Y%m%d_%H%M%S.") << std::setfill('0')
      << std::setw(6) << us.count();
  return oss.str();
}

void write_frame(const AVFrame* frame, const std::string &prefix) {
  // frame format is NV12, two channels
  bm_device_mem_t input_addr[2];
  int size[2] = { frame->linesize[0] * frame->height, frame->linesize[0] * frame->height / 2};

  std::string filename = prefix + getTime() + "_" + std::to_string(frame->width) + "x" + std::to_string(frame->height) + "_NV12.yuv";
  std::cout << filename << std::endl;
  std::ofstream file(filename, std::ios::ate | std::ios::binary);
  if (file.bad()) {
    std::cerr << "Error opening file for writing" << std::endl;
    exit(-1);
  }
  file.write(reinterpret_cast<char*>(frame->data[0]), size[0]);
  file.write(reinterpret_cast<char*>(frame->data[1]), size[1]);
}

void handler(int sig)
{
    quit_flag = 1;
    printf("program will exit \n");
}