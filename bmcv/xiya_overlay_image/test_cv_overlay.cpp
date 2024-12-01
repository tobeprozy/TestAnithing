#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#include <stdio.h>
#include <stdlib.h>
#include "bmcv_api_ext.h"
#include <sys/time.h>
#include <random>
#include <vector>
#include <iostream>


#define TIME_COST_US(start, end) ((end.tv_sec - start.tv_sec) * 1000000 + (end.tv_usec - start.tv_usec))

static void read_bin(const char *input_path, unsigned char *input_data, int width, int height) {
    FILE *fp_src = fopen(input_path, "rb");
    if (fp_src == NULL) {
        printf("unable to open input file %s\n", input_path);
        return;
    }
    if(fread(input_data, sizeof(unsigned char), width * height * 3, fp_src) != 0)
        printf("read image success\n");
    fclose(fp_src);
}

static void write_bin(const char *output_path, unsigned char *output_data, int width, int height) {
    FILE *fp_dst = fopen(output_path, "wb");
    if (fp_dst == NULL) {
        printf("unable to open output file %s\n", output_path);
        return;
    }
    if(fwrite(output_data, sizeof(unsigned char), width * height * 3, fp_dst) != 0)
        printf("write image success\n");
    fclose(fp_dst);
}

bm_status_t overlay_cpu(int overlay_num, int base_width, int base_height, unsigned char* output_cpu, int* overlay_height, int* overlay_width,
                          unsigned char** overlay_image, int* pos_x, int* pos_y) {
    //rgb_packed
    for (int i = 0; i < overlay_num; i++) {
        for (int y = 0; y < overlay_height[i]; y++) {
            for (int x = 0; x < overlay_width[i]; x++) {
                int base_x = pos_x[i] + x;
                int base_y = pos_y[i] + y;
                if (base_x >= 0 && base_x < base_width && base_y >= 0 && base_y < base_height) {
                    int base_index = (base_y * base_width + base_x) * 3;
                    int overlay_index = (y * overlay_width[i] + x) * 4;
                    float alpha = overlay_image[i][overlay_index + 3] / 255.0f;
                    output_cpu[base_index] = (unsigned char)((1 - alpha) * output_cpu[base_index] + alpha * overlay_image[i][overlay_index]);
                    output_cpu[base_index + 1] = (unsigned char)((1 - alpha) * output_cpu[base_index + 1] + alpha * overlay_image[i][overlay_index + 1]);
                    output_cpu[base_index + 2] = (unsigned char)((1 - alpha) * output_cpu[base_index + 2] + alpha * overlay_image[i][overlay_index + 2]);
                } else {
                    printf("Overlay image out of bounds!\n");
                    return BM_ERR_FAILURE;
                }
            }
        }
    }

    return BM_SUCCESS;
}

bm_status_t overlay_tpu(
    bm_handle_t handle,
    int overlay_num,
    int base_width,
    int base_height,
    unsigned char* output_tpu,
    int* overlay_height,
    int* overlay_width,
    unsigned char** overlay_image,
    int* pos_x,
    int* pos_y) {
    bm_image input_base_img;
    bm_image input_overlay_img[overlay_num];
    struct timeval t1, t2;
    //pthread_mutex_lock(&lock);
    for (int i = 0; i < overlay_num; i++) {
        bm_image_create(handle,
                        overlay_width[i],
                        overlay_height[i],
                        (bm_image_format_ext)FORMAT_ABGR_PACKED,
                        DATA_TYPE_EXT_1N_BYTE,
                        input_overlay_img + i,
                        NULL);
    }

    for (int i = 0; i < overlay_num; i++) {
        bm_image_alloc_dev_mem(input_overlay_img[i], 1);
    }
    unsigned char** in_overlay_ptr[overlay_num];
    for (int i = 0; i < overlay_num; i++) {
        in_overlay_ptr[i] = new unsigned char*[1];
        in_overlay_ptr[i][0] = overlay_image[i];
    }
    for (int i = 0; i < overlay_num; i++) {
        bm_image_copy_host_to_device(input_overlay_img[i], (void **)in_overlay_ptr[i]);
    }

    bm_image_create(handle, base_height, base_width, (bm_image_format_ext)FORMAT_RGB_PACKED, DATA_TYPE_EXT_1N_BYTE, &input_base_img, NULL);
    bm_image_alloc_dev_mem(input_base_img, 1);
    unsigned char* in_base_ptr[1] = {output_tpu};
    bm_image_copy_host_to_device(input_base_img, (void **)in_base_ptr);
     bmcv_rect rect_array[overlay_num];
    for (int i = 0; i < overlay_num; i++) {
        rect_array[i].start_x = pos_x[i];
        rect_array[i].start_y = pos_y[i];
        rect_array[i].crop_w = overlay_width[i];
        rect_array[i].crop_h = overlay_height[i];
    }

    gettimeofday(&t1, NULL);
    bmcv_image_overlay(handle, input_base_img, overlay_num, rect_array, input_overlay_img);
    gettimeofday(&t2, NULL);
    printf("Overlay TPU using time = %ld(us)\n", TIME_COST_US(t1, t2));
    unsigned char* out_ptr[1] = {output_tpu};
    bm_image_copy_device_to_host(input_base_img, (void **)out_ptr);
    bm_image_destroy(input_base_img);

    for (int i = 0; i < overlay_num; i++) {
        bm_image_destroy(input_overlay_img[i]);
    }
    return BM_SUCCESS;
}

