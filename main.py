from obswebsocket import obsws, requests
import json
import os
import flask
import time
import random
import threading
import sqlite3
import logging

class Config:
    def __init__(self, filename):
        self.filename = filename
        self.config = {"minTime":5, "maxTime":10, "ip":"127.0.0.1", "port":4455, "password":"YOURPASSWORD"}
        if os.path.exists(self.filename):
            self.load()
        else:
            self.create()

    def load(self):
        with open(self.filename, "r") as f:
            self.config = json.load(f)

    def create(self):
        with open(self.filename, "w") as f:
            json.dump(self.config, f)

    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.config, f)

    def get(self, key):
        return self.config[key]
    
    def set(self, key, value):
        self.config[key] = value

class Logs:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        if not os.path.exists(self.filename):
            self.create()

    def create(self):
        with open(self.filename, "w") as f:
            json.dump([], f)

    def addDebug(self, message):
        stringLog = f"[DEBUG] {time.strftime('%d/%m/%Y %H:%M:%S')} - {message}"
        if self.mode:
            print(stringLog)
        with open(self.filename, "a",encoding='utf8') as f:
            f.write(stringLog+"\n")

    def addError(self, message):
        stringLog = f"[ERROR] {time.strftime('%d/%m/%Y %H:%M:%S')} - {message}"
        print(stringLog)
        with open(self.filename, "a",encoding='utf8') as f:
            f.write(stringLog+"\n")

    def addWarning(self, message):
        stringLog = f"[WARNING] {time.strftime('%d/%m/%Y %H:%M:%S')} - {message}"
        print(stringLog)
        with open(self.filename, "a",encoding='utf8') as f:
            f.write(stringLog+"\n")

class LogsScene:
    def __init__(self, filename):
        self.filename = filename
        req = "CREATE TABLE IF NOT EXISTS scenes (id INTEGER PRIMARY KEY AUTOINCREMENT, scene TEXT, date TEXT)"
        self.conn = sqlite3.connect(self.filename)
        self.cursor = self.conn.cursor()
        self.cursor.execute(req)
        self.conn.commit()

    def addScene(self, scene):
        req = f"INSERT INTO scenes(scene, date) VALUES('{scene}', '{time.strftime('%d/%m/%Y %H:%M:%S')}')"
        self.conn = sqlite3.connect(self.filename)
        self.cursor = self.conn.cursor()
        self.cursor.execute(req)
        self.conn.commit()

    def getScenes(self):
        req = "SELECT * FROM scenes"
        self.conn = sqlite3.connect(self.filename)
        self.cursor = self.conn.cursor()
        self.cursor.execute(req)
        return self.cursor.fetchall()
    
    def getLastScenes(self,nb):
        req = f"SELECT scene FROM scenes ORDER BY id DESC LIMIT {nb}"
        self.conn = sqlite3.connect(self.filename)
        self.cursor = self.conn.cursor()
        self.cursor.execute(req)
        return self.cursor.fetchall()
    
    def clearDb(self):
        req = "DELETE FROM scenes"
        self.conn = sqlite3.connect(self.filename)
        self.cursor = self.conn.cursor()
        self.cursor.execute(req)
        self.conn.commit()

class OBS:
    def __init__(self, config, logs):
        self.config = config
        self.logs = logs
        self.obs = None
        self.scenes = []
        self.currentScene = None
        self.currentSceneName = None

    def connect(self):
        try:
            self.obs = obsws(self.config.get("ip"), self.config.get("port"), self.config.get("password"),legacy=False)
            self.obs.connect()
            self.logs.addDebug("Connection to OBS successful")
        except Exception as e:
            self.logs.addError(f"Connection to OBS failed : {e}")

    def disconnect(self):
        try:
            self.obs.disconnect()
            self.logs.addDebug("Disconnection to OBS successful")
        except Exception as e:
            self.logs.addError(f"Disconnection to OBS failed : {e}")

    def getScenes(self):
        try:
            self.scenes = self.obs.call(requests.GetSceneList()).getScenes()
            self.logs.addDebug("Get scenes successful")
        except Exception as e:
            self.logs.addError(f"Get scenes failed : {e}")
        return self.scenes

    def getCurrentScene(self):
        try:
            self.currentScene = self.obs.call(requests.GetCurrentScene()).getName()
            self.logs.addDebug("Get current scene successful")
        except Exception as e:
            self.logs.addError(f"Get current scene failed : {e}")

    def setCurrentScene(self, scene):
        scene = scene["sceneName"]
        try:
            self.obs.call(requests.SetCurrentProgramScene(sceneName=scene))
            self.logs.addDebug(f"Set current scene to {scene} successful")
            logsScene.addScene(scene)
        except Exception as e:
            self.logs.addError(f"Set current scene to {scene} failed : {e}")

class NeededScenes:
    def __init__(self, mode):
        self.mode = mode
    
    def setMode(self, mode):
        self.mode = mode

    def getMode(self):
        return self.mode
    
    def getModeStr(self):
        if self.mode == 0:
            return "Random"
        elif self.mode == 1:
            return "Scene"
        elif self.mode == 2:
            return "Public"
        elif self.mode == 3:
            return "Piano"
        else:
            return "Not defined"

