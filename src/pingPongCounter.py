from counterTemplate import MotifCountingSteps
from motifLibrary import searchComments, snap_searchComments, searchReplies, snap_searchReplies, indexOfEntry
import math, time

class PingPongCounter(MotifCountingSteps):

    def __init__(self, parameters):
        self.deltaT = int(parameters.getTimeWindowLength())
        self.log = parameters.getLog()
        self.logLength = len(self.log)
        self.parameters = parameters
        self.pingPongs = {}

    def countMotif(self):
        currentIndex = 0
        while(currentIndex < self.logLength):
            currentAuthor = self.log[currentIndex][3]
            type = self.log[currentIndex][0]
            if type == "P":
                comments = searchComments(self.parameters, currentIndex)
                for c in comments:
                    #ogni commento fa partire un pingpong a sè
                    commentIndex = c[5]
                    commentAuthor = c[3]
                    #interactions = 1 #considero come prima interazione quella della entry corrente (P <- C)
                    replies = searchReplies(self.parameters, commentIndex)
                    authors = (currentAuthor, commentAuthor)
                    interactions = self.countPCInteractions(replies, authors)
                    self.addInCounter(interactions)
            elif type == "C":
                replies = searchReplies(self.parameters, currentIndex)
                if len(replies) > 1:
                    for r in range(0, len(replies) - 1):
                        reply = replies[r]
                        replyAuthor = reply[3]
                        authors = (currentAuthor, replyAuthor)
                        interactions = self.countRInteractions(replies, authors, r+1)
                        self.addInCounter(interactions)
            elif type == "R":
                targetID = self.log[currentIndex][4]
                currentID = self.log[currentIndex][2]
                targetIndex = indexOfEntry(self.parameters, targetID, currentIndex)
                replies = searchReplies(self.parameters, targetIndex)
                #rimuovo risposte troppo vecchie temporalmente
                r = 0
                reached = 0
                while(r < len(replies)) and (reached == 0):
                    reply = replies[r]
                    replyID = reply[2]
                    if replyID == currentID: reached = 1
                    #rimuovo la risposta
                    replies.pop(r)
                if(len(replies) > 1):
                    for r in range(0, len(replies)):
                        reply = replies[r]
                        replyAuthor = reply[3]
                        authors = (currentAuthor, replyAuthor)
                        interactions = self.countRInteractions(replies, authors, r+1)
                        self.addInCounter(interactions)
            #ho analizzato tutte le risposte, se interactions rispetta le condizioni aggiungo il motif
            currentIndex = currentIndex + 1
        return self.pingPongs

    def snap_countMotif(self):
        currentIndex = 0
        startTime = int(self.log[currentIndex][1])
        snapshotEnd = startTime + self.deltaT
        while (currentIndex < self.logLength):
            currentTime = int(self.log[currentIndex][1])
            currentAuthor = self.log[currentIndex][3]
            type = self.log[currentIndex][0]
            if currentTime >= snapshotEnd:
                startTime = currentTime
                snapshotEnd = startTime + self.deltaT
            else:
                if type == "P":
                    comments = snap_searchComments(self.parameters, currentIndex, snapshotEnd)
                    for c in comments:
                        # ogni commento fa partire un pingpong a sè
                        commentIndex = c[5]
                        commentAuthor = c[3]
                        # interactions = 1 #considero come prima interazione quella della entry corrente (P <- C)
                        replies = snap_searchReplies(self.parameters, commentIndex, snapshotEnd)
                        authors = (currentAuthor, commentAuthor)
                        interactions = self.countPCInteractions(replies, authors)
                        self.addInCounter(interactions)
                elif type == "C":
                    replies = snap_searchReplies(self.parameters, currentIndex, snapshotEnd)
                    if len(replies) > 1:
                        for r in range(0, len(replies) - 1):
                            reply = replies[r]
                            replyAuthor = reply[3]
                            authors = (currentAuthor, replyAuthor)
                            interactions = self.countRInteractions(replies, authors, r + 1)
                            self.addInCounter(interactions)
                elif type == "R":
                    targetID = self.log[currentIndex][4]
                    currentID = self.log[currentIndex][2]
                    targetIndex = indexOfEntry(self.parameters, targetID, currentIndex)
                    replies = snap_searchReplies(self.parameters, targetIndex, snapshotEnd)
                    # rimuovo risposte troppo vecchie temporalmente
                    r = 0
                    reached = 0
                    while (r < len(replies)) and (reached == 0):
                        reply = replies[r]
                        replyID = reply[2]
                        if replyID == currentID: reached = 1
                        # rimuovo la risposta
                        replies.pop(r)
                    if (len(replies) > 1):
                        for r in range(0, len(replies)):
                            reply = replies[r]
                            replyAuthor = reply[3]
                            authors = (currentAuthor, replyAuthor)
                            interactions = self.countRInteractions(replies, authors, r + 1)
                            self.addInCounter(interactions)
                currentIndex = currentIndex + 1
        return self.pingPongs

    def countUsrMotif(self):
        currentIndex = 0
        while currentIndex < self.logLength:
            user1 = self.log[currentIndex][0]
            user2 = self.log[currentIndex][1]
            authors = (user1, user2)
            interactions = self.countUsrInteractions(self.parameters, authors, currentIndex)
            self.addInCounter(interactions)
            currentIndex = currentIndex + 1
        return self.pingPongs

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
                user1 = self.log[currentIndex][0]
                user2 = self.log[currentIndex][1]
                authors = (user1, user2)
                interactions = self.snap_countUsrInteractions(self.parameters, authors, currentIndex, snapshotEnd)
                self.addInCounter(interactions)
                currentIndex = currentIndex + 1
        return self.pingPongs


    def countUsrInteractions(self, parameters, authors, startIndex):
        interactions = 1
        searchedAuthor = 1
        deltaT = int(parameters.getTimeWindowLength())
        log = parameters.getLog()
        startTime = int(log[startIndex][3])
        currentIndex = startIndex + 1
        while currentIndex < len(log):
            currentTime = int(log[currentIndex][3])
            src = log[currentIndex][0]
            dest = log[currentIndex][1]
            if currentTime - startTime > deltaT:
                return interactions
            if src == authors[(searchedAuthor + 1) % 2] and dest == authors[searchedAuthor]: #inizio di un altro motif
                return interactions
            if src == authors[searchedAuthor] and dest == authors[(searchedAuthor + 1) % 2]:
                interactions = interactions + 1
                searchedAuthor = (searchedAuthor + 1) % 2
            currentIndex = currentIndex + 1
        return interactions

    def snap_countUsrInteractions(self, parameters, authors, startIndex, snapshotEnd):
        interactions = 1
        searchedAuthor = 1
        log = parameters.getLog()
        currentIndex = startIndex + 1
        while currentIndex < len(log):
            currentTime = int(log[currentIndex][3])
            src = log[currentIndex][0]
            dest = log[currentIndex][1]
            if currentTime >= snapshotEnd:
                return interactions
            else:
                if src == authors[(searchedAuthor + 1) % 2] and dest == authors[searchedAuthor]:  # inizio di un altro motif
                    return interactions
                if src == authors[searchedAuthor] and dest == authors[(searchedAuthor + 1) % 2]:
                    interactions = interactions + 1
                    searchedAuthor = (searchedAuthor + 1) % 2
                currentIndex = currentIndex + 1
        return interactions





    #interazioni (in risposte) tra autore di un post e di un commento
    #posso usarla anche per gli snap motif, perchè il discorso temporale è già sistemato
    #post, commenti e risposte stanno di sicuro nella finestra
    #lo stesso vale per le funzioni successive
    def countPCInteractions(self, repliesList, authors):
        interactions = 1
        searchedAuthor = 0
        for r in repliesList:
            replyAuthor = r[3]
            if replyAuthor == authors[(searchedAuthor + 1) % 2]:
                return interactions
            if(replyAuthor == authors[searchedAuthor]):
                interactions = interactions + 1
                searchedAuthor = (searchedAuthor + 1) % 2
        return interactions

    def countRInteractions(self, repliesList, authors, nextReply):
        interactions = 1
        searchedAuthor = 0
        for r in range(nextReply, len(repliesList)):
            reply = repliesList[r]
            replyAuthor = reply[3]
            if replyAuthor == authors[(searchedAuthor + 1) % 2]:
                return interactions
            if(replyAuthor == authors[searchedAuthor]):
                interactions = interactions + 1
                searchedAuthor = (searchedAuthor + 1) % 2
        return interactions

    def addInCounter(self, interactionsNumber):
        if interactionsNumber % 2 == 0:
            pingPongLength = interactionsNumber
        else:
            pingPongLength = interactionsNumber - 1
        for i in range(pingPongLength, 0, -2):
            if i not in list(self.pingPongs):
                self.pingPongs[i] = 1
            else:
                self.pingPongs[i] = self.pingPongs[i] + 1




