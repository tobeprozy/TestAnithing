#include "bmcv_api_ext.h"

extern "C" {
#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libavutil/imgutils.h>
#include <libavutil/opt.h>
#include <libswscale/swscale.h>
}

#include <iostream>
#include <fstream>
#include <string.h>

#include "opencv2/opencv.hpp"

using namespace std;

typedef struct{
        bm_image *bmImg;
        uint8_t* buf0;
        uint8_t* buf1;
        uint8_t* buf2;
}transcode_t;

static inline int map_bmformat_to_avformat(int bmformat)
{
    int format;
    switch(bmformat){
        case FORMAT_YUV420P: format = AV_PIX_FMT_YUV420P; break;
        case FORMAT_YUV422P: format = AV_PIX_FMT_YUV422P; break;
        case FORMAT_YUV444P: format = AV_PIX_FMT_YUV444P; break;
        case FORMAT_NV12:    format = AV_PIX_FMT_NV12; break;
        case FORMAT_NV16:    format = AV_PIX_FMT_NV16; break;
        case FORMAT_GRAY:    format = AV_PIX_FMT_GRAY8; break;
        case FORMAT_RGBP_SEPARATE: format = AV_PIX_FMT_GBRP; break;
        default: printf("unsupported image format %d\n", bmformat); return -1;
    }
    return format;
}

static inline void bmBufferDeviceMemFree(void *opaque, uint8_t *data)
{
    if(opaque == NULL){
        printf("parameter error\n");
    }
    transcode_t *testTranscoed = (transcode_t *)opaque;
    av_freep(&testTranscoed->buf0);
    testTranscoed->buf0 = NULL;

    int ret =  0;
    ret = bm_image_destroy(*(testTranscoed->bmImg));
    if(testTranscoed->bmImg){
        free(testTranscoed->bmImg);
        testTranscoed->bmImg =NULL;
    }
    if(ret != 0)
        printf("bm_image destroy failed\n");
    free(testTranscoed);
    testTranscoed = NULL;
    return ;
}


static inline void bmBufferDeviceMemFree2(void *opaque, uint8_t *data)
{
    return ;
}

/**
 * @name    bm_image_to_avframe
 * @brief   Convert bmcv bm_image object to ffmpeg a avframe object
 * @ingroup bmruntime
 *
 * @param [in]           bm_handle   the low level device handle
 * @param [in]           in          a read-only  BMCV bm_image object.
 * @param [out]          out         a output avframe
                         just support YUV420P ,NV12 format.
 * @retval BM_SUCCESS    convert success.
 * @retval other values  convert failed.
 */

/**
 * @name    bm_image_to_avframe
 * @brief   Convert bmcv bm_image object to ffmpeg a avframe object
 * @ingroup bmruntime
 *
 * @param [in]           bm_handle   the low level device handle
 * @param [in]           in          a read-only  BMCV bm_image object.
 * @param [out]          out         a output avframe
                         just support YUV420P ,NV12 format.
 * @retval BM_SUCCESS    convert success.
 * @retval other values  convert failed.
 */
