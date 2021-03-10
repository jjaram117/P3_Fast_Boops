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
    DistThresh = 4 #Minimum distance threshold for function to base calculations. Distance in meters  
    AngStep = 30 #Step size for determining which measured distances are farther away

    DistIdeal = DistThresh*1.5 #Value used to determine if SPIKE moves in that given direction based on surpassing an ideal threshold

    #Attempt to calculate indices. Otherwise, return a "False" Flag 
    try:
        indx = [idx for idx, val in enumerate(d) if val > DistThresh] #Gives indices of list "d" where values are above DistThresh

        #Grab angle and distance values that correspond with indx values we calculated
        a_thresh = list(itemgetter(*indx)(a)) 
        d_thresh = list(itemgetter(*indx)(d))

        #Sort the a and d lists together as soon as they come in to avoid data mixups. Sort ascendingly according to a
        sorted_lists = sorted(zip(a_thresh, d_thresh))

        tuples = zip(*sorted_lists)
        a_sorted, d_sorted = [ list(tuple) for tuple in  tuples] #Splits up newly sorted lists        
        
    except: #What to do if try statement fails
        print("SUPREME FAILURE")
        success = False
        DesAng = 0 
        DesDist = 0

        return success, DesAng, DesDist


    ##----Iterate to find the first cluster where median distance surpasses DistIdeal
    i = a_sorted[0] #Start at the minimum angle filtered in the previous step
    MaxDist = 0 #Keeps track of the farthest distance calculated. Used in case DistIdeal is never surpassed 
    LoopCount = 0 #Used to track which loop iteration loop exited on

    while i <= a_sorted[-1]: #While loop runs until angle step surpasses maximum angle filtered by previous step        
        CurrElements = [t for t, x in enumerate(a_sorted) if i <= x < i+AngStep] #Finds indices in a_sorted where values fall within certain range

        try:
            medDist = statistics.median(itemgetter(*CurrElements)(d_sorted))
            LoopCount += 1
        except:
            medDist = 0
            LoopCount += 1

        if medDist >= DistIdeal:
            DesAng = round((i)+(AngStep/2)) #Should be whatever angle "i" we're on, plus half of AngStep to go straight down the middle
            DesDist = round(medDist*.8, 1) #Go X% of whatever the desired distance was calculated to be
            break

        else: 
            i += AngStep

            if medDist >= MaxDist: #Update MaxDist with the current medDist if it's larger.
                MaxDist = medDist

    success = True
    return success, DesAng, DesDist



#--------DATA READ-IN-------#
a,d = [], []
with open('/home/pi/Desktop/Lidar/p3Data_AD3.csv') as csv_file:
    csvreader = csv.reader(csv_file)
    for column in csvreader:
        a.append(float(column[0]))
        #a.append(column[0])
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
        #Lidar intialization and data grab
        success, DesAng, DesDist = CalcMove(a, d)
        if not success: #"CalcMove" function calculates a failure, will reattempt 
            print('Reattempting Calculations')
            continue

        print("\nWill rotate %f Degrees" % DesAng)
        print("Will travel %f meters forward" % DesDist)


profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumtime')
stats.print_stats()
stats.dump_stats('results.prof')



##Changes made to this "faster" version:
    #Filter out all values below DistThresh 
    #Sorting a and d lists together in a ascending order based on "a". Indices should remain matched
    #Determine the median distance within current AngStep. If >= DistIdeal, jump out and go with that. Else, continue to next step

