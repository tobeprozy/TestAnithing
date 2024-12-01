add_library(multi "")
# add_library(multi SHARED "") # 生成动态库

# 添加库依赖的源码
target_sources(multi 
PRIVATE
    multi.cpp
)

# 添加库依赖的头文件
target_include_directories(multi 
PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}
)