def autoCam(stop_event):
    obs.connect()
    scenes=obs.getScenes()
    validScenes = []
    sceneScenes = []
    publicScenes = []
    pianoScenes = []
    if len(scenes) == 0:
        logs.addError("No scene found")
        return
    for scene in range(len(scenes)):
        if "CAM" in scenes[scene]["sceneName"]:
            validScenes.append(scenes[scene])
    logs.addDebug(f"Scènes trouvées : {validScenes}")
    for scene in validScenes:
        logs.addDebug(f"Checking {scene['sceneName']}")
        if "SCE" in str(scene["sceneName"]):
            logs.addDebug(f"Adding {scene['sceneName']} to scene scenes")
            sceneScenes.append(scene)
        if "PUB" in str(scene["sceneName"]):
            logs.addDebug(f"Adding {scene['sceneName']} to public scenes")
            publicScenes.append(scene)
        if "PIA" in str(scene["sceneName"]):
            logs.addDebug(f"Adding {scene['sceneName']} to piano scenes")
            pianoScenes.append(scene)
    logs.addDebug(f"Scènes de scène trouvées : {sceneScenes}")
    logs.addDebug(f"Scènes du public trouvées : {publicScenes}")
    logs.addDebug(f"Scènes du piano trouvées : {pianoScenes}")
    while not stop_event.is_set():
        needed = neededScenes.getMode()
        if needed == 0:
            logs.addDebug("Changement de scène aléatoire car pas priorité")
            sceneSize = len(validScenes)
            randomScene = validScenes[random.randint(0, sceneSize-1)]
            obs.setCurrentScene(randomScene)
        elif needed == 1:
            logs.addDebug("Changement de scène aléatoire dans les scènes de scène")
            sceSceneSize = len(sceneScenes)
            randomScene = sceneScenes[random.randint(0, sceSceneSize-1)]
            obs.setCurrentScene(randomScene)
        elif needed == 2:
            logs.addDebug("Changement de scène aléatoire dans les scènes du public")
            pubSceneSize = len(publicScenes)
            randomScene = publicScenes[random.randint(0, pubSceneSize-1)]
            obs.setCurrentScene(randomScene)
        elif needed == 3:
            logs.addDebug("Changement de scène aléatoire dans les scènes du piano")
            piaSceneSize = len(pianoScenes)
            randomScene = pianoScenes[random.randint(0, piaSceneSize-1)]
            obs.setCurrentScene(randomScene)
        waitingTime = random.randint(config.get("minTime"), config.get("maxTime"))
        for i in range(waitingTime+1):
            if logs.mode:
                print(f"Waiting {waitingTime-i} seconds", end="\r")
            time.sleep(1)
            if stop_event.is_set():
                break
        if not stop_event.is_set():
            if logs.mode:
                print("Switching scene   ", end="\r")
            time.sleep(1)
    obs.disconnect()
    
def startAutoCam():
    global thread
    if thread is None or not thread.is_alive():
        thread = threading.Thread(target=autoCam, args=(thread_stop,))
        thread.start()
        return True
    else:
        return False

def stopAutoCam():
    global thread
    global thread_stop
    if thread is not None and thread.is_alive():
        thread_stop.set()
        try:
            thread.join()
        except Exception as e:
            logs.addError(f"Error while stopping thread : {e}")
        finally:
            thread_stop.clear()
        return True
    else:
        return False

def isThereAutoCam():
    global thread
    if thread is not None and thread.is_alive():
        return True
    else:
        return False

app = flask.Flask(__name__)
app.secret_key = "super secret key"
app.config["SESSION_TYPE"] = "filesystem"

@app.route("/")
def index():
    return flask.redirect(flask.url_for("control"))

@app.route("/neededScene/<int:needed>")
def neededScene(needed):
    logs.addDebug(f"Needed scene set to {needed}")
    neededScenes.setMode(needed)
    flask.flash(f"Needed scene set to {needed}")
    return flask.redirect(flask.url_for("control"))

@app.route("/start")
def start():
    startFunc = startAutoCam()
    if startFunc:
        flask.flash("Started auto loop")
        return flask.redirect(flask.url_for("control"))
    else:
        flask.flash("Auto loop already started")
        return flask.redirect(flask.url_for("control"))

@app.route("/stop")
def stop():
    stopFunc = stopAutoCam()
    if stopFunc:
        flask.flash("Stopped auto loop")
        return flask.redirect(flask.url_for("control"))
    else:
        flask.flash("Auto loop already stopped")
        return flask.redirect(flask.url_for("control"))
    
@app.route("/control")
def control():
    lastScenes = logsScene.getLastScenes(5)
    status = isThereAutoCam()
    return flask.render_template("control.html", lastScene=lastScenes, currentMode=neededScenes.getMode(), currentScene=obs.currentSceneName, status=status)

if __name__ == "__main__":
    neededScenes = NeededScenes(0)
    config = Config("config.json")
    logs = Logs("logs.log", False)
    logsScene = LogsScene("logsScene.log.db")
    logsScene.clearDb()
    obs = OBS(config, logs)
    thread = None
    thread_stop = threading.Event()
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.run(host="0.0.0.0", port=5000) 
