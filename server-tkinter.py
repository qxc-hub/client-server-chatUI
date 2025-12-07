# -*- coding=utf-8 -*-
# @Time: 2025/12/7 14:58
# @File: server-tkinter.py
# @Software: PyCharm




import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from socket import socket, AF_INET, SOCK_STREAM


class Server(tk.Tk):
    def __init__(self):
        # 调用父类的初始化方法
        super().__init__()
        # 加载服务器端界面
        self.set_window()
        """服务器功能实现的必要属性"""
        self.isOn = False  # 存储服务器的启动状态，默认值为False，默认没有启动
        self.host_port = ('', 8888)  # 空的字符串代码的是本机的所有IP
        # 创建socket对象
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        # 绑定IP地址和端口
        self.server_socket.bind(self.host_port)
        # 监听
        self.server_socket.listen(5)
        # 创建一个字典，存储与客户端对话的会话线程
        self.session_thread_dict = {}  # key_value{客户端的名称key: 会话线程value}



    def set_window(self):
        """服务器端界面的绘制"""
        # 设置窗口名称
        self.title(f"服务器端界面")
        # 设置窗口大小
        self.geometry(f"380x420")
        self.resizable(0, 0)
        # 在窗口中放置Frame, 用来放置两个按钮
        frame1 = tk.Frame(self)
        frame1.pack(fill=tk.X)
        # 创建两个按钮
        start_server_btn = tk.Button(frame1, text = "启动服务", height = 2,
                                     command = lambda event=None: self.start_server(event))
        record_server_btn = tk.Button(frame1, text = "保存聊天记录", height = 2,
                                      command = lambda event=None: self.save_record(event))
        stop_server_btn = tk.Button(frame1, text = "停止服务", height = 2,
                                    command=lambda event=None: self.stop_server(event))
        start_server_btn.pack(side=tk.LEFT, fill=tk.X, expand=1)
        record_server_btn.pack(side=tk.LEFT, fill=tk.X, expand=1)
        stop_server_btn.pack(side=tk.LEFT, fill=tk.X, expand=1)

        # 只读文本框, 显示聊天内容
        frame2 = tk.Frame(self)
        frame2.pack(fill=tk.BOTH)
        self.show_text = scrolledtext.ScrolledText(frame2, width = 380, height = 40, state="disabled")
        self.show_text.pack(fill=tk.BOTH, expand=1)

    def save_record(self, event):
        # 获取只读文本框中的内容
        record_data = self.show_text.get("1.0","end")
        with open(f"record - {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}.log".replace(":", "："),
                  "w", encoding="utf-8") as f:
            f.write(record_data)
        print("已完成聊天记录保存")

    def stop_server(self, event):
        print("服务器已经停止服务")
        self.isOn = False

    def start_server(self, event):
        # 判断服务器是否已经启动，只有服务器没有启动时才启动
        if not self.isOn:  # 等价于self.isOn == False
            # 启动服务器
            self.isOn = True
            # 输出提示语
            print("服务器启动成功")
            # 创建主线程对象，函数式创建主线程
            # daemon=True，设置为守护线程，父线程（窗体界面）执行结束子线程他自动关闭
            main_thread = threading.Thread(target=self.do_work, daemon=True)
            # 启动主线程
            main_thread.start()

    def do_work(self):
        # 判断isOn的值
        while self.isOn:
            # 接收客户端的连接请求
            session_socket, client_addr = self.server_socket.accept()
            # 客户端发送连接请求之后，发送过来的第一条数据作为客户端的名称，客户端的名称去作为字典中的键
            user_name = session_socket.recv(1024).decode("utf-8")
            # 创建一个会话线程对象
            session_thread = SessionThread(session_socket, user_name, self)
            # 存储到字典中
            self.session_thread_dict[user_name] = session_thread
            # 启动会话线程
            session_thread.start()
            # 输出服务器的提示信息
            self.show_info_and_send_client('服务器通知', f"欢迎{user_name}进入聊天室",
                                           time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        # 当self.isOn的值为False时，执行关闭socket对象
        self.server_socket.close()

    def show_info_and_send_client(self, data_source, data, date_time):
        # 字符串操作
        send_data = f'{data_source}:{data}\n时间{date_time}'
        # 只读文本框
        self.show_text.configure(state = "normal")
        self.show_text.insert("end","-" * 40 + "\n" + send_data + "\n")
        self.show_text.configure(state = "disabled")
        # 每一个客户端都发送一次
        for client in self.session_thread_dict.values():
            # 如果当前的会话是开启状态
            if client.isOn:
                client.client_socket.send(send_data.encode("utf-8"))


class SessionThread(threading.Thread):
    def __init__(self, client_socket, user_name, server):
        # 调用父类的初始化方法
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.user_name = user_name
        self.server = server
        self.isOn = True  # 会话线程是否启动，当创建SessionThread对象时会话线程即启动

    def run(self) -> None:
        print(f'客户端:{self.user_name}已经和服务器连接成功')
        while self.isOn:
            # 从客户端接收数据 存储到data中
            data = self.client_socket.recv(1024).decode('utf-8')
            # 如果客户端点击断开按钮，先给服务器发送一句话，消息自定义
            if data == "Y-disconnect-SJ":
                self.isOn = False
                # 发送一条服务器通知
                self.server.show_info_and_send_client("服务器通知", f"{self.user_name}离开聊天室",
                                                      time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            else:
                # 其他聊天信息显示给所有的客户端，包含服务器也显示
                # 调用编写的方法
                self.server.show_info_and_send_client(self.user_name, data,
                                                      time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

        # 关闭socket
        self.client_socket.close()


if __name__ == "__main__":
    app = Server()
    app.mainloop()


