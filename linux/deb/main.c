#include <stdio.h>

// 打印系统时间
#include <time.h>

int main() {
    time_t now = time(NULL);
    printf("当前时间: %s", ctime(&now));
    return 0;
}
