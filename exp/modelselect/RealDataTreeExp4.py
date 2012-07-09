"""
Try to figure out the learning rate 
"""
import logging 
import numpy 
import sys 
import multiprocessing 
import scipy.stats 
from apgl.util.PathDefaults import PathDefaults 
from exp.modelselect.ModelSelectUtils import ModelSelectUtils 
from apgl.util.Sampling import Sampling
from exp.sandbox.predictors.DecisionTreeLearner import DecisionTreeLearner
import matplotlib.pyplot as plt 
from sklearn import linear_model 
from apgl.util.FileLock import FileLock

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
numpy.seterr(all="raise")
numpy.random.seed(45)
dataDir = PathDefaults.getDataDir() 
dataDir += "modelPenalisation/regression/"

figInd = 0 

loadMethod = ModelSelectUtils.loadRegressDataset
datasets = ModelSelectUtils.getRegressionDatasets(True)

sampleSizes = numpy.array([50, 100, 200])
foldSizes = numpy.arange(2, 13, 1)
alpha = 1.0

gammas = numpy.unique(numpy.array(numpy.round(2**numpy.arange(1, 7.25, 0.25)-1), dtype=numpy.int))

paramDict = {} 
paramDict["setGamma"] = gammas
numParams = paramDict["setGamma"].shape[0]

sampleMethod = Sampling.crossValidation
numProcesses = multiprocessing.cpu_count()
Cvs = numpy.array([1])

outputDir = PathDefaults.getOutputDir() + "modelPenalisation/regression/CART/"

for datasetName, numRealisations in datasets:
    logging.debug("Dataset " + datasetName)
    betas = numpy.zeros((gammas.shape[0], sampleSizes.shape[0]))
    
    learner = DecisionTreeLearner(criterion="mse", maxDepth=100, minSplit=1, pruneType="CART", processes=numProcesses)
    learner.setChunkSize(3)   
    
    outfileName = outputDir + datasetName + "Beta"
    
    fileLock = FileLock(outfileName + ".npz")
    if not fileLock.isLocked() and not fileLock.fileExists():
        fileLock.lock()    
    
        for m in range(sampleSizes.shape[0]): 
            sampleSize = sampleSizes[m]
            logging.debug("Sample size " + str(sampleSize))
        
            meanPenalties = numpy.zeros((foldSizes.shape[0], numParams))
        
            numRealisations = 10
            
            k = 0 
            for folds in foldSizes: 
                logging.debug("Folds " + str(folds))
                errors = numpy.zeros(numRealisations)
                        
                for j in range(numRealisations):
                    print("")
                    logging.debug("Realisation: " + str(j))
                    trainX, trainY, testX, testY = loadMethod(dataDir, datasetName, j)
                    
                    trainInds = numpy.random.permutation(trainX.shape[0])[0:sampleSize]
                    trainX = trainX[trainInds,:]
                    trainY = trainY[trainInds]
                    
                    idx = sampleMethod(folds, trainX.shape[0])        
                    
                    #Now try penalisation
                    resultsList = learner.parallelPen(trainX, trainY, idx, paramDict, Cvs)
                    bestLearner, trainErrors, currentPenalties = resultsList[0]
                    meanPenalties[k, :] += currentPenalties
    
                k+= 1
                
            numRealisations = float(numRealisations)
            meanPenalties /=  numRealisations 
            
            for i in range(gammas.shape[0]): 
                inds = numpy.logical_and(numpy.isfinite(meanPenalties[:, i]), meanPenalties[:, i]>0)
                tempMeanPenalties = meanPenalties[:, i][inds]
                tempFoldSizes = numpy.array(foldSizes, numpy.float)[inds]                
                
                
                if tempMeanPenalties.shape[0] > 1: 
                    x = numpy.log((tempFoldSizes-1)/tempFoldSizes*sampleSize)
                    y = numpy.log(tempMeanPenalties)+numpy.log(tempFoldSizes)    
                
                    clf = linear_model.LinearRegression()
                    clf.fit(numpy.array([x]).T, y)
                    betas[i, m] = clf.coef_[0]
                    print(gammas[i], betas[i, m])        
            
        print(-betas) 
        
        
        numpy.savez(outfileName, -betas)
        logging.debug("Saved results as file " + outfileName + ".npz")
        fileLock.unlock()