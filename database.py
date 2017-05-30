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
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='ji3g45/4cl4up3', db='chatbot',use_unicode=True, charset="utf8")
        self.cur = self.conn.cursor()
        return self.cur

    def __exit__(self, ex_type, ex_value, ex_tb):
        self.conn.commit()
        self.conn.close()

#table chatbot.weather
'''
create table weather ( time timestamp default current_timestamp on update current_timestamp,
                id smallint,
                tpr float(3,1),
                wet float(3,1),
                uv tinyint(2),
                 foreign key (id) references chatbot.station(pk));

'''

#table chatbot.staion
'''
 create table station(pk smallint(5) not null auto_increment,
 name varchar(5),
 station_id varchar(5) ,
 lng double(10,6),
 lat double(10,6),
 primary key (pk));
'''

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
