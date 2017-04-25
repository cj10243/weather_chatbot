# -*- coding: utf-8 -*-
# /usr/bin/python3
import os
import sys
import json

import requests
from bs4 import BeautifulSoup
from flask import Flask, request
#from flask.ext.mysql import MySQL
app = Flask(__name__)
'''
mysql = MySQL(
app.config['MYSQL_DATABASE_USER'] = 'joanthan'
app.config['MYSQL_DATABASE_PASSWORD'] = 'PASS'
app.config['MYSQL_DATABASE_DB'] = 'Weather'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
conn = mysql.connect()
cursor = conn.cursor()
data = cursor.fetchall()
'''
@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

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
                    send_text = message_response(message_text)
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


# 爬蟲中央氣象局氣象資訊
def get_soup(url):
    res = requests.get(url)  # 從網址存網站頁面
    res.encoding = 'utf-8'  # 修正requests和bs4自行猜測的編碼為utf-8
    soup = BeautifulSoup(res.text, "lxml")  # 存成文字內容
    return soup


def weather_infor():
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


def message_response(message):
    s = luis.Luis("https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/c88fd2ed-73f8-4255-ae7f-7c07824252f6?subscription-key=b5a6e33be4244c189920b61a0249eefd&timezoneOffset=0&verbose=true&q=")
    text = s.analyze(message)
    if text.best_intent().intent == 'Weather':
        for i in range(text):
            if text.entities[i].type == 'Taipei':
                return weather_infor()
    else:
        return "我聽不懂你在說什麼"






print(weather_infor())

if __name__ == '__main__':
    app.run(debug=True)