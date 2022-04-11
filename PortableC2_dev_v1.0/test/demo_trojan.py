from json import loads,dumps
from base64 import b64decode,b64encode
from os.path import exists,getsize,basename,isfile
from time import sleep
from socket import socket

IP = "127.0.0.1"

def downfile():
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
                                s.send(dumps({"whoami":"t","data":"exit"}).encode("utf-8")) #这是发给代理端的退出信号
    sleep(1)
    s.send(dumps({"whoami":"exit"}).encode("utf-8"))
    s.close()

def uploadfile(filepath,targetfilepath=''):
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
    while True:
        data = s.recv(1024)
        if data:
            data = data.decode("utf-8")
            if data == "exit":
                print("文件上传成功！")
                break
    s.send(dumps({"whoami":"exit"}).encode("utf-8"))
    s.close()

if __name__ == "__main__":
    #print("控制端上传文件测试")
    #downfile()
    uploadfile("/home/pkcn/tools/fscan")