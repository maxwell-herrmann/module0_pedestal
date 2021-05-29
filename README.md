# module0_pedestal
The folders datalogs and bad_channel_files should both be filled by running (in the directory)
```
$ wget -i wgetlist
```
To generate any mean ADC or standard deviation of ADC plots (including boxplots), first make a text file in the main directory with the file names of the datalog files you're interested in running over. Running
```
$ python3 pedestal_functional.py dataFileList channelFileList
```
will produce .json files in the jsons directory that correspond to the original .h5 datalog files. The .json files contain a unique channel ID, the mean, and the standard deviation of the ADC counts for that channel in that run. These files contain all channels, including those marked as bad. To produce files with only good channels, use the pedestal_filter.py script:
```
$ python3 pedestal_filter.py jsonList channelFileList
```
This will produce the jsons and place them all in the good_jsons folder (this code is easy to edit if you want to put them somewhere else or use a different naming scheme). To make plots using this data, use the functions in pedestal_plotting.py and do 
```
$ python3 pedestal_plotting.py jsonList
```
where jsonFileList is, again, a text file with the names of the .json files desired. This python script can also make ADC vs time plots for individual channels given a unique channel ID and a datalog file to run over. 
```
$ python3 pedestal_plotting.py datalog.h5
```
As set up now, plots made by pedestal_plotting.py will be saved to the plots directory with names generated from either the date of the run or the unique chanenl ID. Disregard placeholder textfiles in the plots and jsons directories.
