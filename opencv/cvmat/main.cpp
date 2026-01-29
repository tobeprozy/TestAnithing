
#include "opencv2/opencv.hpp"
#include <string.h>
#include <iostream>
#include "bmcv_api_ext.h"

using namespace std;
int main(int argc, char** argv)
{
    int dev_id = 0;
    bm_handle_t bmcv_handle;
    bm_status_t dev_ret = bm_dev_request(&bmcv_handle, dev_id);
 
    int ret = 0;
    std::string input_file_path = "../400x400.png";
 
    int h = 1080;
    int w = 1920;
    cv::Mat m_sys1;
    cv::Mat m_sys2;
    m_sys1.allocator = m_sys1.getDefaultAllocator();     // get system allocator
    m_sys2.allocator = m_sys2.getDefaultAllocator();     // get system allocator
    // m_sys1.create(h, w, CV_8UC3);
    // cv::randu(m_sys1, cv::Scalar(0, 0, 0), cv::Scalar(255, 255, 255));
    cv::imread(input_file_path).copyTo(m_sys1);
    cv::imread(input_file_path).copyTo(m_sys2);
    cv::imwrite("m_sys1.jpg", m_sys1);
    cv::imwrite("m_sys2.jpg", m_sys2);
 
    bm_image bmcv_image1;
    bm_image bmcv_image2;
    std::cout << "m_sys1.u->addr : " << m_sys1.u->addr << std::endl;
    std::cout << "m_sys2.u->addr : " << m_sys2.u->addr << std::endl;
 
    cv::bmcv::toBMI(m_sys1, &bmcv_image1, true);
    cv::bmcv::toBMI(m_sys2, &bmcv_image2, true);
    std::cout << "m_sys1 toBMI failed" << std::endl;
    std::cout << "m_sys2 toBMI failed" << std::endl;
 
 
    std::cout << "Method 1, create a new mat with device memory by copyTo()" << std::endl;
    cv::Mat m_dev1;
    m_sys1.copyTo(m_dev1);
    cv::bmcv::toBMI(m_dev1, &bmcv_image1, true);
    std::cout << "m_dev1 toBMI success" << std::endl;
    bm_image_write_to_bmp(bmcv_image1, "bmcv_image1.bmp");
 
    std::cout << "Method 2, create a new bm_image and copy host memory of m_sys to device memory of bm_image" << std::endl;
    void* buff[1] = {m_sys2.data};
    bm_image_create(bmcv_handle, 400, 400, bmcv_image1.image_format, bmcv_image1.data_type, &bmcv_image2);
    bm_image_copy_host_to_device(bmcv_image2, buff);
    std::cout << "m_sys2 to bm_image success" << std::endl;
    bm_image_write_to_bmp(bmcv_image2, "bmcv_image2.bmp");
 
    // release mat bm_image handle
    // bm_image_destroy ...
    // m.release
    // bm_dev_free
    return 0;
}