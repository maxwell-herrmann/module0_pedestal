import yaml
import numpy as np
import sys
import json
import matplotlib.pyplot as plt
import seaborn as sns
import re
from functools import reduce
from scipy.stats import kde
import math
import pandas as pd

def heatMap(fileList, geometryJson):
    f = open(fileList, "r")

    f1 = open (geometryJson.strip(), "r")
    geometryDict = json.loads(f1.read())

    coords = list(map(list, zip(*list(geometryDict.values()))))
    xMax = round(max(coords[0]))+1
    xMin = round(min(coords[0]))-1
    yMax = round(max(coords[1]))+1
    yMin = round(min(coords[1]))-1
    
    print(xMax, yMax)
    print(xMin, yMin)
    for file in f:
        f2 = open ('good_jsons/'+file.strip(), "r")
        
        out = json.loads(f2.read())
        
        runNo = re.search(r'\d\d\d\d_\d\d_\d\d_\d\d_\d\d_\d\d',file.strip()).group(0)

        heatMap = np.zeros((xMax-xMin, yMax-yMin))
        
        for channel in out:
            try:
                heatMap[round(geometryDict[str(channel[0])][0])-xMin][round(geometryDict[str(channel[0])][1])-yMin] += channel[1]
              
            except KeyError:
               continue
        
        fig = plt.figure(figsize=[20,10])
        ax = sns.heatmap(heatMap, cmap='viridis', robust=True)


        plt.savefig(f"plots/{runNo}_heat.png", transparent=True)       
        




if __name__ == '__main__':
    heatMap(sys.argv[1], sys.argv[2])
