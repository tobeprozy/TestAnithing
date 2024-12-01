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
#include "bmcv_api_ext.h"

using namespace std;

// ---npu ---vpp ---vpu ---
// ---0001---0010---0100---

int main(int argc, char* argv[]) {

  int dev_id = 0;
  bm_handle_t bm_handle;
  bm_status_t status = bm_dev_request(&bm_handle, 0);
  bm_image frame1;
  bm_image_create(bm_handle, 1080, 1920, FORMAT_BGR_PACKED,                  DATA_TYPE_EXT_1N_BYTE, &frame1);
  status=bm_image_alloc_dev_mem_heap_mask(frame1,5);//指定到npu heap和vpu heap
  std::cout << "frame1.width:" << frame1.width << " frame1.height:" << frame1.height << std::endl;

  bm_image frame2;
  bm_image_create(bm_handle, 1080, 1920, FORMAT_BGR_PACKED,                  DATA_TYPE_EXT_1N_BYTE, &frame2);
  status=bm_image_alloc_dev_mem_heap_mask(frame2,5);//指定到npu heap和vpu heap
  std::cout << "frame2.width:" << frame2.width << " frame2.height:" << frame2.height << std::endl;


  bm_image frame3;
  bm_image_create(bm_handle, 1080, 1920, FORMAT_BGR_PACKED,                  DATA_TYPE_EXT_1N_BYTE, &frame3);
  status=bm_image_alloc_dev_mem_heap_mask(frame3,0b0100);//指定到vpu
  std::cout << "frame3.width:" << frame3.width << " frame3.height:" << frame3.height << std::endl;

  bm_image frame4;
  bm_image_create(bm_handle, 1080, 1920, FORMAT_BGR_PACKED,                  DATA_TYPE_EXT_1N_BYTE, &frame4);
  status=bm_image_alloc_dev_mem_heap_mask(frame4,0b0010);//指定到vpp
  std::cout << "frame4.width:" << frame4.width << " frame4.height:" << frame4.height << std::endl;

}
