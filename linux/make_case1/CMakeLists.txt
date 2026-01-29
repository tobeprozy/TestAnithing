cmake_minimum_required(VERSION 3.10)
project(UndefinedReferenceExample)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(add SHARED)
target_include_directories(add PUBLIC  ${CMAKE_SOURCE_DIR}/include)
target_sources(add PRIVATE ${CMAKE_SOURCE_DIR}/src/add.cpp)

add_executable(main main.cpp)
target_link_libraries(main PRIVATE add)