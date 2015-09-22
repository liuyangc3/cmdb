#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import json
import base64
import requests


#
# # url = 'http://172.16.200.39:8080/audios/ce62779e-f31e-40cb-beec-a4a40bccafea.mp3'
#
# url = 'http://zntwy.t.nxin.com/audios/ce62779e-f31e-40cb-beec-a4a40bccafea.mp3'
#
# header = {
#     "Range": "bytes=0-"
# }
#
# resp = requests.get(url, headers=header)
# print(resp.status_code)
#
# # print(resp.raw.read())
# # with open('a.mp3', 'w') as f:
#     # f.write(resp.raw.read())

def phone_num():
    num = ''
    for x in range(11):
        num += str(random.randint(1, 9))
    return num


def gen_phone_num(n):
    res = []
    for x in range(n):
        res.append(phone_num())
    return ','.join(res)


url = "http://10.201.11.127/zntServices2.action"

headers = {"Host": "chat.nxin.com"}
data = {
    "r": "002015",
    "v": "1",
    "d": {
        "attrs": {
            "sign": "A1A59736962CA832277C77493FCFF5FC",
            "mobileNums": gen_phone_num(681),
            "timestamp": "1432500000000"
        }
    }
}

data_str = json.dumps(data)
print(len(base64.b64encode(data_str)))
resp = requests.post(url, headers=headers, data=base64.b64encode(data_str))
print(resp.text)

# print(len(base64.b64encode(data_str)))

