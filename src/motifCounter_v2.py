import argparse, csv, os, time, sys
from fileLibrary import usrFileNameParser, removeIfBackslashN
from parameters import Parameters
from chainCounter import ChainCounter
from pingPongCounter import PingPongCounter
from inStarsCounter import InStarsCounter
from outStarsCounter import OutStarsCounter
from PTriangleCounter import PTriangleCounter
from oneWayCoupleCounter import OneWayCoupleCounter


# a four-level dictionary:
# the first-level dictionary has the values of k as keys and the second-level dictionaries as values
# the second-level dictionaries have the time windows as keys and the third-level dictionaries as values
# the third-level dictionaries have the group metadata as keys and the fourth-level dictionaries as values
# the fourth-level dictionaries have the motif types as keys and the number of motifs of that type counted
# within a specific file and with specific k and time window
# Overall, this dictionary will contain all the results collected by the counters
postResults = {}
usrResults = {}
snap_postResults = {}
snap_usrResults = {}
timeWindows = {}

def createFileList(fileToRead):
    """
    Creates a list of all the data tuples contained in the file
    :param fileToRead: the file from which the tuples are extracted
    :return: a list of the data tuples
    """
    try:
        with open(fileToRead, 'r') as fileStream:
            fileList = [l for l in fileStream]
            fileList.pop(0)  # the first line contains a header for the file, not useful
            return fileList
    except IOError:
        print("Error when opening the file")
        sys.exit()

def fileNameParser(fileName):
    """
    Does the parsing of a file name in two parts: the category of the group and the group number
    :param fileName: the file name that is associated with a file that contains a Facebook group's data
    :return: a tuple containing the category of the group and the group number
    """
    fileNameToks = fileName.split("_")
    fileCategory = fileNameToks[1]
    groupNumber = (fileNameToks[2].split("."))[0]
    return (fileCategory, groupNumber)

def resultsUpdater(update, motifType, fileName, motifResults):
    """
    Adds a new stat in the results dictionary
    :param update: the new result to add. Consists in a tuple containing the time window associated with the result and
                   a hash table where the keys are different values of k and the values are the number of motifs found
                   for each one of them
    :param motifType: the type of motif the new result refers to
    :param fileName: the name of the file from which the new result is retrieved
    """
    results = update[1]
    timeWindow = update[0]
    #print("Lista: " + str(list(motifResults[fileName])))
    #time.sleep(1)
    for key in list(results):
        if not (key in list(motifResults[fileName][timeWindow])):
            motifResults[fileName][timeWindow][key] = {}
            motifResults[fileName][timeWindow][key]["Chains"] = 0
            motifResults[fileName][timeWindow][key]["PingPongs"] = 0
            motifResults[fileName][timeWindow][key]["In-Stars"] = 0
            motifResults[fileName][timeWindow][key]["Out-Stars"] = 0
            motifResults[fileName][timeWindow][key]["P-Triangles"] = 0
            motifResults[fileName][timeWindow][key]["One-Way-Couples"] = 0
        motifResults[fileName][timeWindow][key][motifType] = motifResults[fileName][timeWindow][key][motifType] + results[key]

def resultTuplesCreator(motifResults):
    """
    Creates a list of tuples containing all the results collected by the program
    :return: The list of tuples containing all the results collected by the program
    """
    resultTuples = []
    for f in list(motifResults):
        for tw in list(motifResults[f]):
            parsedFileKey = f.split("_")
            category = parsedFileKey[0]
            number = parsedFileKey[1]
            for k in sorted(list(motifResults[f][tw])):
                chainsNumber = motifResults[f][tw][k]["Chains"]
                pingPongNumber = motifResults[f][tw][k]["PingPongs"]
                inStarsNumber = motifResults[f][tw][k]["In-Stars"]
                outStarsNumber = motifResults[f][tw][k]["Out-Stars"]
                pTrianglesNumber = motifResults[f][tw][k]["P-Triangles"]
                oneWayCouplesNumber = motifResults[f][tw][k]["One-Way-Couples"]
                resultTuples.append((category, number, tw, k, chainsNumber,
                                     pingPongNumber, inStarsNumber, outStarsNumber, oneWayCouplesNumber, pTrianglesNumber))
    return resultTuples

