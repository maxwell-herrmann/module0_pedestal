# module0_pedestal
The folders datalogs and bad_channel_files should both be filled by running (in the directory)
```
$ wget wgetlist
```
To generate any mean ADC or standard deviation of ADC plots (including boxplots), first make a text file in the main directory with the file names of the datalog files you're interested in running over, then a similar file for the bad channel list files. Running
```
$ python3 pedestal_functional.py dataFileList channelFileList
```
will produce .json files in the jsons directory that correspond to the original .h5 datalog files. The .json files contain a unique channel ID, the mean, and the standard deviation of the ADC counts for that channel in that run. To make plots using this data, use the functions in pedestal_plotting.py and do 
```
$ python3 pedestal_plotting.py jsonFileList
```
where jsonFileList is, again, a text file with the names of the .json files desired. This python script can also make ADC vs time plots for individual channels given a unique channel ID and a datalog file to run over. As set up now, all plots will be saved to the plots directory. 
