from cgitb import reset
import sys
import time
import random
import logging
import socket
import sqlite3
from unicodedata import name
from obswebsocket import obsws, requests  # noqa: E402
import pyaudio
import struct
import math

INITIAL_TAP_THRESHOLD = 0.25
FORMAT = pyaudio.paInt16 
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 2
RATE = 44100  
INPUT_BLOCK_TIME = 0.05
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
# if we get this many noisy blocks in a row, increase the threshold
OVERSENSITIVE = 15.0/INPUT_BLOCK_TIME                    
# if we get this many quiet blocks in a row, decrease the threshold
UNDERSENSITIVE = 120.0/INPUT_BLOCK_TIME 
# if the noise was longer than this many blocks, it's not a 'tap'
MAX_TAP_BLOCKS = 0.15/INPUT_BLOCK_TIME

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

def get_rms( block ):
    # RMS amplitude is defined as the square root of the 
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into 
    # a string of 16-bit samples...

    # we will get one short out for each 
    # two chars in the string.
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768. 
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt( sum_squares / count )

class TapTester(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.tap_threshold = INITIAL_TAP_THRESHOLD
        self.noisycount = MAX_TAP_BLOCKS+1 
        self.quietcount = 0 
        self.errorcount = 0

    def stop(self):
        self.stream.close()

    def find_input_device(self):
        device_index = None            
        for i in range( self.pa.get_device_count() ):     
            devinfo = self.pa.get_device_info_by_index(i)   
            print( "Device %d: %s"%(i,devinfo["name"]) )

            for keyword in ["mic","input"]:
                if keyword in devinfo["name"].lower():
                    print( "Found an input: device %d - %s"%(i,devinfo["name"]) )
                    device_index = i
                    return device_index

        if device_index == None:
            print( "No preferred input found; using default input device." )

        return device_index

    def open_mic_stream( self ):
        device_index = self.find_input_device()

        stream = self.pa.open(   format = FORMAT,
                                 channels = CHANNELS,
                                 rate = RATE,
                                 input = True,
                                 input_device_index = device_index,
                                 frames_per_buffer = INPUT_FRAMES_PER_BLOCK)

        return stream

    def tapDetected(self): #DETECTED
        return True

    def listen(self):
        try:
            block = self.stream.read(INPUT_FRAMES_PER_BLOCK)
        except IOError as e:
            # dammit. 
            self.errorcount += 1
            print( "(%d) Error recording: %s"%(self.errorcount,e) )
            self.noisycount = 1
            return

        amplitude = get_rms( block )
        if amplitude > self.tap_threshold:
            # noisy block
            self.quietcount = 0
            self.noisycount += 1
        else:            
            # quiet block.

            if 1 <= self.noisycount <= MAX_TAP_BLOCKS:
                self.tapDetected()
            self.noisycount = 0
            self.quietcount += 1

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

def testPiano():
    # detect if piano is playing in microphone
    result=False
    return result

def testApplause():
    # detect if applause is heard in microphone
    for i in range(1000):
        result=tt.listen()
    return result

def testStatus():
    # 0 = all, 1 = obj, 2 = pu, 3 = pi
    # TO DO : test of situation by default return 0 (no reason)
    status=0
    if te: #RandomObj (no piano, no applause)
        status=1
    elif testApplause(): #RandomPu (applause detected)
        status=2
    elif True: #RandomPi (piano detected)
        status=3
    else: #RandomAll
        status=0
    return status

def loopRandomChange():
    scenes = ws.call(requests.GetSceneList())
    transition = ws.call(requests.GetCurrentTransition())
    ws.call(requests.SetCurrentTransition("Fondu"))
    status=0
    while True:
        status=testStatus()
        if status==0:
            now=randomChangeAll()
            ScenesDb.add(nowTime(), str(now), "No reason")
        elif status==1:
            now=randomChangeObj()
            ScenesDb.add(nowTime(), str(now), "Object")
        elif status==2:
            now=randomChangePu()
            ScenesDb.add(nowTime(), str(now), "Public")
        elif status==3:
            now=randomChangePi()
            ScenesDb.add(nowTime(), str(now), "Piano")
        else:
            now=randomChangeAll()
        timeSleeped=random.randint(5,15)
        print(f"{nowTime()} [INFO] Changement de scene vers {now} pendant {timeSleeped} secondes")
        for compteur in range(timeSleeped):
            time.sleep(1)   

if __name__ == '__main__':
    tt = TapTester()
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