def printResults(resultsFilePath, resultsTuples):
    """
    Writes all the results collected by the program in a file
    :param resultsFilePath: The file where the results need to be written
    :param resultsTuples: A list of tuples containing all the results
    """
    try:
        with open(resultsFilePath, 'w', newline='') as resultsFile:
            resultsWriter = csv.writer(resultsFile)
            header = ("Group Type", "Group Number", "Time Window", "k", "Chains", "Ping pongs",
                      "In-stars", "Out-stars", "One-Way-Couples", "P-Triangles")
            resultsWriter.writerow(header)
            resultsWriter.writerows(resultsTuples)
    except IOError:
        print("Error when opening the file")
        sys.exit()

print("Program started")

# parsing of command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--tf', type=str, dest='timeWindowFile', help='the directory which contains all the time window parameters')
#FARE TUTTO IN UN'ALTRA DIR
parser.add_argument('--rd', type=str, dest='resultsDir', help='the directory which will contain all the collected results')
parser.add_argument('--sd', type=str, dest='snap_resultsDir', help='the directory which will contain all the collected results'
                                                                   'for the snapshot approach')
parser.add_argument('--pd', type=str, dest='postDatasetDir', help='the directory which contains the ordered groups\' data (post centered)')
parser.add_argument('--ud', type=str, dest='usrDatasetDir', help='the directory which contains the ordered groups\' data (usr centered)')
arguments = parser.parse_args()
twFile = arguments.timeWindowFile
postDir = arguments.postDatasetDir
usrDir = arguments.usrDatasetDir
resDir = arguments.resultsDir
snap_resDir = arguments.snap_resultsDir

#per ogni file (nelle due cartelle) conto tutti i motifs
for fileName in os.listdir(postDir):
    parsedFileName = fileNameParser(fileName)
    newKey = parsedFileName[0] + "_" + parsedFileName[1]
    timeWindows[newKey] = []
    postResults[newKey] = {}
    usrResults[newKey] = {}
    snap_postResults[newKey] = {}
    snap_usrResults[newKey] = {}

timeWindowRows = createFileList(twFile)
for row in timeWindowRows:
    rowValues = row.split(",")
    rowFile = rowValues[0]
    for field in range(1,4):
        newTimeWindow = removeIfBackslashN(rowValues[field])
        timeWindows[rowFile].append(newTimeWindow)
        postResults[rowFile][newTimeWindow] = {}
        usrResults[rowFile][newTimeWindow] = {}
        snap_postResults[rowFile][newTimeWindow] = {}
        snap_usrResults[rowFile][newTimeWindow] = {}

print("FASE 1: POST")
for postFile in os.listdir(postDir):
    print("Analisi del file: " + postFile)
    parsedFileName = fileNameParser(postFile)
    keyName = parsedFileName[0] + "_" + parsedFileName[1]
    fileTimeWindowsList = timeWindows[keyName]
    fileLog = createFileList(postDir + "/" + postFile)
    fileRows = []
    for l in fileLog:  # l contains a line of the file
        splittedRow = l.split(",")  # splittedRow[i] contains the i-th field of the corresponding line
        # each line is transformed in a tuple
        rowTup = (splittedRow[0], splittedRow[1], splittedRow[2], splittedRow[3])
        if splittedRow[0] != "P":  # posts don't have the fourth field (containing the targetID)
            rowTup = rowTup + (splittedRow[4],)
        fileRows.append(rowTup)

    for tw in fileTimeWindowsList:
        print("Analisi della time window: " + str(tw))
        #cerco tutti i motifs

        # the motif counter objects are constructed with the time window and the group events list as parameters
        parameters = Parameters(tw, fileRows)
        chainCounterObj = ChainCounter(parameters)
        pingPongObj = PingPongCounter(parameters)
        inStarObj = InStarsCounter(parameters)
        outStarObj = OutStarsCounter(parameters)
        pTriObj = PTriangleCounter(parameters)
        oneWayCoObj = OneWayCoupleCounter(parameters)

        # creating results for this time window and this file
        resultsUpdater((tw, chainCounterObj.countMotif()), "Chains", keyName, postResults)
        resultsUpdater((tw, pingPongObj.countMotif()), "PingPongs", keyName, postResults)
        resultsUpdater((tw, inStarObj.countMotif()), "In-Stars", keyName, postResults)
        resultsUpdater((tw, outStarObj.countMotif()), "Out-Stars", keyName, postResults)
        resultsUpdater((tw, pTriObj.countMotif()), "P-Triangles", keyName, postResults)
        resultsUpdater((tw, oneWayCoObj.countMotif()), "One-Way-Couples", keyName, postResults)
        print("Motif trovati per time window " + str(tw))
