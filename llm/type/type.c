#include <stdio.h>

struct float_bits {
    unsigned int frac : 23;
    unsigned int exp : 8;
    unsigned int sign : 1;
};


typedef union {
    unsigned short bits;
    struct {
        unsigned short frac : 7; // mantissa
        unsigned short exp  : 8; // exponent
        unsigned short sign : 1; // sign
    } format;
} bf16;


// 功能：打印整数的二进制表示
void print_binary(unsigned int value, int bits) {
    for (int i = bits - 1; i >= 0; i--) {
        printf("%d", (value >> i) & 1);// 打印当前位
    }
    printf("\t value_10:%d, value_2:%x", value,value);
    printf("\n");
}

int main() {
    struct float_bits float_value = {0b101111, 0b111, 0b01};  // 

    // 打印每个字段的二进制表示
    printf("Sign: ");
    print_binary(float_value.sign, 32);

    printf("Exponent: ");
    print_binary(float_value.exp, 32);

    printf("Fraction: ");
    print_binary(float_value.frac, 32);

    // 打印整个结构体的二进制表示
    unsigned int all_bits;
    // 将结构体的地址转换为 unsigned int 指针，并解引用获取整个结构体的值
    // 注意：这种方式依赖于具体的平台和编译器行为
    all_bits = *(unsigned int *)&float_value;
    printf("All bits: ");
    print_binary(all_bits, 32);


    bf16 value;
    value.bits = 0b1001111010111111; // 示例值，可以自行修改

    // 打印每个字段的二进制表示
    printf("Sign: ");
    print_binary(value.format.sign, 16);

    printf("Exponent: ");
    print_binary(value.format.exp, 16);

    printf("Fraction: ");
    print_binary(value.format.frac, 16);

    // 打印整个 union 的二进制表示
    printf("All bits: ");
    print_binary(value.bits, 16);

    return 0;
}
