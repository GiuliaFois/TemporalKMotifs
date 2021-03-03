import argparse, sys, time
import matplotlib.pyplot as plt
import numpy as np
import fileLibrary

groupLabels = {}
groupLabels['Education_Group1'] = 'Edu1'
groupLabels['Education_Group2'] = 'Edu2'
groupLabels['Education_Group3'] = 'Edu3'
groupLabels['Entertainment_Group1'] = 'Ent1'
groupLabels['Entertainment_Group2'] = 'Ent2'
groupLabels['Entertainment_Group3'] = 'Ent3'
groupLabels['Entertainment_Group4'] = 'Ent4'
groupLabels['News_Group1'] = 'News1'
groupLabels['News_Group2'] = 'News2'
groupLabels['News_Group3'] = 'News3'
groupLabels['News_Group4'] = 'News4'
groupLabels['Sport_Group1'] = 'Sport1'
groupLabels['Sport_Group2'] = 'Sport2'
groupLabels['Sport_Group3'] = 'Sport3'
groupLabels['Sport_Group4'] = 'Sport4'
groupLabels['Work_Group1'] = 'Work1'
groupLabels['Work_Group2'] = 'Work2'
groupLabels['Work_Group3'] = 'Work3'
groupLabels['Work_Group4'] = 'Work4'

def makeDataList(dataset, maxIndex, saveGroups):
    groupNames = set() # names of the groups
    results = [] # result list
    for r in dataset: # iterating on the file lines

        # extraction of the line fields
        splittedRow = r.split(",")

        if saveGroups: # if saveGroups is 1 the groups' names are stored in a set
            currentGroupName = splittedRow[0] + "_" + splittedRow[1]
            groupNames = groupNames | {currentGroupName}

        # creation of the tuple that will contain all the line fields
        result = tuple()
        for i in range(0, maxIndex + 1):
            result = result + (splittedRow[i], )
        results.append(result)
    if saveGroups:
        return results, groupNames
    else:
        return results

def makeDiagramResults(baseResults, maxIndex):
    # structure that will contain the minimum common k values for each motif
    # the initialized fields' indexes correspond to each motif's index in the lines of the post/user results
    # each element in position i is a tuple (a, b): a is the minimum common k value for the motif in position i
    # in the file (initialized to a big integer for a successful comparison with smaller values), b is the minimum
    # k for each motif
    commonK = [(0, 0), (0, 0), (0, 0), (0, 0), [sys.maxsize, 3], [sys.maxsize, 1], [sys.maxsize, 3], [sys.maxsize, 3],
               [sys.maxsize, 1]]

    # temporary structure that will contain the minimum k values for each quartile
    tempValues = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    # all the values in commonK are updated when the quartile in the results changes
    prevQuartile = int(baseResults[0][2]) # first quartile encountered
    for l in baseResults:
        currentQuartile = int(l[2])
        currentK = int(l[3])

        if currentQuartile != prevQuartile: # new quartile: updating of commonK
            for i in range(4, maxIndex + 1):
                # commonK is updated only if a smaller value of k for the i-th motif is found
                if (tempValues[i] <= commonK[i][0]) and (tempValues[i] > 0):
                    commonK[i][0] = tempValues[i]
                tempValues[i] = 0

        for i in range(4, maxIndex + 1):
            motifMinLen = commonK[i][1]
            currentElem = int(l[i])
            # tempValues[i] contains the max value of k for each quartile. it needs to be greater than
            # the min value of k for the i-th motif and there needs to be at least 1 motif of that length
            if currentK >= motifMinLen and currentElem > 0:
                tempValues[i] = currentK
        prevQuartile = currentQuartile

    # update for the last quartile
    for i in range(4, maxIndex + 1):
        if (tempValues[i] <= commonK[i][0]) and (tempValues[i] > 0):
            commonK[i][0] = tempValues[i]

    # the min common k for each motif are stored in kValues
    kValues = {}
    kValues["Chains"] = commonK[4][0]
    kValues["Ping-Pongs"] = commonK[5][0]
    kValues["In-Stars"] = commonK[6][0]
    kValues["Out-Stars"] = commonK[7][0]
    kValues["P-Triangles"] = commonK[8][0]

    # diagramResults will contain, for each group and quartile, the number of motifs with length found above
    diagramResults = {}
    for l in baseResults:
        groupName = l[0] + "_" + l[1]
        quartile = l[2]
        currentK = str(l[3])
        # initialization of the hash table with each new group encountered
        if not (groupName in list(diagramResults)):
            diagramResults[groupName] = {}
        if not (quartile in list(diagramResults[groupName])):
            diagramResults[groupName][quartile] = {}
            diagramResults[groupName][quartile]["Chains"] = 0
            diagramResults[groupName][quartile]["Ping-Pongs"] = 0
            diagramResults[groupName][quartile]["In-Stars"] = 0
            diagramResults[groupName][quartile]["Out-Stars"] = 0
            diagramResults[groupName][quartile]["P-Triangles"] = 0

        # extraction from the dataset of the number of each motif with length calculated above
        for i in range(0, len(list(kValues))):
            currentKey = list(kValues)[i]
            if currentK == str(kValues[currentKey]):
                motifNumber = l[i + 4]
                diagramResults[groupName][quartile][currentKey] = int(motifNumber)

    return diagramResults, kValues


