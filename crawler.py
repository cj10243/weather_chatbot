# -*- coding: utf-8 -*-
# /usr/bin/python3
import requests
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime,timedelta

import pymysql
import database


def get_soup(url):
    res = requests.get(url)  # 從網址存網站頁面
    res.encoding = 'utf-8'  # 修正requests和bs4自行猜測的編碼為utf-8
    soup = BeautifulSoup(res.text, "lxml")  # 存成文字內容
    return soup
def weather_crawler(id,weather_id):
    url = "http://www.cwb.gov.tw/V7/observe/24real/Data/{}.htm".format(weather_id)
    tw_soup = get_soup(url)#tpr+wtr
    url = "http://www.cwb.gov.tw/V7/observe/UVI/UVI.htm"
    uv_soup = get_soup(url)#uv
    count = 0
    for i in tw_soup.table.tr.next_siblings:
        if i == '\n':
            pass
        else:
            print("主鍵id={}".format(id))
            time = str(i).split("</th>")[0].split(">")[2]
            year = datetime.now().year
            time = datetime.strptime('{} {}'.format(year,time), '%Y %m/%d %H:%M')
            print("時間： {}".format(time))  # ex: 2017-05-29 13:30:00
            tpr = str(i).split("</td>")[0].split(">")[4]  # 攝氏溫度 ex:29.5
            #print("攝氏溫度： {}".format(tpr))
            wet = str(i).split("</td>")[1].split(">")[1]
            #print("相對溼度： {}".format(wet))  # 相對溼度 ex:85.1
            uv_soup.find("span", id="Data_{}".format(weather_id))
            try:
                uv = int(uv_soup.find("span", id="Data_{}".format(weather_id)).get_text().split(" ")[3])
            except AttributeError as error:
                #取不出字時　ex: uv = -
                print("{}".format(error))
                uv = None
            except ValueError as error:
                print("{}".error)
            else:
                #兩種情況：數字或文字　ex:1. uv=3 ;2. uv=機器維修
                uv = int(uv)
            print("紫外線值： {}".format(uv))
            with database.Database() as db:
                print("中央氣象局時間： {}".format(time))  # ex: 2017-05-29 13:30:00
                sql = """SELECT COUNT(*) FROM  weather where id = {} order by time desc;""".format(id)
                db.execute(sql)
                space = db.fetchone()[0]#檢驗是否為空的資料庫
                sql = """SELECT * FROM  weather where id = {} order by time desc;""".format(id)
                db.execute(sql)
                if space:
                    try:
                        db_time =  db.fetchone()[0]
                    except TypeError as error:
                        print("{}".format(error))
                    else:
                        print("資料庫最新一筆資料為：{}".format(db_time))

                try:

                    print("進入try區塊")
                    #資料表為空則跳出try前往存值
                    print("Table有{}筆資料".format(space))
                    if space == 0:
                        print("Table為空")
                        sql = """INSERT INTO weather (time,id,tpr,wet,uv) VALUES (%s,%s,%s,%s,%s)"""
                        db.execute(sql, (time,id, tpr, wet, uv))
                        count += 1
                        continue
                    #print("單筆資料:{}".format(db.fetchone()))
                except TypeError as err:
                    print("單筆data為空：{}".format(err))
                else:
                    print("資料庫最新一筆資料合法")
                    #資料庫最新一筆資料合法
                    print("是否用有最新資料:{}".format(time > db_time))
                    print("中央氣象局最新資料時間:{}".format(time))
                    print("資料庫最新資料時間:{}".format(db_time))
                    print("相差時間:{}".format(time - db_time))


                    if time  <= db_time:
                        print("資料庫全數更新")
                        break
                    elif time > db_time:

                        print("網站中資料較資料庫資料新")
                        # 網站中資料較資料庫資料新
                        while ((time - db_time != timedelta(minutes=15))):
                            print("中央氣象局最新資料時間:{}".format(time))
                            print("資料庫最新資料時間:{}".format(db_time))
                            print("相差時間:{}".format(time - db_time))
                            print("資料庫是否有最新資料:{}".format(db_time > time))
                            time -= timedelta(minutes=15)
                            #尋找與資料庫最新一筆差１５分鐘的資料
                            print("時間差是否只差15分鐘：{}".format(time - db_time == timedelta(minutes=15)))
                        print("insert")
                        count += 1
                        print("uv {}".format(uv))
                        sql = """INSERT INTO weather (time,id,tpr,wet,uv) VALUES (%s,%s,%s,%s,%s)"""
                        db.execute(sql, (time, id,tpr, wet, uv))
    print(count)





