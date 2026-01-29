
// #include "bmruntime_cpp.h"
#include "bmruntime_interface.h"
#include <assert.h> //assert
#include "bmlib_runtime.h"
#include <iostream>
#include <dirent.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include "opencv2/opencv.hpp"
using namespace std;

/**
 * @name    bm_image_create_batch
 * @brief   create bm images with continuous device memory
 * @ingroup bmruntime
 *
 * @param [in]           handle       handle of low level device
 * @param [in]           img_h        image height
 * @param [in]           img_w        image width
 * @param [in]           img_format   format of image: BGR or YUV
 * @param [in]           data_type    data type of image: INT8 or FP32
 * @param [out]          image        pointer of bm image object
 * @param [in]           batch_num    batch size
 * @param [in]           stride       bm_image stride
 * @param [in]           head_id      bm_image head id
 * @retval BM_SUCCESS    change success.
 * @retval other values  change failed.
 */
bm_status_t bm_image_create_batch (bm_handle_t              handle,
                                                 int                      img_h,
                                                 int                      img_w,
                                                 bm_image_format_ext      img_format,
                                                 bm_image_data_format_ext data_type,
                                                 bm_image                 *image,
                                                 int                      batch_num,
                                                 int                      *stride = NULL,
                                                 int                      heap_mask = -1) {
  bm_status_t res;
  // init images
  for (int i = 0; i < batch_num; i++) {
    if (stride != NULL)
        bm_image_create(handle, img_h, img_w, img_format, data_type, &image[i], stride);
    else
        bm_image_create(handle, img_h, img_w, img_format, data_type, &image[i]);
  }

  // alloc continuous memory for multi-batch
  if (-1 == heap_mask)
      res = bm_image_alloc_contiguous_mem (batch_num, image);
  else
      res = bm_image_alloc_contiguous_mem_heap_mask (batch_num, image, heap_mask);
  return res;
}

/**
 * @name    bm_image_destroy_batch
 * @brief   destroy bm images with continuous device memory
 * @ingroup bmruntime
 *
 * @param [in]           image        pointer of bm image object
 * @param [in]           batch_num    batch size
 * @retval BM_SUCCESS    change success.
 * @retval other values  change failed.
 */
bm_status_t bm_image_destroy_batch (bm_image *image, int batch_num) {
  bm_status_t res;
  // free memory
  res = bm_image_free_contiguous_mem (batch_num, image);

  // deinit bm image
  for (int i = 0; i < batch_num; i++) {
  #if BMCV_VERSION_MAJOR > 1
    bm_image_destroy (&image[i]);
  #else
    bm_image_destroy (image[i]);
  #endif
  }

  return res;
}

