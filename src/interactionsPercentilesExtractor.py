import fileLibrary
from interactionTimesCounters import UsrGroupIntervalsContainer, InteractionTimesCounters, GeneralResults
from groupsCharacteristicsLibrary import findMedianElement
import argparse, os, time, sys, math

def userGraphFileNameParser(fileName):
    fileNameToks = fileName.split("_")
    fileCategory = fileNameToks[3]
    groupNumber = (fileNameToks[4].split("."))[0]
    return (fileCategory, groupNumber)

def findMedianElement(start, end):
    nElem = end - start + 1
    if nElem % 2 == 1:
        return [int((nElem + 1) / 2) - 1]
    else:
        return [int(nElem / 2) - 1, int(nElem / 2)]

def retQuartVal(indexes, intervalsList):
    if len(indexes) == 1:
       return intervalsList[indexes[0]]
    else:
        return (intervalsList[indexes[0]] + intervalsList[indexes[1]]) / 2

def extractQuartileIndexes(intervalsList):
    medianElem = findMedianElement(0, len(intervalsList)-1)
    if len(medianElem) == 1:
        firstQuartElem = findMedianElement(0, medianElem[0] - 1)
        secondQuartElem = findMedianElement(medianElem[0] + 1, len(intervalsList)-1)
        if len(secondQuartElem) == 1:
            secondQuartElem[0] = secondQuartElem[0] + medianElem[0]
        else:
            secondQuartElem[0] = secondQuartElem[0] + medianElem[0]
            secondQuartElem[1] = secondQuartElem[1] + medianElem[0]
    else:
        firstQuartElem = findMedianElement(0, medianElem[0] - 1)
        secondQuartElem = findMedianElement(medianElem[1] + 1, len(intervalsList)-1)
        if len(secondQuartElem) == 1:
            secondQuartElem[0] = secondQuartElem[0] + medianElem[1]
        else:
            secondQuartElem[0] = secondQuartElem[0] + medianElem[1]
            secondQuartElem[1] = secondQuartElem[1] + medianElem[1]
    quartileIndexes = [firstQuartElem, medianElem, secondQuartElem]
    return quartileIndexes

parser = argparse.ArgumentParser()
parser.add_argument('-d', type=str, dest='datasetDir', help='the directory which contains the ordered groups\' data')
parser.add_argument('-r', type=str, dest='resultsFile', help='the file which will contain all the results')
parser.add_argument('--ld', type=str, dest='intervalsListsDir', help='the directory which will contain a file for '
                                                                     'each group, where all the interactions intervals'
                                                                     'are listed')
arguments = parser.parse_args()
datasetDir = arguments.datasetDir
resultsFile = arguments.resultsFile
intervalsListsDir = arguments.intervalsListsDir

dataset = []
results = []
fileHeader = ("IntervalsList", )
for usrGroupFile in os.listdir(datasetDir):
    print("Analisi del file: " + usrGroupFile)
    fileLog = fileLibrary.createFileLog(datasetDir + "/" + usrGroupFile)
    parsedFileName = userGraphFileNameParser(usrGroupFile)
    fileRows = []

    # extracting the group's data from the file
    for l in fileLog:
        splittedRow = l.split(",")
        rowTup = (splittedRow[0], splittedRow[1], splittedRow[2], fileLibrary.removeIfBackslashN(splittedRow[3]))
        fileRows.append(rowTup)

    # listing all the intervals between contiguous interactions
    intervalsList = []
    intervalsTuples = []
    for i in range(0, len(fileRows)-1):
        newInterval = int(fileRows[i + 1][3]) - int(fileRows[i][3])
        intervalsList.append(newInterval)
        intervalsTuples.append((newInterval,))

    # sorting of the intervals list
    intervalsList.sort(key = lambda t : t)
    intervalsTuples.sort(key = lambda t : t[0])

    # printing of the list on a file
    intervalsDest = intervalsListsDir + "/" + parsedFileName[0] + "_" + parsedFileName[1] + ".csv"
    #fileLibrary.printResults(intervalsDest, intervalsTuples, fileHeader)

    # extraction of the elements that represent the first, second and third quartile
    quartileIndexes = extractQuartileIndexes(intervalsList)
    firstQuartElem = retQuartVal(quartileIndexes[0], intervalsList)
    secondQuartElem = retQuartVal(quartileIndexes[1], intervalsList)
    thirdQuartElem = retQuartVal(quartileIndexes[2], intervalsList)
    newResult = (usrGroupFile, int(firstQuartElem), int(secondQuartElem), int(thirdQuartElem))
    results.append(newResult)

# printing of the quartile extracted for each file
header = ("Group", "First quartile", "Second quartile", "Third Quartile")
fileLibrary.printResults(resultsFile, results, header)


