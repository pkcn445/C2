from os import system
input("你确定自己已经配置好 settings.py 文件了吗？确定好了就敲回车")
print("启动环境配置...")
system("pip3 install -r requirements.txt")
print("正在启动 server.py ...")
system("nohup python3 server.py &")
print("启动执行完毕！")
print("你可以使用 ps -aux | grep server.py 来查看脚本是否成功运行")
