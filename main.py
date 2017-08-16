import math
import random as rand
import numpy as np
import matplotlib.pyplot as plt
import pandas
from scipy import interpolate

inputData = pandas.read_csv("stats.csv")
results_cols = list(inputData)[3:] # Colums titles for grades and total


def transform(x): # Transforms a row of percentages into total population
    tot = x["Total"]
    return x[1:].apply(lambda y: (y*tot)/100.0)

# Generate a function that represents the distribution in the input data
def genDist(dataIn, bands, points):
    total = dataIn["Total"].sum() # Get total population in this dataset
    resultsData = dataIn[results_cols] # Limit dataset to results
    popData = resultsData.apply(transform, axis=1) # Transform to population figures
    values = popData.sum().values[::-1]/total # Normalise and reverse
    valuesWithEndpoints = np.insert(values,[0,len(values)],[0,0]) # Add 0s to both ends of the scale
    midPoints = map(lambda (x,y): (x+y)/2,zip(bands,bands[1:])) # Calculate histogram midpoints
    # Interpolate percentage function
    scoreFunc = interpolate.interp1d([0]+midPoints+[100],valuesWithEndpoints,kind="cubic")
    newY = scoreFunc(np.arange(0,100)) # Apply new function to all percentages
    newY/=sum(newY) # Normalise
    sumTable = [0]*100 # Sum table to get probability distribution
    for i in range(1,100):
        sumTable[i]=newY[i]+sumTable[i-1]

    def outFunc():
        n = rand.randint(0,100) # Pick a point in a uniform distribution
        n/=100.0
        for i,sm in enumerate(sumTable): # Find percentage
            if sm>=n:
                return i
        return 99

    return outFunc

# Turn percentage to points
def percToPoints(x,bands,points):
    i=0
    while(i+2 < len(bands) and x >= bands[i+1]):
        i+=1
    return points[i]

higherData = inputData[inputData["Level"]=='A'] # Data for higher level
lowerData = inputData[inputData["Level"]=='G'] # Data for lower level

oldBands = [0,10,25,40,45,50,55,60,65,70,75,80,85,90,100]
oldPointsHigher = [0,0,0,45,50,55,60,65,70,75,80,85,90,100]
oldPointsLower = [0,0,0,5,10,15,20,25,30,35,40,45,50,60]

newBands = [0,30,40,50,60,70,80,90,100]
newPointsHigher = [0,37,46,56,66,77,88,100]
newPointsLower = [0,0,12,20,28,37,46,56]

higherF = genDist(higherData, oldBands, oldPointsHigher) # Get distribution for higher level
lowerF = genDist(lowerData, oldBands,oldPointsLower) # Get distribution for lower level

# Function to simulate a student
def simStudent(bands,higherPoints,lowerPoints):
    # pick how many lower level subjects, average is around 2 or 3 from personal experience
    nLower = rand.randint(0,3)
    lAnchor = lowerF() # Find an anchor for the lower level exams
    hAnchor = higherF() # Find an anchor for the higher level exams
    # Map the percToPoints function over exams at each level, where the student scores
    # in a uniform distribution of +-20% from the anchor point
    results = map(lambda x: percToPoints(x,bands,lowerPoints),[rand.randint(max(0,lAnchor-20),min(lAnchor+20,100)) for _ in range(nLower)])
    results += map(lambda x: percToPoints(x,bands,higherPoints),[rand.randint(max(0,hAnchor-20),min(hAnchor+20,100)) for _ in range(7-nLower)])
    # Sort results
    results.sort(reverse=True)
    return reduce(lambda x,y: x+y, results[:6]) # Return sum of top 6
    

oldStudents = [simStudent(oldBands,oldPointsHigher,oldPointsLower) for _ in range(10000)]
newStudents = [simStudent(newBands,newPointsHigher,newPointsLower) for _ in range(10000)]

plt.hist(oldStudents,normed=1,color='red')
plt.hist(newStudents,normed=1,color='blue')
plt.show()
