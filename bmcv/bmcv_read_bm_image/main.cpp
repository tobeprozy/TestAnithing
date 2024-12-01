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
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>


using namespace std;

int main(int argc, char* argv[]) {
  cout << "nihao!!" << endl;

  string img_file = "./1920x1080_yuvj420.jpg";
  int dev_id = 0;
  bm_handle_t bm_handle;
  bm_status_t status = bm_dev_request(&bm_handle, 0);

  bm_image bmimg;
  picDec(bm_handle, img_file.c_str(), bmimg);

  bm_image frame;
  bm_image_create(bm_handle, bmimg.height, bmimg.width, FORMAT_YUV420P,
                  bmimg.data_type, &frame);
  bmcv_image_storage_convert(bm_handle, 1, &bmimg, &frame);

  int width = frame.width;
  int height = frame.height;

  int y_size = width * height;
  int uv_size = (width / 2) * (height / 2);

  int byte_size = y_size + 2 * uv_size; // YUV420P 格式的总字节数

  unsigned char* output_ptr = (unsigned char *)malloc(byte_size);
  void* out_ptr[4] = {(void*)output_ptr,
                      (void*)(output_ptr + y_size),
                      (void*)(output_ptr + y_size + uv_size),
                      (void*)(output_ptr + y_size + uv_size * 2)};


  bm_image_copy_device_to_host(frame, (void **)out_ptr);

// 创建一个 NumPy 数组共享数据
  py::array_t<unsigned char> array({byte_size}, {1}, output_ptr);

  // 获取 buffer_info
  py::buffer_info info = array.request();

  // 创建 Python 字节对象
  py::bytes result(reinterpret_cast<const char*>(info.ptr), byte_size);

  // 释放内存
  free(output_ptr);

}

// static_cast<int>(output_ptr[i]) 只是将 output_ptr[i] 的值从 uint8_t 类型转换为 int 类型，但并不改变读取的地址长度。
// reinterpret_cast<int*>(output_ptr + i) 这样的操作会将 output_ptr + i 的地址解释为 int* 类型的指针，然后你可以通过这个指针来连续读取 sizeof(int) 长度的数据作为一个整数。
