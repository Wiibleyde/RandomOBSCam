from obswebsocket import obsws, requests
import json
import os
# import requests
import time
import random

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
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(self.filename):
            self.create()

    def create(self):
        with open(self.filename, "w") as f:
            json.dump([], f)

    def addInfo(self, message):
        stringLog = f"[INFO] {time.strftime('%d/%m/%Y %H:%M:%S')} - {message}"
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
            self.logs.addInfo("Connection to OBS successful")
        except Exception as e:
            self.logs.addError(f"Connection to OBS failed : {e}")

    def disconnect(self):
        try:
            self.obs.disconnect()
            self.logs.addInfo("Disconnection to OBS successful")
        except Exception as e:
            self.logs.addError(f"Disconnection to OBS failed : {e}")

    def getScenes(self):
        try:
            self.scenes = self.obs.call(requests.GetSceneList()).getScenes()
            self.logs.addInfo("Get scenes successful")
        except Exception as e:
            self.logs.addError(f"Get scenes failed : {e}")
        return self.scenes

    def getCurrentScene(self):
        try:
            self.currentScene = self.obs.call(requests.GetCurrentScene()).getName()
            self.logs.addInfo("Get current scene successful")
        except Exception as e:
            self.logs.addError(f"Get current scene failed : {e}")

    def setCurrentScene(self, scene):
        try:
            self.obs.call(requests.SetCurrentProgramScene(sceneName=scene))
            self.logs.addInfo(f"Set current scene to {scene} successful")
        except Exception as e:
            self.logs.addError(f"Set current scene to {scene} failed : {e}")

def neededScene():
    return 0

def autoCam():
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
    logs.addInfo(f"Scènes trouvées : {validScenes}")
    for scene in validScenes:
        logs.addInfo(f"Checking {scene['sceneName']}")
        if "SCE" in str(scene["sceneName"]):
            logs.addInfo(f"Adding {scene['sceneName']} to scene scenes")
            sceneScenes.append(scene["sceneName"])
        if "PUB" in str(scene["sceneName"]):
            logs.addInfo(f"Adding {scene['sceneName']} to public scenes")
            publicScenes.append(scene["sceneName"])
        if "PIA" in str(scene["sceneName"]):
            logs.addInfo(f"Adding {scene['sceneName']} to piano scenes")
            pianoScenes.append(scene["sceneName"])
    logs.addInfo(f"Scènes de scène trouvées : {sceneScenes}")
    logs.addInfo(f"Scènes du public trouvées : {publicScenes}")
    logs.addInfo(f"Scènes du piano trouvées : {pianoScenes}")
    while True:
        needed = neededScene()
        if needed == 0:
            # chose a random scene
            logs.addInfo("Changement de scène aléatoire car pas priorité")
            sceneSize = len(validScenes)
            randomScene = validScenes[random.randint(0, sceneSize-1)]
            obs.setCurrentScene(randomScene["sceneName"])
        elif needed == 1:
            # chose a random scene only in scene scenes
            logs.addInfo("Changement de scène aléatoire dans les scènes de scène")
            sceSceneSize = len(sceneScenes)
            randomScene = sceneScenes[random.randint(0, sceSceneSize-1)]
            obs.setCurrentScene(randomScene["sceneName"])
        elif needed == 2:
            # chose a random scene only in public scenes
            logs.addInfo("Changement de scène aléatoire dans les scènes du public")
            pubSceneSize = len(publicScenes)
            randomScene = publicScenes[random.randint(0, pubSceneSize-1)]
            obs.setCurrentScene(randomScene["sceneName"])
        elif needed == 3:
            # chose a random scene only in piano scenes
            logs.addInfo("Changement de scène aléatoire dans les scènes du piano")
            piaSceneSize = len(pianoScenes)
            randomScene = pianoScenes[random.randint(0, piaSceneSize)]
            obs.setCurrentScene(randomScene)
        waitingTime = random.randint(config.get("minTime"), config.get("maxTime"))
        logs.addInfo(f"Waiting {waitingTime} seconds")
        time.sleep(waitingTime)

if __name__ == "__main__":
    config = Config("config.json")
    logs = Logs("logs.log")
    obs = OBS(config, logs)
    autoCam()