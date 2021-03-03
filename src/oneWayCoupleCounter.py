from counterTemplate import MotifCountingSteps
from motifLibrary import searchComments, snap_searchComments, searchReplies, snap_searchReplies
import fileLibrary
import time

class OneWayCoupleCounter(MotifCountingSteps):

    def __init__(self, parameters):
        self.deltaT = int(parameters.getTimeWindowLength())
        self.log = parameters.getLog()
        self.logLength = len(self.log)
        self.parameters = parameters
        self.oneWayCouples = {}

    def countMotif(self):
        currentIndex = 0
        while currentIndex < self.logLength:
            type = self.log[currentIndex][0]
            if type == "P":
                comments = searchComments(self.parameters, currentIndex)
                counterList = self.findOneWayInteractions(comments)
                for c in counterList:
                    self.addInCounter(c)
            elif type == "C":
                replies = searchReplies(self.parameters, currentIndex)
                counterList = self.findOneWayInteractions(replies)
                for c in counterList:
                    self.addInCounter(c)
            currentIndex = currentIndex + 1
        return self.oneWayCouples

    #controllo: che l'interazione corrente stia nello snap, che i successivi commenti/risposte ci stiano
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
                if type == "P":
                    comments = snap_searchComments(self.parameters, currentIndex, snapshotEnd)
                    counterList = self.findOneWayInteractions(comments)
                    for c in counterList:
                        self.addInCounter(c)
                elif type == "C":
                    replies = searchReplies(self.parameters, currentIndex)
                    counterList = self.findOneWayInteractions(replies)
                    for c in counterList:
                        self.addInCounter(c)
                currentIndex = currentIndex + 1
        return self.oneWayCouples


    def countUsrMotif(self):
        currentIndex = 0
        while currentIndex < self.logLength:
            currentAuthor = self.log[currentIndex][0]
            currentDest = self.log[currentIndex][1]
            users = (currentAuthor, currentDest)
            interactionsNumber = self.findCoupleInteractions(currentIndex, self.parameters, users)
            self.addInCounter(interactionsNumber + 1)
            currentIndex = currentIndex + 1
        return self.oneWayCouples

    def snap_countUsrMotif(self):
        currentIndex = 0
        startTime = int(self.log[currentIndex][3])
        snapshotEnd = startTime + self.deltaT
        while currentIndex < self.logLength:
            currentAuthor = self.log[currentIndex][0]
            currentDest = self.log[currentIndex][1]
            users = (currentAuthor, currentDest)
            currentTime = int(self.log[currentIndex][3])
            if currentTime >= snapshotEnd:
                startTime = currentTime
                snapshotEnd = startTime + 1
            else:
                interactionsNumber = self.snap_findCoupleInteractions(currentIndex, self.parameters, users, snapshotEnd)
                self.addInCounter(interactionsNumber + 1) #CONTROLLARE PERCHE'
                currentIndex = currentIndex + 1
        return self.oneWayCouples




    def findOneWayInteractions(self, interactionsList):
        authors =  []
        counterList = []
        for i in range(0, len(interactionsList)):
            counter = 0
            interactionAuth = fileLibrary.removeIfBackslashN(interactionsList[i][3])
            if not (interactionAuth in authors):
                authors.append(interactionAuth)
                for j in range(i+1, len(interactionsList)):
                    currentAuth = fileLibrary.removeIfBackslashN(interactionsList[j][3])
                    if interactionAuth == currentAuth:
                        counter = counter + 1
                counterList.append(counter)
        return counterList

    def findCoupleInteractions(self, startIndex, parameters, usersCouple):
        log = parameters.getLog()
        deltaT = int(parameters.getTimeWindowLength())
        startTime = int(log[startIndex][3])
        currentIndex = startIndex + 1
        interactions = 0
        while currentIndex < len(log):
            currentTime = int(log[currentIndex][3])
            currentAuth = log[currentIndex][0]
            currentDest = log[currentIndex][1]
            if currentTime - startTime > deltaT:
                return interactions
            elif (currentAuth == usersCouple[0]) and (currentDest == usersCouple[1]):
                interactions = interactions + 1
            currentIndex = currentIndex + 1
        #if interactions >= 4: print("START INDEX " + str(startIndex))
        return interactions

    def snap_findCoupleInteractions(self, startIndex, parameters, usersCouple, snapshotEnd):
        log = parameters.getLog()
        currentIndex = startIndex + 1
        interactions = 0
        while currentIndex < len(log):
            currentTime = int(log[currentIndex][3])
            currentAuth = log[currentIndex][0]
            currentDest = log[currentIndex][1]
            if currentTime >= snapshotEnd:
                return interactions
            elif (currentAuth == usersCouple[0]) and (currentDest == usersCouple[1]):
                interactions = interactions + 1
            currentIndex = currentIndex + 1
        return interactions


    def addInCounter(self, oneWayInteractions):
        if oneWayInteractions >= 3: #3 o 2???
            for i in range(oneWayInteractions, 2, -1):
                if i not in list(self.oneWayCouples):
                    self.oneWayCouples[i] = 1
                else:
                    self.oneWayCouples[i] = self.oneWayCouples[i] + 1



