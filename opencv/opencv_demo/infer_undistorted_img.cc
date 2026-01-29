#include <string>
#include <iostream>
#include <chrono>
#include "nlohmann/json.hpp"
#include <fstream>
#include <opencv2/opencv.hpp> // 引入OpenCV头文件
#include <vector>
#include <thread>


using json = nlohmann::json;
json camera_config;


// 将二维向量转换为OpenCV矩阵
int vector_to_mat(const std::vector<std::vector<double>>& input_vector, cv::Mat &res) {
    res = cv::Mat(input_vector.size(), input_vector[0].size(), CV_64F);
    for (size_t i = 0; i < input_vector.size(); ++i) {
        for (size_t j = 0; j < input_vector[i].size(); ++j) {
            res.at<double>(i, j) = input_vector[i][j];
        }
    }
    return 0;
}


int calculate_distance_to_parkingline(cv::Mat &img, json &camear_conf)
{
  // 1.从json转换需要的相机内参的参数
  std::vector<std::vector<double>> tmp_K = camear_conf["K"];
  cv::Mat K(tmp_K.size(), tmp_K[0].size(), CV_64F);
  auto start_time_3 = std::chrono::high_resolution_clock::now();
  vector_to_mat(tmp_K, K);

  std::vector<std::vector<double>> tmp_D = camear_conf["D"];
  cv::Mat D(tmp_D.size(), tmp_D[0].size(), CV_64F);
  vector_to_mat(tmp_D, D);

  std::vector<std::vector<double>> tmp_R = camear_conf["R"];
  // std::cout<<"R:"<<tmp_R[0][0]<<std::endl;
  cv::Mat R(tmp_R.size(), tmp_R[0].size(), CV_64F);
  vector_to_mat(tmp_R, R);

  std::vector<std::vector<double>> tmp_T = camear_conf["T"];
  cv::Mat T(tmp_T.size(), tmp_T[0].size(), CV_64F);
  vector_to_mat(tmp_T, T);
  // std::vector<int> DIM = camera_config["DIM"];
  cv::Size DIM(2688, 1520);

  std::vector<double> frontRearParkingLine = camear_conf["frontRearParkingLine"];
  std::vector<double> leftRightParkingLine = camear_conf["leftRightParkingLine"];

  auto end_time_4 = std::chrono::high_resolution_clock::now();
  auto duration_4 = std::chrono::duration_cast<std::chrono::milliseconds>(end_time_4 - start_time_3);
  std::cout << "vector_to_mat_all_time: " << duration_4.count() << " ms" << std::endl;

  // std::cout << "read json end" << std::endl;
  auto start_time_13 = std::chrono::high_resolution_clock::now();
  // 2.图像去除畸变
  cv::Mat Knew, valid_ROI;
  Knew = cv::getOptimalNewCameraMatrix(K, D, DIM, 0);
  auto end_time_23 = std::chrono::high_resolution_clock::now();
  auto duration_23 = std::chrono::duration_cast<std::chrono::milliseconds>(end_time_23 - start_time_13);
  std::cout << "cv::getOptimalNewCameraMatrix运行时间: " << duration_23.count() << " ms" << std::endl;

  // 初始化校正映射,这里可以映射一次，后续多次使用
  auto start_time_14 = std::chrono::high_resolution_clock::now();
  cv::Mat map1, map2;
  cv::initUndistortRectifyMap(K, D, cv::Mat::eye(3, 3, CV_64F), Knew, DIM, CV_32FC1, map1, map2);
  auto end_time_24 = std::chrono::high_resolution_clock::now();
  auto duration_24 = std::chrono::duration_cast<std::chrono::milliseconds>(end_time_24 - start_time_14);
  std::cout << "cv::initUndistortRectifyMap运行时间: " << duration_24.count() << " ms" << std::endl;

  // 去畸变
  auto start_time_15 = std::chrono::high_resolution_clock::now();
  cv::Mat undistorted_img;
  cv::remap(img, undistorted_img, map1, map2, cv::INTER_LINEAR, cv::BORDER_CONSTANT);
  auto end_time_25 = std::chrono::high_resolution_clock::now();
  auto duration_25 = std::chrono::duration_cast<std::chrono::milliseconds>(end_time_25 - start_time_15);
  std::cout << "cv::remap运行时间: " << duration_25.count() << " ms" << std::endl;

  auto start_time_4 = std::chrono::high_resolution_clock::now();
  cv::imwrite("../undistorted_img.jpg", undistorted_img);
  auto end_time_5 = std::chrono::high_resolution_clock::now();
  auto duration_5 = std::chrono::duration_cast<std::chrono::milliseconds>(end_time_5 - start_time_4);
  std::cout << "write_img_time: " << duration_5.count() << " ms" << std::endl;


  return 0;

}


