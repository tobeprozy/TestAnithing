# 停止脚本执行如果任何命令返回非零状态
set -e

# 复制库文件到指定目录
sudo cp -r ./data/libbmcv.so.0 /opt/sophon/libsophon-current/lib/

# 复制头文件到指定目录
sudo cp ./data/bmcv_api_ext.h /opt/sophon/libsophon-current/include

# 链接libopenblas
sudo rm -i /usr/lib/libopenblas.so.0
sudo ln -s $(pwd)/data/libopenblas.so.0 /usr/lib/libopenblas.so.0

sudo cp ./data/libbm1684x_kernel_module.so /opt/sophon/libsophon-current/lib/tpu_module/

# 创建build目录并进入
mkdir -p build && cd build

# 运行cmake并编译项目
cmake .. && make -j

# 运行测试程序
echo "******./test ../data/6k.txt output1.txt 128 256 0.01 2 8 2******"

./test ../data/6k.txt output1.txt 128 256 0.01 2 8 2

echo "******./test ../data/6k.txt output2.txt 600 256 0.01 2 8 2******"

./test ../data/6k.txt output2.txt 600 256 0.01 2 8 2

echo "******./test ../data/6k.txt output3.txt 2400 256 0.01 2 8 2******"

./test ../data/6k.txt output3.txt 2400 256 0.01 2 8 2
# 返回到原始目录
cd ..

echo "脚本执行完成"
