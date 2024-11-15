#include <iostream>
#include <bitset>
#include <cstdint>

template <typename T>
void printBits(T value) {
    // 使用 std::bitset 来转换值为二进制字符串
    std::bitset<sizeof(T) * 8> bits(*reinterpret_cast<uint64_t*>(&value));
    std::cout << "Binary representation of " << typeid(T).name() << " (" << value << "): " << bits << std::endl;
}

int main() {
    // 定义一个整数
    int i = 5;

    // 定义一个浮点数并初始化为整数的值
    float f = static_cast<float>(i);

    // 定义一个双精度浮点数并初始化为整数的值
    double d = static_cast<double>(i);

    // 打印每种类型的二进制表示
    printBits(i);
    printBits(f);
    printBits(d);

    return 0;
}
