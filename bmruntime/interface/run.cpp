
// #include "bmruntime_cpp.h"
#include "bmruntime_interface.h"
#include <assert.h> //assert
#include "bmlib_runtime.h"
#include <iostream>
#include <dirent.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

int main(){

    std::string bmodel_path="../datasets/matmul.bmodel";
    bm_net_info_t *net_info;
    bm_tensor_t input_tensors[2];
    bm_tensor_t output_tensors[1];
    std::cout<<"bmodel_path:"<<bmodel_path<<std::endl;
    
    // 1.加载模型
    bm_handle_t bm_handle;
    bm_status_t status = bm_dev_request(&bm_handle, 0);

    void *p_bmrt = bmrt_create(bm_handle);

    bmrt_load_bmodel(p_bmrt, bmodel_path.c_str());

    net_info = const_cast<bm_net_info_t*>(bmrt_get_network_info(p_bmrt, "matmul"));
    assert(NULL != net_info);

    // // //2.初始化输入
    bm_malloc_device_byte(bm_handle, &input_tensors[0].device_mem,
                                    net_info->max_input_bytes[0]);
    input_tensors[0].dtype = BM_FLOAT32;
    
    bm_malloc_device_byte(bm_handle, &input_tensors[1].device_mem,
                                    net_info->max_input_bytes[1]);
    input_tensors[1].dtype = BM_FLOAT32;
    
    float input0[100*100];
    float input1[100*100];
 
    // 初始化 input/input1
    for(int i = 0; i < 100*100; i++) {
        input0[i] = 1;
    }

    for(int i = 0; i < 100*100; i++) {
        input1[i] = 2;
    }
    
    input_tensors[0].shape = {3, {1,100,100}};
    input_tensors[1].shape = {3, {1,100,100}};

    // 3.初始化输出 
    status=bm_malloc_device_byte_heap(bm_handle, &output_tensors[0].device_mem,2,net_info->max_output_bytes[0]);
    output_tensors[0].dtype = BM_FLOAT32;
    assert(BM_SUCCESS == status);

    bm_memcpy_s2d_partial(bm_handle, input_tensors[0].device_mem, (void *)input0,
                            bmrt_tensor_bytesize(&input_tensors[0]));
    bm_memcpy_s2d_partial(bm_handle, input_tensors[1].device_mem, (void *)input1,
                            bmrt_tensor_bytesize(&input_tensors[1]));


    // 4. 推理
    auto ret=bmrt_launch_tensor_ex(p_bmrt, "matmul", input_tensors, 2,output_tensors, 1, true, false);  
    assert(true == ret);
    //等待推理完成
    bm_thread_sync(bm_handle);

    // 6.获取输出
    float output0[1*100*100];
    bm_memcpy_d2s_partial(bm_handle, (void *)output0, output_tensors[0].device_mem,bmrt_tensor_bytesize(&output_tensors[0]));

    for (size_t i = 0; i < 100*100; i++)
    {
        std::cout<<output0[i]<<" ";
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