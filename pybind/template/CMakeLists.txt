cmake_minimum_required(VERSION 3.10)
project(math1)
# set(CMAKE_CXX_STANDARD 14)
SET(CMAKE_BUILD_TYPE "Debug")
# set(CMAKE_CXX_FLAGS "-O3")
# SET(EXECUTABLE_OUTPUT_PATH ${CMAKE_CURRENT_SOURCE_DIR})
# message("cur dir: ${CMAKE_CURRENT_SOURCE_DIR}")
SET(EXECUTABLE_OUTPUT_PATH ${CMAKE_CURRENT_BINARY_DIR})
message("cur dir: ${CMAKE_CURRENT_BINARY_DIR}")


if (NOT DEFINED TARGET_ARCH)
    set(TARGET_ARCH base)
endif()

if (${TARGET_ARCH} STREQUAL "base")
    message( "${TARGET_ARCH} mode, starting......")
     
    add_definitions(-DDEBUG --std=c++17 -fPIC -Wall -Werror)
    find_package(pybind11 REQUIRED CONFIG)
    file(GLOB CPP_FILES ${PROJECT_SOURCE_DIR}/*.cpp)

    foreach(CPP_FILE ${CPP_FILES})
        get_filename_component(MODULE_NAME ${CPP_FILE} NAME_WE)
        pybind11_add_module(${MODULE_NAME} ${CPP_FILE})
        target_link_libraries(${MODULE_NAME} PUBLIC)
        install(TARGETS ${MODULE_NAME} DESTINATION python)
    endforeach()

elseif (${TARGET_ARCH} STREQUAL "pcie")
    message( "${TARGET_ARCH} mode, starting......")

  

elseif (${TARGET_ARCH} STREQUAL "soc")
    message( "${TARGET_ARCH} mode, starting......")

else ()
    message( FATAL_ERROR  "not support mode, eg: soc/pcie, cur: ${TARGET_ARCH}")
endif ()




