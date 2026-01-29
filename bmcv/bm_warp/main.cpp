#include <string.h>
#include <iostream>
#include "stdio.h"
#include "stdlib.h"
#include <fstream>
#include <memory>
#include "bmcv_api_ext.h"

using namespace std;
#define FFALIGN(x, a) (((x)+(a)-1)&~((a)-1))


void bm_read_bin(bm_image src, const char *input_name)
{
  int image_byte_size[4] = {0};
  bm_image_get_byte_size(src, image_byte_size);

#if 0
  printf("src plane0 size: %d\n", image_byte_size[0]);
  printf("src plane1 size: %d\n", image_byte_size[1]);
  printf("src plane2 size: %d\n", image_byte_size[2]);
  printf("src plane3 size: %d\n", image_byte_size[3]);
#endif

  int byte_size = image_byte_size[0] + image_byte_size[1] + image_byte_size[2] + image_byte_size[3];
  char* input_ptr = (char *)malloc(byte_size);

  void* in_ptr[4] = {(void*)input_ptr,
                     (void*)((char*)input_ptr + image_byte_size[0]),
                     (void*)((char*)input_ptr + image_byte_size[0] + image_byte_size[1]),
                     (void*)((char*)input_ptr + image_byte_size[0] + image_byte_size[1] + image_byte_size[2])};


  FILE *fp_src = fopen(input_name, "rb");

  if (fread((void *)input_ptr, 1, byte_size, fp_src) < (unsigned int)byte_size){
      printf("file size is less than %d required bytes\n", byte_size);
  };

  fclose(fp_src);

  bm_image_copy_host_to_device(src, (void **)in_ptr);
  free(input_ptr);
  return;
}

int main(int argc, char* argv[]) {

    int image_h = 360;
    int image_w = 640;

    int dst_h = 640;
    int dst_w = 360;

    std::ifstream file("../bgr_planar.bin", std::ios::binary | std::ios::in);
    if (!file.is_open()) {
        std::cerr << "Error opening file" << std::endl;
        return 1;
    }
    file.seekg(0, std::ios::end);
    std::streampos fileSize = file.tellg();
    file.seekg(0, std::ios::beg);
    char* buffer = new char[fileSize];
    file.read(buffer, fileSize);

    std::cout << "fileSize:" << fileSize << std::endl;
    if (fileSize != image_h*image_w*3)
    {
        std::cerr << "Error fileSize" << std::endl;
        return 2;
    }

    bm_handle_t handle;
    bm_dev_request(&handle, 0);
    bmcv_affine_image_matrix matrix_image;
    matrix_image.matrix_num = 1;
    std::shared_ptr<bmcv_affine_matrix> matrix_data
            = std::make_shared<bmcv_affine_matrix>();
    matrix_image.matrix = matrix_data.get();

    /*matrix_image.matrix->m[0] = 3.848430;
    matrix_image.matrix->m[1] = -0.02484;
    matrix_image.matrix->m[2] = 916.7;
    matrix_image.matrix->m[3] = 0.02;
    matrix_image.matrix->m[4] = 3.8484;
    matrix_image.matrix->m[5] = 56.4748;*/

    matrix_image.matrix->m[0] = 0;
    matrix_image.matrix->m[1] = 1;
    matrix_image.matrix->m[2] = 0;
    matrix_image.matrix->m[3] = -1;
    matrix_image.matrix->m[4] = 0;
    matrix_image.matrix->m[5] = 0;

    bm_image src, dst;
    bm_image_create(handle, image_h, image_w, FORMAT_BGR_PLANAR,
            DATA_TYPE_EXT_1N_BYTE, &src);
    bm_image_create(handle, dst_h, dst_w, FORMAT_BGR_PLANAR,
            DATA_TYPE_EXT_1N_BYTE, &dst);
    bm_image_alloc_dev_mem_heap_mask(src,5);
    bm_image_alloc_dev_mem_heap_mask(dst,5);
    //std::shared_ptr<uint8_t*> src_ptr = std::make_shared<uint8_t*>(
    //        new uint8_t[image_h * image_w * 3]);
    //memset((void *)(*src_ptr.get()), 148, image_h * image_w * 3);
    //uint8_t *host_ptr[] = {*src_ptr.get()};

    // 改为读取的图片
    uint8_t *host_ptr[] = {(uint8_t*)buffer};
    bm_image_copy_host_to_device(src, (void **)host_ptr);
    bm_image_write_to_bmp(src, "src.bmp");

    bmcv_image_warp_affine(handle, 1, &matrix_image, &src, &dst);
    
    bm_image_write_to_bmp(dst, "dst.bmp");
    // 处理后的图片保存成文件
    int out_size = dst_h*dst_w*3;
    char* out_data = new char[out_size];
    uint8_t *buffers[] = {(uint8_t*)out_data};
    bm_image_copy_device_to_host(dst, (void**)buffers);
    
    std::ofstream outfile("out.bin", std::ios::out | std::ios::binary);
    outfile.write(out_data, out_size);
    outfile.close();


    bm_image_destroy(src);
    bm_image_destroy(dst);
    bm_dev_free(handle);

    delete[] out_data;
    delete[] buffer;
    file.close();

    return 0;

}
