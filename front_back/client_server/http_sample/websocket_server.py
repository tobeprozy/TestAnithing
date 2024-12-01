import socket
import threading 
import os
WEBROOT = "webroot"
def handle_client(conn, addr):
    print('Connected by', addr)
    with conn:
        request = conn.recv(1024)

        headers = request.split(b'\r\n')
        file = headers[0].split()[1].decode()

        if file == '/':
            file =  '/index.html'
        try:
            with open(WEBROOT + file, 'rb') as f:
                content = f.read()
            response = b'HTTP/1.1 200 OK\r\n\r\n' + content
        except FileNotFoundError:
            response = b'HTTP/1.1 404 NOT FOUND\r\n\r\n<h1>404 NOT FOUND</h1>'

        conn.sendall(response)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 创建一个TCP/IP套接字，AF_INET表示使用IPv4地址，SOCK_STREAM表示使用TCP协议
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(('0.0.0.0', 80)) # 主机上的任意网课都可以使用这个socket进行通信，8888端口
    s.listen()  # 开始监听连接请求
    while True:
        conn, addr = s.accept() # 接受来自任意客户端的连接请求
        t=threading.Thread(target=handle_client, args=(conn, addr)) # 创建一个线程来处理客户端请求
        t.start()