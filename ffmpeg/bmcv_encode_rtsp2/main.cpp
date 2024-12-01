#include "ff_decode.hpp"

#include "bmcv_api_ext.h"
#include <unistd.h>
#include <dirent.h>
#include <sys/stat.h>
#include <regex>
#include <iostream>
#include <fstream>
#include <string.h>
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


int encode_rtsp(bm_handle_t handle,int dev_id,string output_path,int output_type){
   
}


int main(int argc, char* argv[]) {
  cout << "nihao!!" << endl;

  string img_file = "../../../../datasets/images/demo.png";

  string output_path="rtsp://127.0.0.1:8554/mystream";
  string enc_fmt="h264_bm";
  string pix_fmt="NV12";
  string enc_params="width=1920:height=1080:gop=32:gop_preset=3:framerate=25:bitrate=2000";

  int dev_id = 0;
  bm_handle_t handle;
  bm_status_t status = bm_dev_request(&handle, 0);

  int output_type=1;

  AVPixelFormat pix_fmt_;
    // AVFrame *frame_;
  AVCodec *encoder;
  AVDictionary *enc_dict;
  AVIOContext *avio_ctx;
  AVFormatContext *enc_format_ctx;
  AVOutputFormat *enc_output_fmt;
  AVCodecContext *enc_ctx;
  AVStream *out_stream;
  AVPacket *pkt;
  bool is_rtsp;
  bool opened;
  std::map<std::string, int> params_map;

  bm_dev_request(&handle,dev_id);

  unsigned int chip_id=0x1684;
  bm_get_chipid(handle, &(chip_id));

    //先写一个，rtsp
  switch(output_type){
      case 1:   
            avformat_alloc_output_context2(&enc_format_ctx, NULL, "rtsp", output_path.c_str());
            is_rtsp = true;
            break;
  }
  if(!enc_format_ctx){
    throw std::runtime_error("Could not create output context");
  }

  encoder = avcodec_find_encoder_by_name(enc_fmt.c_str());
  if(!encoder){
    throw std::runtime_error("Could not find encoder");
  }

  enc_ctx = avcodec_alloc_context3(encoder);
  if(!enc_ctx){
    throw std::runtime_error("Could not allocate video codec context");
  }

  if(enc_format_ctx->oformat->flags & AVFMT_GLOBALHEADER)
    enc_ctx->flags |= AV_CODEC_FLAG_GLOBAL_HEADER;


  //解析参数
  params_map.insert(std::pair<std::string, int>("width", 1920));
  params_map.insert(std::pair<std::string, int>("height", 1080));
  params_map.insert(std::pair<std::string, int>("framerate", 25));
  params_map.insert(std::pair<std::string, int>("bitrate", 2000));
  params_map.insert(std::pair<std::string, int>("gop", 32));
  params_map.insert(std::pair<std::string, int>("gop_preset", 3));
  params_map.insert(std::pair<std::string, int>("mb_rc", 0));
  params_map.insert(std::pair<std::string, int>("qp", -1));
  params_map.insert(std::pair<std::string, int>("bg", 0));
  params_map.insert(std::pair<std::string, int>("nr", 0));
  params_map.insert(std::pair<std::string, int>("weightp", 0));


  std::string s1;
  s1.append(1, ':');
  std::regex reg1(s1);

  std::string s2;
  s2.append(1, '=');
  std::regex reg2(s2);

  std::vector<std::string> elems(std::sregex_token_iterator(enc_params.begin(), enc_params.end(), reg1, -1),
                                  std::sregex_token_iterator());
  for (auto param : elems)
  {
      std::vector<std::string> key_value_(std::sregex_token_iterator(param.begin(), param.end(), reg2, -1),
                                      std::sregex_token_iterator());

      std::string temp_key = key_value_[0];
      std::string temp_value = key_value_[1];

      params_map[temp_key] = std::stoi(temp_value);
  }


   if (pix_fmt == "I420")
    {
        pix_fmt = AV_PIX_FMT_YUV420P;
    }
    else if (pix_fmt == "NV12")
    {
        pix_fmt = AV_PIX_FMT_NV12;
    }
    else
    {
        throw std::runtime_error("Not support encode pix format.");
    }


    enc_ctx->codec_id      =   encoder->id;
    enc_ctx->pix_fmt       =   pix_fmt_;
    enc_ctx->width         =   params_map["width"];
    enc_ctx->height        =   params_map["height"];
    enc_ctx->gop_size      =   params_map["gop"];
    enc_ctx->time_base     =   (AVRational){1, params_map["framerate"]};
    enc_ctx->framerate     =   (AVRational){params_map["framerate"], 1};
    if(-1 == params_map["qp"])
    {
        enc_ctx->bit_rate_tolerance = params_map["bitrate"]*1000;
        enc_ctx->bit_rate      =   (int64_t)params_map["bitrate"]*1000;
    }else{
        av_dict_set_int(&enc_dict, "qp", params_map["qp"], 0);
    }

    av_dict_set_int(&enc_dict, "sophon_idx", dev_id, 0);
    av_dict_set_int(&enc_dict, "gop_preset", params_map["gop_preset"], 0);
    // av_dict_set_int(&enc_dict_, "mb_rc",      params_map_["mb_rc"],      0);    0);
    // av_dict_set_int(&enc_dict_, "bg",         params_map_["bg"],         0);
    // av_dict_set_int(&enc_dict_, "nr",         params_map_["nr"],         0);
    // av_dict_set_int(&enc_dict_, "weightp",    params_map_["weightp"],    0);
    av_dict_set_int(&enc_dict, "is_dma_buffer", 1, 0);

    // open encoder
    int ret = avcodec_open2(enc_ctx, encoder, &enc_dict);
    if(ret < 0){
        throw std::runtime_error("avcodec_open failed.");
    }
    av_dict_free(&enc_dict);

    // new stream
    out_stream = avformat_new_stream(enc_format_ctx, encoder);
    out_stream->time_base      = enc_ctx->time_base;
    out_stream->avg_frame_rate = enc_ctx->framerate;
    out_stream->r_frame_rate   = out_stream->avg_frame_rate;

    ret = avcodec_parameters_from_context(out_stream->codecpar, enc_ctx);
    if(ret < 0)
    {
        throw std::runtime_error("avcodec_parameters_from_context failed.");
    }

    if (!(enc_format_ctx->oformat->flags & AVFMT_NOFILE)) {
        ret = avio_open(&enc_format_ctx->pb, output_path.c_str(), AVIO_FLAG_WRITE);
        if (ret < 0) {
  
            throw std::runtime_error("avio_open2 failed.");
        }
    }

    ret = avformat_write_header(enc_format_ctx, NULL);
        if (ret < 0) {
            throw std::runtime_error("avformat_write_header failed.");
        }
    opened = true;


    bm_image image;
    AVFrame *frame = av_frame_alloc();
    ret = bm_image_to_avframe(handle, &image, frame);

}
