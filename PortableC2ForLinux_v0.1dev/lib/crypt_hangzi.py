#encoding=utf-8
#作者：@破壳雏鸟
#github仓库：https://github.com/pkcn445
from json import dumps,loads
class CryptHangZi:
    def __init__(self) -> None:
        #这个基础密码字典，用户也可以在这里添加，它的格式是：{密文:明文}
        self.pwd_dict = {
            "啊":"A","阿":"a",
            "吧":"B","被":"b",
            "岑":"C","从":"c",
            "的":"D","到":"d",
            "额":"E","饿":"e",
            "发":"F","分":"f",
            "个":"G","该":"g",
            "好":"H","和":"h",
            "①":"I","②":"i",
            "就":"J","将":"j",
            "看":"K","空":"k",
            "了":"L","来":"l",
            "吗":"M","秒":"m",
            "你":"N","那":"n",
            "哦":"O","噢":"o",
            "平":"P","盘":"p",
            "去":"Q","其":"q",
            "人":"R","如":"r",
            "是":"S","时":"s",
            "他":"T","它":"t",
            "③":"U","④":"u",
            "⑦":"V","⑧":"v",
            "⑤":"W","⑥":"w",
            "想":"X","下":"x",
            "妖":"Y","有":"y",
            "在":"Z","中":"z",
            "←":"<","→":">",
            "￥":"$"
        }

    def __add_dict(self,add_dict:dict,reverse:bool) -> dict:
        """
        该方法是私有方法，用来处理用户有额外添加密码字典的情况

        用法：self.__add_dict(目标字典，bool值)

        注意：
            上面的 reverse 的值分两种情况 (之所以做这个转换是为了契合基础的密码字典)
                 True 表示将用户输入的密码字典由 {明文:密文} 变成 {密文:明文}
                 False 这个是默认值，表示不转换
        """
        if reverse:
            re_dict = dict()
            l = [i for i in add_dict.keys()]
            for i in l:
                re_dict[str(add_dict.get(i))] = str(i) #进行字典的 key 值和 vlaue 值进行转换
            self.pwd_dict.update(re_dict) #注意，如果添加字典的 key 值与原有的基础字典一样，原有字典的 key-value 值会被替换
            return self.pwd_dict
        else:
            self.pwd_dict.update(add_dict)
            return self.pwd_dict

    def encrypt_pwd(self,target_string:str,add_dict:dict=dict(),reverse:bool=False) -> tuple:
        """
        该方法用来提供加密功能，调用后会返回一个元组，第一个元素是加密后的字符串，第二个元素是一段 bytes 类型的数据
        它是由解密字典通过 json 格式化后再 encode 为 utf-8 编码

        用法：encrypt_pwd(要加密的字符串，用户额外添加的密码字典，bool值)

        注意：
            以上的 bool 值会传递给 __add_dict 方法，原因请看该方法的说明
            当前加密方法不支持中文加密，所以要加密的字符串最好没有中文，否则可能会出问题！
        """
        if {isinstance(target_string,str),isinstance(add_dict,dict),isinstance(reverse,bool)} & {True,False} != {True}:
            raise KeyError("输入参数值类型错误！")
        if add_dict:
            pwd = self.__add_dict(add_dict,reverse)
        else:
            pwd = self.pwd_dict
        pwd_dict = dict()
        set_values ={i for i in pwd.values()}      
        list_keys = [i for i in pwd.keys()]
        for i in list_keys: #这里将密码字典反转成 {明文:密文} 的形式
            pwd_dict[pwd.get(i)] = i
        encrypt_str = ''
        #这里会一个一个取出用户给定的要加密的字符串
        for i in target_string:
            if {i} & set_values == {i}: #判断该字符串是否与反转后的密码字典 {明文:密文} 的 key 值集合有交集，有则加密，否则就直接拼接
                encrypt_str += str(pwd_dict.get(i)) #如果在就取其 value 值，即密文，并拼接
            else:
                encrypt_str += str(i) #不是则按原来拼接
        return encrypt_str,dumps(pwd_dict).encode('utf-8')
    
    def crypt_pwd(self,target_string:str,json_dict:str) -> str:
        """
        该方法是用来解密的，它会返回解密后的明文字符串
        用法：crypt_pwd(密文字符串，json格式的密码字典字符串)
        """
        if {isinstance(target_string,str),isinstance(json_dict,str)} & {True,False} != {True}:
            raise KeyError("输入参数值类型错误！")
        j_dict = loads(json_dict) #将 json 序列化后的数据反序列化出来，这里会得到加密的字典，{明文:密文}
        pwd_dict = dict()
        crypt_str = ''
        for i in [j for j in j_dict.keys()]: #这里将字典反转成 {密文:明文} 的形式
            pwd_dict[j_dict.get(i)] = i
        for i in target_string: #一个一个依次取出密文字符串
            if {i} & {j for j in pwd_dict.keys()} == {i}: #判断其是否与加密字典 {密文:明文} 的 key 值集合有交集，如果有则需要解密，否则不用解密
                crypt_str += str(pwd_dict.get(i)) #取出明文value值，然后拼接
            else:
                crypt_str += str(i)
        return crypt_str


        
        
