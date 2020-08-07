# This module is required for scheduling the script to run every 5 minutes.
from twisted.internet import task, reactor
from datetime import datetime
import requests
import json
import os
import pymysql
import sys

timeout = 600  # 10 minutes

REGION = 'us-east-1d'
rds_host = 'newdublinbikesinstance.cevl8km57x9m.us-east-1.rds.amazonaws.com'
name = "root"
password = 'secretpass'
db_name = "innodb"
# credentials used for connecting to RDS instance.


def Weather_Work():
    # Scrapping data from openweather API in form of JSON
    data = requests.get(
        "http://api.openweathermap.org/data/2.5/weather?q=Dublin&appid=6fb76ecce41a85161d4c6ea5e2758f2b").json()
    del data['coord']
    del data['base']
    del data['visibility']
    del data['wind']
    del data['clouds']
    del data['sys']
    del data['id']
    del data['name']
    del data['cod']
    for k in data['weather']:
        for key, value in list(k.items()):
            if key == "id" or key == "icon":
                del k[key]
            elif key == "main":
                desc = k[key]
    del data['main']['pressure']
    del data['main']['humidity']
    del data['main']['temp_min']
    del data['main']['temp_max']
    # Deleting information which are not required for SQL table.
    dt = data['dt']
    dt = int(dt)
    # formatting the data time as required using data time module.
    date = datetime.utcfromtimestamp(dt).strftime('%Y-%m-%d %H:%M:%S')
    date, time = date.split(" ")
    # print(date)
    # print(time)
    temp = data['main']['temp']
    # print(temp)
    # print(data)
    # print(desc)
    #print("inside 1")
    conn = pymysql.connect(rds_host, user=name,
                           passwd=password, db=db_name, connect_timeout=5)
    with conn.cursor() as cur:
        #print("inside 1")
        #cur.execute("""delete from weather""")
        cur.execute("""insert into weather (temperature, description, time ,date) values( %s, '%s' , '%s' , '%s')""" % (
            temp, desc, time, date))
        cur.execute("""select * from innodb.weather""")
        #print("inside 11")
        conn.commit()
        cur.close()


l = task.LoopingCall(Weather_Work)
l.start(timeout)  # call every 10 minutes
reactor.run()
