## setup
To get this github repository on your local machine, first navigate to the directory you want it to be in and run
```
git clone https://github.com/maxwell-herrmann/module0_pedestal.git
```
This will fill the directory with the files you see here. Next, the folders datalogs and bad_channel_files should both be filled by running (in the main directory)
```
chmod +x getdata.sh
```
then 
```
./get data.sh
```
To generate any mean ADC or standard deviation of ADC plots (including boxplots), first make a text file in the main directory with the file names of the datalog files you're interested in running over. Running
```
python pedestal_functional.py fileList
```
(note: you may need to replace python with python3) will produce .json files in the jsons directory that correspond to the original .h5 datalog files. The .json files contain a unique channel ID, the mean, and the standard deviation of the ADC counts for that channel in that run. These files contain all channels, including those marked as bad. To produce files with only good channels, use the pedestal_filter.py script:
```
python pedestal_filter.py jsonList channelList
```
This will produce the jsons and place them all in the good_jsons folder (this code is easy to edit if you want to put them somewhere else or use a different naming scheme). I had a weird time trying to implement the functionality of this inside pedestal_functional.py, so I've left them separate for now because that seems to work best. 

## plotting

To make plots using this data, use the functions in pedestal_plotting.py and do 
```
python pedestal_plotting.py goodJsonList
```
where jsonFileList is, again, a text file with the names of the .json files desired. This python script can also make ADC vs time plots for individual channels given a unique channel ID and a datalog file to run over. 
```
python pedestal_plotting.py datalogs/[desired datalog file]
```
As set up now, plots made by pedestal_plotting.py will be saved to the plots directory with names generated from either the date of the run or the unique chanenl ID. Also, the list files in this repo are lists of all the files that would be created from the pedestal .h5 files. Disregard placeholder textfiles in the plots and jsons directories.

To make heatmap plots, first run
```
python location_dict geometry_files/multi_tile_layout-2.1.16.yaml
```
This will create a .json file with a dictionary giving the position of a channel from its unique id. Then to produce the actual plots, run
```
python goodJsonList geometry_files/multi_tile_layout-2.1.16.json
```
This will save the plots in the format (run_date)_ heat.png to the plots folder.
