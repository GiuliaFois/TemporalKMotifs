import argparse, os, math
import fileLibrary
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('-d', type=str, dest='intervalsDir', help='the directory which contains all the intervals for the CDF')
arguments = parser.parse_args()
intervalsDir = arguments.intervalsDir

def cdf(dataList, groupName):
    dataLen = len(dataList)

    dataSet = sorted(set(dataList))
    bins = np.append(dataSet, dataSet[-1]+1)

    counts, binEdges = np.histogram(dataList, bins=bins, density=False)

    counts = counts.astype(float) / dataLen
    cdf = np.cumsum(counts)

    plt.semilogx(binEdges[0:-1], cdf, linestyle='--',  color='b')

    plt.ylim((0,1))
    plt.xlim(1, 10000)
    plt.xlabel("Time (s)")
    plt.ylabel("CDF")
    plt.suptitle(groupName)
    plt.grid(True)
    plt.show()

for fileName in os.listdir(intervalsDir):
    parsedFileName = fileName.split(".")
    xLabel = parsedFileName[0]
    filePath = intervalsDir + "/" + fileName
    dataList = fileLibrary.createFileLog(filePath)
    myDataList = []
    for d in dataList:
        x = int(d)
        myDataList.append(x)
    cdf(myDataList, xLabel)

