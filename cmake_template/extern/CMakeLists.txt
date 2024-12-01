add_library(sum "")
# add_library(sum SHARED "") # 生成动态库

# 添加库依赖的源码
target_sources(sum 
PRIVATE
    sum.cpp
)

# 添加库依赖的头文件
target_include_directories(sum 
PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}
)