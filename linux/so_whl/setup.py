from setuptools import setup, Extension
from Cython.Build import cythonize

ext_modules = [
    Extension("pyadd",
              sources=["pyadd.pyx"],
              libraries=["add"],
              library_dirs=["."],
              runtime_library_dirs=["."])
]

setup(
    name="pyadd",
    version="0.1",
    ext_modules=cythonize(ext_modules)
)
