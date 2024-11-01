
#!/bin/bash
# wrap pcie new version
python3 setup.py bdist_wheel
if [[ $? != 0 ]];then
  echo "Failed to build mytools wheel"
  exit 1
fi
echo "---- setup mytools wheel"
rm -rf ./mytool*.egg-info ./build

