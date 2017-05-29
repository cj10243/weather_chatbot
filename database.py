# -*- coding: utf-8 -*-
# /usr/bin/python3
import pymysql
class Database:

    def __enter__(self):
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='nhshbot', db='chatbot')
        self.cur = self.conn.cursor()
        return self.cur

    def __exit__(self, ex_type, ex_value, ex_tb):
        self.conn.commit()
        self.conn.close()





Database