postResultsFile = resDir + "/postResults_v2.csv"
printResults(postResultsFile, resultTuplesCreator(postResults))


print("FASE 2: UTENTI")
for usrFile in os.listdir(usrDir):
    print("Analisi del file: " + usrFile)
    parsedFileName = usrFileNameParser(usrFile)
    keyName = parsedFileName[0] + "_" + parsedFileName[1]
    fileTimeWindowsList = timeWindows[keyName]

    fileLog = createFileList(usrDir + "/" + usrFile)
    fileRows = []
    for l in fileLog:  # l contains a line of the file
        splittedRow = l.split(",")  # splittedRow[i] contains the i-th field of the corresponding line
        # each line is transformed in a tuple
        rowTup = (splittedRow[0], splittedRow[1], splittedRow[2], splittedRow[3])
        fileRows.append(rowTup)
    for tw in fileTimeWindowsList:
        print("Analisi della time window: " + str(tw))
        #cerco tutti i motifs


        # the motif counter objects are constructed with the time window and the group events list as parameters
        parameters = Parameters(tw, fileRows)
        chainCounterObj = ChainCounter(parameters)
        pingPongObj = PingPongCounter(parameters)
        inStarObj = InStarsCounter(parameters)
        outStarObj = OutStarsCounter(parameters)
        pTriObj = PTriangleCounter(parameters)
        oneWayCoObj = OneWayCoupleCounter(parameters)

        # creating results for this time window and this file
        resultsUpdater((tw, chainCounterObj.countUsrMotif()), "Chains", keyName, usrResults)
        resultsUpdater((tw, pingPongObj.countUsrMotif()), "PingPongs", keyName, usrResults)
        resultsUpdater((tw, inStarObj.countUsrMotif()), "In-Stars", keyName, usrResults)
        resultsUpdater((tw, outStarObj.countUsrMotif()), "Out-Stars", keyName, usrResults)
        resultsUpdater((tw, oneWayCoObj.countUsrMotif()), "One-Way-Couples", keyName, usrResults)
        #resultsUpdater((tw, pTriObj.countMotif()), "P-Triangles", parsedFileName, usrResults)
        print("Motif trovati per time window " + str(tw))

usrResultsFile = resDir + "/usrResults_v2.csv"
printResults(usrResultsFile, resultTuplesCreator(usrResults))


