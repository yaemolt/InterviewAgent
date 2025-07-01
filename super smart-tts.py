# -*- coding:utf-8 -*-

import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import os

#本demo示例是单次上传文本的示例，如果用在对时效要求高的交互场景，需要流式上传文本
# STATUS_FIRST_FRAME = 0  # 第一帧的标识
# STATUS_CONTINUE_FRAME = 1  # 中间帧标识
# STATUS_LAST_FRAME = 2  # 最后一帧的标识


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Text):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.Text = Text

        # 公共参数(common)
        # 在这里通过res_id 来设置通过哪个音库合成
        self.CommonArgs = {"app_id": self.APPID,"status":2}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {
        "tts": {
            "vcn": "x4_lingxiaoxuan_oral",  # 发音人参数，更换不同的发音人会有不同的音色效果
            "volume": 50,    #设置音量大小
            "rhy": 0,   #是否返回拼音标注		0:不返回拼音, 1:返回拼音（纯文本格式，utf8编码）
            "speed": 50,    #设置合成语速，值越大，语速越快
            "pitch": 50,    #设置振幅高低，可通过该参数调整效果
            "bgs": 0,   #背景音	0:无背景音, 1:内置背景音1, 2:内置背景音2
            "reg": 0,   #英文发音方式 	0:自动判断处理，如果不确定将按照英文词语拼写处理（缺省）, 1:所有英文按字母发音, 2:自动判断处理，如果不确定将按照字母朗读
            "rdn": 0,   #合成音频数字发音方式	0:自动判断, 1:完全数值, 2:完全字符串, 3:字符串优先
            "audio": {
                "encoding": "lame",  #合成音频格式， lame 合成音频格式为mp3
                "sample_rate": 24000,  #合成音频采样率，	16000, 8000, 24000
                "channels": 1,  # 音频声道数
                "bit_depth": 16, #合成音频位深 ：16, 8
                "frame_size": 0
            }
        }
    }
        
        self.Data = {
        "text": {
            "encoding": "utf8",
            "compress": "raw",
            "format": "plain",
            "status": 2,
            "seq": 0,
            "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")   # 待合成文本base64格式
        }
        }


class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class Url:
    def __init__(this, host, path, schema):
        this.host = host
        this.path = path
        this.schema = schema
        pass


# calculate sha256 and encode to base64
def sha256base64(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
    return digest


def parse_url(requset_url):
    stidx = requset_url.index("://")
    host = requset_url[stidx + 3:]
    schema = requset_url[:stidx + 3]
    edidx = host.index("/")
    if edidx <= 0:
        raise AssembleHeaderException("invalid request url:" + requset_url)
    path = host[edidx:]
    host = host[:edidx]
    u = Url(host, path, schema)
    return u


# build websocket auth request url
def assemble_ws_auth_url(requset_url, method="GET", api_key="", api_secret=""):
    u = parse_url(requset_url)
    host = u.host
    path = u.path
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    print(date)
    # date = "Thu, 12 Dec 2019 01:57:27 GMT"
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
    # print(signature_origin)
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    # print(authorization_origin)
    values = {
        "host": host,
        "date": date,
        "authorization": authorization
    }

    return requset_url + "?" + urlencode(values)

def on_message(ws, message):
    try:
        print(message)
        # data = json.dumps(message)
        message = json.loads(message)
        # print(message)
        # message =json.loads(message)
        code = message["header"]["code"]
        sid = message["header"]["sid"]
        if("payload" in message):
            audio = message["payload"]["audio"]['audio']
            audio = base64.b64decode(audio)
            status = message["payload"]['audio']["status"]
            print(message)
            if status == 2:
                print("ws is closed")
                ws.close()
            if code != 0:
                errMsg = message["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:

                with open('./demo.mp3', 'ab') as f:    # 这里文件后缀名，需要和业务参数audio.encoding 对应
                    f.write(audio)

    except Exception as e:
        print("receive msg,but parse exception:", e)



# 收到websocket错误的处理
def on_error(ws, error):
    # return 0
    print("### error:", error)




# 收到websocket关闭的处理
def on_close(ws,ts,end):
    return 0
    # print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws):
    def run(*args):
        d = {"header": wsParam.CommonArgs,
             "parameter": wsParam.BusinessArgs,
             "payload": wsParam.Data,
             }
        d = json.dumps(d)
        print("------>开始发送文本数据")
        ws.send(d)
        if os.path.exists('./demo.mp3'):
            os.remove('./demo.mp3')

    thread.start_new_thread(run, ())


if __name__ == "__main__":

    # 从控制台页面获取以下密钥信息，控制台地址：https://console.xfyun.cn/app/myapp
    appid = 'XXXXXXXX'
    apisecret = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    apikey = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

    wsParam = Ws_Param(APPID=appid, APISecret=apisecret,
                       APIKey=apikey,
                       Text="全红婵，2007年3月28日出生于广东省湛江市，中国国家跳水队女运动员，主项为女子10米跳台。")
    websocket.enableTrace(False)
    # wsUrl = wsParam.create_url()
    requrl = 'wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6'
    wsUrl = assemble_ws_auth_url(requrl,"GET",apikey,apisecret)
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
