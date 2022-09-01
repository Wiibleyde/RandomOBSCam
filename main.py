import sys
import time
import random
import logging
import socket
import sqlite3
from unicodedata import name
from obswebsocket import obsws, requests  # noqa: E402

class ScenesDb:
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.conn = sqlite3.connect(dbfile)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS scenes (id INTEGER PRIMARY KEY, hour TEXT, scene TEXT, reason TEXT)''')
        self.conn.commit()
    
    def add(self, hour, scene, reason):
        self.cursor.execute('''INSERT INTO scenes (hour, scene, reason) VALUES (?, ?, ?)''', (str(hour), str(scene), str(reason)))
        self.conn.commit()
    
    def getLast(self):
        self.cursor.execute('''SELECT * FROM scenes ORDER BY id DESC LIMIT 1''')
        return self.cursor.fetchone()
    
    def get20Last(self):
        self.cursor.execute('''SELECT * FROM scenes ORDER BY id DESC LIMIT 20''')
        return self.cursor.fetchall()
    
def nowTime():
    """Format : [hh:mm:ss]"""
    currentTime=time.strftime("%H:%M:%S")
    currentDate=time.strftime("%d/%m/%Y")
    return f"[{currentTime}|{currentDate}]"

def hourDate():
    """Format : [hh:mm:ss]"""
    currentTime=time.strftime("%H%M%S")
    currentDate=time.strftime("%d%m%Y")
    return f"{currentTime}.{currentDate}"

def randomChangeAll():
    lst=scenes.getScenes()
    nLst=[]
    for i in lst:
        if "CAM" in i['name']:
            nLst.append(i)
    random_scene = random.choice(nLst)
    name = random_scene['name']
    ws.call(requests.SetCurrentScene(name))
    return name

def randomChangeObj():
    lst=scenes.getScenes()
    nLst=[]
    for i in lst:
        if "CAM" in i['name'] and "OBJ" in i['name']:
            nLst.append(i)
    random_scene = random.choice(nLst)
    name = random_scene['name']
    ws.call(requests.SetCurrentScene(name))
    return name

def randomChangePu():
    lst=scenes.getScenes()
    nLst=[]
    for i in lst:
        if "CAM" in i['name'] and "PU" in i['name']:
            nLst.append(i)
    random_scene = random.choice(nLst)
    name = random_scene['name']
    ws.call(requests.SetCurrentScene(name))
    return name

def randomChangePi():
    lst=scenes.getScenes()
    nLst=[]
    for i in lst:
        if "CAM" in i['name'] and "PI" in i['name']:
            nLst.append(i)
    random_scene = random.choice(nLst)
    name = random_scene['name']
    ws.call(requests.SetCurrentScene(name))
    return name

def testStatus():
    # TO DO : test of situation by default return 0
    status=0
    return status

def loopRandomChange():
    scenes = ws.call(requests.GetSceneList())
    transition = ws.call(requests.GetCurrentTransition())
    ws.call(requests.SetCurrentTransition("Fondu"))
    status=0
    while True:
        if status==0:
            now=randomChangeAll()
        elif status==1:
            now=randomChangeObj()
        elif status==2:
            now=randomChangePu()
        elif status==3:
            now=randomChangePi()
        else:
            now=randomChangeAll()
        timeSleeped=random.randint(5,15)
        print(f"{nowTime()} [INFO] Changement de scene vers {now} pendant {timeSleeped} secondes")
        ScenesDb.add(nowTime(), str(now), "randomChangeClassic")
        for compteur in range(timeSleeped):
            time.sleep(1)   

if __name__ == '__main__':
    ScenesDb = ScenesDb('scenes.db')
    socket.getaddrinfo('localhost', 8080)
    logging.basicConfig(level=logging.INFO)
    sys.path.append('../')
    host = "localhost"
    port = 4444
    password = "4011"
    ws = obsws(host, port, password)
    ws.connect()
    scenes = ws.call(requests.GetSceneList())
    loopRandomChange()