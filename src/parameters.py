class Parameters:
    deltaT = 0
    log = []

    def __init__(self, newTimeWindow, newLog):
        self.deltaT = newTimeWindow
        self.log = newLog

    def getTimeWindowLength(self):
        return self.deltaT

    def getK(self):
        return self.k

    def getLog(self):
        return self.log


