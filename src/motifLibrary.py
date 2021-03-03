import time

def searchComments(parameters, targetIndex):
    comments = []
    log = parameters.getLog()
    deltaT = int(parameters.getTimeWindowLength())
    logLength = len(log)
    targetID = log[targetIndex][2]
    targetTime = int(log[targetIndex][1])
    currentIndex = targetIndex + 1
    while (currentIndex < logLength):
        currentEntry = log[currentIndex]
        currentTime = int(currentEntry[1])
        if(currentTime - targetTime > deltaT):
            return comments
        elif(currentTime - targetTime <= deltaT):
            if (currentEntry[0] == "C") and (int(currentEntry[4]) == int(targetID)):
                commentTuple = log[currentIndex] + (currentIndex,)
                comments.append(commentTuple)
        currentIndex = currentIndex + 1
    return comments

def snap_searchComments(parameters, targetIndex, snapshotEnd):
    comments = []
    log = parameters.getLog()
    logLength = len(log)
    targetID = log[targetIndex][2]
    currentIndex = targetIndex + 1
    while (currentIndex < logLength):
        currentEntry = log[currentIndex]
        currentTime = int(currentEntry[1])
        if currentTime >= snapshotEnd:
            return comments
        else:
            if (currentEntry[0] == "C") and (int(currentEntry[4]) == int(targetID)):
                commentTuple = log[currentIndex] + (currentIndex,)
                comments.append(commentTuple)
            currentIndex = currentIndex + 1
    return comments


def searchReplies(parameters, targetIndex):
    replies = []
    log = parameters.getLog()
    deltaT = int(parameters.getTimeWindowLength())
    targetID = int(log[targetIndex][2])
    logLength = len(log)
    targetTime = int(log[targetIndex][1])
    currentIndex = targetIndex + 1
    while (currentIndex < logLength):
        currentEntry = log[currentIndex]
        currentTime = int(currentEntry[1])
        if(currentTime - targetTime > deltaT):
            return replies
        elif(currentTime - targetTime <= deltaT):
            if (currentEntry[0] == "R") and (int(currentEntry[4]) == targetID):
                replyTuple = log[currentIndex] + (currentIndex,)
                replies.append(replyTuple)
        currentIndex = currentIndex + 1
    return replies

def snap_searchReplies(parameters, targetIndex, snapshotEnd):
    replies = []
    log = parameters.getLog()
    targetID = int(log[targetIndex][2])
    logLength = len(log)
    currentIndex = targetIndex + 1
    while (currentIndex < logLength):
        currentEntry = log[currentIndex]
        currentTime = int(currentEntry[1])
        if(currentTime >= snapshotEnd):
            return replies
        else:
            if (currentEntry[0] == "R") and (int(currentEntry[4]) == targetID):
                replyTuple = log[currentIndex] + (currentIndex,)
                replies.append(replyTuple)
        currentIndex = currentIndex + 1
    return replies






def indexOfEntry(parameters, targetID, startIndex):
    log = parameters.getLog()
    returnedIndex = 0
    for i in range(startIndex, -1, -1):
        plausibleElement = log[i]
        plausibleID = plausibleElement[2]
        if(int(plausibleID) == int(targetID)):
            returnedIndex = i
            break
    return returnedIndex


def findUsrChains(parameters, startIndex, startTime, neededAuthor, chainAuthors):
    log = parameters.getLog()
    deltaT = int(parameters.getTimeWindowLength())
    returnedEntries = []
    chainAuthors.append(log[startIndex][0])
    for entry in range(startIndex + 1, len(log)):
        currentTime = int(log[entry][3])
        if currentTime - startTime > deltaT:
            break
        currentAuthor = log[entry][0]
        currentDest = log[entry][1]
        if (currentAuthor == neededAuthor) and not chainAuthors.__contains__(currentDest):
            returnedEntries = returnedEntries + findUsrChains(parameters, entry, startTime, currentDest, chainAuthors)
    if len(returnedEntries) == 0:
        return [1]
    else:
        for entry in range(0, len(returnedEntries)):
            returnedEntries[entry] = returnedEntries[entry] + 1
        return returnedEntries

def snap_findUsrChains(parameters, startIndex, endSnapshot, neededAuthor, chainAuthors):
    log = parameters.getLog()
    returnedEntries = []
    chainAuthors.append(log[startIndex][0])
    for entry in range(startIndex + 1, len(log)):
        currentTime = int(log[entry][3])
        if currentTime >= endSnapshot:
            break
        currentAuthor = log[entry][0]
        currentDest = log[entry][1]
        if (currentAuthor == neededAuthor) and not chainAuthors.__contains__(currentDest):
            returnedEntries = returnedEntries + snap_findUsrChains(parameters, entry, endSnapshot, currentDest, chainAuthors)
    if len(returnedEntries) == 0:
        return [1]
    else:
        for entry in range(0, len(returnedEntries)):
            returnedEntries[entry] = returnedEntries[entry] + 1
        return returnedEntries


