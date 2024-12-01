#include <string.h>
#include <iostream>
#include "bmcv_api_ext.h"
#include <vector>
#include <memory>
#include <bmvpp.h>
#include <cstring>
#include <chrono>
#include <numeric>
#include <thread>

using namespace std;
#define FFALIGN(x, a) (((x)+(a)-1)&~((a)-1))



void test_bmcv_image_vpp_convert(const int iter_num)
{
        std::vector<int64_t> time_list;
        bm_handle_t handle;
        int image_h = 1080;
        int image_w = 1920;
        bm_image src, dst[4];
        bm_dev_request(&handle, 0);
        bm_image_create(handle, image_h, image_w, FORMAT_NV12, DATA_TYPE_EXT_1N_BYTE, &src);
        bm_image_alloc_dev_mem(src, 1);
        for (int i = 0; i < 4; i++) {
                bm_image_create(handle, image_h / 2, image_w / 2, FORMAT_BGR_PACKED,
                                DATA_TYPE_EXT_1N_BYTE, dst + i);
                bm_image_alloc_dev_mem(dst[i]);
        }
        std::unique_ptr<u8[]> y_ptr(new u8[image_h * image_w]);
        std::unique_ptr<u8[]> uv_ptr(new u8[image_h * image_w / 2]);
        memset((void *)(y_ptr.get()), 148, image_h * image_w);
        memset((void *)(uv_ptr.get()), 158, image_h * image_w / 2);
        u8 *host_ptr[] = { y_ptr.get(), uv_ptr.get() };
        bm_image_copy_host_to_device(src, (void **)host_ptr);

        bmcv_rect_t rect[] = { { 0, 0, image_w / 2, image_h / 2 },
                               { 0, image_h / 2, image_w / 2, image_h / 2 },
                               { image_w / 2, 0, image_w / 2, image_h / 2 },
                               { image_w / 2, image_h / 2, image_w / 2, image_h / 2 } };

        std::cout << "start to invoke bmcv_image_vpp_convert " << iter_num << " times!"
                  << std::endl;
        for (int i = 0; i < iter_num; i++) {
                auto start = std::chrono::high_resolution_clock::now();
                if (bmcv_image_vpp_convert(handle, 4, src, dst, rect) != BM_SUCCESS) {
                        std::cout << "[bmcv_image_vpp_convert] invoke error!" << std::endl;
                }
                auto end = std::chrono::high_resolution_clock::now();
                const int64_t elapsed =
                    std::chrono::duration<double, std::micro>(end - start).count();
                time_list.emplace_back(elapsed);
        }
        std::cout << "invoke bmcv_image_vpp_convert " << iter_num << " times done!" << std::endl;
        std::cout << "[bmcv_image_vpp_convert] average time: "
                  << double(std::accumulate(time_list.begin(), time_list.end(), 0)) / 1000 /
                         time_list.size()
                  << "ms/p" << std::endl;

        for (int i = 0; i < 4; i++) {
                bm_image_destroy(dst[i]);
        }

        bm_image_destroy(src);
        bm_dev_free(handle);
}

void test_bmcv_image_csc_convert_to(const int iter_num)
{
        std::vector<int64_t> time_list;
        bm_handle_t handle;
        bm_dev_request(&handle, 0);
        int image_h = 1080;
        int image_w = 1920;
        int output_h = 256;
        int output_w = 256;
        int input_num = 4;
        int crop_nums[] = { 1, 1, 1, 1 };
        bmcv_padding_atrr_t padding_attr = { 0, 0, 256, 256, 0, 0, 0, 1 };
        bmcv_padding_atrr_t padding_attrs[] = { padding_attr, padding_attr, padding_attr,
                                                padding_attr };
        bmcv_convert_to_attr convert_attr = { 0.24, 0.55, 0.11, 0.71, 0.33, 0.67 };
        bmcv_convert_to_attr convert_attrs[] = { convert_attr, convert_attr, convert_attr,
                                                 convert_attr };
        bm_image src[input_num], dst[input_num];
        bmcv_rect rois[input_num];
        // 构造输入图像
        for (int i = 0; i < input_num; i++) {
                bm_image_create(handle, image_h, image_w, FORMAT_BGR_PACKED,
                                DATA_TYPE_EXT_1N_BYTE, src + i);
                bm_image_alloc_dev_mem(src[i], BMCV_HEAP1_ID);
                //                bm_image_alloc_contiguous_mem_heap_mask(1, src + i, 2);
                std::unique_ptr<u8[]> data_ptr(new u8[image_h * image_w * 3]);
                memset((void *)(data_ptr.get()), 148, image_h * image_w * 3);
                u8 *host_ptr[] = { data_ptr.get() };
                bm_image_copy_host_to_device(src[i], (void **)host_ptr);
                rois[i] = { 0, image_h / 2, image_w / 2, image_h / 2 };
        }
        // 构造输出图像
        for (int i = 0; i < input_num; i++) {
                bm_image_create(handle, image_h / 2, image_w / 2, FORMAT_RGB_PLANAR,
                                DATA_TYPE_EXT_1N_BYTE, dst + i);
                bm_image_alloc_dev_mem(dst[i], BMCV_HEAP1_ID);
                //                bm_image_alloc_contiguous_mem_heap_mask(1, dst + i, 2);
        }

        std::cout << "start to invoke bmcv_image_csc_convert_to " << iter_num << " times!"
                  << std::endl;
        for (int i = 0; i < iter_num; i++) {
                auto start = std::chrono::high_resolution_clock::now();
                if (bmcv_image_csc_convert_to(handle, input_num, src, dst, crop_nums, rois,
                                              padding_attrs, BMCV_INTER_LINEAR, CSC_MAX_ENUM,
                                              nullptr, convert_attrs) != BM_SUCCESS) {
                        std::cout << "[bmcv_image_csc_convert_to] invoke error!" << std::endl;
                }
                auto end = std::chrono::high_resolution_clock::now();
                const int64_t elapsed =
                    std::chrono::duration<double, std::micro>(end - start).count();
                time_list.emplace_back(elapsed);
        }
        std::cout << "invoke bmcv_image_csc_convert_to " << iter_num << " times done!"
                  << std::endl;
        std::cout << "[bmcv_image_csc_convert_to] average time: "
                  << double(std::accumulate(time_list.begin(), time_list.end(), 0)) / 1000 /
                         time_list.size()
                  << "ms/p" << std::endl;

        for (int i = 0; i < input_num; i++) {
                bm_image_destroy(src[i]);
                bm_image_destroy(dst[i]);
        }

        bm_dev_free(handle);
}

