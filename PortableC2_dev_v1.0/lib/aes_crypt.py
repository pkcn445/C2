from Crypto.Cipher import AES
from binascii import a2b_hex, b2a_hex

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