int main(){

    std::string bmodel_path="../scripts/yolov8s_getmask_32_int8.bmodel";
    bm_net_info_t *net_info;
    bm_tensor_t input_tensors[2];
    bm_tensor_t output_tensors[1];
    std::cout<<"bmodel_path:"<<bmodel_path<<std::endl;
    
    // 1.加载模型
    bm_handle_t bm_handle;
    bm_status_t status = bm_dev_request(&bm_handle, 0);

    void *p_bmrt = bmrt_create(bm_handle);

    bmrt_load_bmodel(p_bmrt, bmodel_path.c_str());

    net_info = const_cast<bm_net_info_t*>(bmrt_get_network_info(p_bmrt, "yolov8s"));
    assert(NULL != net_info);

    float mask_net_scale = net_info->output_scales[0];
    float m_confThreshold = 0.25;

    // // //2.初始化输入
    bm_malloc_device_byte(bm_handle, &input_tensors[0].device_mem,
                                    net_info->max_input_bytes[0]);
    input_tensors[0].dtype = BM_FLOAT32;
    
    bm_malloc_device_byte(bm_handle, &input_tensors[1].device_mem,
                                    net_info->max_input_bytes[1]);
    input_tensors[1].dtype = BM_FLOAT32;
    int box_size=10;
    float input0[box_size*32];
    float input1[32*160*160];
 
    // 初始化 input/input1
    for(int i = 0; i < box_size*30; i++) {
        input0[i] = 1;
    }

    for(int i = 0; i < 32*160*160; i++) {
        input1[i] = 2;
    }
    
    input_tensors[0].shape = {3, {1,box_size,32}};
    input_tensors[1].shape = {3, {1,32,160,160}};

    // 3.初始化输出 
    status=bm_malloc_device_byte_heap(bm_handle, &output_tensors[0].device_mem,2,net_info->max_output_bytes[0]);
    output_tensors[0].dtype = BM_FLOAT32;
    assert(BM_SUCCESS == status);

    bm_memcpy_s2d_partial(bm_handle, input_tensors[0].device_mem, (void *)input0,
                            bmrt_tensor_bytesize(&input_tensors[0]));
    bm_memcpy_s2d_partial(bm_handle, input_tensors[1].device_mem, (void *)input1,
                            bmrt_tensor_bytesize(&input_tensors[1]));


    // 4. 推理
    auto ret=bmrt_launch_tensor_ex(p_bmrt, "yolov8s", input_tensors, 2,output_tensors, 1, true, false);  
    assert(true == ret);
    //等待推理完成
    bm_thread_sync(bm_handle);

    // 6.获取输出

    float output0[1*box_size*160*160];
    bm_memcpy_d2s_partial(bm_handle, output0, output_tensors[0].device_mem,
                            bmrt_tensor_bytesize(&output_tensors[0]));

    if(output_tensors[0].dtype == BM_UINT8){
        
        // std::cout << "====================== BM_UINT8=====================" <<std::endl;
        // uint8_t m_confThreshold_int8 = static_cast<uint8_t>(m_confThreshold / mask_net_scale);
  
        int num = box_size;
        // 转bm_image
        std::vector<bm_image> bmimg_vec(num);
        auto ret = bm_image_create_batch(bm_handle,160,160,FORMAT_GRAY,DATA_TYPE_EXT_1N_BYTE,bmimg_vec.data(),num);
        assert(ret == BM_SUCCESS);
        
        // attach
        ret = bm_image_attach_contiguous_mem(num,bmimg_vec.data(),output_tensors[0].device_mem);
        assert(ret == BM_SUCCESS);

        bm_image image_resize;
        bm_image_create(bm_handle, 160,160,FORMAT_GRAY,DATA_TYPE_EXT_1N_BYTE,&image_resize);
        

        bmcv_rect_t rects{0, 0, 160, 160}; //bmcv_rect_t rects{paras.r_x, paras.r_y, paras.r_w, paras.r_h};
        int crop_num_vec = 1;
        bmcv_resize_t resize_img_attr{0, 0, 160, 160,160, 160}; // bmcv_resize_t resize_img_attr{paras.r_x, paras.r_y,paras.r_w, paras.r_h,paras.width, paras.height};
        bmcv_resize_image resize_attr{&resize_img_attr,1,1,0,0,0,BMCV_INTER_LINEAR};
     
        int i = 0;
        for (auto& bmimg:bmimg_vec){
        
            // resize
            // auto ret =  bmcv_image_resize(m_bmContext->handle(),1,&resize_attr,&bmimg,&image_resize);
            auto ret =  bmcv_image_vpp_basic(bm_handle, 1, &bmimg, &image_resize, &crop_num_vec, &rects, NULL, BMCV_INTER_LINEAR);
            assert(ret == BM_SUCCESS);
            // toMAT
            cv::Mat mask;
            ret = cv::bmcv::toMAT(&image_resize,mask,true);
            assert(ret == BM_SUCCESS);

            // cv::Rect bound=cv::Rect{yolobox_vec[i].x1, yolobox_vec[i].y1, yolobox_vec[i].x2 - yolobox_vec[i].x1,yolobox_vec[i].y2 - yolobox_vec[i].y1};
            // yolobox_vec[i].mask_img=mask(bound) > m_confThreshold * 255.0 / mask_net_scale;
            // yolobox_vec_tmp.push_back(yolobox_vec[i]);
            i++;
       
        }
        
        bm_image_destroy(image_resize);
        // detach
        ret = bm_image_dettach_contiguous_mem(num,bmimg_vec.data());
        assert(ret == BM_SUCCESS);
        bm_image_destroy_batch(bmimg_vec.data(),num);
    }else{
        //crop and resize    
        for (int i = 0; i < box_size; i++) {
            //crop 160*160-->r_w*r_h
            cv::Mat temp_mask(160, 160, CV_32FC1, output0+i*160*160);
            cv::Mat masks_feature = temp_mask(cv::Rect(0, 0, 160, 160));//cv::Mat masks_feature = temp_mask(cv::Rect(paras.r_x, paras.r_y, paras.r_w, paras.r_h));
            cv::Mat mask;
            resize(masks_feature, mask, cv::Size(160, 160));// resize(masks_feature, mask, cv::Size(paras.width, paras.height));

            // cv::Rect bound=cv::Rect{yolobox_vec[i].x1, yolobox_vec[i].y1, yolobox_vec[i].x2 - yolobox_vec[i].x1,
            //                         yolobox_vec[i].y2 - yolobox_vec[i].y1};
            // yolobox_vec[i].mask_img=mask(bound) > m_confThreshold;
            // yolobox_vec_tmp.push_back(yolobox_vec[i]);
        }
    }


        // at last, free device memory
    for (int i = 0; i < net_info->input_num; ++i) {
        bm_free_device(bm_handle, input_tensors[i].device_mem);
    }
    for (int i = 0; i < net_info->output_num; ++i) {
        bm_free_device(bm_handle, output_tensors[i].device_mem);
    }
        
    bmrt_destroy(p_bmrt);
    bm_dev_free(bm_handle);

    std::cout<<"matmul done"<<std::endl;
}