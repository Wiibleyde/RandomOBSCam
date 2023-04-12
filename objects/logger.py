import os
import json
import time

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