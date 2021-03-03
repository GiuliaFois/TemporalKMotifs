import csv
import sys


def createLog(postsFile,commentsRepliesFile, targetFile):
    """
    :param postsFile: file containing the list of the group's posts
    :param commentsRepliesFile: file containing a list of the group's comments and replies
    :return: a list containing the posts and the comments temporally sorted
    """

    postsAndComments = []

    try:
        with open(postsFile, 'r') as postsFile:
            postsLines = [l for l in postsFile]
    except IOError:
        print("Error when opening the posts file")
        sys.exit()

    try:
        with open(commentsRepliesFile, 'r') as commentsFile:
            commentsLines = [l for l in commentsFile]
    except IOError:
        print("Error when opening the comments file")
        sys.exit()

    for l in postsLines:
        # storing each post in a tuple t containing: type, timestamp, postID, post author
        # I added the type "P" to later differentiate posts from comments and replies
        tuple = ("P", l.split(",")[2], l.split(",")[1], l.split(",")[0])
        if tuple[1].isnumeric(): # this way I don't consider the first line of the file
            postsAndComments.append(tuple)

    for l in commentsLines:
        # storing each comment/reply in a tuple t containing: type, timestamp, comment/replyID, comment/reply author, targetID
        # comments and replies have one additional field  (targetID) compared to posts
        tuple = (l.split(",")[3], l.split(",")[2], l.split(",")[0], l.split(",")[1], l.split(",")[4])
        if tuple[1].isnumeric():
            postsAndComments.append(tuple)

    # sorting of the list
    postsAndComments.sort(key=lambda tup: tup[1])

    # storing the ordered list in a file
    with open(targetFile, 'w', newline='') as target:
        tuplesWriter = csv.writer(target)
        header = ("type", "timestamp", "ID", "author", "targetID (for C and R)")
        tuplesWriter.writerow(header)
        tuplesWriter.writerows(postsAndComments)
        target.close()

    return postsAndComments

def countCommentChains(list, timeWindowLen, k, startIndex):
    """
    :param list: the list containing the temporally sorted posts and comments
    :param timeWindowLen: the length of the time window (in seconds)
    :param k: k >= 0 -> to count chains of size k in the time window
              k < 0 -> to search the maximum chain length in the time window
              the original k is decremented by the caller functions
    :param startIndex: the start index to scan the list
    :return: k > 1 -> the number of chains of size k made by replies to a target comment
             k = 0 -> the maximum length of the chain made by replies to a target comment
    """
    targetID = list[startIndex][2] # the ID of this comment
    # chain length: k-1 (replies to this comment) + 1 (the comment)
    motifCounter = countReplyChains(list, timeWindowLen, k-1, startIndex, targetID)
    return motifCounter

def countReplyChains(list, timeWindowLen, k, startIndex, targetID):
    """
    :param list: the list containing the temporally sorted posts and comments
    :param timeWindowLen: the length of the time window (in seconds)
    :param k: k >= 0 -> to count chains of size k in the time window
              k < 0 -> to search the maximum chain length in the time window
              the original k is decremented by the caller functions
    :param startIndex: the start index to scan the list
    :param targetID: the targetID of the replies that form the chain
    :return: k > 1 -> the number of chains of size k made by replies to a target comment
             k = 0 -> the maximum length of the chain made by replies to a target comment
    """
    i = startIndex + 1
    motifCounter = 0
    startTime = int(list[startIndex][1])
    if(i < len(list)):
        currTime = int(list[i][1]) # timestamp of the line we are analyzing
    currLen = 0 # current length of the chain
    while (i < len(list)) and (currTime - startTime <= timeWindowLen):
        if (k < 0) and (list[i][0] == "R") and (list[i][4] == targetID):
            currLen = currLen + 1
        elif (currLen == k):
            motifCounter = motifCounter + 1
            break
        elif (list[i][0] == "R") and (list[i][4] == targetID):
            currLen = currLen + 1
        i = i + 1
        if( i < len(list)):
            currTime = int(list[i][1])
    if k < 0:
        return currLen + (0 - k) # k is decremented by the caller
    else:
        return motifCounter

def countChains(list,timeWindowLen,k):
    """

    :param list: the list containing the temporally sorted posts and comments
    :param timeWindowLen: the length of the time window (in seconds)
    :param k: k > 1 -> to count chains of size k in the time window
              k = 0 -> to search the maximum chain length in the time window
    :return:  k > 1 -> the number of chains of size k
              k = 0 -> a tuple (m,n)
                       m: the maximum chain length
                       n: the number of chains of length m
    """
    if k == 1: # the chain has to be at least of length 2
        return -2
    i = 0
    j = 0
    chainCounter = 0 # counter of chains of len k (only if k > 1)
    maxLen = 0 # max len of chains (only if k = 0)
    maxLenCounter = 0 # counter of chains with max len (only if k = 0)
    while(i < len(list)) and (j + 1 < len(list)):
        j = i + 1
        type = list[i][0]
        startTime = int(list[i][1]) # timestamp of the event i in the list (plausible start of a chain)
        currTime = int(list[j][1])  # timestamp of the event j in the list (j = i + 1)
        startID = list[i][2] # ID of the event i in the list
        # temporary return value
        # k = 0: it stores the temporal maximum length found in each iteration
        # k > 1: it stores the temporal number of motifs of len k found in each iteration
        tempValue = 0
        tempMaxLen = 0 # temporary maximum length found in each iteration
        if type == "P":
            # saving of all the comments referred to this post
            comments = [] # it will contain the comments' data and their index in list
            m = j
            while (m < len(list)) and (currTime - startTime <= timeWindowLen):
                if (list[m][0] == "C") and (list[m][4] == startID):
                    index = (m,)
                    t = list[m] + index
                    comments.append(t)
                m = m + 1
                if(m < len(list)):
                    currTime = int(list[m][1])
            for c in comments:
                comment = c
                commentIndex = comment[5]
                # chain length: k-1 (comment and its replies) + 1 (the post)
                tempCommentValue = countCommentChains(list, timeWindowLen, k-1, commentIndex)
                # it finds the longest chain originated from a comment to this post
                if (k == 0) and (tempMaxLen < tempCommentValue):
                    tempMaxLen = tempCommentValue
                else:
                    tempValue = tempValue + tempCommentValue
        elif type == "C":
            tempValue = countCommentChains(list, timeWindowLen, k, i)
        elif type == "R":
            targetID = list[i][4] # comment target of this reply (only replies to the same comment can form a chain)
            # chain length: k-1 (other replies to the same comment) + 1 (the reply)
            tempValue = countReplyChains(list, timeWindowLen, k-1, i, targetID)
        if k > 0:
            chainCounter = chainCounter + tempValue
        elif (k == 0):
            if type == "P":
                tempValue = tempMaxLen # in the posts branch the maxLen of this iteration is stored in tempMaxLen
            if maxLen == tempValue: # motif of max length found
                maxLenCounter = maxLenCounter + 1
            elif tempValue > maxLen: # new max length
                maxLen = tempValue
                maxLenCounter = 1
        i = i + 1
    if k > 0:
        return chainCounter
    else:
        t = (maxLen, maxLenCounter)
        return t



