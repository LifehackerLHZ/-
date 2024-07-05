from socket import *
import os

print("Current directory contents:")
print(os.listdir("."))  # 列出当前目录的文件

#创建服务器套接字并绑定到本地地址和端口
serverSocket = socket(AF_INET, SOCK_STREAM)
# Prepare a server socket564564
serverSocket.bind(("127.0.0.1", 8080))  # 这里将端口改为8080
serverSocket.listen(1)

try:
    while True:
        print('开始WEB服务...')
        #接受客户端连接请求：
        connectionSocket, addr = serverSocket.accept()
        try:
            #接收客户端HTTP请求
            message = connectionSocket.recv(1024).decode()  # 获取客户发送的报文
            print(f"Received message: {message}")  # 调试信息

            if not message:
                connectionSocket.close()
                continue

            # 解析HTTP请求并读取文件内容
            parts = message.split()
            #检查分割后的列表长度是否小于2。如果小于2,说明收到的请求格式不正确,缺少必要的部分。
            if len(parts) < 2:#至少要有请求方法和路径
                header = 'HTTP/1.1 400 Bad Request\n\n'
                connectionSocket.send(header.encode())
                connectionSocket.close()
                continue

            filename = parts[1]  # message=["GET", "/index.html", "HTTP/1.1", ...]
            print(f"Requested filename: {filename}")  # 添加调试信息
            if filename == "/":
                filename = "/index.html"  # 默认返回index.html

            try:
                #读取请求的文件内容
                with open(filename[1:], 'r') as f:
                    outputdata = f.read()
                print(f"File content: {outputdata}")  # 打印文件内容

                # 生成并发送HTTP响应，向套接字发送头部信息
                header = 'HTTP/1.1 200 OK\nConnection: close\nContent-Type: text/html\nContent-Length: %d\n\n' % (
                    len(outputdata))
                connectionSocket.send(header.encode())
                print("Sent header")  # 添加调试信息

                # 发送请求文件的内容
                connectionSocket.send(outputdata.encode())
                print("Sent file content")  # 添加调试信息
            except IOError:  # 文件未找到等其他IO异常
                header = 'HTTP/1.1 404 Not Found\n\n'
                connectionSocket.send(header.encode())
                print("Sent 404 Not Found")  # 添加调试信息
        finally:
            # 关闭当前连接
            connectionSocket.close()
            print("Connection closed")  # 添加调试信息
finally:
    # 关闭套接字
    serverSocket.close()
    print("Server socket closed")  # 添加调试信息  
