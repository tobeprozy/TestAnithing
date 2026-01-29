#!/bin/bash

# wrap pcie new version
python3 setup.py bdist_wheel
if [[ $? != 0 ]];then
  echo "Failed to build profile wheel"
  exit 1
fi
echo "---- setup profile wheel"
rm -rf ./profile*.egg-info ./build

