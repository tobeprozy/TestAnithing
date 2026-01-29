# 停止脚本执行如果任何命令返回非零状态
set -e

# 复制库文件到指定目录
sudo cp -r ./data/libbmcv.so.0 /opt/sophon/libsophon-current/lib/

# 复制头文件到指定目录
sudo cp ./data/bmcv_api_ext.h /opt/sophon/libsophon-current/include

# 创建build目录并进入
mkdir -p build && cd build

# 运行cmake并编译项目
cmake .. && make -j

# 运行测试程序
./test ../data/6k.txt output.txt 128 256 0.01 2 8 2

# 返回到原始目录
cd ..

echo "脚本执行完成"
