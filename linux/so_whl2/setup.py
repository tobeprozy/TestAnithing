

import os
import shutil
from distutils.core import setup


if __name__ == "__main__":

    current_folder = os.path.dirname(os.path.abspath(__file__))
    dst_path=os.path.join(current_folder,"mytools/profile")
    if os.path.exists(dst_path):
        shutil.rmtree(dst_path)
    os.makedirs(dst_path,exist_ok=True)

    shutil.copy(os.path.join(current_folder,"__init__.py"), dst_path)
    shutil.copy(os.path.join(current_folder,"__main__.py"), dst_path)
    shutil.copy(os.path.join(current_folder,"log_profile.py"), dst_path)

    # mytools python module
    PACKAGES = ['mytools']
    module_name = "profile"
    version="0.0.1"

    # wrap mytools python module
    setup(name=module_name,
        version=version,
        url='https://github.com/tobeprozy',
        packages=PACKAGES,
        include_package_data=True)



