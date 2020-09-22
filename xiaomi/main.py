import requests
import re
import time
import random
from Crypto.Hash import SHA
import json
from prometheus_client import Gauge
import prometheus_client
from requests.adapters import HTTPAdapter
import configparser

# 读取配置
config = configparser.ConfigParser()
config.read('config.ini')
password = config.get('config', 'PASSWORD')
route_ip = config.get('config', 'ROUTE_IP')
sleep_time = config.getint('config', 'SLEEP_TIME')
exporter_port = config.getint('config', 'EXPORTER_PORT')
max_retries = config.getint('config', 'MAX_RETRIES')
timeout = config.getint('config', 'TIMEOUT')

# 创建请求对象
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=max_retries))
s.mount('https://', HTTPAdapter(max_retries=max_retries))

# 定义根url
route_url = 'http://' + route_ip


# 模拟登陆获取token
def get_token():
    # 获取nonce和mac_addr

    req = s.get(route_url + '/cgi-bin/luci/web', timeout=timeout)
    key = re.findall(r'key: \'(.*)\',', req.text)[0]
    mac_addr = re.findall(r'deviceId = \'(.*)\';', req.text)[0]
    nonce = "0_" + mac_addr + "_" + str(int(time.time())) + "_" + str(random.randint(1000, 10000))

    # 第一次加密 对应CryptoJS.SHA1(pwd + this.key)
    password_encrypt1 = SHA.new()
    password_encrypt1.update((password + key).encode('utf-8'))

    # 第二次加密对应 CryptoJS.SHA1(this.nonce + CryptoJS.SHA1(pwd + this.key).toString()).toString();
    password_encrypt2 = SHA.new()
    password_encrypt2.update((nonce + password_encrypt1.hexdigest()).encode('utf-8'))
    hexpwd = password_encrypt2.hexdigest()

    data = {
        "logtype": 2,
        "nonce": nonce,
        "password": hexpwd,
        "username": "admin"
    }

    url = route_url + '/cgi-bin/luci/api/xqsystem/login'

    response = s.post(url=url, data=data, timeout=timeout)
    res = json.loads(response.content)
    if res['code'] == 0:
        token = res['token']
        return token
    else:
        return False


def get_route_status(token):
    url = route_url + '/cgi-bin/luci/;stok=' + token + '/api/misystem/status'
    req = s.get(url, timeout=timeout)
    route_status = json.loads(req.content)
    mem_usage = route_status["mem"]["usage"]
    uptime = round(float(route_status["upTime"]) / 60.0 / 60.0 / 24.0, 2)
    cpu_load = route_status["cpu"]["load"]
    wan_downspeed = round(float(route_status["wan"]["downspeed"]) / 1024.0 / 1024.0, 2)
    wan_maxdownloadspeed = round(float(route_status["wan"]["maxdownloadspeed"]) / 1024.0 / 1024.0, 2)
    wan_upload = round(float(route_status["wan"]["upload"]) / 1024.0 / 1024.0, 2)
    wan_upspeed = round(float(route_status["wan"]["upspeed"]) / 1024.0 / 1024.0, 2)
    wan_maxuploadspeed = round(float(route_status["wan"]["maxuploadspeed"]) / 1024.0 / 1024.0, 2)
    wan_download = round(float(route_status["wan"]["download"]) / 1024.0 / 1024.0, 2)
    count = route_status["count"]["online"]
    status = {
        "mem_usage": mem_usage,
        "uptime": uptime,
        "cpu_load": cpu_load,
        "wan_download": wan_download,
        "wan_downspeed": wan_downspeed,
        "wan_maxdownloadspeed": wan_maxdownloadspeed,
        "wan_upload": wan_upload,
        "wan_upspeed": wan_upspeed,
        "wan_maxuploadspeed": wan_maxuploadspeed,
        "count": count
    }
    return status


if __name__ == '__main__':
    prometheus_client.start_http_server(exporter_port)
    miwifi_prom = Gauge("MIWIFI", "miwifi status", ["miwifi_status"])

    while True:
        try:
            token = get_token()
            status = get_route_status(token)
            mem_usage = status["mem_usage"]
            uptime = status["uptime"]
            cpu_load = status["cpu_load"]
            wan_downspeed = status["wan_downspeed"]
            wan_maxdownloadspeed = status["wan_maxdownloadspeed"]
            wan_upload = status["wan_upload"]
            wan_upspeed = status["wan_upspeed"]
            wan_maxuploadspeed = status["wan_maxuploadspeed"]
            wan_download = status["wan_download"]
            count = status["count"]

            miwifi_prom.labels("mem_usage").set(mem_usage)
            miwifi_prom.labels("uptime").set(uptime)
            miwifi_prom.labels("cpu_load").set(cpu_load)
            miwifi_prom.labels("wan_downspeed").set(wan_downspeed)
            miwifi_prom.labels("wan_maxdownloadspeed").set(wan_maxdownloadspeed)
            miwifi_prom.labels("wan_upload").set(wan_upload)
            miwifi_prom.labels("wan_upspeed").set(wan_upspeed)
            miwifi_prom.labels("wan_maxuploadspeed").set(wan_maxuploadspeed)
            miwifi_prom.labels("wan_download").set(wan_download)
            miwifi_prom.labels("count").set(count)
        except Exception as e:
            print(e)
        time.sleep(sleep_time)
