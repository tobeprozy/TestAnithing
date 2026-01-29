PROJECT(infer_demo C CXX)
CMAKE_MINIMUM_REQUIRED (VERSION 3.10)
# 指定下载解压后的fastdeploy库路径
set(FASTDEPLOY_INSTALL_DIR "${CMAKE_CURRENT_SOURCE_DIR}/fastdeploy-sophgo")

# 多线程测试用
find_package(Threads REQUIRED)

set(ENABLE_LITE_BACKEND OFF)
#set(FDLIB ${FASTDEPLOY_INSTALL_DIR})

include(${FASTDEPLOY_INSTALL_DIR}/FastDeploy.cmake)

# 添加FastDeploy依赖头文件
include_directories(${FASTDEPLOY_INCS} "/opt/sophon/libsophon-0.4.9/include" "/opt/sophon/sophon-opencv_1.8.0/include" "/opt/sophon/sophon-ffmpeg_1.8.0/include/")
include_directories(${FastDeploy_INCLUDE_DIRS})

set(LIB_DIR /usr/local/lib /opt/sophon/libsophon-0.4.9/lib/ /opt/sophon/sophon-ffmpeg_1.8.0/lib /opt/sophon/sophon-opencv_1.8.0/lib)
link_directories(${LIB_DIR})
add_executable(infer_demo ${PROJECT_SOURCE_DIR}/infer_undistorted_img.cc)
# 添加FastDeploy库依赖
# target_link_libraries(infer_demo ${FASTDEPLOY_LIBS}) 
target_link_libraries(infer_demo PRIVATE ${FASTDEPLOY_LIBS} Threads::Threads) 
