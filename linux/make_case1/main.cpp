#include <string_view>
#include <iostream>
#include "add.h"

int main() {
    std::string_view sv = "Hello, C++17!";
    std::cout << sv << std::endl;
    std::cout << add(1, 2) << std::endl;
    return 0;
}