int main()
// int test_opencv_demo()
{ 
  for(size_t i=0; i<100; ++i)
  {
    auto start_time = std::chrono::high_resolution_clock::now();
    cv::Mat img1 = cv::imread("../1.jpg");
    auto end_time_1 = std::chrono::high_resolution_clock::now();
    auto duration_1 = std::chrono::duration_cast<std::chrono::milliseconds>(end_time_1 - start_time);
    std::cout << "read_img_mat_time: " << duration_1.count() << " ms" << std::endl;

    auto start_time_1 = std::chrono::high_resolution_clock::now();
    cv::Size newSize(2688, 1520); // 新的宽度和高度
    cv::resize(img1, img1, newSize);
    auto end_time_2 = std::chrono::high_resolution_clock::now();
    auto duration_2 = std::chrono::duration_cast<std::chrono::milliseconds>(end_time_2 - start_time_1);
    std::cout << "resize_img_time: " << duration_2.count() << " ms" << std::endl;

    auto start_time_11 = std::chrono::high_resolution_clock::now();
    cv::rotate(img1, img1, cv::ROTATE_90_CLOCKWISE);
    auto end_time_21 = std::chrono::high_resolution_clock::now();
    auto duration_21 = std::chrono::duration_cast<std::chrono::milliseconds>(end_time_21 - start_time_11);
    std::cout << "rotate_img_time: " << duration_21.count() << " ms" << std::endl;

    auto start_time_12 = std::chrono::high_resolution_clock::now();
    cv::Point topLeft(1, 10);
    cv::Point bottomRight(10, 20);
    cv::rectangle(img1, topLeft, bottomRight, cv::Scalar(0, 0, 255), 10);
    auto end_time_22 = std::chrono::high_resolution_clock::now();
    auto duration_22 = std::chrono::duration_cast<std::chrono::milliseconds>(end_time_22 - start_time_12);
    std::cout << "cv_rectangle_img_time: " << duration_22.count() << " ms" << std::endl;

    auto start_time_16 = std::chrono::high_resolution_clock::now();
    cv::line(img1, cv::Point2f(0,5), cv::Point2f(5,10),cv::Scalar(0,255,0), 18);
    auto end_time_26 = std::chrono::high_resolution_clock::now();
    auto duration_26 = std::chrono::duration_cast<std::chrono::milliseconds>(end_time_26 - start_time_16);
    std::cout << "cv::line_time: " << duration_26.count() << " ms" << std::endl;
    
    auto start_time_17 = std::chrono::high_resolution_clock::now();
    cv::circle(img1, cvPoint(int(25), int(25)), 8, cv::Scalar(0, 0, 255), -1);
    auto end_time_27 = std::chrono::high_resolution_clock::now();
    auto duration_27 = std::chrono::duration_cast<std::chrono::milliseconds>(end_time_27 - start_time_17);
    std::cout << "cv::circle_time: " << duration_27.count() << " ms" << std::endl;

    auto start_time_18 = std::chrono::high_resolution_clock::now();
    // 定义四边形的四个顶点坐标
    std::vector<cv::Point> points;
    points.push_back(cv::Point(20, 20));
    points.push_back(cv::Point(40, 20));
    points.push_back(cv::Point(40, 40));
    points.push_back(cv::Point(20, 40));
    // 将四个顶点坐标放入一个vector的vector中，因为fillPoly()函数要求这样的数据结构
    std::vector<std::vector<cv::Point>> pts{points};
    // 绘制四边形的边界线
    cv::polylines(img1, pts, true, cv::Scalar(255, 0, 0), 15, cv::LINE_AA);
    auto end_time_28 = std::chrono::high_resolution_clock::now();
    auto duration_28 = std::chrono::duration_cast<std::chrono::milliseconds>(end_time_28 - start_time_18);
    std::cout << "cv::polylines_time: " << duration_28.count() << " ms" << std::endl;

    auto start_time_21 = std::chrono::high_resolution_clock::now();
    cv::Mat binary_spaces = cv::Mat::zeros(1080, 1920, CV_8UC1);
    cv::fillPoly(binary_spaces, pts, 255);
    auto end_time_31 = std::chrono::high_resolution_clock::now();
    auto duration_31 = std::chrono::duration_cast<std::chrono::milliseconds>(end_time_31 - start_time_21);
    std::cout << "cv::fillPoly_time: " << duration_31.count() << " ms" << std::endl;

    auto start_time_22 = std::chrono::high_resolution_clock::now();
    int parkingSpacePixels = cv::countNonZero(binary_spaces);          // 车位像素值个数（面积）
    auto end_time_32 = std::chrono::high_resolution_clock::now();
    auto duration_32 = std::chrono::duration_cast<std::chrono::milliseconds>(end_time_32 - start_time_22);
    std::cout << "cv::countNonZero_time: " << duration_32.count() << " ms" << std::endl;

    auto start_time_23 = std::chrono::high_resolution_clock::now();
    cv::Mat grayImage;
    cv::cvtColor(img1, grayImage, cv::COLOR_BGR2GRAY);
    auto end_time_33 = std::chrono::high_resolution_clock::now();
    auto duration_33 = std::chrono::duration_cast<std::chrono::milliseconds>(end_time_33 - start_time_23);
    std::cout << "cv::cvtColor_time: " << duration_33.count() << " ms" << std::endl;


    auto start_time_19 = std::chrono::high_resolution_clock::now();
    // 获取图像的最小值和最大值
    double minVal, maxVal;
    cv::Point minLoc, maxLoc;
    cv::minMaxLoc(grayImage, &minVal, &maxVal, &minLoc, &maxLoc);
    auto end_time_29 = std::chrono::high_resolution_clock::now();
    auto duration_29 = std::chrono::duration_cast<std::chrono::milliseconds>(end_time_29 - start_time_19);
    std::cout << "cv::minMaxLoc_time: " << duration_29.count() << " ms" << std::endl;

    auto start_time_20 = std::chrono::high_resolution_clock::now();
    cv::Scalar meanValue = cv::mean(grayImage);
    auto end_time_30 = std::chrono::high_resolution_clock::now();
    auto duration_30 = std::chrono::duration_cast<std::chrono::milliseconds>(end_time_30 - start_time_20);
    std::cout << "cv::mean_time: " << duration_30.count() << " ms" << std::endl;



    int park_id = 7;
    std::ifstream config_file("../camera_config.json");
    config_file >> camera_config;
    config_file.close();
    json park_id_conf = camera_config["park_" + std::to_string(park_id)];
    if (camera_config["park_" + std::to_string(park_id)].is_null())
    {
        std::cout << "Please check camera_config.json, not found camera_conf: " << park_id_conf << std::endl;
        return -1;
    }
    json leftfront_conf = park_id_conf["left_front"];
    json leftrear_conf = park_id_conf["left_rear"];
    json rightfront_conf = park_id_conf["right_front"];
    json rightrear_conf = park_id_conf["right_rear"];

    // auto start_time = std::chrono::high_resolution_clock::now();
    int ret1 = calculate_distance_to_parkingline(img1, leftfront_conf);

  }

  std::cout << "OpenCV version: " << cv::getVersionString() << std::endl;

  return 0;

}


// void run_threads(int num_threads) {
//     std::vector<std::thread> threads;

//     // 创建线程并启动它们
//     for (int i = 0; i < num_threads; ++i) {
//         threads.emplace_back(test_opencv_demo);
//     }

//     // 等待所有线程完成
//     for (auto& th : threads) {
//         if (th.joinable()) {
//             th.join();
//         }
//     }
// }

// int main() {
//     const int num_threads = 7;
//     run_threads(num_threads);
//     return 0;
// }


