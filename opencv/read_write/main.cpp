
#include "opencv2/opencv.hpp"
#include <string.h>
#include <iostream>
#include "bmcv_api_ext.h"

using namespace std;

int main(int argc, char* argv[]) {


  cv::Mat cvmat;
  cvmat = cv::imread("input.jpg");
  cv::imwrite("test.jpg", cvmat);

  cv::Mat m_dev1;
  cvmat.copyTo(m_dev1);
  printf("m_dev1.data: %p\n", m_dev1.data);

}