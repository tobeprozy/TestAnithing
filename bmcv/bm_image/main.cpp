#include <string.h>
#include <iostream>
#include "bmcv_api_ext.h"

using namespace std;
#define FFALIGN(x, a) (((x)+(a)-1)&~((a)-1))

int main(int argc, char* argv[]) {

  int dev_id = 0;
  bm_handle_t bm_handle;
  bm_status_t status = bm_dev_request(&bm_handle, 0);
  bm_image frame1;
  bm_image_create(bm_handle, 460, 1184, FORMAT_BGR_PACKED,                  DATA_TYPE_EXT_1N_BYTE, &frame1);
  bm_image frame2;
  bm_image_create(bm_handle, 460, 1184, FORMAT_BGR_PACKED,                  DATA_TYPE_EXT_1N_BYTE, &frame2);

  int aligned_w = FFALIGN(frame2.width, 64);
  int stride[3] = {aligned_w*3,0,0};
  bm_image frame3;
  status=bm_image_create(bm_handle, frame2.height, frame2.width, FORMAT_BGR_PACKED, DATA_TYPE_EXT_1N_BYTE, &frame3, stride);

}
