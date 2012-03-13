
import numpy
import logging
import sys 
import matplotlib.pyplot as plt 

from apgl.graph import *
from apgl.util.PathDefaults import PathDefaults
from apgl.util.Util import Util 
from apgl.viroscopy.model.HIVGraph import HIVGraph
from apgl.viroscopy.model.HIVVertices import HIVVertices

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

plotStyles = ['ko-', 'kx-', 'k+-', 'k.-', 'k*-']

outputDir = PathDefaults.getOutputDir() + "viroscopy/"
figureDir = PathDefaults.getOutputDir() + "viroscopy/figures/toyExample/"
saveResults = False
graphStats = GraphStatistics()

if saveResults:
    infectedGraphList = []
    removedGraphList = []
    endGraphList = []  #This is a list of each graph at the end time point
    numGraphs = 10

    timesFileName = outputDir + "epidemicTimes.pkl"
    times = Util.loadPickle(timesFileName)
    numTimes = len(times)
    infectedArray = numpy.zeros((numGraphs, numTimes))
    removedArray = numpy.zeros((numGraphs, numTimes))
    maleArray = numpy.zeros((numGraphs, numTimes))
    femaleArray = numpy.zeros((numGraphs, numTimes))
    heteroArray = numpy.zeros((numGraphs, numTimes))
    biArray = numpy.zeros((numGraphs, numTimes))

    for i in range(numGraphs):
        graphFileName = outputDir + "epidemicGraph" + str(i) 
        evolutionFileName = outputDir + "epidemicEvolution"  + str(i) + ".pkl"

        graph = HIVGraph.load(graphFileName, globals()["HIVVertices"])
        vList = graph.getVertexList()
        V = vList.getVertices()
        infectedIndices, removedIndices, times = Util.loadPickle(evolutionFileName)
        allIndices = [range(graph.getNumVertices())]

        infectedGraphList.append((graph, infectedIndices))
        removedGraphList.append((graph, removedIndices))
        endGraphList.append((graph, allIndices))

        infectedArray[i, :] = numpy.array([len(x) for x in infectedIndices])
        removedArray[i, :] = numpy.array([len(x) for x in removedIndices])
        maleArray[i, :] = numpy.array([numpy.sum(V[x, HIVVertices.genderIndex]==HIVVertices.male) for x in removedIndices])
        femaleArray[i, :] = numpy.array([numpy.sum(V[x, HIVVertices.genderIndex]==HIVVertices.female) for x in removedIndices])
        heteroArray[i, :] = numpy.array([numpy.sum(V[x, HIVVertices.orientationIndex]==HIVVertices.hetero) for x in removedIndices])
        biArray[i, :] = numpy.array([numpy.sum(V[x, HIVVertices.orientationIndex]==HIVVertices.bi) for x in removedIndices])

    resultsFileName = outputDir + "SimInfectedContactGrowthScalarStats.pkl"
    meanStatsArray, stdStatsArray = graphStats.meanSeqScalarStats(infectedGraphList, True)
    Util.savePickle(meanStatsArray, resultsFileName)

    resultsFileName = outputDir + "SimContactGrowthScalarStats.pkl"
    meanStatsArray, stdStatsArray = graphStats.meanSeqScalarStats(removedGraphList, True)
    Util.savePickle(meanStatsArray, resultsFileName)

    #Scalar stats for whole contact graph
    resultsFileName = outputDir + "SimContactScalarStats.pkl"
    meanStatsArray, stdStatsArray = graphStats.meanSeqScalarStats(endGraphList, False)
    Util.savePickle(meanStatsArray, resultsFileName)

    resultsFileName = outputDir + "SimContactVectorScalarStats.pkl"
    finalRemovedInds = removedIndices[-1]
    removedGraph = graph.subgraph(finalRemovedInds)
    statsDict = graphStats.vectorStatistics(removedGraph)
    Util.savePickle(statsDict, resultsFileName)

    #Compute some statistics over the vertex values
    resultsFileName = outputDir + "SimContactVertexStats.pkl"
    vertexStatsDict = {}
    vertexStatsDict["meanInfectedArray"] = numpy.mean(infectedArray, 0)
    vertexStatsDict["meanRemovedArray"] = numpy.mean(removedArray, 0)
    vertexStatsDict["meanMale"] = numpy.mean(maleArray, 0)
    vertexStatsDict["meanFemale"] = numpy.mean(femaleArray, 0)
    vertexStatsDict["meanHetero"] = numpy.mean(heteroArray, 0)
    vertexStatsDict["meanBi"] = numpy.mean(biArray, 0)
    Util.savePickle(vertexStatsDict, resultsFileName)
