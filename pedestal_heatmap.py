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

    for file in f:
        f2 = open ('good_jsons/'+file.strip(), "r")
        out = json.loads(f2.read())

        runNo = re.search(r'\d\d\d\d_\d\d_\d\d_\d\d_\d\d_\d\d',file.strip()).group(0)

        hits=[]

        for channel in out:
            try:
                limit=math.ceil(channel[1])
                for i in range(0, limit):
                    hits.append(list((geometryDict[str(channel[0])][0],geometryDict[str(channel[0])][1])))
            except KeyError:
                continue

        nphits=np.array(hits)
        dframe = pd.DataFrame(nphits, columns=['X', 'Y'])
        fig = plt.figure(figsize=[20, 10])
        ax = plt.hist2d(dframe.Y, -dframe.X, bins=[600, 300])
        plt.xlabel("Pixel plane X [mm]")
        plt.ylabel("Pixel plane Y [mm]")
        cb = plt.colorbar(label = 'ADC count')
        plt.savefig("plots/{}_heatmap.png".format(runNo))
        plt.show()
        plt.close()

        

if __name__ == '__main__':
    heatMap(sys.argv[1], sys.argv[2])

