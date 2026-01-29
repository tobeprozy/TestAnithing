cmake_minimum_required(VERSION 3.10)
project(my_transpose)
# set(CMAKE_CXX_STANDARD 14)
SET(CMAKE_BUILD_TYPE "Debug")

# SET(EXECUTABLE_OUTPUT_PATH ${CMAKE_CURRENT_SOURCE_DIR})
# message("cur dir: ${CMAKE_CURRENT_SOURCE_DIR}")
SET(EXECUTABLE_OUTPUT_PATH ${CMAKE_CURRENT_BINARY_DIR})
message("cur dir: ${CMAKE_CURRENT_BINARY_DIR}")

# use libbmrt libbmlib
# include_directories(/opt/sophon/libsophon-current/include)
# link_directories(/opt/sophon/libsophon-current/lib/)

# use libbmrt libbmlib
find_package(libsophon REQUIRED)
include_directories(${LIBSOPHON_INCLUDE_DIRS})
link_directories(${LIBSOPHON_LIB_DIRS})

aux_source_directory(. SRC_FILES)

aux_source_directory(. SRC_FILES)
add_executable(my_transpose ${SRC_FILES})
# target_link_libraries(my_transpose bmlib bmrt bmcv pthread dl)
target_link_libraries(my_transpose ${the_libbmlib.so} ${the_libbmrt.so} ${the_libbmcv.so} pthread dl)