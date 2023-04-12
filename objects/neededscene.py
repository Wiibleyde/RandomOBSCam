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