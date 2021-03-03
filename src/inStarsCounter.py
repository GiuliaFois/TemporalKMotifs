from counterTemplate import MotifCountingSteps
from motifLibrary import searchComments, snap_searchComments, searchReplies, snap_searchReplies, \
                        usrCountByDest, snap_usrCountByDest

class InStarsCounter(MotifCountingSteps):

    def __init__(self, parameters):
        self.deltaT = int(parameters.getTimeWindowLength())
        self.log = parameters.getLog()
        self.logLength = len(self.log)
        self.parameters = parameters
        self.inStars = {}

    def countMotif(self):
        currentIndex = 0
        while(currentIndex < self.logLength):
            type = self.log[currentIndex][0]
            currentAuthor = self.log[currentIndex][3]
            if type == "P":
                commentsList = searchComments(self.parameters, currentIndex)
                #itero su tutti i commenti e rimuovo tutti quelli dell'autore del post
                #poi rimuovo tutti i duplicati (creo un set e considero la sua cardinalità)
                commentsSet = set()
                for c in range (0, len(commentsList)):
                    commentAuthor = commentsList[c][3]
                    if commentAuthor != currentAuthor:
                        commentsSet = commentsSet | {commentAuthor}
                self.addInCounter(len(commentsSet) + 1) #anche il post fa parte della stella
            elif type == "C":
                repliesList = searchReplies(self.parameters, currentIndex)
                repliesSet = set()
                for r in range(0, len(repliesList)):
                    replyAuthor = repliesList[r][3]
                    if replyAuthor != currentAuthor:
                        repliesSet = repliesSet | {replyAuthor}
                self.addInCounter(len(repliesSet) + 1)
            currentIndex = currentIndex + 1
        return self.inStars

    def snap_countMotif(self):
        currentIndex = 0
        startTime = int(self.log[currentIndex][1])
        snapshotEnd = startTime + self.deltaT
        while(currentIndex < self.logLength):
            type = self.log[currentIndex][0]
            currentAuthor = self.log[currentIndex][3]
            currentTime = int(self.log[currentIndex][1])
            if currentTime >= snapshotEnd:
                startTime = currentTime
                snapshotEnd = startTime + self.deltaT
            else:
                if type == "P":
                    commentsList = snap_searchComments(self.parameters, currentIndex, snapshotEnd)
                    commentsSet = set()
                    for c in range(0, len(commentsList)):
                        commentAuthor = commentsList[c][3]
                        if commentAuthor != currentAuthor:
                            commentsSet = commentsSet | {commentAuthor}
                    self.addInCounter(len(commentsSet) + 1)  # anche il post fa parte della stella
                elif type == "C":
                    repliesList = snap_searchReplies(self.parameters, currentIndex, snapshotEnd)
                    repliesSet = set()
                    for r in range(0, len(repliesList)):
                        replyAuthor = repliesList[r][3]
                        if replyAuthor != currentAuthor:
                            repliesSet = repliesSet | {replyAuthor}
                    self.addInCounter(len(repliesSet) + 1)
                currentIndex = currentIndex + 1
        return self.inStars




    def countUsrMotif(self):
        currentIndex = 0
        while currentIndex < self.logLength:
            inStarLen = usrCountByDest(self.parameters, currentIndex)
            self.addInCounter(inStarLen)
            currentIndex = currentIndex + 1
        return self.inStars

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
                inStarLen = snap_usrCountByDest(self.parameters, currentIndex, snapshotEnd)
                self.addInCounter(inStarLen)
                currentIndex = currentIndex + 1
        return self.inStars


    def addInCounter(self, inStarsLength):
        if inStarsLength >= 3:
            for i in range(inStarsLength, 2, -1):
                if i not in list(self.inStars):
                    self.inStars[i] = 1
                else:
                    self.inStars[i] = self.inStars[i] + 1
