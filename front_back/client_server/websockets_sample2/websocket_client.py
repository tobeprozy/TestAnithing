import socket

# 创建一个TCP/IP套接字，AF_INET表示使用IPv4地址，SOCK_STREAM表示使用TCP协议
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('127.0.0.1', 1234)) # 连接到服务端
    s.sendall(b'Hello, server!') # 发送信息给服务端
    data = s.recv(1024) # 接收服务端传来的信息
    print('Received', repr(data)) # 打印接收到的信息