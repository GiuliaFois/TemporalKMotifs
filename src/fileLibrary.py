import sys, csv, time

def createFileLog(fileToRead):
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

def createGroupList(fileLog):
    fileRows = []
    for l in fileLog:  # l contains a line of the file
        splittedRow = l.split(",")  # splittedRow[i] contains the i-th field of the corresponding line
        # each line is transformed in a tuple
        rowTup = (splittedRow[0], int(splittedRow[1]), splittedRow[2], splittedRow[3])
        if splittedRow[0] != "P":  # posts don't have the fourth field (containing the targetID)
            rowTup = rowTup + (splittedRow[4],)
        fileRows.append(rowTup)
    return fileRows

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

def usrFileNameParser(fileName):
    fileNameToks = fileName.split("_")
    fileCategory = fileNameToks[3]
    groupNumber = (fileNameToks[4].split("."))[0]
    return (fileCategory, groupNumber)

def printResults(resultsFilePath, resultsTuples, header):
    """
    Writes all the results collected by the program in a file
    :param resultsFilePath: The file where the results need to be written
    :param resultsTuples: A list of tuples containing all the results
    """
    try:
        with open(resultsFilePath, 'w', newline='') as resultsFile:
            resultsWriter = csv.writer(resultsFile)
            resultsWriter.writerow(header)
            resultsWriter.writerows(resultsTuples)
            #resultsWriter.writerow(resultsTuples)
    except IOError:
        print("Error when opening the file")
        sys.exit()

def removeIfBackslashN(stringToCheck):
    stringLen = len(stringToCheck) - 1
    if stringToCheck[stringLen] == '\n':
        return stringToCheck[:stringLen]
    else: return stringToCheck