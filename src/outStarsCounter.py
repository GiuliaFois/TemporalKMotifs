from counterTemplate import MotifCountingSteps
from motifLibrary import countByAuthor, snap_countByAuthor, usrCountByAuthor, snap_usrCountByAuthor
import time


class OutStarsCounter(MotifCountingSteps):

    def __init__(self, parameters):
        self.deltaT = int(parameters.getTimeWindowLength())
        self.log = parameters.getLog()
        self.logLength = len(self.log)
        self.parameters = parameters
        self.outStars = {}

    def countMotif(self):
        currentIndex = 0
        count = 0
        while currentIndex < self.logLength:
            type = self.log[currentIndex][0]
            if type == "C" or type == "R":
                outStarLen = countByAuthor(self.parameters, currentIndex, type)
                self.addInCounter(outStarLen + 1)
            currentIndex = currentIndex + 1
        return self.outStars

    def snap_countMotif(self):
        currentIndex = 0
        startTime = int(self.log[currentIndex][1])
        snapshotEnd = startTime + self.deltaT
        while currentIndex < self.logLength:
            type = self.log[currentIndex][0]
            currentTime = int(self.log[currentIndex][1])
            if currentTime >= snapshotEnd:
                startTime = currentTime
                snapshotEnd = startTime + self.deltaT
            else:
                if type == "C" or type == "R":
                    outStarLen = snap_countByAuthor(self.parameters, currentIndex, type, snapshotEnd)
                    self.addInCounter(outStarLen + 1)
                currentIndex = currentIndex + 1
        return self.outStars



    def countUsrMotif(self):
        currentIndex = 0
        while currentIndex < self.logLength:
            outStarLen = usrCountByAuthor(self.parameters, currentIndex)
            self.addInCounter(outStarLen + 1)
            currentIndex = currentIndex + 1
        return self.outStars

    def snap_countUsrMotif(self):
        currentIndex = 0
        startTime = int(self.log[currentIndex][3])
        snapshotEnd = startTime + self.deltaT
        while currentIndex < self.logLength:
            currentTime = int(self.log[currentIndex][3])
            if currentTime >= snapshotEnd:
                startTime = currentTime
                snapshotEnd = startTime + self.deltaT
            else:
                outStarLen = snap_usrCountByAuthor(self.parameters, currentIndex, snapshotEnd)
                self.addInCounter(outStarLen)
                currentIndex = currentIndex + 1
        return self.outStars


    def addInCounter(self, outStarLength):
        if outStarLength >= 3:
            for i in range(outStarLength, 2, -1):
                if i not in list(self.outStars):
                    self.outStars[i] = 1
                else:
                    self.outStars[i] = self.outStars[i] + 1
