#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

class Func {
public:
    int c; // 成员变量 c
    void init(); // 初始化函数
    int add(int a, int b); // 加法函数
private:
    int d; // 私有成员变量 d
};

int Func::add(int a, int b) {
    return a + b;
}

void Func::init() {
    d = 10;
}

namespace py = pybind11;

// 定义 Python 模块
PYBIND11_MODULE(math1, m) {
    // 将 Func 类绑定到 Python 模块中
    py::class_<Func>(m, "Func")
        .def(py::init<>()) // 构造函数
        .def("init", &Func::init) // 绑定初始化函数
        .def("add", &Func::add) // 绑定加法函数
        .def_readwrite("c", &Func::c); // 读写成员变量 c
}
