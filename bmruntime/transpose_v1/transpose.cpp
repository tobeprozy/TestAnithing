// #include "bmruntime_interface.h"
#include <assert.h> //assert
#include "bmlib_runtime.h"
#include <iostream>
#include <vector>
#include <cstring>
using namespace std;


#define MAX_SHAPE_DIMS 8
typedef struct {
    uint64_t input_global_addr;
    uint64_t output_global_addr;
    int input_shape[MAX_SHAPE_DIMS];
    uint32_t order[MAX_SHAPE_DIMS];
    int dims;
    // u64 buffer_global_addr;
    // u64 buffer_size;
    int dtype;
} __attribute__((packed)) tpu_kernel_api_transpose_t;


typedef enum {
    DT_INT8   = (0 << 1) | 1,
    DT_UINT8  = (0 << 1) | 0,
    DT_INT16  = (3 << 1) | 1,
    DT_UINT16 = (3 << 1) | 0,
    DT_FP16   = (1 << 1) | 1,
    DT_BFP16  = (5 << 1) | 1,
    DT_INT32  = (4 << 1) | 1,
    DT_UINT32 = (4 << 1) | 0,
    DT_FP32   = (2 << 1) | 1,
    DT_INT4   = (6 << 1) | 1,
    DT_UINT4  = (6 << 1) | 0
} data_type_t;


void print_tensor(float *data, int n, int c, int h, int w){
    for (int i=0; i<n; i++){
        for (int j=0; j<c; j++){
            for (int k=0; k<h; k++){
                for (int l=0; l<w; l++){
                    
                    printf("%f ", data[i*c*h*w+j*h*w+k*w+l]);
                }
                printf("\n");
            }
            printf("\n");
        }
        printf("\n");
    }
}

int main(){

    bm_handle_t bm_handle;
    bm_status_t status = bm_dev_request(&bm_handle, 0);
    tpu_kernel_module_t tpu_module;
    tpu_module = tpu_kernel_load_module_file(bm_handle, "../libbm1684x_kernel_module.so");
    tpu_kernel_function_t func_id;
    func_id = tpu_kernel_get_function(bm_handle, tpu_module, "tpu_kernel_api_transpose");
    std::cout << func_id << std::endl;
    
    tpu_kernel_api_transpose_t  api;
    memset(&api, 0, sizeof(tpu_kernel_api_transpose_t));
    // input
    int n=1;
    int c=4;
    int h=3;
    int w=3;
    float input[n*c*w*h];
    for (int i=0; i<n*c*w*h; i++){
        input[i] = i;
    }
    printf("input:\n");
    print_tensor(input, n, c, h, w);
    bm_device_mem_t input_tensors;
    bm_malloc_device_byte(bm_handle, &input_tensors, n*c*w*h*sizeof(float));
    bm_memcpy_s2d_partial(bm_handle, input_tensors, input, n*c*w*h*sizeof(float));
    int num=1;
    bm_device_mem_t output_tensors;
    bm_malloc_device_byte(bm_handle, &output_tensors, n*c*w*h*sizeof(float));

    api.input_global_addr = bm_mem_get_device_addr(input_tensors);
    api.output_global_addr =bm_mem_get_device_addr(output_tensors);
    api.dims = 4;
    api.dtype = DT_FP32;
    api.input_shape[0] = n;
    api.input_shape[1] = c;
    api.input_shape[2] = w;
    api.input_shape[3] = h;
    //np.transpose(input, (0, 2, 1, 3))
    api.order[0] = 0;
    api.order[1] = 2;
    api.order[2] = 1;
    api.order[3] = 3;
    // 调用
    tpu_kernel_launch(bm_handle,func_id,&api,sizeof(api));
    float output[n*c*w*h];
    //d2s
    bm_memcpy_d2s_partial(bm_handle, output, output_tensors, n*c*w*h*sizeof(float));
    printf("output:\n");
    print_tensor(output, n, c, h, w);

    //np.transpose(input, (0, 1,3, 2)
    api.order[0] = 0;
    api.order[1] = 1;
    api.order[2] = 3;
    api.order[3] = 2;

    // 调用
    tpu_kernel_launch(bm_handle,func_id,&api,sizeof(api));
    //d2s
    bm_memcpy_d2s_partial(bm_handle, output, output_tensors, n*c*w*h*sizeof(float));
    printf("output:\n");
    print_tensor(output, n, c, h, w);


}