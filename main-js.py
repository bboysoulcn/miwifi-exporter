import execjs
import os
import requests

# 定义变量
deviceId = ""
route_url = ""
key = ""
password = ""

os.environ["EXECJS_RUNTIME"] = "Node"
# 打开js文件
with open('xiaomi.js', 'r') as f:
    js = f.read()
ctx = execjs.compile(js)
# 生成nonce
nonce = ctx.call("Encrypt.nonceCreat",deviceId)
# 加密密码
pwdkey = password + key
password = ctx.call("Encrypt.oldPwd", pwdkey, nonce)


url = "http://"+route_url+"/cgi-bin/luci/api/xqsystem/login"
data = {
    "logtype": 2,
    "nonce": nonce,
    "password": password,
    "username": "admin"
}
#发送请求
re = requests.post(url, data)
print(re.text)
