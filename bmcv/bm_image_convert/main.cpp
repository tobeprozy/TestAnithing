//===----------------------------------------------------------------------===//
//
// Copyright (C) 2023 Sophgo Technologies Inc.  All rights reserved.
//
// SOPHON-DEMO is licensed under the 2-Clause BSD License except for the
// third-party components.
//
//===----------------------------------------------------------------------===//

#include <string.h>
#include <iostream>
#include "ff_decode.hpp"

using namespace std;

int main(int argc, char* argv[]) {
  cout << "nihao!!" << endl;

  string img_file = "../../../../datasets/images/demo.png";
  
  int dev_id = 0;
  bm_handle_t bm_handle;
  bm_status_t status = bm_dev_request(&bm_handle, 0);

  bm_image bmimg;
  picDec(bm_handle, img_file.c_str(), bmimg);

  int i = 0;
  cv::Mat cvmat;
  cv::bmcv::toMAT(&bmimg, cvmat);
  std::string fname = cv::format("cbmat_%d.jpg", i);
  cv::imwrite(fname, cvmat);

  cv::Mat cvmat2;
  cvmat2 = cv::imread(img_file);

  bm_image bmimg2;
  cv::bmcv::toBMI(cvmat2, &bmimg2, true);
  bm_image_write_to_bmp(bmimg2, "bmimg2.bmp");

  bm_image frame;
  bm_image_create(bm_handle, bmimg2.height, bmimg2.width, FORMAT_YUV420P,
                  bmimg2.data_type, &frame);
  bmcv_image_storage_convert(bm_handle, 1, &bmimg2, &frame);



  bmcv_copy_to_atrr_t copyToAttr;
  memset(&copyToAttr, 0, sizeof(copyToAttr));
  copyToAttr.start_x = 0;
  copyToAttr.start_y = 0;
  copyToAttr.if_padding = 1;

  bm_image frame1;
  bm_image_create(bm_handle, 460, 1184, FORMAT_BGR_PACKED,
                  DATA_TYPE_EXT_1N_BYTE, &frame1);
  bm_image frame2;
  bm_image_create(bm_handle, 460, 1184, FORMAT_BGR_PACKED,
                  DATA_TYPE_EXT_1N_BYTE, &frame2);

  bm_image_alloc_dev_mem(frame1,BMCV_IMAGE_FOR_IN);
  bm_image_alloc_dev_mem(frame2,BMCV_IMAGE_FOR_IN);

  
  auto start =std::chrono::system_clock::now();
  bmcv_image_copy_to(bm_handle, copyToAttr, frame1, frame2);
  auto end =std::chrono::system_clock::now();
  std::chrono::duration<double> elapsed_seconds = end-start;
  std::cout << "elapsed time: " << elapsed_seconds.count() * 1000 << "ms" << std::endl;


  // string img_path
  // void *jpeg_data = NULL;
  // size_t out_size = 0;
  // int ret = bmcv_image_jpeg_enc(bm_handle, 1, &frame, &jpeg_data, &out_size);
  // if (ret == BM_SUCCESS)
  // {
  //   FILE *fp = fopen(img_path.c_str(), "wb");
  //   fwrite(jpeg_data, out_size, 1, fp);
  //   fclose(fp);
  // }
  // free(jpeg_data);
  // bm_image_destroy(frame);

  // VideoDecFFM decoder;
  // decoder.openDec(&bm_handle, input.c_str());
  // bm_image* img = decoder.grab();
}
