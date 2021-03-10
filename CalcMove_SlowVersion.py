import serial, time, struct
import csv
import math
import matplotlib.pyplot as plt
from operator import itemgetter 
import statistics
import os
import cProfile
import pstats

def CalcMove(a, d): #Uses the data from GrabPts to determine what angle to rotate to and distance to travel
    DistThresh = 3 #Minimum distance threshold for function to base calculations. Distance in meters  
    AngStep = 30 #Step size for determining which measured distances are farther away

    #Attempt to calculate indices. Otherwise, return a "False" Flag 
    try:
        indx = [idx for idx, val in enumerate(d) if val > DistThresh] #Gives indices of list "d" where values are above DistThresh

    except:
        print("SUPREME FAILURE")
        success = False
        DesAng = 0 
        DesDist = 0

        return success, DesAng, DesDist

    AngThresh = list(itemgetter(*indx)(a)) #Zips elements of "a" with indices in "indx" to give list of all angles above DistThresh. Sorts in ascending order as well
    
    ##----Iterate to find where most, farthest clusters are
    i = 0 #Increments based on the value of AngStep
    LoopCount = 0 #Counter variable indicating how many times we've iterated through the loop  
    NumMaxElements = 0 #Tracks what the highest number of elements was between all loo iterations
    MaxLoop = 0 #Variable updated with the version of the loop determined to have the highest number of values

    while i < 360: #While loop will analyze AngThresh values by chunks to determine where the largest cluster of distances are
        CurrElements = len(list(x for x in AngThresh if i < x <= i+AngStep)) #Determines how many values in the list fall within the angle range of AngStep
        LoopCount += 1

        if CurrElements >= NumMaxElements: #If greater than or equal to, update NumMaxElements, keep track of loop iteration
            NumMaxElements = CurrElements #Update max elements
            MaxLoop = LoopCount #Update which version of the loop we were counted in
            
            i += AngStep

        else: #If not greater than, just move on to next step size
            i += AngStep

    print("MaxLoop =", MaxLoop)
    print("LoopCount =", LoopCount)

    DesAng = round((MaxLoop*AngStep)-(AngStep/2)) #Calculates what angle we want to rotate to

    IndxDist = [i for i, x in enumerate(a) if x <= DesAng+(AngStep/2) and x >= DesAng-(AngStep/2)] #Use AngStep to determine the upper and lower half indices we're looking for
    MedDist = statistics.median(itemgetter(*IndxDist)(d)) #Calculates the median distance from the index values

    DesDist = round(0.75*MedDist,1) #Distance we want SPIKE to travel. Scaled down to avoid crashing

    print("DesAng =", DesAng)
    print("DesDist =", DesDist)

    success = True
    return success, DesAng, DesDist



#--------DATA READ-IN-------#
a,d = [], []
with open('/home/pi/Desktop/Lidar/p3Data_AD3.csv') as csv_file:
    csvreader = csv.reader(csv_file)
    for column in csvreader:
        a.append(float(column[0]))
        d.append(float(column[1]))

#----Setting up the Profiler
profiler = cProfile.Profile()
profiler.enable()

##--------MAIN TEST LOOP-------#
cycles = 1
for i in range(cycles):
    #startTime = time.time()
    success = False

    while not success:
        success, DesAng, DesDist = CalcMove(a, d)

        if not success: #"CalcMove" function calculates a failure, will reattempt 
            print('Reattempting Calculations')
            continue


profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumtime')
stats.print_stats()
stats.dump_stats('results.prof')