print("FASE 3: POST SNAP")
for postFile in os.listdir(postDir):
    print("Analisi del file: " + postFile)
    parsedFileName = fileNameParser(postFile)
    keyName = parsedFileName[0] + "_" + parsedFileName[1]
    fileTimeWindowsList = timeWindows[keyName]
    fileLog = createFileList(postDir + "/" + postFile)
    fileRows = []
    for l in fileLog:  # l contains a line of the file
        splittedRow = l.split(",")  # splittedRow[i] contains the i-th field of the corresponding line
        # each line is transformed in a tuple
        rowTup = (splittedRow[0], splittedRow[1], splittedRow[2], splittedRow[3])
        if splittedRow[0] != "P":  # posts don't have the fourth field (containing the targetID)
            rowTup = rowTup + (splittedRow[4],)
        fileRows.append(rowTup)

    for tw in fileTimeWindowsList:
        print("Analisi della time window: " + str(tw))
        #cerco tutti i motifs

        # the motif counter objects are constructed with the time window and the group events list as parameters
        parameters = Parameters(tw, fileRows)
        chainCounterObj = ChainCounter(parameters)
        pingPongObj = PingPongCounter(parameters)
        inStarObj = InStarsCounter(parameters)
        outStarObj = OutStarsCounter(parameters)
        pTriObj = PTriangleCounter(parameters)
        oneWayCoObj = OneWayCoupleCounter(parameters)

        # creating results for this time window and this file
        resultsUpdater((tw, chainCounterObj.snap_countMotif()), "Chains", keyName, snap_postResults)
        resultsUpdater((tw, pingPongObj.snap_countMotif()), "PingPongs", keyName, snap_postResults)
        resultsUpdater((tw, inStarObj.snap_countMotif()), "In-Stars", keyName, snap_postResults)
        resultsUpdater((tw, outStarObj.snap_countMotif()), "Out-Stars", keyName, snap_postResults)
        resultsUpdater((tw, pTriObj.snap_countMotif()), "P-Triangles", keyName, snap_postResults)
        resultsUpdater((tw, oneWayCoObj.snap_countMotif()), "One-Way-Couples", keyName, snap_postResults)
        print("Motif trovati per time window " + str(tw))
postResultsFile = snap_resDir + "/snap_postResults_v2.csv"
printResults(postResultsFile, resultTuplesCreator(snap_postResults))

print("FASE 2: UTENTI")
for usrFile in os.listdir(usrDir):
    print("Analisi del file: " + usrFile)
    parsedFileName = usrFileNameParser(usrFile)
    keyName = parsedFileName[0] + "_" + parsedFileName[1]
    fileTimeWindowsList = timeWindows[keyName]

    fileLog = createFileList(usrDir + "/" + usrFile)
    fileRows = []
    for l in fileLog:  # l contains a line of the file
        splittedRow = l.split(",")  # splittedRow[i] contains the i-th field of the corresponding line
        # each line is transformed in a tuple
        rowTup = (splittedRow[0], splittedRow[1], splittedRow[2], splittedRow[3])
        fileRows.append(rowTup)
    for tw in fileTimeWindowsList:
        print("Analisi della time window: " + str(tw))
        #cerco tutti i motifs


        # the motif counter objects are constructed with the time window and the group events list as parameters
        parameters = Parameters(tw, fileRows)
        chainCounterObj = ChainCounter(parameters)
        pingPongObj = PingPongCounter(parameters)
        inStarObj = InStarsCounter(parameters)
        outStarObj = OutStarsCounter(parameters)
        pTriObj = PTriangleCounter(parameters)
        oneWayCoObj = OneWayCoupleCounter(parameters)

        # creating results for this time window and this file
        resultsUpdater((tw, chainCounterObj.snap_countUsrMotif()), "Chains", keyName, snap_usrResults)
        resultsUpdater((tw, pingPongObj.snap_countUsrMotif()), "PingPongs", keyName, snap_usrResults)
        resultsUpdater((tw, inStarObj.snap_countUsrMotif()), "In-Stars", keyName, snap_usrResults)
        resultsUpdater((tw, outStarObj.snap_countUsrMotif()), "Out-Stars", keyName, snap_usrResults)
        resultsUpdater((tw, oneWayCoObj.snap_countUsrMotif()), "One-Way-Couples", keyName, snap_usrResults)
        #resultsUpdater((tw, pTriObj.countMotif()), "P-Triangles", parsedFileName, snap_usrResults)
        print("Motif trovati per time window " + str(tw))

usrResultsFile = snap_resDir + "/snap_usrResults_v2.csv"
printResults(usrResultsFile, resultTuplesCreator(snap_usrResults))
