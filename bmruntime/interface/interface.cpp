// #include "bmruntime_interface.h"
// #include <assert.h> //assert

// void bmrt_test() {
//   // request bm_handle
//   bm_handle_t bm_handle;
//   bm_status_t status = bm_dev_request(&bm_handle, 0);
//   assert(BM_SUCCESS == status);

//   // create bmruntime
//   void *p_bmrt = bmrt_create(bm_handle);
//   assert(NULL != p_bmrt);

//   // load bmodel by file
//   bool ret = bmrt_load_bmodel(p_bmrt, "testnet.bmodel");
//   assert(true == ret);

//   auto net_info = bmrt_get_network_info(p_bmrt, "testnet");
//   assert(NULL != net_info);

//   // init input tensors
//   bm_tensor_t input_tensors[2];
//   status = bm_malloc_device_byte(bm_handle, &input_tensors[0].device_mem,
//                                  net_info->max_input_bytes[0]);
//   assert(BM_SUCCESS == status);
//   input_tensors[0].dtype = BM_INT8;
//   input_tensors[0].st_mode = BM_STORE_1N;
//   status = bm_malloc_device_byte(bm_handle, &input_tensors[1].device_mem,
//                                  net_info->max_input_bytes[1]);
//   assert(BM_SUCCESS == status);
//   input_tensors[1].dtype = BM_FLOAT32;
//   input_tensors[1].st_mode = BM_STORE_1N;

//   // init output tensors
//   bm_tensor_t output_tensors[2];
//   status = bm_malloc_device_byte(bm_handle, &output_tensors[0].device_mem,
//                                  net_info->max_output_bytes[0]);
//   assert(BM_SUCCESS == status);
//   status = bm_malloc_device_byte(bm_handle, &output_tensors[1].device_mem,
//                                  net_info->max_output_bytes[1]);
//   assert(BM_SUCCESS == status);

//   // before inference, set input shape and prepare input data
//   // here input0/input1 is system buffer pointer.
//   input_tensors[0].shape = {2, {1,2}};
//   input_tensors[1].shape = {4, {4,3,28,28}};
//   bm_memcpy_s2d_partial(bm_handle, input_tensors[0].device_mem, (void *)input0,
//                         bmrt_tensor_bytesize(&input_tensors[0]));
//   bm_memcpy_s2d_partial(bm_handle, input_tensors[1].device_mem, (void *)input1,
//                         bmrt_tensor_bytesize(&input_tensors[1]));

//   ret = bmrt_launch_tensor_ex(p_bmrt, "testnet", input_tensors, 2,
//                               output_tensors, 2, true, false);
//   assert(true == ret);

//   // sync, wait for finishing inference
//   bm_thread_sync(bm_handle);

//   /**************************************************************/
//   // here all output info stored in output_tensors, such as data type, shape, device_mem.
//   // you can copy data to system memory, like this.
//   // here output0/output1 are system buffers to store result.
//   bm_memcpy_d2s_partial(bm_handle, output0, output_tensors[0].device_mem,
//                         bmrt_tensor_bytesize(&output_tensors[0]));
//   bm_memcpy_d2s_partial(bm_handle, output1, output_tensors[1].device_mem,
//                         bmrt_tensor_bytesize(&output_tensors[1]));
//   // do other things
//   /**************************************************************/

//   // at last, free device memory
//   for (int i = 0; i < net_info->input_num; ++i) {
//     bm_free_device(bm_handle, input_tensors[i].device_mem);
//   }
//   for (int i = 0; i < net_info->output_num; ++i) {
//     bm_free_device(bm_handle, output_tensors[i].device_mem);
//   }

//   bmrt_destroy(p_bmrt);
//   bm_dev_free(bm_handle);
// }