static inline bm_status_t bm_image_to_avframe(bm_handle_t &bm_handle,bm_image *in,AVFrame *out){
    transcode_t *ImgOut  = NULL;
    ImgOut = (transcode_t *)malloc(sizeof(transcode_t));
    ImgOut->bmImg = in;
    bm_image_format_info_t image_info;
    int idx       = 0;
    int plane     = 0;
    if(in == NULL || out == NULL){
        free(ImgOut);
        return BM_ERR_FAILURE;
    }

    if(ImgOut->bmImg->image_format == FORMAT_NV12){
        plane = 2;
    }
    else if(ImgOut->bmImg->image_format == FORMAT_YUV420P){
        plane = 3;
    }
    else{
        free(ImgOut);
        free(in);
        return BM_ERR_FAILURE;
    }

    out->format = (AVPixelFormat)map_bmformat_to_avformat(ImgOut->bmImg->image_format);
    out->height = ImgOut->bmImg->height;
    out->width = ImgOut->bmImg->width;

    if(ImgOut->bmImg->width > 0 && ImgOut->bmImg->height > 0
        && ImgOut->bmImg->height * ImgOut->bmImg->width <= 8192*4096) {
        ImgOut->buf0 = (uint8_t*)av_malloc(ImgOut->bmImg->height * ImgOut->bmImg->width * 3 / 2);
        ImgOut->buf1 = ImgOut->buf0 + (unsigned int)(ImgOut->bmImg->height * ImgOut->bmImg->width);
        if(plane == 3){
            ImgOut->buf2 = ImgOut->buf0 + (unsigned int)(ImgOut->bmImg->height * ImgOut->bmImg->width * 5 / 4);
        }
    }

    out->buf[0] = av_buffer_create(ImgOut->buf0,ImgOut->bmImg->width * ImgOut->bmImg->height,
        bmBufferDeviceMemFree,ImgOut,AV_BUFFER_FLAG_READONLY);
    out->buf[1] = av_buffer_create(ImgOut->buf1,ImgOut->bmImg->width * ImgOut->bmImg->height / 2 /2 ,
        bmBufferDeviceMemFree2,NULL,AV_BUFFER_FLAG_READONLY);
    out->data[0] = ImgOut->buf0;
    out->data[1] = ImgOut->buf0;

    if(plane == 3){
        out->buf[2] = av_buffer_create(ImgOut->buf2,ImgOut->bmImg->width * ImgOut->bmImg->height / 2 /2 ,
            bmBufferDeviceMemFree2,NULL,AV_BUFFER_FLAG_READONLY);
        out->data[2] = ImgOut->buf0;
    }

    if(plane == 3 && !out->buf[2]){
        av_buffer_unref(&out->buf[0]);
        av_buffer_unref(&out->buf[1]);
        av_buffer_unref(&out->buf[2]);
        free(ImgOut);
        free(in);
        return BM_ERR_FAILURE;
    }
    else if(plane == 2 && !out->buf[1]){
        av_buffer_unref(&out->buf[0]);
        av_buffer_unref(&out->buf[1]);
        free(ImgOut);
        free(in);
        return BM_ERR_FAILURE;
    }

    bm_device_mem_t mem_tmp[3];
    if(bm_image_get_device_mem(*(ImgOut->bmImg),mem_tmp) != BM_SUCCESS ){
        free(ImgOut);
        free(in);
        return BM_ERR_FAILURE;
    }
    if(bm_image_get_format_info(ImgOut->bmImg, &image_info) != BM_SUCCESS ){
        free(ImgOut);
        free(in);
        return BM_ERR_FAILURE;
    }
    for (idx=0; idx< plane; idx++) {
        out->data[4+idx]     = (uint8_t *)mem_tmp[idx].u.device.device_addr;
        out->linesize[idx]   = image_info.stride[idx];
        out->linesize[4+idx] = image_info.stride[idx];
    }
    return BM_SUCCESS;
}

