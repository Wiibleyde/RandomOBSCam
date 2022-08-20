import sys
import time
import random
import logging
import socket
import sqlite3
from obswebsocket import obsws, requests  # noqa: E402

class ScenesDb:
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.conn = sqlite3.connect(dbfile)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS scenes (id INTEGER PRIMARY KEY, hour TEXT, scene TEXT, duration INTEGER)''')
        self.conn.commit()

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

def randomChange(fileName):
    lst=scenes.getScenes()
    nLst=[]
    for i in lst:
        if "CAM" in i['name']:
            nLst.append(i)
    random_scene = random.choice(nLst)
    name = random_scene['name']
    switch=u"{} : Switching to {}".format(nowTime(),name)
    print(switch)
    saveSwitch(switch,fileName)
    saveCurrentScene(name)
    ws.call(requests.SetCurrentScene(name))

def loopRandomChange(fileName):
    scenes = ws.call(requests.GetSceneList())
    transition = ws.call(requests.GetCurrentTransition())
    ws.call(requests.SetCurrentTransition("Fondu"))
    while True:
        randomChange(fileName)
        timeSleeped=random.randint(5,15)
        newLine=u"{} : Waiting {} seconds".format(nowTime(),timeSleeped)
        print(newLine)
        saveSwitch(newLine,fileName)
        for compteur in range(timeSleeped):
            saveWaitingTime(timeSleeped-compteur)
            time.sleep(1)   

def saveSwitch(changes,fileName):
    with open(fileName, "a") as f:
        f.write(changes)
        f.write("\n")

def saveCurrentScene(scene):
    """save the current scene with a parameter overwrite it all time"""
    with open("currentScene.txt", "w") as f:
        f.write(scene)
        f.write("\n")

def saveWaitingTime(time):
    """save the waiting time with a parameter overwrite it all time"""
    with open("waitingTime.txt", "w") as f:
        f.write(str(time))
        f.write("\n")

def clearTxtFile(fileName):
    with open(fileName, "w") as f:
        f.write("")

def beginPrgrm(fileName):
    with open(fileName, "a") as f:
        f.write(u"PROGRAM STARTED at {}".format(nowTime()))
        f.write("\n")

def endPrgrm(fileName):
    with open(fileName, "a") as f:
        f.write(u"PROGRAM ENDED at {}".format(nowTime()))
        f.write("\n")

if __name__ == '__main__':
    socket.getaddrinfo('localhost', 8080)
    logging.basicConfig(level=logging.INFO)
    sys.path.append('../')
    host = "localhost"
    port = 4444
    password = "4011"
    ws = obsws(host, port, password)
    ws.connect()
    scenes = ws.call(requests.GetSceneList())
    fileName=f"switch.txt"
    clearTxtFile(fileName)
    beginPrgrm(fileName)
    loopRandomChange(fileName)