else:
    resultsFileName = outputDir + "SimContactGrowthScalarStats.pkl"
    statsArray = Util.loadPickle(resultsFileName)

    resultsFileName = outputDir + "SimContactScalarStats.pkl"
    statsArrayFinal = Util.loadPickle(resultsFileName)

    resultsFileName = outputDir + "SimContactVectorScalarStats.pkl"
    statsDict = Util.loadPickle(resultsFileName)

    resultsFileName = outputDir + "SimContactVertexStats.pkl"
    vertexStatsDict = Util.loadPickle(resultsFileName)

    timesFileName = outputDir + "epidemicTimes.pkl"
    times = Util.loadPickle(timesFileName)

    graphStats = GraphStatistics()
    
    print("Statistics for contact graph.")
    print("------------------------------")
    print(graphStats.strScalarStatsArray(statsArrayFinal[0, :]))

    print("Statistics for removed graph.")
    print("------------------------------")
    print(graphStats.strScalarStatsArray(statsArray[-1, :]))

    #Let's plot the statistics
    plotInd = 1
    
    plt.figure(plotInd)
    plt.plot(times, statsArray[:, graphStats.numComponentsIndex])
    plt.xlabel("Time (days)")
    plt.ylabel("Number of components")
    plt.savefig(figureDir + "NumComponents" + ".eps")
    plotInd += 1

    plt.figure(plotInd)
    plt.plot(times, statsArray[:, graphStats.maxComponentSizeIndex])
    plt.xlabel("Time (days)")
    plt.ylabel("Max Component Size")
    plt.savefig(figureDir + "MaxComponentSize" + ".eps")
    plotInd += 1

    plt.figure(plotInd)
    plt.plot(times, statsArray[:, graphStats.effectiveDiameterIndex])
    plt.xlabel("Time (days)")
    plt.ylabel("Max Component Effective Diameter")
    plotInd += 1

    plt.figure(plotInd)
    plt.plot(times, statsArray[:, graphStats.geodesicDistMaxCompIndex])
    plt.xlabel("Time (days)")
    plt.ylabel("Max Component Geodesic Distance")
    plotInd += 1

    #Make sure we don't include 0 in the array
    vertexIndex = numpy.argmax(statsArray[:, graphStats.numVerticesIndex] > 0)
    edgeIndex = numpy.argmax(statsArray[:, graphStats.numEdgesIndex] > 0)
    minIndex = numpy.maximum(vertexIndex, edgeIndex)

    plt.figure(plotInd)
    plt.plot(numpy.log(statsArray[minIndex:, graphStats.numVerticesIndex]), numpy.log(statsArray[minIndex:, graphStats.numEdgesIndex]))
    plt.xlabel("log(numVertices)")
    plt.ylabel("log(numEdges)")
    plotInd += 1

    #Plot also some properties of the vertices (include detection types)
    vertexStatsDict["meanRemovedArray"] += vertexStatsDict["meanRemovedArray"]==0
    coverage = vertexStatsDict["meanRemovedArray"]/(vertexStatsDict["meanRemovedArray"]+vertexStatsDict["meanInfectedArray"])
    plt.figure(plotInd)
    plt.plot(times, coverage, 'r')
    plt.xlabel("Time (days)")
    plt.ylabel("Coverage")
    plt.savefig(figureDir + "Coverage" + ".eps")
    plotInd += 1

    plt.figure(plotInd)
    plt.plot(times, vertexStatsDict["meanMale"], plotStyles[0], times, vertexStatsDict["meanFemale"], plotStyles[1])
    plt.plot(times, vertexStatsDict["meanHetero"], plotStyles[2], times, vertexStatsDict["meanBi"], plotStyles[3])
    plt.xlabel("Time (days)")
    plt.ylabel("Individuals")
    plt.legend(("Male", "Female", "Heterosexual", "Bisexual"), loc="upper left")
    plt.savefig(figureDir + "GenderOrient" + ".eps")
    plotInd += 1

    plt.show()
