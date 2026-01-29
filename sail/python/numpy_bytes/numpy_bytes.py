import numpy as np

# 创建一个NumPy数组
arr = np.array([1, 2, 3, 4, 5])
arr_bytes = arr.tobytes()
new_arr = np.frombuffer(arr_bytes, dtype=arr.dtype)

print("Original Array:")
print(arr)

print("\nArray converted to bytes:")
print(arr_bytes)

print("\nArray recreated from bytes:")
print(new_arr)

# 根据提供的字节流 b'\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00'，我们可以看到每个整数是以小端序（little-endian）编码的。
# 第一个整数是 b'\x01\x00\x00\x00'，按照小端序解析为十进制整数为 1