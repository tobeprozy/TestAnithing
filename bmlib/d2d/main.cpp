#include <string>
#include <fstream>
#include <iostream>
#include <cassert>
#include <bmlib_runtime.h>
#include <chrono>
using namespace std;
#define DEBUG 1


int main(int argc, char *argv[]){

    
    // handle初始化
    bm_handle_t handle;
    auto ret = bm_dev_request(&handle,0);
    assert(ret == BM_SUCCESS);

    bm_device_mem_t src;
    // 预分配堆内存
    ret = bm_malloc_device_byte_heap_mask(handle,&src,0b001,1080*1920*sizeof(float));
    assert(ret == BM_SUCCESS);

    // 以上完成初始化操作
    auto  start = std::chrono::high_resolution_clock::now();
    float* pFP32 = nullptr;
    pFP32 = new float[1080*1920];
    assert(pFP32 != nullptr);
    ret = bm_memcpy_d2s_partial(handle, pFP32, src,
                                  1080*1920 * sizeof(float));
    assert(BM_SUCCESS == ret);
    auto  end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed_seconds = end-start;
    std::cout << "d2s elapsed time: " << elapsed_seconds.count() << "s\n";

    
    bm_device_mem_t dst;
    ret = bm_malloc_device_byte_heap_mask(handle,&dst,0b001,1080*1920*sizeof(float));

    start = std::chrono::high_resolution_clock::now();
    bm_memcpy_s2d_partial(handle, dst, pFP32, 1080*1920*sizeof(float));
    end = std::chrono::high_resolution_clock::now();
    elapsed_seconds = end-start;
    std::cout << "s2d elapsed time: " << elapsed_seconds.count() << "s\n";

    start = std::chrono::high_resolution_clock::now();
    bm_memcpy_d2d(handle, dst, 0,src, 0, 1080*1920);
    end = std::chrono::high_resolution_clock::now();
    elapsed_seconds = end-start;
    std::cout << "d2d elapsed time: " << elapsed_seconds.count() << "s\n";



    // 释放handle
    bm_free_device(handle,src);
    bm_free_device(handle,dst);
    bm_dev_free(handle);

    return 0;
}
