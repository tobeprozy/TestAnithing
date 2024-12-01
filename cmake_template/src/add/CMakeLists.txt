add_library(add "")
# add_library(add SHARED "") # 生成动态库

# 添加库依赖的源码
target_sources(add 
PRIVATE
    add.cpp
)

# 添加库依赖的头文件
target_include_directories(add 
PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}
)