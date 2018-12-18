#!/usr/bin/python2.7
# coding=utf-8

from aliyunsdkcore import client as acsclient
from aliyunsdkalidns.request.v20150109 import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordsRequest

import os
import sys
import time
import json
import requests
import re as regular
import xml.etree.ElementTree as ET


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
        for i, RR in enumerate(self.config['RR']):
            if self.config['RecordID'][i] == '0000000000000000' or \
                    self.config['RecordID'][i] == '0':
                self.GetRecordID(i)
            # RecordID isn't exist in aliyun
            if self.config['RecordID'][i] == '0':
                continue
            self.config['IP'] = ip
            self.UpdateRecord(i)
        with open(self.filepath, "w") as f:
            f.write(json.dumps(self.config))

    # 获取记录ID
    def GetRecordID(self, i):
        id_r = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
        id_r.set_DomainName(self.config['Domain'].encode())
        id_r.set_RRKeyWord(self.config['RR'][i].encode())
        id_re = self.clt.do_action(id_r)
        # parser aliyun dns Record xml
        root = ET.fromstring(str(id_re))
        for domainrecord in root.findall("DomainRecords"):
            if len(domainrecord) < 1:
                Log('"%s.%s" record is not register in aliyun, please register first'
                        % (self.config['RR'][i], self.config['Domain']))
                self.config['RecordID'][i] = '0'
            else:
                for record in domainrecord.findall("Record"):
                    Line = record.find("Line").text
                    if Line == self.config['Line'][i]:
                        self.config['RecordID'][i] = record.find("RecordId").text

    # 更新域名记录
    def UpdateRecord(self, i):
        ur_r = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
        ur_r.set_RR(self.config['RR'][i].encode())
        ur_r.set_RecordId(self.config['RecordID'][i].encode())
        ur_r.set_Type('A')
        ur_r.set_Value(self.config['IP'].encode())
        ur_r.set_Line(self.config['Line'][i])
        ur_re = self.clt.do_action(ur_r)

        #print ur_re
        # 记录域名设置结果
        Log("********************************")
        root = ET.fromstring(str(ur_re))
        if "UpdateDomainRecordResponse" == root.tag:
            Log('Update dns %s: A %s.%s %s %s' % (self.config['RecordID'][i],
                self.config['RR'][i], self.config['Domain'], self.config['IP'], self.config['Line'][i]))
        elif "Error" == root.tag:
            Log('"%s.%s" record : %s' % (self.config['RR'][i], self.config['Domain'],
                root.find("Message").text))
        Log("********************************")


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
    print '正在获取公网IP'
    for i in range(1, 10):
        # 请求api接口
        response = requests.get(
                "http://ip.taobao.com/service/getIpInfo.php?ip=myip")
        if response.status_code == 200:
            break
        if i == 9:
            Log("Can't get public IP")
            sys.exit("Can't get public IP")
        time.sleep(0.05)

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

    Log('-------------------start aliyun ddns-------------------------')

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
    Log('Run Time: ' + time.ctime())

    # 移除锁
    # RemoveLock()

    Log('---------------------------------------------------------')

    exit()