void test_image_overlay(bm_handle_t handle, int overlay_num, const char* base_image_path, int base_width, int base_height, const char** overlay_image_path,
                    const char* output_image_cpu_path, const char* output_image_tpu_path, int* pos_x, int* pos_y) {
    unsigned char* base_image = (unsigned char*)malloc(base_width * base_height * 3 * sizeof(unsigned char));
    unsigned char* output_cpu = (unsigned char*)malloc(base_width * base_height * 3 * sizeof(unsigned char));
    unsigned char* output_tpu = (unsigned char*)malloc(base_width * base_height * 3 * sizeof(unsigned char));
    unsigned char* overlay_image[overlay_num];
    int overlay_width[overlay_num], overlay_height[overlay_num], overlay_channels[overlay_num];
    bm_status_t ret;

    read_bin(base_image_path, base_image, base_width, base_height);
    memcpy(output_cpu, base_image, base_width * base_height * 3);
    memcpy(output_tpu, base_image, base_width * base_height * 3);
    for (int i = 0; i < overlay_num; i++) {
        overlay_image[i] = stbi_load(overlay_image_path[i], &overlay_width[i], &overlay_height[i], &overlay_channels[i], STBI_rgb_alpha);
        if (!overlay_image[i]) {
            fprintf(stderr, "Failed to load image: %s\n", stbi_failure_reason());
        goto free_mem;
        }
    }

    ret = overlay_cpu(overlay_num, base_width, base_height, output_cpu, overlay_height, overlay_width,
                        overlay_image, pos_x, pos_y);
    if (BM_SUCCESS != ret) {
        printf("overlay_cpu failed!");
        goto free_mem;
    }

    ret = overlay_tpu(handle, overlay_num, base_width, base_height, output_tpu, overlay_height, overlay_width,
                        overlay_image, pos_x, pos_y);
    if (BM_SUCCESS != ret) {
        printf("overlay_tpu failed!");
        goto free_mem;
    }
    write_bin(output_image_cpu_path, output_cpu, base_width, base_height);
    write_bin(output_image_tpu_path, output_tpu, base_width, base_height);
free_mem:
    free(base_image);
    free(output_cpu);
    free(output_tpu);
    for (int i = 0; i < overlay_num; i++) {
        stbi_image_free(overlay_image[i]);
    }
    return;
}

int main(int argc, char *args[]) {

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 500);
    int overlay_num = 5;
    int base_width = 1920;
    int base_height = 1080;
    int pos_x[overlay_num];
    int pos_y[overlay_num];

    const char* overlay_image_path[overlay_num];
    const char* oip = "overlay_image.png";

    for (int i = 0; i < overlay_num; i++) {
        pos_x[i] = dis(gen);
        pos_y[i] = dis(gen);
        overlay_image_path[i] = oip;
    }


    const char* base_image_path = "1920_1080_rgb_packed.bin";
    const char* output_image_cpu_path = "multi_overlay_cpu2.bin";
    const char* output_image_tpu_path = "multi_overlay_tpu2.bin";

    bm_handle_t handle;
    bm_status_t ret = bm_dev_request(&handle, 0);
    if (ret != BM_SUCCESS) {
        printf("Create bm handle failed. ret = %d\n", ret);
        return -1;
    }

    if (argc == 2 && atoi(args[1]) == -1) {
        printf("usage:\n");
        printf("%s src_w src_h start_x start_y src_path dst_cpu_path dst_tpu_path overlay_image_path\n", args[0]);
        return 0;
    }


    if (argc > 1) {
        overlay_num = atoi(args[1]);
    }

    // 确定参数的起始位置
    int base_width_pos = 2;
    int base_height_pos = 3;
    int pos_x_start = 4;
    int pos_y_start = 4 + overlay_num;
    int base_image_path_pos = 4 + 2 * overlay_num;
    int output_image_cpu_path_pos = base_image_path_pos + 1;
    int output_image_tpu_path_pos = output_image_cpu_path_pos + 1;
    int overlay_image_path_start = output_image_tpu_path_pos + 1;

    // 解析参数
    if (argc > base_width_pos) {
        base_width = atoi(args[base_width_pos]);
    }

    if (argc > base_height_pos) {
        base_height = atoi(args[base_height_pos]);
    }

    base_image_path = argc > base_image_path_pos ? args[base_image_path_pos] : base_image_path;
    output_image_cpu_path = argc > output_image_cpu_path_pos ? args[output_image_cpu_path_pos] : output_image_cpu_path;
    output_image_tpu_path = argc > output_image_tpu_path_pos ? args[output_image_tpu_path_pos] : output_image_tpu_path;


    for (int i = 0; i < overlay_num; i++) {
        pos_x[i] = argc > pos_x_start + i ? atoi(args[pos_x_start + i]) : pos_x[i];
        pos_y[i] = argc > pos_y_start + i ? atoi(args[pos_y_start + i]) : pos_y[i];
        overlay_image_path[i] = argc > overlay_image_path_start + i ? args[overlay_image_path_start + i] : overlay_image_path[i];
    }

    test_image_overlay(handle, overlay_num, base_image_path, base_width, base_height, overlay_image_path,
                         output_image_cpu_path, output_image_tpu_path, pos_x, pos_y);

    return 0;
}
