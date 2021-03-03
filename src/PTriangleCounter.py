from counterTemplate import MotifCountingSteps
from motifLibrary import searchComments, snap_searchComments, searchReplies, snap_searchReplies
import pingPongCounter
import math

class PTriangleCounter(MotifCountingSteps):

    def __init__(self, parameters):
        self.deltaT = int(parameters.getTimeWindowLength())
        self.log = parameters.getLog()
        self.logLength = len(self.log)
        self.parameters = parameters
        self.pTriangles = {}


    def countMotif(self):
        currentIndex = 0
        pingPongMethods = pingPongCounter.PingPongCounter(self.parameters)
        while currentIndex < self.logLength:
            type = self.log[currentIndex][0]
            if type == "P":
                comments = searchComments(self.parameters, currentIndex)
                if len(comments) >= 2:
                    for i in range(0, len(comments)):
                        firstAuth = comments[i][3]
                        firstCommentIndex = comments[i][5]
                        firstCommentReplies = searchReplies(self.parameters, firstCommentIndex)
                        if i < len(comments) - 1:
                            for j in range(i+1, len(comments)):
                                secondAuth = comments[j][3]
                                secondCommentIndex = comments[j][5]
                                if secondAuth != firstAuth:
                                    authors = (firstAuth, secondAuth)
                                    secondCommentReplies = searchReplies(self.parameters, secondCommentIndex)
                                    #prima cerco i ping pong sotto al commento di I
                                    for k in range(0, len(firstCommentReplies)):
                                        if firstCommentReplies[k][3] == secondAuth:
                                            interactions = pingPongMethods.countRInteractions(firstCommentReplies, authors, k+1)
                                            self.addInCounter(interactions)
                                    #poi cerco i ping pong sotto al commento di J
                                    authors = (secondAuth, firstAuth)
                                    for k in range(0, len(secondCommentReplies), 1):
                                        if secondCommentReplies[k][3] == firstAuth:
                                            interactions = pingPongMethods.countRInteractions(secondCommentReplies, authors, k+1)
                                            self.addInCounter(interactions)
            elif type == "C":
                replies = searchReplies(self.parameters, currentIndex)
                for i in range(0, len(replies), 1):
                    firstAuth = replies[i][3]
                    for j in range(i+1, len(replies)):
                        secondAuth = replies[j][3]
                        if secondAuth != firstAuth:
                            authors = (firstAuth, secondAuth)
                            #cerco un ping pong di risposte tra i due autori
                            interactions = pingPongMethods.countRInteractions(replies, authors, j+1)
                            self.addInCounter(interactions)
                            authors = (secondAuth, firstAuth)
                            interactions = pingPongMethods.countRInteractions(replies, authors, j + 1)
                            self.addInCounter(interactions)
            currentIndex = currentIndex + 1
        return self.pTriangles


    def snap_countMotif(self):
        currentIndex = 0
        startTime = int(self.log[currentIndex][1])
        snapshotEnd = startTime + self.deltaT
        pingPongMethods = pingPongCounter.PingPongCounter(self.parameters)
        while currentIndex < len(self.log):
            type = self.log[currentIndex][0]
            currentTime = int(self.log[currentIndex][1])
            if currentTime >= snapshotEnd:
                startTime = currentTime
                snapshotEnd = startTime + self.deltaT
            else:
                if type == "P":
                    comments = snap_searchComments(self.parameters, currentIndex, snapshotEnd)
                    if len(comments) >= 2:
                        for i in range(0, len(comments)):
                            firstAuth = comments[i][3]
                            firstCommentIndex = comments[i][5]
                            firstCommentReplies = snap_searchReplies(self.parameters, firstCommentIndex, snapshotEnd)
                            if i < len(comments) - 1:
                                for j in range(i + 1, len(comments)):
                                    secondAuth = comments[j][3]
                                    secondCommentIndex = comments[j][5]
                                    if secondAuth != firstAuth:
                                        authors = (firstAuth, secondAuth)
                                        secondCommentReplies = snap_searchReplies(self.parameters, secondCommentIndex, snapshotEnd)
                                        # prima cerco i ping pong sotto al commento di I
                                        for k in range(0, len(firstCommentReplies)):
                                            if firstCommentReplies[k][3] == secondAuth:
                                                interactions = pingPongMethods.countRInteractions(firstCommentReplies,
                                                                                                  authors, k + 1)
                                                self.addInCounter(interactions)
                                        # poi cerco i ping pong sotto al commento di J
                                        authors = (secondAuth, firstAuth)
                                        for k in range(0, len(secondCommentReplies), 1):
                                            if secondCommentReplies[k][3] == firstAuth:
                                                interactions = pingPongMethods.countRInteractions(secondCommentReplies,
                                                                                                  authors, k + 1)
                                                self.addInCounter(interactions)


                elif type == "C":
                    replies = snap_searchReplies(self.parameters, currentIndex, snapshotEnd)
                    for i in range(0, len(replies), 1):
                        firstAuth = replies[i][3]
                        for j in range(i + 1, len(replies)):
                            secondAuth = replies[j][3]
                            if secondAuth != firstAuth:
                                authors = (firstAuth, secondAuth)
                                # cerco un ping pong di risposte tra i due autori
                                interactions = pingPongMethods.countRInteractions(replies, authors, j + 1)
                                self.addInCounter(interactions)
                                authors = (secondAuth, firstAuth)
                                interactions = pingPongMethods.countRInteractions(replies, authors, j + 1)
                                self.addInCounter(interactions)

                currentIndex = currentIndex + 1
        return self.pTriangles

    def addInCounter(self, interactionsNumber):
        if interactionsNumber % 2 == 0:
            pTriangleLength = interactionsNumber
        else:
            pTriangleLength = interactionsNumber - 1
        if pTriangleLength >= 1:
            for i in range(pTriangleLength, 0, -2):
                if i not in list(self.pTriangles):
                    self.pTriangles[i] = 1
                else:
                    self.pTriangles[i] = self.pTriangles[i] + 1