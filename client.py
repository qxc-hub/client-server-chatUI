# -*- coding=utf-8 -*-
# @Time: 2025/12/6 21:21
# @File: client.py
# @Software: PyCharm




import wx
import threading
from socket import socket,AF_INET,SOCK_STREAM

class Client(wx.Frame):
    def __init__(self, client_name):
        # 调用父类的初始化方法
        # None: 没有父级窗口
        # id表示当前窗口的一个编号
        # pos: 窗体的打开位置
        wx.Frame.__init__(self,None,id = 1001, title = client_name + "的客户端界面",
                          pos = wx.DefaultPosition, size = (400,450))
        # 创建面板对象
        pl = wx.Panel(self)
        # 在面板中放上盒子
        box = wx.BoxSizer(wx.VERTICAL)      # 垂直方向布局
        # 可伸缩的网格布局
        fgz1 = wx.FlexGridSizer(wx.HSCROLL) # 水平方向布局
        # 创建两个按钮
        conn_btn = wx.Button(pl, size = (200,40), label = "连接")
        dis_btn = wx.Button(pl, size=(200, 40), label="断开")
        # 把两个按钮放到可伸缩的网格布局
        fgz1.Add(conn_btn, wx.TOP|wx.LEFT)
        fgz1.Add(dis_btn, wx.TOP | wx.RIGHT)
        # 可伸缩的网格布局，添加到box中
        box.Add(fgz1,wx.ALIGN_CENTRE)   # wx.ALIGN_CENTRE: 居中对齐

        # 只读文本框,显示聊天内容
        self.show_text = wx.TextCtrl(pl, size = (400,210), style = wx.TE_MULTILINE|wx.TE_READONLY)
        box.Add(self.show_text,1,wx.ALIGN_CENTRE)
        # 创建聊天内容的文本框
        self.chat_text = wx.TextCtrl(pl, size=(400, 120), style=wx.TE_MULTILINE)
        box.Add(self.chat_text, 1, wx.ALIGN_CENTRE)

        # 可伸缩的网格布局
        fgz2 = wx.FlexGridSizer(wx.HSCROLL)  # 水平方向布局
        # 创建两个按钮
        reset_btn = wx.Button(pl, size=(200, 40), label="重置")
        send_btn = wx.Button(pl, size=(200, 40), label="发送")
        fgz2.Add(reset_btn, wx.TOP | wx.LEFT)
        fgz2.Add(send_btn, wx.TOP | wx.RIGHT)
        # 可伸缩的网格布局，添加到box中
        box.Add(fgz2, wx.ALIGN_CENTRE)  # wx.ALIGN_CENTRE: 居中对齐

        # 将盒子放到面板中
        pl.SetSizer(box)

        """---------------------------以上代码时客户端界面的绘制-------------------------------"""
        self.Bind(wx.EVT_BUTTON,self.connect_to_server,conn_btn)
        # 实例属性的设置
        self.client_name = client_name
        self.isConnected = False        # 存储客户端连接服务器的状态，默认为False，没有连接
        self.client_socket = None       # 设置客户端的socket对象为空
        # 给发送按钮绑定一个事件
        self.Bind(wx.EVT_BUTTON, self.send_to_server, send_btn)
        # 给断开按钮绑定一个事件
        self.Bind(wx.EVT_BUTTON, self.dis_conn, dis_btn)
        # 给重置按钮绑定一个事件
        self.Bind(wx.EVT_BUTTON, self.reset, reset_btn)



    def connect_to_server(self,event):
        print(f"客户端{self.client_name}连接服务器成功")
        # 如果客户端没有连接服务器，刚开始连接
        if not self.isConnected:
            # TCP编程的步骤
            server_host_port = ("127.0.0.1",8888)
            # 创建socket对象
            self.client_socket = socket(AF_INET,SOCK_STREAM)
            # 发送连接请求
            self.client_socket.connect(server_host_port)
            # 只要连接成功，发送一条数据
            self.client_socket.send(self.client_name.encode("utf-8"))
            # 启动一个线程，客户端的线程与服务器的会话线程进行会话
            # 设置成守护线程，窗体关掉，子线程也结束了
            client_thread = threading.Thread(target = self.recv_data, daemon=True)
            # 修改一下连接状态
            self.isConnected = True
            # 启动线程
            client_thread.start()

    def send_to_server(self, event):
        # 判断连接状态
        if self.isConnected:
            # 从可写文本框中获取
            input_data = self.chat_text.GetValue()
            if input_data != "":
                # 向服务器发送数据
                self.client_socket.send(input_data.encode('utf-8'))
                # 发完数据之后，清空文本框
                self.chat_text.SetValue('')
                if input_data == "Y-disconnect-SJ":
                    self.isConnected = False

    def dis_conn(self,event):
        # 发送断开的信息
        self.client_socket.send("Y-disconnect-SJ".encode("utf-8"))
        # 改变连接状态
        self.isConnected = False

    def reset(self,event):
        self.chat_text.Clear()     # 文本框内容清除


    def recv_data(self):
        # 如果是连接状态
        while self.isConnected:
            # 接收来自服务器的数据
            data = self.client_socket.recv(1024).decode("utf-8")
            # 显示到只读文本中
            self.show_text.AppendText("-" * 40 + "\n" + data + "\n")



if __name__ == "__main__":
    # 初始化APP
    app = wx.App()
    name = input("请输入昵称:")
    client = Client(name)
    client.Show()   # 可以改成: Client("Python娟子姐").Show()

    # 循环刷新显示
    app.MainLoop()