def usrCountByAuthor(parameters, startIndex):
    log = parameters.getLog()
    author = log[startIndex][0]
    destSet = set()
    destSet = destSet | {log[startIndex][1]}
    startTime = int(log[startIndex][3])
    deltaT = int(parameters.getTimeWindowLength())
    targetScanIndex = startIndex + 1
    while targetScanIndex < len(log):
        currentAuth = log[targetScanIndex][0]
        currentDest = log[targetScanIndex][1]
        currentTime = int(log[targetScanIndex][3])
        if currentTime - startTime > deltaT:
            return len(destSet)
        elif currentAuth == author:
            destSet = destSet | {currentDest}
        targetScanIndex = targetScanIndex + 1
    return len(destSet)

def snap_usrCountByAuthor(parameters, startIndex, snapshotEnd):
    log = parameters.getLog()
    author = log[startIndex][0]
    destSet = set()
    destSet = destSet | {log[startIndex][1]}
    targetScanIndex = startIndex + 1
    while targetScanIndex < len(log):
        currentAuth = log[targetScanIndex][0]
        currentDest = log[targetScanIndex][1]
        currentTime = int(log[targetScanIndex][3])
        if currentTime >= snapshotEnd:
            return  len(destSet)
        elif currentAuth == author:
            destSet = destSet | {currentDest}
        targetScanIndex = targetScanIndex + 1
    return len(destSet)




def usrCountByDest(parameters, startIndex):
    log = parameters.getLog()
    dest = log[startIndex][1]
    authorSet = set()
    authorSet = authorSet | {log[startIndex][0]}
    startTime = int(log[startIndex][3])
    deltaT = int(parameters.getTimeWindowLength())
    targetScanIndex = startIndex + 1
    while targetScanIndex < len(log):
        currentAuth = log[targetScanIndex][0]
        currentDest = log[targetScanIndex][1]
        currentTime = int(log[targetScanIndex][3])
        if currentTime - startTime > deltaT:
            return len(authorSet)
        elif currentDest == dest:
            authorSet = authorSet | {currentAuth}
        targetScanIndex = targetScanIndex + 1
    return len(authorSet)

def snap_usrCountByDest(parameters, startIndex, snapshotEnd):
    log = parameters.getLog()
    dest = log[startIndex][1]
    authorSet = set()
    authorSet = authorSet | {log[startIndex][0]}
    targetScanIndex = startIndex + 1
    while targetScanIndex < len(log):
        currentAuth = log[targetScanIndex][0]
        currentDest = log[targetScanIndex][1]
        currentTime = int(log[targetScanIndex][3])
        if currentTime >= snapshotEnd:
            return len(authorSet)
        elif currentDest == dest:
            authorSet = authorSet | {currentAuth}
        targetScanIndex = targetScanIndex + 1
    return len(authorSet)


def countByAuthor(parameters, currentIndex, startType): #post count by author
    log = parameters.getLog()
    author = log[currentIndex][3]
    targetsSet = set()
    targetsSet = targetsSet | {int(log[currentIndex][4])}
    startTime = int(log[currentIndex][1])
    deltaT = int(parameters.getTimeWindowLength())
    targetScanIndex = currentIndex + 1
    while(targetScanIndex < len(log)):
        type = log[targetScanIndex][0]
        entryAuth = log[targetScanIndex][3]
        currentTime = int(log[targetScanIndex][1])
        if(currentTime - startTime > deltaT):
            return len(targetsSet)
        elif (type == startType) and (entryAuth == author):
            target = int(log[targetScanIndex][4])
            targetsSet = targetsSet | {target}
        targetScanIndex = targetScanIndex + 1
    return len(targetsSet)

def snap_countByAuthor(parameters, currentIndex, startType, snapshotEnd):
    log = parameters.getLog()
    author = log[currentIndex][3]
    targetsSet = set()
    targetsSet = targetsSet | {int(log[currentIndex][4])}
    targetScanIndex = currentIndex + 1
    while targetScanIndex < len(log):
        type = log[targetScanIndex][0]
        entryAuth = log[targetScanIndex][3]
        currentTime = int(log[targetScanIndex][1])
        if currentTime >= snapshotEnd:
            return len(targetsSet)
        elif (type == startType) and (entryAuth == author):
            target = int(log[targetScanIndex][4])
            targetsSet = targetsSet | {target}
        targetScanIndex = targetScanIndex + 1
    return len(targetsSet)