def showGroupDiagrams(diagramResults, kValues):
    label = ['First Quartile', 'Second Quartile', ' Third Quartile']
    for i in list(diagramResults):
        groupLabel = groupLabels[i]
        for k in list(kValues):
            quartileResults = []
            for j in list(diagramResults[i]):
                quartileResult = diagramResults[i][j][k]
                quartileResults.append(quartileResult)
            index = np.arange(len(label))
            x_pos = [0.4, 0.5, 0.6]
            fig = plt.figure()
            ax = fig.add_subplot(111)
            barlist = ax.bar(x_pos, quartileResults, align='center', width=0.1)
            barlist[0].set_color('red')
            barlist[1].set_color('blue')
            barlist[2].set_color('green')
            ax.set_ylim(bottom=0.)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(label, fontsize=10, rotation=12)
            ax.set_title(k + " with k = " + str(kValues[k]) + "\n" + "in " + groupLabel)
            plt.show()

def showQuartileDiagrams(diagramResults, kValues):
    label = ['Edu1', 'Edu2', 'Edu3', 'Ent1', 'Ent2', 'Ent3', 'Ent4', 'News1', 'News2',
                'News3', 'Sport1', 'Sport2', 'Sport3', 'Sport4', 'Work1', 'Work2', 'Work3', 'Work4']
    colors = ['xkcd:red','xkcd:blue','xkcd:green', 'xkcd:orange', 'xkcd:light blue', 'xkcd:teal', 'xkcd:magenta', 'xkcd:dark blue',
              'xkcd:forest green', 'xkcd:dark pink', 'xkcd:turquoise', 'xkcd:olive green', 'xkcd:dark red', 'xkcd:royal blue',
              'xkcd:neon green', 'xkcd:burnt orange', 'xkcd:bright blue', 'xkcd:yellowish green']
    quartiles = ['first', 'second', 'third']
    #per ogni gruppo: prendo il risultato per un determinato quartile per un determinato motif
    for k in list(kValues):
        for q in range(0, 3):
            quartileResults = []
            for g in sorted(list(diagramResults)):
                groupQuartiles = list(diagramResults[g])
                quartileIndex = groupQuartiles[q]
                newResult = diagramResults[g][quartileIndex][k]
                quartileResults.append(newResult)
            index = np.arange(len(label))
            fig = plt.figure()
            ax = fig.add_subplot(111)
            barlist = ax.bar(index, quartileResults, align='center', width=0.5)
            for i in range(0, len(barlist)):
                barlist[i].set_color(colors[i])
            ax.set_ylim(bottom=0.)
            ax.set_xticks(index)
            ax.set_xticklabels(sorted(label), fontsize=12, rotation=20)
            ax.set_title(k + " with k = " + str(kValues[k]) + "\n" + "in the " + quartiles[q] + " quartile")
            plt.show()

parser = argparse.ArgumentParser()
parser.add_argument('--pf', type=str, dest='postResultsFile', help='the file which contains the post-related results')
parser.add_argument('--uf', type=str, dest='usrResultsFile', help='the file which contains the user-related results')
arguments = parser.parse_args()
postFile = arguments.postResultsFile
usrFile = arguments.usrResultsFile

# extraction of data from the files
postResultsData = fileLibrary.createFileLog(postFile)
usrResultsData = fileLibrary.createFileLog(usrFile)

# creating two lists from the data extracted above
postResults, groupNames = makeDataList(postResultsData,8,1)
usrResults = makeDataList(usrResultsData,7,0)

# extracting the significant results for the bar diagrams
postDiagramResults, postKValues = makeDiagramResults(postResults, 8)
usrDiagramResults, usrKValues = makeDiagramResults(usrResults, 7)

# creation of group-diagrams
showGroupDiagrams(postDiagramResults, postKValues)
showGroupDiagrams(usrDiagramResults, usrKValues)

# creation of quartile-diagrams
showQuartileDiagrams(postDiagramResults, postKValues)
showQuartileDiagrams(usrDiagramResults, usrKValues)