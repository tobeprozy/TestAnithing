cmake_minimum_required(VERSION 3.10)

project(Helloworld)
set(CMAKE_INSTALL_PREFIX "/opt/hello")
add_executable(hello hello.cpp)

install(TARGETS hello DESTINATION bin)
