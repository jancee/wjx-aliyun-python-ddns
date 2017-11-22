#!/usr/bin/python2.7
# coding=utf-8

from aliyunsdkcore import client as acsclient
from aliyunsdkalidns.request.v20150109 import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordsRequest

import time
import json
import re as regular
import requests
import os


class Client:
    def __init__(self, filepath, ip):
        # 获取配置信息
        self.filepath = filepath
        self.config = json.load(file(self.filepath))

        # 创建Acs客户端
        self.clt = acsclient.AcsClient(self.config['Key'].encode(),
                                       self.config['Secret'].encode(),
                                       self.config['Region'].encode())

        # 不存在RecordID，则获取RecordID
        if not self.config.has_key('RecordID'):
            self.GetRecordID()

        self.config['IP'] = ip
        self.UpdateRecord()

    # 获取记录ID
    def GetRecordID(self):
        id_r = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
        id_r.set_DomainName(self.config['Domain'].encode())
        id_r.set_RRKeyWord(self.config['RR'].encode())
        id_re = self.clt.do_action(id_r)
        print id_re
        self.config['RecordID'] = regular.findall(pattern="<RecordId>(\d*)</RecordId>", string=id_re)[0]
        with open(self.filepath, "w") as f:
            f.write(json.dumps(self.config))

    # 更新域名记录
    def UpdateRecord(self):
        ur_r = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
        ur_r.set_RR(self.config['RR'].encode())
        ur_r.set_RecordId(self.config['RecordID'].encode())
        ur_r.set_Type('A')
        ur_r.set_Value(self.config['IP'].encode())
        ur_r.set_Line("default")
        ur_re = self.clt.do_action(ur_r)

        # 记录域名设置结果
        Log('Aliyun DNS Response: ' + ur_re)


# 日志持久化
def Log(content):
    print content
    if not is_log:
        return
    with open(path + "/output.log", "a+") as logFile:
        logFile.write(content)
        logFile.write("\n")


# 获取IP
def GetIP():
    # 请求api接口
    response = requests.get("http://ip.taobao.com/service/getIpInfo.php?ip=myip")

    # 提取出其中的IP
    jsonBody = json.loads(response.text)
    ip = jsonBody['data']['ip']

    Log(str('Public IP: ') + ip)

    return ip


# 检查是否锁定
def CheckLock():
    if os.path.exists(path + "/Aliyun-DDNS.lock"):
        with open(path + "/Aliyun-DDNS.lock", 'r') as file:
            pid = file.read()
        os.system("kill -9 " + pid)
        os.remove(path + "/Aliyun-DDNS.lock")
        CheckLock()
    else:
        with open(path + "/Aliyun-DDNS.lock", 'w') as file:
            file.write(str(os.getpid()))


# 移除锁
def RemoveLock():
    os.remove(path + "/Aliyun-DDNS.lock")


if __name__ == '__main__':
    path = os.path.split(os.path.realpath(__file__))[0]  # 获取当前路径
    # 是否记录
    is_log = 1

    Log('---------------------------------------------------------')

    # 锁
    # CheckLock()

    match = regular.compile("(.*\.json)")
    configWalk = os.walk(path + "/conf.d")

    # 获取IP
    ip = GetIP()

    #
    for dirpath, dirnames, filenames in configWalk:
        for filename in filenames:
            if match.match(filename) and filename != "config-template.json":
                client = Client(os.path.join(dirpath, filename), ip)

    # 记录时间
    Log('Time: ' + time.ctime())

    # 移除锁
    # RemoveLock()

    Log('---------------------------------------------------------')

    exit()
