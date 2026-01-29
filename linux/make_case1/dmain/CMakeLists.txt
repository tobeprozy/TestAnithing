cmake_minimum_required(VERSION 3.10)
project(UndefinedReferenceExample)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


# 包含头文件目录
include_directories(${CMAKE_SOURCE_DIR}/include)

add_executable(main main.cpp)

# 添加库文件搜索路径
link_directories(${CMAKE_SOURCE_DIR}/lib)
target_link_libraries(main PRIVATE add)