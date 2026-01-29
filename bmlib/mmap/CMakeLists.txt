cmake_minimum_required(VERSION 3.10)
project(test)
# set(CMAKE_CXX_STANDARD 14)
SET(CMAKE_BUILD_TYPE "Debug")
set(CMAKE_CXX_FLAGS "-O3")
# SET(EXECUTABLE_OUTPUT_PATH ${CMAKE_CURRENT_SOURCE_DIR})
# message("cur dir: ${CMAKE_CURRENT_SOURCE_DIR}")
SET(EXECUTABLE_OUTPUT_PATH ${CMAKE_CURRENT_BINARY_DIR})
message("cur dir: ${CMAKE_CURRENT_BINARY_DIR}")

SET(CMAKE_BUILD_TYPE "DEBUG")

if (NOT DEFINED TARGET_ARCH)
    set(TARGET_ARCH base)
endif()
if (${TARGET_ARCH} STREQUAL "base")
     message( "${TARGET_ARCH} mode, starting......")
     
    # use libbmrt libbmlib
    find_package(libsophon REQUIRED)
    include_directories(${LIBSOPHON_INCLUDE_DIRS})
    link_directories(${LIBSOPHON_LIB_DIRS})

    # use ffmpeg
    set(FFMPEG_DIR  /opt/sophon/sophon-ffmpeg-latest/lib/cmake)
    find_package(FFMPEG REQUIRED)
    include_directories(${FFMPEG_INCLUDE_DIRS})
    link_directories(${FFMPEG_LIB_DIRS})

    # use opencv
    set(OpenCV_DIR /opt/sophon/sophon-opencv-latest/lib/cmake/opencv4/)
    find_package(OpenCV REQUIRED)
    include_directories(${OpenCV_INCLUDE_DIRS})

    aux_source_directory(. SRC_FILES)
    add_executable(test ${SRC_FILES})
    target_link_libraries(test ${the_libbmlib.so} ${the_libbmrt.so} ${the_libbmcv.so} ${OpenCV_LIBS} ${FFMPEG_LIBS} -lpthread -lavcodec)

elseif (${TARGET_ARCH} STREQUAL "pcie")
    message( "${TARGET_ARCH} mode, starting......")
    # set(lib_DIR /usr/lib/x84_64-linux-gnu)
    # link_directories(${lib_DIR})

    # use libbmrt libbmlib
    find_package(libsophon REQUIRED)
    include_directories(${LIBSOPHON_INCLUDE_DIRS})
    link_directories(${LIBSOPHON_LIB_DIRS})

    aux_source_directory(. SRC_FILES)
    add_executable(test.pcie ${SRC_FILES})
    target_link_libraries(test.pcie ${the_libbmlib.so} ${the_libbmrt.so} ${the_libbmcv.so} -lpthread)

elseif (${TARGET_ARCH} STREQUAL "soc")
    message( "${TARGET_ARCH} mode, starting......")
    
    set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
    set(CMAKE_ASM_COMPILER aarch64-linux-gnu-gcc)
    set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -march=armv8-a")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=armv8-a -std=c++11 -O2")
    set(BM_LIBS bmlib bmrt bmcv yuv)
    # set(JPU_LIBS bmjpuapi bmjpulite)
    set(OPENCV_LIBS opencv_imgproc opencv_core opencv_highgui opencv_imgcodecs opencv_videoio)
    include_directories("${SDK}/include/")
    include_directories("${SDK}/include/opencv4")
    link_directories("${SDK}/lib/")

    message("SDK: " ${SDK})
    aux_source_directory(. SRC_FILES)
    add_executable(test.soc ${SRC_FILES})
    target_link_libraries(test.soc ${BM_LIBS} ${OPENCV_LIBS} -lpthread -lavcodec -lavformat -lavutil)
else ()
    message( FATAL_ERROR  "not support mode, eg: soc/pcie, cur: ${TARGET_ARCH}")
endif ()