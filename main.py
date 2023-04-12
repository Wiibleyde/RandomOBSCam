from obswebsocket import obsws, requests
import flask
import time
import random
import threading
import logging
import argparse
import asyncio

# Importing objects
from objects.config import Config
from objects.logger import Logs
from objects.neededscene import NeededScenes
from objects.scenelogs import LogsScene

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
            self.logs.addInfo(f"Set current scene to {scene} successful")
            logsScene.addScene(scene)
        except Exception as e:
            self.logs.addError(f"Set current scene to {scene} failed : {e}")

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
        logs.addInfo(f"Waiting {waitingTime} seconds before switching scene")
        for i in range(waitingTime+1):
            if logs.mode:
                print(f"Waiting {waitingTime-i} seconds", end="\r")
            try:
                if varForceChange:
                    logs.addDebug("Forcing change")
                    break
            except Exception as e:
                logs.addError(f"Error while checking varForceChange : {e}")
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
    
async def forceChangeScene():
    global varForceChange
    varForceChange = True
    await asyncio.sleep(1)
    varForceChange = False
    
def isThereAutoCam():
    global thread
    if thread is not None and thread.is_alive():
        return True
    else:
        return False
    
def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="Enable debug mode", action="store_true")
    args = parser.parse_args()
    return args

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

@app.route("/setStart")
def setStart():
    obs.connect()
    obs.setCurrentScene({"sceneName":"BEGIN"})
    obs.disconnect()
    flask.flash("Start scene set")
    return flask.redirect(flask.url_for("control"))

@app.route("/setEnd")
def setEnd():
    obs.connect()
    obs.setCurrentScene({"sceneName":"END"})
    obs.disconnect()
    flask.flash("End scene set")
    return flask.redirect(flask.url_for("control"))

@app.route("/forceChange")
def forceChange():
    logs.addDebug("Forcing scene change")
    asyncio.run(forceChangeScene())
    flask.flash("Forcing scene change")
    return flask.redirect(flask.url_for("control"))
    
@app.route("/control")
def control():
    lastScenes = logsScene.getLastScenes(5)
    status = isThereAutoCam()
    return flask.render_template("control.html", lastScene=lastScenes, currentMode=neededScenes.getMode(), currentScene=obs.currentSceneName, status=status)

if __name__ == "__main__":
    global logsScene
    neededScenes = NeededScenes(0)
    config = Config("config.json")
    if getArgs().debug:
        logs = Logs("logs.log", True)
    else:
        logs = Logs("logs.log", False)
    logsScene = LogsScene("logsScene.log.db")
    logsScene.clearDb()
    obs = OBS(config, logs)
    thread = None
    thread_stop = threading.Event()
    varForceChange = False
    log = logging.getLogger('werkzeug')
    if logs.mode:
        log.disabled = False
    else:
        log.disabled = True
    app.run(host="0.0.0.0", port=5000) 
