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
    valuesWithEndpoints = np.insert(values,[0,len(values)],[0.001,0.003]) # Add 0s to both ends of the scale
    midPoints = map(lambda (x,y): (x+y)/2,zip(bands,bands[1:])) # Calculate histogram midpoints
    widths = map(lambda (x,y): y-x,zip(bands,bands[1:])) # Calculate histogram widths
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

def randI(c,sd):
    return int(round(np.random.normal(c,sd)))

def lowerN():
    n = randI(2.8,1.5)
    return max(0,min(6,n))

def studentToPoints(student,bands,lPoints,hPoints):
    (l,h) = student
    lRes = reduce(lambda x,y: x + percToPoints(y,bands,lPoints),l,0)
    hRes = reduce(lambda x,y: x + percToPoints(y,bands,hPoints),h,0)
    return lRes+hRes

# Function to simulate a student
def simStudent():
    # pick how many lower level subjects, average is around 2 or 3 from personal experience
    nLower = lowerN()
    lAnchor = lowerF() # Find an anchor for the lower level exams
    hAnchor = higherF() # Find an anchor for the higher level exams
    lResults = [max(0,min(randI(lAnchor,5),100)) for _ in range(nLower)]
    hResults = [max(0,min(randI(hAnchor,5),100)) for _ in range(6-nLower)]
    return (lResults,hResults)

students = [simStudent() for _ in range(100000)]

oldResults = map(lambda x: studentToPoints(x,oldBands,oldPointsLower,oldPointsHigher),students)
newResults = map(lambda x: studentToPoints(x,newBands,newPointsLower,newPointsHigher),students)

mx=mn=0
sm=0
for i in range(len(students)):
    dif = oldResults[i] - newResults[i]
    if(dif < oldResults[mn]-newResults[mn]):
        mn=i
    if(dif > oldResults[mx]-newResults[mx]):
        mx=i
    sm+=dif

sm/=len(students)

print students[mx],oldResults[mx],newResults[mx],oldResults[mx]-newResults[mx]
print students[mn],oldResults[mn],newResults[mn],oldResults[mn]-newResults[mn]
print sm

plt.title("Points distributions compared")
plt.hist(oldResults,normed=1,color='red',bins=20,label="Old System")
plt.hist(newResults,normed=1,color='blue',bins=20,alpha=0.7,label="New System")
plt.legend(loc="upper left")
plt.xlabel("Points")
#plt.show()