void test_bmcv_image_convert_to(const int iter_num)
{
        std::vector<int64_t> time_list;
        bm_handle_t handle;
        bm_dev_request(&handle, 0);
        int image_num = 4, image_channel = 3;
        int image_w = 1920, image_h = 1080;
        bm_image input_images[4], output_images[4];
        bmcv_convert_to_attr convert_to_attr;
        convert_to_attr.alpha_0 = 1;
        convert_to_attr.beta_0 = 0;
        convert_to_attr.alpha_1 = 1;
        convert_to_attr.beta_1 = 0;
        convert_to_attr.alpha_2 = 1;
        convert_to_attr.beta_2 = 0;
        int img_size = image_w * image_h * image_channel;
        std::unique_ptr<unsigned char[]> img_data(new unsigned char[img_size * image_num]);
        std::unique_ptr<unsigned char[]> res_data(new unsigned char[img_size * image_num]);
        memset(img_data.get(), 0x11, img_size * image_num);
        for (int img_idx = 0; img_idx < image_num; img_idx++) {
                bm_image_create(handle, image_h, image_w, FORMAT_BGR_PLANAR,
                                DATA_TYPE_EXT_1N_BYTE, &input_images[img_idx]);
        }
        bm_image_alloc_contiguous_mem(image_num, input_images, 0);
        for (int img_idx = 0; img_idx < image_num; img_idx++) {
                unsigned char *input_img_data = img_data.get() + img_size * img_idx;
                bm_image_copy_host_to_device(input_images[img_idx], (void **)&input_img_data);
        }

        for (int img_idx = 0; img_idx < image_num; img_idx++) {
                bm_image_create(handle, image_h, image_w, FORMAT_BGR_PLANAR,
                                DATA_TYPE_EXT_1N_BYTE, &output_images[img_idx]);
        }
        bm_image_alloc_contiguous_mem(image_num, output_images, 1);
        for (int i = 0; i < iter_num; i++) {
                auto start = std::chrono::high_resolution_clock::now();
                if (bmcv_image_convert_to(handle, image_num, convert_to_attr, input_images,
                                          output_images) != BM_SUCCESS) {
                        std::cout << "[bmcv_image_convert_to] invoke error!" << std::endl;
                }
                auto end = std::chrono::high_resolution_clock::now();
                const int64_t elapsed =
                    std::chrono::duration<double, std::micro>(end - start).count();
                time_list.emplace_back(elapsed);
        }
        std::cout << "invoke bmcv_image_convert_to " << iter_num << " times done!" << std::endl;
        std::cout << "[bmcv_image_convert_to] average time: "
                  << double(std::accumulate(time_list.begin(), time_list.end(), 0)) / 1000 /
                         time_list.size()
                  << "ms/p" << std::endl;
        for (int img_idx = 0; img_idx < image_num; img_idx++) {
                unsigned char *res_img_data = res_data.get() + img_size * img_idx;
                bm_image_copy_device_to_host(output_images[img_idx], (void **)&res_img_data);
        }
        bm_image_free_contiguous_mem(image_num, input_images);
        bm_image_free_contiguous_mem(image_num, output_images);
        for (int i = 0; i < image_num; i++) {
                bm_image_destroy(input_images[i]);
                bm_image_destroy(output_images[i]);
        }
}

/**
 * argv0: 程序名称
 * argv1: 测试用例个数
 * argv2 ~ arg2+n-1: 测试bmcv API名称序列(假设API个数为n)
 * argv2+n: api调用次数
 * */
int main(const int argc, const char *argv[])
{
        bmlib_log_set_level(BMLIB_LOG_DEBUG);
        const int test_api_num = std::stoi(argv[1]);
        const int iter_num = std::stoi(argv[2 + test_api_num]);
        std::vector<std::thread> threads;
        for (int i = 0; i < test_api_num; i++) {
                const char *test_api = argv[2 + i];
                if (strcmp(test_api, "bmcv_image_vpp_convert") == 0) {
                        threads.emplace_back(test_bmcv_image_vpp_convert, iter_num);
                } else if (strcmp(test_api, "bmcv_image_csc_convert_to") == 0) {
                        threads.emplace_back(test_bmcv_image_csc_convert_to, iter_num);
                } else {
                        threads.emplace_back(test_bmcv_image_convert_to, iter_num);
                }
        }

        for (auto &t : threads) {
                t.join();
        }

        return 0;
}