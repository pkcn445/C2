from hashlib import md5
from random import randint
from Crypto.Cipher import AES
from binascii import a2b_hex, b2a_hex
from subprocess import Popen,PIPE


key = md5((str(randint(1,65535))+"pkcn").encode("utf-8")).hexdigest()
c = 0
newkey = ''
#取随机秘钥的前16位
for i in key:
    if c == 16:
        break
    newkey += i
    c += 1
#newkey = newkey.encode("utf-8")
r = Popen("cat /etc/passwd",shell=True,stderr=PIPE,stdout=PIPE)
r = r.stdout.read()    
r = r.decode("utf-8")
#text = r+(16 - (len(r) % 16)) * "=" #数据位数校验
#aes = AES.new(newkey,AES.MODE_ECB)
#encrypt_text = aes.encrypt(text.encode("utf-8"))
#encrypt_text = b2a_hex(encrypt_text)
#en_data = encrypt_text.decode("utf-8")

#处理解密

#aes2 = AES.new(newkey,AES.MODE_ECB)
#en_text = a2b_hex(en_data.encode("utf-8"))
#de_text = aes2.decrypt(en_text)
#print(de_text.decode("utf-8").split("=")[0])

class DateAesCrypt:
    def __init__(self,keys:str,data:str) -> None:
        self.keys = keys[:16].encode("utf-8") #取随机秘钥的前16位
        self.data = data

    def encrypt(self):
        text = self.data + (16 - (len(self.data) % 16)) * "=" #对数据进行位数校验
        aes = AES.new(self.keys, AES.MODE_ECB)
        en_text = b2a_hex(aes.encrypt(text.encode("utf-8")))
        return en_text.decode("utf-8")
    
    def decrypt(self):
        aes = AES.new(self.keys, AES.MODE_ECB)
        text = aes.decrypt(a2b_hex(self.data.encode("utf-8")))
        return text.decode("utf-8").split("=")[0]

c_data = DateAesCrypt(newkey,r).encrypt()
print(c_data)
print(DateAesCrypt(newkey,c_data).decrypt())