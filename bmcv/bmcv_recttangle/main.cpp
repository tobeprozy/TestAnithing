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
#include "bmcv_api_ext_c.h"
#include "chrono"

using namespace std;

int main(int argc, char* argv[]) {
  cout << "nihao!!" << endl;

  string img_file = "../1920x1080_yuvj420.jpg";
  int dev_id = 0;
  bm_handle_t bm_handle;
  bm_status_t status = bm_dev_request(&bm_handle, 0);

  bm_image bmimg;
  picDec(bm_handle, img_file.c_str(), bmimg);

  bmcv_rect_t rect;
  rect.start_x = 100;
  rect.start_y = 100;
  rect.crop_w = 200;
  rect.crop_h = 300;
  auto start = std::chrono::high_resolution_clock::now();
  bmcv_image_draw_rectangle(bm_handle, bmimg, 1, &rect, 3, 255, 0, 0);
  auto end = std::chrono::high_resolution_clock::now();
  std::chrono::duration<double> elapsed = end - start;
  std::cout << "elapsed time: " << elapsed.count()*1000 << " ms\n";

  bm_image_write_to_bmp(bmimg, "output.bmp");

  
  cv::Mat cvmat;
  cv::bmcv::toMAT(&bmimg, cvmat);
  start= std::chrono::high_resolution_clock::now();
  cv::rectangle(cvmat, cv::Point(rect.start_x, rect.start_y), cv::Point(rect.start_x + rect.crop_w, rect.start_y + rect.crop_h), cv::Scalar(0, 255, 0), 3);
  end = std::chrono::high_resolution_clock::now();
  elapsed = end - start;
  std::cout << "elapsed time: " << elapsed.count()*1000 << " ms\n";
  std::string fname = cv::format("cbmat_%d.jpg", 0);
  cv::imwrite(fname, cvmat);
  
  bm_dev_free(bm_handle);
  

}

