
add_subdirectory(${PROJECT_SOURCE_DIR}/include/pybind11 pybind.dir)
include_directories(${PROJECT_SOURCE_DIR}/include/mytools/)
set(CORE_SRC mytool.cpp)
add_library(pyperf SHARED bind.cpp ${CORE_SRC})

if(CUSTOM_PY_LIBDIR)
  link_directories(${CUSTOM_PY_LIBDIR})
  target_include_directories(pyperf PUBLIC ${PYBIND11_INCLUDE_DIR} ${PYTHON_INCLUDE_DIRS})
  message(STATUS "CUSTOM_PY_LIBDIR = ${CUSTOM_PY_LIBDIR}")
else()
  target_include_directories(pyperf PUBLIC ${PYBIND11_INCLUDE_DIR})
endif()
target_compile_definitions(pyperf PUBLIC -DPYTHON=1)

target_link_libraries(pyperf PRIVATE ${basic_link_libs} pybind11::module)

set(PYSILK_SUFFIX "${PYTHON_MODULE_EXTENSION}")


set_target_properties(pyperf PROPERTIES PREFIX "${PYTHON_MODULE_PREFIX}"
                      SUFFIX "${PYSILK_SUFFIX}" OUTPUT_NAME "mytools")

