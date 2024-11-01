# so_whl

1. 安装
```bash
mkdir build && cd build && cmake .. && make
cd ../python
chmod +x build_whl.sh
./build_whl.sh
pip3 install dist/mytools-*-py3-none-any.whl --force-reinstall
```

2. 使用
```bash
cd ../sample
python3 add.py
```