# -*- coding=utf-8 -*-
# @Time: 2025/12/7 13:39
# @File: client-tkinter.py
# @Software: PyCharm




import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from socket import socket, AF_INET, SOCK_STREAM


class Client(tk.Tk):
    def __init__(self, client_name):
        # 调用父类的初始化方法
        super().__init__()
        # 实例属性的设置
        self.isConnected = False  # 存储客户端连接服务器的状态，默认为False，没有连接
        self.client_socket = None  # 设置客户端的socket对象为空
        self.client_name = client_name
        # 加载客户端界面
        self.set_window()

    def set_window(self):
        """客户端界面的绘制"""
        # 设置窗口名称
        self.title(f"{self.client_name}的客户端界面")
        # 设置窗口大小
        self.geometry(f"380x420")
        self.resizable(0, 0)
        # 在窗口中放置Frame, 用来放置两个按钮
        frame1 = tk.Frame(self)
        frame1.pack(fill = tk.X)
        # 创建两个按钮
        conn_btn = tk.Button(frame1, text = "连接", height = 2,
                             command = lambda event=None: self.connect_to_server(event))
        dis_btn = tk.Button(frame1, text = "断开", height = 2, command = lambda event = None: self.dis_conn(event))
        conn_btn.pack(side = tk.LEFT, fill = tk.X, expand = 1)
        dis_btn.pack(side = tk.LEFT, fill = tk.X, expand = 1)
        # 只读文本框, 显示聊天内容
        frame2 = tk.Frame(self)
        frame2.pack(fill=tk.BOTH)
        self.show_text = scrolledtext.ScrolledText(frame2, width = 380, height = 15, state = "disabled")
        self.show_text.pack(fill=tk.BOTH, expand=1)
        # 创建聊天内容的文本框
        frame3 = tk.Frame(self)
        frame3.pack(fill=tk.BOTH)
        self.chat_text = scrolledtext.ScrolledText(frame3, width=380, height=10)
        self.chat_text.pack(fill=tk.BOTH, expand=1)
        # 创建两个按钮
        frame4 = tk.Frame(self)
        frame4.pack(fill = tk.X)
        reset_btn = tk.Button(frame4, text = "重置", height = 2, command = lambda event=None: self.reset(None))
        send_btn = tk.Button(frame4, text = "发送", height = 2, command=lambda event=None: self.send_to_server(None))
        reset_btn.pack(side=tk.LEFT, fill=tk.X, expand=1)
        send_btn.pack(side=tk.LEFT, fill=tk.X, expand=1)


    def connect_to_server(self, event):
        """回调函数: 连接"""
        print(f"客户端{self.client_name}连接服务器成功")
        # 如果客户端没有连接服务器，刚开始连接
        if not self.isConnected:
            # TCP编程的步骤
            server_host_port = ("127.0.0.1", 8888)
            # 创建socket对象
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            # 发送连接请求
            self.client_socket.connect(server_host_port)
            # 只要连接成功，发送一条数据
            self.client_socket.send(self.client_name.encode("utf-8"))
            # 启动一个线程，客户端的线程与服务器的会话线程进行会话
            # 设置成守护线程，窗体关掉，子线程也结束了
            client_thread = threading.Thread(target=self.recv_data, daemon=True)
            # 修改一下连接状态
            self.isConnected = True
            # 启动线程
            client_thread.start()

    def send_to_server(self, event):
        """回调函数: 发送"""
        # 判断连接状态
        if self.isConnected:
            # 从可写文本框中获取
            input_data = self.chat_text.get("1.0","end")
            if input_data != "":
                # 向服务器发送数据
                self.client_socket.send(input_data.strip().encode('utf-8'))
                # 发完数据之后，清空文本框
                self.chat_text.delete("1.0", "end")
                if input_data.strip() == "Y-disconnect-SJ":
                    # 发送断开的信息
                    self.isConnected = False

    def dis_conn(self, event):
        """回调函数: 断开"""
        # 发送断开的信息
        self.client_socket.send("Y-disconnect-SJ".encode("utf-8"))
        # 改变连接状态
        self.isConnected = False

    def reset(self, event):
        """回调函数: 重置"""
        self.chat_text.delete("1.0","end")

    def recv_data(self):
        """接收数据"""
        # 如果是连接状态
        while self.isConnected:
            # 接收来自服务器的数据
            data = self.client_socket.recv(1024).decode("utf-8")
            # 显示到只读文本中
            self.show_text.configure(state = "normal")
            self.show_text.insert("end", "-" * 40 + "\n" + data + "\n")
            self.show_text.configure(state = "disabled")


if __name__ == "__main__":
    # 初始化APP
    # name = input("请输入昵称:")
    name = "qxc"
    app = Client(name)

    # 循环刷新显示
    app.mainloop()
