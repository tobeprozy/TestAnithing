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
    # use ffmpeg
    set(FFMPEG_DIR  /opt/sophon/sophon-ffmpeg-latest/lib/cmake)
    find_package(FFMPEG REQUIRED)
    include_directories(${FFMPEG_INCLUDE_DIRS})
    link_directories(${FFMPEG_LIB_DIRS})

    aux_source_directory(. SRC_FILES)

    add_executable(test ${SRC_FILES})
    target_link_libraries(test ${FFMPEG_LIBS} -lpthread)

elseif (${TARGET_ARCH} STREQUAL "pcie")
    message( "${TARGET_ARCH} mode, starting......")
    # use ffmpeg
    set(FFMPEG_DIR  /opt/sophon/sophon-ffmpeg-latest/lib/cmake)
    find_package(FFMPEG REQUIRED)
    include_directories(${FFMPEG_INCLUDE_DIRS})
    link_directories(${FFMPEG_LIB_DIRS})

    aux_source_directory(. SRC_FILES)

    add_executable(test ${SRC_FILES})
    target_link_libraries(test ${FFMPEG_LIBS} -lpthread)


elseif (${TARGET_ARCH} STREQUAL "soc")
    message( "${TARGET_ARCH} mode, starting......")
    check_and_replace_path(SDK)
    set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
    set(CMAKE_ASM_COMPILER aarch64-linux-gnu-gcc)
    set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)
    set(BM_LIBS bmlib bmrt bmcv yuv)
    
    include_directories("${SDK}/include/")
    link_directories("${SDK}/lib/")

    message("SDK: " ${SDK})
    include_directories("./include/")

    aux_source_directory(. SRC_FILES)
    aux_source_directory(./src/ SRC_FILES)
    add_executable(test.soc ${SRC_FILES})
    target_link_libraries(test.soc ${FFMPEG_LIBS} -lpthread)
else ()
    message( FATAL_ERROR  "not support mode, eg: soc/pcie, cur: ${TARGET_ARCH}")
endif ()