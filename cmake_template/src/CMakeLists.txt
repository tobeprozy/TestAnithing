add_executable(main main.cpp) # 生成可执行文件

add_subdirectory(add) # 添加子文件目录
add_subdirectory(multi) # 添加子文件目录

# 链接库
target_link_libraries(main
PRIVATE
    add
    sum
    multi
)