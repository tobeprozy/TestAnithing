cmake_minimum_required(VERSION 3.10)
project(Performance VERSION 1.0.0)

if (NOT DEFINED BUILD_TYPE)
    set(BUILD_TYPE "pcie")
endif()

if (NOT DEFINED LOCAL_ARCH)
    set(LOCAL_ARCH ${CMAKE_HOST_SYSTEM_PROCESSOR})
endif()
message(STATUS "CMAKE_HOST_SYSTEM_PROCESSOR: ${LOCAL_ARCH}")

if (NOT DEFINED PYTHON_EXECUTABLE)
    set(PYTHON_EXECUTABLE python3)
else()
    if (DEFINED CUSTOM_PY_LIBDIR)
    string(FIND ${CUSTOM_PY_LIBDIR} ./ res)
    if (${res} STREQUAL "0")
        string(REPLACE ./  ${PROJECT_BINARY_DIR}/ CUSTOM_PY_LIBDIR ${CUSTOM_PY_LIBDIR})
    endif()
    string(FIND ${CUSTOM_PY_LIBDIR} / res)
    if (NOT ${res} STREQUAL "0")
        set(CUSTOM_PY_LIBDIR ${PROJECT_BINARY_DIR}/${CUSTOM_PY_LIBDIR})
    endif()
    SET(ENV{LD_LIBRARY_PATH} ${CUSTOM_PY_LIBDIR}:$ENV{LD_LIBRARY_PATH})
    endif()
endif()

set(EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR}/bin)
set(LIBRARY_OUTPUT_PATH    ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_MODULE_PATH      ${CMAKE_SOURCE_DIR}/cmake)

set(CMAKE_CXX_STANDARD     14)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -w")
set(CMAKE_CXX_FLAGS_DEBUG    "-g")
set(CMAKE_CXX_FLAGS_RELEASE  "-O3")


# native compile
if (("${LOCAL_ARCH}" STREQUAL "riscv64") OR
    ("${LOCAL_ARCH}" STREQUAL "sw_64") OR
    ("${LOCAL_ARCH}" STREQUAL "loongarch64"))
    set(BUILD_X86_PCIE ON)
    set(CMAKE_INSTALL_PREFIX /opt/sophon)
elseif ("${BUILD_TYPE}" STREQUAL "pcie")
    set(BUILD_X86_PCIE ON)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=native")
    set(CMAKE_INSTALL_PREFIX /opt/sophon)
else()
    MESSAGE(FATAL_ERROR "ERROR BUILD_TYPE!")
endif()

message(STATUS "CROSS_COMPILE: ${CROSS_COMPILE}")

if (DEFINED INSTALL_PREFIX)
    set(CMAKE_INSTALL_PREFIX ${INSTALL_PREFIX})
endif()

message(STATUS "CMAKE_INSTALL_PREFIX: ${CMAKE_INSTALL_PREFIX}")
set(common_inc_dirs ${CMAKE_CURRENT_SOURCE_DIR}/include)

include_directories(${common_inc_dirs})

add_subdirectory(src)




