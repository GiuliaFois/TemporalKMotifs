from counterTemplate import MotifCountingSteps
from motifLibrary import searchComments, snap_searchComments, findUsrChains, snap_findUsrChains
import time

class ChainCounter(MotifCountingSteps):

    def __init__(self, parameters):
        self.deltaT = int(parameters.getTimeWindowLength())
        self.log = parameters.getLog()
        self.logLength = len(self.log)
        self.parameters = parameters
        self.chains = {}
        self.snap_chains = {}

    def countMotif(self):
        currentIndex = 0
        while currentIndex < self.logLength:
            type = self.log[currentIndex][0]
            currentTime = self.log[currentIndex][1]
            currentAuth = self.log[currentIndex][3]
            authorsSet = set()
            authorsSet = authorsSet | {currentAuth}
            if type == "P":
                comments = searchComments(self.parameters, currentIndex)
                for c in comments:
                    commentAuth = c[3]
                    if not (commentAuth in authorsSet):
                        authorsSet = authorsSet | {commentAuth}
                        commentIndex = c[5]
                        chainLength = self.countCommentChains(commentIndex, currentTime, authorsSet) + 1
                        self.addInCounter(chainLength)
            elif type == "C":
                chainLength = self.countCommentChains(currentIndex, currentTime, authorsSet)
                self.addInCounter(chainLength)
            elif type == "R":
                targetID = self.log[currentIndex][4]
                chainLength = self.countReplyChains(currentIndex, targetID, currentTime, authorsSet) + 1
                self.addInCounter(chainLength)
            currentIndex = currentIndex + 1
        return self.chains

    def snap_countMotif(self):
        currentIndex = 0
        startTime = int(self.log[currentIndex][1])
        snapshotEnd = startTime + self.deltaT
        while currentIndex < self.logLength:
            currentAuth = self.log[currentIndex][3]
            authorsSet = set()
            authorsSet = authorsSet | {currentAuth}
            type = self.log[currentIndex][0]
            currentTime = int(self.log[currentIndex][1])
            if currentTime >= snapshotEnd:
                startTime = currentTime
                snapshotEnd = startTime + self.deltaT
            else:
                if type == "P":
                    comments = snap_searchComments(self.parameters, currentIndex, snapshotEnd)
                    for c in comments:
                        commentAuth = c[3]
                        if not (commentAuth in authorsSet):
                            authorsSet = authorsSet | {commentAuth}
                            commentIndex = c[5]
                            chainLength = self.snap_countCommentChains(commentIndex,snapshotEnd, authorsSet) + 1
                            self.addInCounter(chainLength)
                elif type == "C":
                    chainLength = self.snap_countCommentChains(currentIndex,snapshotEnd, authorsSet)
                    self.addInCounter(chainLength)
                elif type == "R":
                    targetID = self.log[currentIndex][4]
                    chainLength = self.snap_countReplyChains(currentIndex, targetID, snapshotEnd, authorsSet) + 1
                    self.addInCounter(chainLength)
                currentIndex = currentIndex + 1
                #print(currentIndex)
        return self.chains






    def countUsrMotif(self):
        currentIndex = 0
        while currentIndex < self.logLength:
            chainAuthors = []
            currentDest = self.log[currentIndex][1]
            currentTime = int(self.log[currentIndex][3])
            returnedChainLengths = findUsrChains(self.parameters, currentIndex, currentTime, currentDest, chainAuthors)
            for idx in range(0, len(returnedChainLengths)):
                self.addInCounter(returnedChainLengths[idx] + 1)
            currentIndex = currentIndex + 1
        return self.chains

    def snap_countUsrMotif(self):
        currentIndex = 0
        startTime = int(self.log[currentIndex][3])
        snapshotEnd = startTime + self.deltaT
        while currentIndex < self.logLength:
            #checking of the timestamp of the event
            chainAuthors = []
            currentDest = self.log[currentIndex][1]
            currentTime = int(self.log[currentIndex][3])
            if currentTime < snapshotEnd:
                returnedChainLengths = snap_findUsrChains(self.parameters, currentIndex, snapshotEnd, currentDest,chainAuthors)
                for idx in range(0, len(returnedChainLengths)):
                    self.addInCounter(returnedChainLengths[idx] + 1)
                currentIndex = currentIndex + 1
            else:
                startTime = currentTime
                snapshotEnd = startTime + self.deltaT
        return self.chains




    #CONTROLLO: SAREBBE DA RITORNARE COUNTER + 1????
    def countCommentChains(self, startIndex, startTime, authorsSet):
        targetID = self.log[startIndex][2]
        counter = self.countReplyChains(startIndex, targetID, startTime, authorsSet) + 1
        return counter

    def snap_countCommentChains(self, startIndex, snapshotEnd, authorsSet):
        targetID = self.log[startIndex][2]
        counter = self.snap_countReplyChains(startIndex, targetID, snapshotEnd, authorsSet) + 1
        return counter

    def countReplyChains(self, startIndex, targetID, startTime, authorsSet):
        currLen = 0
        startTime = int(startTime)
        currentIndex = startIndex + 1
        if currentIndex >= self.logLength:
            return 0
        currTime = int(self.log[currentIndex][1])
        while (currentIndex < self.logLength) and (currTime - startTime <= self.deltaT):
            currentAuth = self.log[currentIndex][3]
            if (self.log[currentIndex][0] == "R") and (self.log[currentIndex][4] == targetID) and not (currentAuth in authorsSet):
                currLen = currLen + 1
                authorsSet = authorsSet | {currentAuth}
            currentIndex = currentIndex + 1
            if currentIndex >= self.logLength:
                return currLen
            currTime = int(self.log[currentIndex][1])
        return currLen

    def snap_countReplyChains(self, startIndex, targetID, snapshotEnd, authorsSet):
        if(self.deltaT == -1):
            print("Inizio count reply chains, snapshotEnd "+ str(snapshotEnd))
            time.sleep(1)
        currLen = 0
        currentIndex = startIndex + 1
        if currentIndex >= self.logLength:
            return 0
        currTime = int(self.log[currentIndex][1])
        if(self.deltaT == -1):
            print("currTime è " + str(currTime))
        while (currentIndex < self.logLength) and (currTime < snapshotEnd):
            if (self.deltaT == -1):
                print(str(snapshotEnd - currTime))
                time.sleep(3)
            currentAuth = self.log[currentIndex][3]
            if (self.log[currentIndex][0] == "R") and (self.log[currentIndex][4] == targetID) and not (currentAuth in authorsSet):
                currLen = currLen + 1
                authorsSet = authorsSet | {currentAuth}
            currentIndex = currentIndex + 1
            if currentIndex >= self.logLength:
                return currLen
            currTime = int(self.log[currentIndex][1])

        return currLen


    def addInCounter(self, chainLength):
        if chainLength >= 3: #the chain needs to have at least length 3
            for i in range(chainLength, 2, -1):
                if i not in list(self.chains):
                    self.chains[i] = 1
                else:
                    self.chains[i] = self.chains[i] + 1

    #def snap_addInCounter(self, chainLength):
    #    if chainLength >= 3:
    #        for i in range(chainLength, 2, -1):
    #            if i not in list(self.snap_chains):
    #                self.snap_chains[i] = 1
    #            else:
    #                self.snap_chains[i] = self.snap_chains[i] + 1