def station_crawler():
    url = "http://www.cwb.gov.tw/V7/observe/real/ObsN.htm"#北部
    soup = get_soup(url)
    print(soup.find("table",id=63).findAll("a"))
    for i in soup.find("table",id=63).findAll("a"):
        name = i.get_text()
        print(name) #ex: 鞍部
        station_id = i['href'].split(".")[0]
        #print(i['href'].split(".")[0]) #ex:46691
        url = "http://www.cwb.gov.tw/V7/google/{}_map.htm".format(station_id)
        soup = get_soup(url)
        #print(str(soup).find("lon="))
        lng_id = str(soup).find("lon=")
        lat_id = str(soup).find("lat=")
        #print(lat_id)
        #print(str(soup)[lng_id+4:lng_id+15])
        lng = float(str(soup)[lng_id + 4:lng_id + 13])
        lat = float(str(soup)[lat_id + 4:lat_id + 12])
        print(lng)
        print(lat)

        print(i['href'].split(".")[0]) #ex:46691
        #url = "http://www.cwb.gov.tw/V7/observe/real/{}.htm#ui-tabs-3".format(station_id)
        url = "http://www.cwb.gov.tw/V7/google/{}_map.htm".format(station_id)
        soup = get_soup(url)
        #print(str(soup))
        id_lat = str(soup).find("lat:")
        id_lng = str(soup).find("lng:")
        print(str(soup)[id_lat+4:id_lat+13])
        print(str(soup)[id_lng + 4:id_lng + 13])
        lat = float(str(soup)[id_lat+4:id_lat+13])#[4579:4595]
        lng = float(str(soup)[id_lng + 4:id_lng + 13])
        print(type(lat))
        print(type(lng))
        with database.Database() as db:
            sql = """SELECT * FROM  station"""
            db.execute(sql)
            sql = """INSERT INTO station (name,station_id, lng,lat) VALUES (%s,%s,%s,%s)"""
            db.execute(sql, (name,station_id, lng,lat))
def iter_station():
    with database.Database() as db:
        sql = """SELECT pk,station_id FROM  station """
        out = db.execute(sql)
        print(out)
        for i in db.fetchall():
            pk = i[0]
            station_id = i[1]
            print("主鍵".format(pk))
            print("測站id".format(station_id))
            weather_crawler(pk,station_id)



def test():


    with database.Database() as db:
        sql = """select * from weather where id = 142 order by time desc ;"""
        db.execute(sql)
        print(db.fetchone())
        sql = """SELECT * FROM  test_weather order by time desc"""
        db.execute(sql)
        print(db.fetchone() is None)
        print(db.fetchone())
        uv = int(uv_soup.find("span", id="Data_{}".format(weather_id)).get_text().split(" ")[3])
        sql = """INSERT INTO test_weather (uv) VALUES (%s)"""
        db.execute(sql,uv)

def test_statement():
    a, b, c = (1, 2, 3)
    print(a, b, c)
    try:
        c +=3
        print(c)
    except:
        print("hi")

    with database.Database() as db:

        def test():
            nonlocal c
            print(a)
            print(b)
            # print(c)  # (A)
            c = c + 1  # (B)



#weather_crawler(102,"C0AC4")
#test()
#test_statement()
iter_station()
#station_crawler()












