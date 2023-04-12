import json
import os

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
