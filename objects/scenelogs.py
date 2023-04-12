import sqlite3
import time

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
