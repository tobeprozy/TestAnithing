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

using namespace std;

int main(int argc, char* argv[]) {
  cout << "nihao!!" << endl;

  string img_file = "./1920x1080_yuvj420.jpg";
  int dev_id = 0;
  bm_handle_t bm_handle;
  bm_status_t status = bm_dev_request(&bm_handle, 0);

  bm_image bmimg;
  picDec(bm_handle, img_file.c_str(), bmimg);



  int size = 0;
  auto ret = bm_image_get_byte_size(bmimg, &size);
  unsigned char* data;
  data = new unsigned char[size];
  memset(data, 0, size);
  ret = bm_image_copy_device_to_host(bmimg, (void**)&data);
  

    // 输出图像数据
  for (int i = 0; i < 1; ++i) {
    for (int j = 0; j < 128; ++j) {
      std::cout << static_cast<float>(data[i * 128 + j]) - 3 << " ";
    }
    std::cout << std::endl;  // 在每行结束时换行
  }
  delete[] data;
  

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

  // // 打印 Y 平面数据
  // printf("Y plane data:\n");
  // for (int i = 0; i < y_size; i++) {
  //     printf("%d ", output_ptr[i]);
  // }
  // printf("\n");

  // // 打印 U 平面数据
  // printf("U plane data:\n");
  // for (int i = y_size; i < y_size + uv_size; i++) {
  //     printf("%d ", output_ptr[i]);
  // }
  // printf("\n");

  // // 打印 V 平面数据
  // printf("V plane data:\n");
  // for (int i = y_size + uv_size; i < y_size + 2 * uv_size; i++) {
  //     printf("%d ", output_ptr[i]);
  // }
  // printf("\n");


  // 打印 Y 平面数据
  std::cout << "Y plane data:" << std::endl;
  for (int i = 0; i < y_size; i++) {
      std::cout << static_cast<int>(output_ptr[i]) << " ";
  }
  std::cout << std::endl;

  // 打印 U 平面数据
  std::cout << "U plane data:" << std::endl;
  for (int i = y_size; i < y_size + uv_size; i++) {
      std::cout << static_cast<int>(output_ptr[i]) << " ";
  }
  std::cout << std::endl;

  // 打印 V 平面数据
  std::cout << "V plane data:" << std::endl;
  for (int i = y_size + uv_size; i < y_size + 2 * uv_size; i++) {
      std::cout << static_cast<int>(output_ptr[i]) << " ";
  }
  std::cout << std::endl;


}

// static_cast<int>(output_ptr[i]) 只是将 output_ptr[i] 的值从 uint8_t 类型转换为 int 类型，但并不改变读取的地址长度。
// reinterpret_cast<int*>(output_ptr + i) 这样的操作会将 output_ptr + i 的地址解释为 int* 类型的指针，然后你可以通过这个指针来连续读取 sizeof(int) 长度的数据作为一个整数。
