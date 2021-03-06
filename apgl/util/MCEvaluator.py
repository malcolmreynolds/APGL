

class MCEvaluator(object):
    """
    A class to evaluate machine learning performance for the matrix completion
    problem.
    """
    def __init__(self):
        pass
    
    @staticmethod 
    def meanSqError(testX, predX): 
        """
        Find the mean squared error between two sparse matrices testX and predX. 
        """
        
        rowInds, colInds = testX.nonzero()
        
        error = 0 
        for i in range(rowInds.shape[0]): 
            error += (testX[rowInds[i], colInds[i]] - predX[rowInds[i], colInds[i]])**2
            
        error /= rowInds.shape[0]
        
        return error 
        