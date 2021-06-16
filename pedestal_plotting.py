import matplotlib.pyplot as plt
import numpy as np
import sys
import json
import re
import h5py

def unique2key(unique):
    channel_id =unique % 64
    chip_id = (unique //64) % 256
    io_channel = (unique // (64*256)) % 256
    io_group = (unique // (64*256*256)) % 256
    return channel_id, chip_id, io_channel, io_group

def getKey(item):
    return item[0]

def np_encoder(object):
    if isinstance(object, np.generic):
        return object.item()

def unique_channel_id(io_group, io_channel, chip_id, channel_id):
    return channel_id+64*(chip_id + 256*(io_channel+256*io_group))

def load(fileList, path):
    f=open(fileList, 'r')
    outs=[]
    dates=[]
    for file in f:
        name=path+file.strip()
        f1=open(name, 'r')
        out=json.loads(f1.read())
        outs.append(out)
        dates.append(re.search(r'\d\d\d\d_\d\d_\d\d_\d\d_\d\d',file.strip()).group(0))
        f1.close()
    f.close()
    return outs, dates

"""
def good_channel(unique, channelList):
    outs=[]
    good=True
    f=open(channelList, 'r')
    channel_id, chip_id, io_channel, io_group = unique2key(unique)
    for file in f:
        filename='bad_channel_files/'+str(file).replace('\n', '')
        f1=open(filename, 'r')
        dict=json.loads(f1.read())
        if str(io_group)+'-'+str(io_channel)+'-'+str(chip_id) in dict:
            if channel_id in dict[str(io_group)+'-'+str(io_channel)+'-'+str(chip_id)]:
                good=False
            if channel_id in dict['All']:
                good=False
    return good
"""

def boxplot(fileList, fliers, path, destination=None):
    f = open(fileList, "r")

    xAxis = []
    series = []
    for file in f:
        name=path+file.strip()
        f1 = open (name, "r")
        out = json.loads(f1.read())
        series.append(list(map(lambda x: x[1], out)))
        timestamp = re.search(r'\d\d\d\d_\d\d_\d\d_\d\d_\d\d_\d\d',file.strip()).group(0)
        xAxis.append(f"{timestamp[:4]}/{timestamp[5:7]}/{timestamp[8:10]}\n{timestamp[11:13]}:{timestamp[14:16]}:{timestamp[17:19]}")
        f1.close()

    fig = plt.figure()
    bp = plt.boxplot(series, showfliers=fliers)
    filename = 'boxplot_no_fliers.png'
    if fliers:
        filename='boxplot_fliers.png'
    if destination:
        filename=destination+filename
    if not destination:
        filename='plots/'+filename
    plt.savefig(filename)
    plt.show()
    f.close()

def histplot(fileList):
    f=open(fileList, 'r')

    means=[]
    stds=[]
    for file in f:
        f1=open(file.strip(), 'r')
        out=json.loads(f1.read())

        means.append(list(map(lambda x: x[1], out)))
        stds.append(list(map(lambda x: x[2], out)))
        f1.close()
    fig=plt.figure()
    plt.hist2d(means, stds, bins=(100, 100), cmap=plt.cm.jet)
    plt.show()
    f.close()

def mean_overlay_hist(fileList, logg, path, destination=None):
    runs,dates=load(fileList, path)
    for i in range(0, len(runs)):
        plt.hist([item[1] for item in runs[i]], bins=100,  histtype=u'step', log=logg, label=str(dates[i]))
    plt.legend()
    plt.xlabel('mean ADC')
    plt.ylabel('channel count')
    if logg:
        plt.ylabel('channel count (log)')
    filename='gathered_mean_distributions.png'
    if logg:
        filename='gathered_mean_distributions_log.png'
    if destination:
        filename=destination+filename
    if not destination:
        filename='plots/'+filename
    plt.savefig(filename)
    plt.show()

def std_overlay_hist(fileList, logg, path, destination=None):
    runs,dates=load(fileList, path)
    for i in range(0, len(runs)):
        plt.hist([item[2] for item in runs[i]], bins=100, histtype=u'step', log=logg, label=str(dates[i]))
    plt.legend()
    plt.xlabel('std of ADC')
    plt.ylabel('channel count')
    if logg:
        plt.ylabel('channel count (log)')
    filename='gathered_std_distributions.png'
    if logg:
        filename='gathered_std_distributions_log.png'
    if destination:
        filename=destination+filename
    if not destination:
        name='plots/'+filename
    plt.savefig(filename)
    plt.show()

def single_mean_hist(fileList, n, logg, path, destination=None):
    runs,dates=load(fileList, path)
    plt.hist([item[1] for item in runs[n]], bins=100, histtype=u'step', log=logg)
    plt.xlabel('mean ADC')
    plt.ylabel('channel count')
    filename=str(dates[n])+'_mean.png'
    if logg:
        filename=str(dates[n])+'_mean_log.png'
    if destination:
        filename=destination+filename
    if not destination:
        filename='plots/'+filename
    plt.savefig(filename)
    plt.show()

def single_channel_adc_vs_time(unique, h5file, destination=None):
    f=h5py.File(h5file, 'r+')
    date=re.search(r'\d\d\d\d_\d\d_\d\d_\d\d_\d\d',h5file).group(0)    
    p=f['packets']['timestamp']

    rollover=np.zeros(len(f['packets']))
    rollover[(f['packets']['packet_type']==6) & (f['packets']['trigger_type']==83)]=1e7 #ticks/second
    rollover=np.cumsum(rollover)
  
    f['packets']['timestamp']=f['packets']['timestamp']+rollover

    data_mask=f['packets'][:]['packet_type']==0
    valid_parity_mask = f['packets'][data_mask]['valid_parity'] == 1
    good_data=(f['packets'][data_mask])[valid_parity_mask]
    
    io_group=good_data['io_group'].astype(np.uint64)
    io_channel=good_data['io_channel'].astype(np.uint64)
    chip_id=good_data['chip_id'].astype(np.uint64)
    channel_id=good_data['channel_id'].astype(np.uint64)

    channel_mask=unique_channel_id(io_group, io_channel, chip_id, channel_id)==unique
    timestamp=good_data[channel_mask]['timestamp']
    
    adc=good_data[channel_mask]['dataword']

    f['packets']['timestamp']=p
    f.close()
    filename=date+str(unique)+'_adc_vs_time.png'
    if destination:
        filename=destination+filename
    if not destination:
        filename='plots/'+filename
    plt.scatter(timestamp, adc)
    plt.savefig(filename)
    plt.show()

if __name__ == '__main__':
    #single_channel_adc_vs_time(8722772, sys.argv[1], 'plots/')
    boxplot(sys.argv[1], False, 'good_jsons/', 'plots/')
    boxplot(sys.argv[1], True, 'good_jsons/', 'plots/')
    mean_overlay_hist(sys.argv[1], False, 'good_jsons/', 'plots/')
    mean_overlay_hist(sys.argv[1], True, 'good_jsons/', 'plots/')
    std_overlay_hist(sys.argv[1], False, 'good_jsons/', 'plots/')
    std_overlay_hist(sys.argv[1], True, 'good_jsons/', 'plots/')
    #for i in range(0, 7):
    #    single_mean_hist(sys.argv[1], i, False)
    #    single_mean_hist(sys.argv[1], i, True)
