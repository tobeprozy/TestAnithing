cmake_minimum_required(VERSION 3.10) # CMake 最低版本要求
project(cmake_template) # 项目名称

set(CMAKE_CXX_STANDARD 17) # 设置C++标准
set(CMAKE_CXX_STANDARD_REQUIRED True) # 设置C++标准为必须

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib) # 设置静态库输出路径
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib) # 设置动态库输出路径
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin) # 设置可执行文件输出路径

add_subdirectory(src) # 添加源代码目录
add_subdirectory(extern) # 添加外部库目录