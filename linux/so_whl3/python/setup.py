
import os

import shutil
from distutils.core import Extension
from setuptools import setup, find_packages


if __name__ == "__main__":

    current_folder = os.path.dirname(os.path.abspath(__file__))
    build_path = os.path.join(current_folder,"../build")


    build_result_path=os.path.join(build_path,"lib")
    build_so_path="mytools.so"
    for root,dirs,files in os.walk(build_result_path):
        for file in files:
            if file.split('.')[0] == 'mytools':
                build_so_path=os.path.join(root,file)

    dst_path=os.path.join(current_folder,"Tool")
    if os.path.exists(dst_path):
        shutil.rmtree(dst_path)
    os.makedirs(dst_path,exist_ok=True)

    shutil.copy(os.path.join(current_folder,"__init__.py"), dst_path)
    if os.path.exists(build_so_path):
        try:
            shutil.copy(build_so_path, dst_path)
        except shutil.SameFileError:
            pass
    else:
        raise IOError("mytools python lib not found")

    shutil.copy(os.path.join(current_folder,"../src/mytool.pyi"),os.path.join(dst_path,"__init__.pyi"))


    # mytools python module
    PACKAGES = ['Tool']
    module_name = "mytools"
    
    # wrap mytools python module
    setup(name=module_name,
        version="0.0.1",
        packages=PACKAGES,
        include_package_data=True)