int main(int argc, char* argv[]) {
  cout << "nihao!!" << endl;

  string left_img = "../Left.png";
  string right_img = "../Right.png";

    int dev_id = 0;
  bm_handle_t bm_handle;
  bm_status_t status = bm_dev_request(&bm_handle, 0);

  bm_image src_img[2];
  // picDec(h, left_img.c_str(), src_img[0]);
  // picDec(h, right_img.c_str(), src_img[1]);


  //decode
  cv::Mat left_img_mat = cv::imread(left_img);
  cv::Mat right_img_mat = cv::imread(right_img);

  cv::bmcv::toBMI(left_img_mat, &src_img[0],true);
  cv::bmcv::toBMI(right_img_mat, &src_img[1],true);

  // vpss
  //dwa
  
  // stitch
  int input_num = 2;
  bmcv_rect_t dst_crop[input_num];
  bmcv_rect_t src_crop[input_num];

  int src_crop_stx = 0;
  int src_crop_sty = 0;
  int src_crop_w = src_img[0].width;
  int src_crop_h = src_img[0].height;

  int dst_w = src_img[0].width+src_img[1].width;
  int dst_h = max(src_img[0].height,src_img[1].height);
  int dst_crop_w = dst_w;
  int dst_crop_h = dst_h;

  src_crop[0].start_x = 0 ;
  src_crop[0].start_y = 0;
  src_crop[0].crop_w = src_img[0].width;
  src_crop[0].crop_h = src_img[0].height;

  src_crop[1].start_x = 0;
  src_crop[1].start_y = 0;
  src_crop[1].crop_w = src_img[1].width;
  src_crop[1].crop_h = src_img[1].height;

  dst_crop[0].start_x = 0 ;
  dst_crop[0].start_y = 0;
  dst_crop[0].crop_w = src_img[0].width;
  dst_crop[0].crop_h = src_img[0].height;

  dst_crop[1].start_x = src_img[0].width;
  dst_crop[1].start_y = 0;
  dst_crop[1].crop_w = src_img[1].width;
  dst_crop[1].crop_h = src_img[1].height;
  


  bm_image dst_img;
  bm_image_format_ext src_fmt=src_img[0].image_format;
  bm_image_create(bm_handle,dst_h,dst_w,src_fmt,DATA_TYPE_EXT_1N_BYTE,&dst_img);

  auto start =std::chrono::system_clock::now();
  bmcv_image_vpp_stitch(bm_handle, input_num, src_img, dst_img, dst_crop, src_crop);
  auto end =std::chrono::system_clock::now();
  std::chrono::duration<double> elapsed_seconds = end-start;
  std::cout<<"elapsed time: "<<elapsed_seconds.count()<<""<<std::endl;

  bm_image_write_to_bmp(dst_img,"dst.png");

  AVFrame frame1;
  bm_image_to_avframe(bm_handle,&dst_img,&frame1);
  
   // 使用FFmpeg发送图像
  av_register_all();

  AVFormatContext* formatContext = nullptr;
  AVOutputFormat* outputFormat = nullptr;
  AVStream* stream = nullptr;
  AVCodecContext* codecContext = nullptr;
  AVCodec* codec = nullptr;
  AVFrame* frame = nullptr;
  AVPacket packet;

  string outputUrl = "rtsp://172.25.92.230/your_stream_name";

  avformat_alloc_output_context2(&formatContext, nullptr, "rtsp", outputUrl.c_str());
  if (!formatContext) {
    cerr << "Failed to allocate output context" << endl;
    return -1;
  }

  outputFormat = formatContext->oformat;

  stream = avformat_new_stream(formatContext, nullptr);
  if (!stream) {
    cerr << "Failed to create new stream" << endl;
    return -1;
  }

  codecContext = stream->codec;
  codecContext->codec_id = outputFormat->video_codec;
  codecContext->codec_type = AVMEDIA_TYPE_VIDEO;
  codecContext->pix_fmt = AV_PIX_FMT_BGR24;
  codecContext->width = dst_w;
  codecContext->height = dst_h;
  codecContext->time_base = {1, 25}; // 设置帧率为25fps

  codec = avcodec_find_encoder(codecContext->codec_id);
  if (!codec) {
    cerr << "Codec not found" << endl;
    return -1;
  }

  if (avcodec_open2(codecContext, codec, nullptr) < 0) {
    cerr << "Failed to open codec" << endl;
    return -1;
  }

  frame = av_frame_alloc();
  if (!frame) {
    cerr << "Failed to allocate frame" << endl;
    return -1;
  }

  frame->format = codecContext->pix_fmt;
  frame->width = codecContext->width;
  frame->height = codecContext->height;

  if (av_frame_get_buffer(frame, 0) < 0) {
    cerr << "Failed to allocate frame buffer" << endl;
    return -1;
  }

  if (avformat_write_header(formatContext, nullptr) < 0) {
    cerr << "Failed to write header" << endl;
    return -1;
  }

  // 将dst图像数据复制到AVFrame中
  av_image_fill_arrays(frame->data, frame->linesize, dst_img, AV_PIX_FMT_BGR24, dst_w, dst_h, 1);

  // 发送图像数据
  av_init_packet(&packet);
  packet.data = nullptr;
  packet.size = 0;

  if (avcodec_send_frame(codecContext, frame) < 0) {
    cerr << "Failed to send frame" << endl;
    return -1;
  }

  while (avcodec_receive_packet(codecContext, &packet) >= 0) {
    av_packet_rescale_ts(&packet, codecContext->time_base, stream->time_base);
    packet.stream_index = stream->index;

    av_interleaved_write_frame(formatContext, &packet);
    av_packet_unref(&packet);
  }

  av_write_trailer(formatContext);

  // 释放资源
  avcodec_free_context(&codecContext);
  av_frame_free(&frame);
  avformat_free_context(formatContext);

  return 0;


}
