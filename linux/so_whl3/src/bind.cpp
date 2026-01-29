
#include <fstream>
#include <sstream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include <pybind11/operators.h>
#include <pybind11/numpy.h>
#include <pybind11/functional.h>
#include "mytool.h"

using namespace zzy;
// Pybind11模块定义
namespace py = pybind11;
PYBIND11_MODULE(mytools, m){
    py::class_<mytool>(m, "mytool")
        .def(py::init<>()) // 绑定默认构造函数
        .def("Add", &mytool::add);
}