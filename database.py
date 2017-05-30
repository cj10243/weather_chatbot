# -*- coding: utf-8 -*-
# /usr/bin/python3
import pymysql
class Database:
    '''
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='nhshbot', db='chatbot',use_unicode=True, charset="utf8")
        self.cur = self.conn.cursor()
    '''

    def __enter__(self):
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='nhshbot', db='chatbot',use_unicode=True, charset="utf8")
        self.cur = self.conn.cursor()
        return self.cur

    def __exit__(self, ex_type, ex_value, ex_tb):
        self.conn.commit()
        self.conn.close()


'''
MySQL chatbot.station 
----------------------
CREATE TABLE station(
    pk SMALLINT(5) AUTO_INCREMENT,
    name VARCHAR(5),
    station_id VARCHAR(6),
    lng DOUBLE(10,6),
    lat DOUBLE(10,6),
    PRIMARY KEY(pk));
'''
