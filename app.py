# -*- coding: utf-8 -*-
# /usr/bin/python3
import os
import sys
import json
import luis
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
import math
import pymysql
import database
from datetime import datetime
#from flask.ext.mysql import MySQL
app = Flask(__name__)

def AskTemperature():
    with database.Database() as db:
        return "溫度:{}".format(db.fetchone()[1])
def AskHumidity():
    with database.Database() as db:
        return "濕度:{}".format(db.fetchone()[2])
def AskUV():
    with database.Database() as db:
        return "紫外線值:{}".format(db.fetchone()[3])
def AskWeather():
    with database.Database() as db:
        return AskTemperature()+'\n'+AskHumidity()+'\n'+AskUV()


weather_list = ["temperature","humidity","uv"]
stations = {"鞍部":{121.5297306,25.18258611},"台北":{121.514853,25.037658},"大直":{121.542853,25.078047}}

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "認證成功", 200


@app.route('/', methods=['POST'])
def webhook():
    print("connect")
    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    lat = messaging_event["attachments"]["payload"]["coordinates"]["lat"]
                    lng = messaging_event["attachments"]["payload"]["coordinates"]["long"]
                    origin = (lat,lng)
                    station = get_station(origin)
                    print(lat)
                    print(long)
                    print(message_text)
                    send_text = message_response(message_text)
                    print(send_text)
                    send_message(sender_id, send_text)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)



def log(message):  # simple wrapper for logging to stdout on heroku
    print (str(message))
    sys.stdout.flush()

def ask_location(recipient_id):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": "請輸入您的所在位置"
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def get_station(origin):
    with database.Database() as db:
        sql = """SELECT lng,lat FROM station"""
        db.execute(sql)
        min = 0
        for desti in db.fetchall():
            if distance(origin,desti)<min:
                station = desti
        return desti


def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6378.137  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
                                                  * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    return d
print(get_station((121.5297306,25.18258611)))
# 爬蟲中央氣象局氣象資訊
def get_soup(url):
    res = requests.get(url)  # 從網址存網站頁面
    res.encoding = 'utf-8'  # 修正requests和bs4自行猜測的編碼為utf-8
    soup = BeautifulSoup(res.text, "lxml")  # 存成文字內容
    return soup

def getIPAddress():
    soup = get_soup("http://www.whatismyip.com/automation/n09230945.asp")
    address = soup.strong.get_text().split(" ")[3].replace('is', '').lstrip()
    return address



def message_response(message):
    s = luis.Luis("https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/c88fd2ed-73f8-4255-ae7f-7c07824252f6?subscription-key=b5a6e33be4244c189920b61a0249eefd&timezoneOffset=0&verbose=true&q=")
    text = "你好"
    text = s.analyze(message)
    print(text.entities)
    print(text.best_intent())
    intent = ""
    answer = ""
    count = 0
    for intent in text.entities:
        if intent.type in weather_list:
            count += 1
    if count < 3:
        for i,j in enumerate(text.intent()):
            if i == count:
                break
            if j.intent == 'AskTemperature':
                answer += AskTemperature()
                answer += '\n'
            if j.intent == "AskHumidity":
                answer += AskHumidity()
                answer += '\n'
            if j.intent == "AskUV":
                answer += AskUV()
                answer += '\n'
    else:
        if j.intent == 'Weather':
            answer += AskHumidity()
        else:
            return "抱歉，我聽不懂你在說什麼"

    return answer

def AskForecast(text):
    url = "http://www.cwb.gov.tw/V7/forecast/taiwan/Taipei_City.htm"
    soup = get_soup(url)

    page = soup.findAll("tr")  # 標籤元素，class元素
    lst = list()
    for i in page:
        lst.append(i.get_text())
    # print(lst)
    for i in range(len(lst)):
        x = lst[i].split('\n')
        lst[i] = x[1:len(x) - 1]
        # print(lst[i])
    infor_lst = lst[0]
    lst = lst[1:4]
    for i in lst:
        i[2:] = i[4:]

    # print(lst)
    message = ""
    for i in lst:
        for j, k in zip(infor_lst, i):
            message += j + '：' + k + '\n'
            # print('------------------------------------------')
    return message

def test_message_response(message):
    s = luis.Luis("https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/c88fd2ed-73f8-4255-ae7f-7c07824252f6?subscription-key=b5a6e33be4244c189920b61a0249eefd&timezoneOffset=0&verbose=true&q=")
    text = "你好"
    text = s.analyze(message)
    print(text.entities)
    count = 0
    for entity in text.entities:
        print(entity.type)
        if entity.type in weather_list:
            count += 1
    print(text.best_intent())
    print(text.intents)


message = "今天的氣溫和紫外線怎樣"
print(test_message_response(message))
#print(AskWeather('Taipei'))



if __name__ == '__main__':
    app.run(debug=True)