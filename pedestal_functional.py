import h5py
import numpy as np
import sys
import json
from functools import reduce
from collections import defaultdict
import os

#_excluded_channels = [6,7,8,9,22,23,24,25,38,39,40,54,55,56,57]

def unique_channel_id(io_group, io_channel, chip_id, channel_id):
    return channel_id + 64*(chip_id + 256*(io_channel + 256*(io_group)))

def unique2key(unique):
    channel_id=unique%64
    chip_id=(unique/64)%256
    io_channel = (unique //(64*256))%256
    io_group = (unique //(64*256*256)) % 256
    return channel_id, chip_id, io_channel, io_group

def getKey(item):
    return item[0]

def np_encoder(object):
    if isinstance(object, np.generic):
        return object.item()

def good_channel(unique, channelList):
    good=True
    f=open(channelList, 'r')
    channel_id, chip_id, io_channel, io_group = unique2key(unique)
    for file in f:
        f1=open('bad_channel_files/'+file.strip(), 'r')
        out=json.loads(f1.read())
        a=str(io_group)+'-'+str(io_channel)+'-'+str(io_group)+'-'+str(chip_id)
        if a in out:
            if channel_id in out[a]:
                good=False
            if channel_id in out['All']:
                good=False
        if channel_id in out['All']:
            good=False
        f1.close()
    f.close()
    return good

def convert(filename):

    print('Opening',filename)
    f = h5py.File(filename,'r')

    data_mask = f['packets'][:]['packet_type'] == 0
    valid_parity_mask = f['packets'][data_mask]['valid_parity'] == 1
    good_data = (f['packets'][data_mask])[valid_parity_mask]

    out = sorted(list(map(lambda x: (unique_channel_id(x['io_group'], x['io_channel'], x['chip_id'], x['channel_id']), x['timestamp'], x['dataword']), good_data)), key=getKey)

    d = defaultdict(list)

    for k, *v in out:
        d[k].append(v)

    out = list(d.items())
    out = list(map(lambda x: [x[0]] + [list(y) for y in zip(*x[1])], out))
    out = list(map(lambda x: (x[0], np.mean(x[2]), np.std(x[2])), out))

    #out=[x for x in out if good_channel(x[0], channelFileList)]


    #removed=0
    #for x in out:
    #    if x[0] in excluded_uniques or x[0]%64 in excluded_channels:
    #        out.remove(x)
    #        removed+=1
    #print(removed)

    f.close()
    return out

def main(dataFileList):
    
    #excluded_uniques=[]
    #excluded_channels=[]

    #g = open(channelFileList, 'r')

    #for file in g:
    #    g1=open('bad_channel_files/'+file.strip(), 'r')
    #    out=json.loads(g1.read())
    #    for x in out:
    #        if x!='All':
    #            io_group, io_channel, chip_id = [int(y) for y in x.split('-')]
    #            for channel_id in out[x]:
    #                excluded_uniques.append(unique_channel_id(io_group, io_channel, chip_id, channel_id))
    #    for x in out['All']:
    #        if x not in excluded_channels:
    #            excluded_channels.append(x)
    #    g1.close() 

    f = open(dataFileList, "r")

    for file in f:
        f1 = open('jsons/'+file.strip()[:-3]+"-summary.json", "w+")
        out=convert('datalogs/'+file.strip())
        #out=[x for x in out if good_channel(x[0], channelFileList)]
        f1.write(json.dumps(out, default=np_encoder))
        f1.close()
    f.close()

def filter(jsonList, channelList):
    f=open(jsonList, 'r')
    lines=f.readlines()
    f.close()
    for file in lines:
        name=file.strip()
        name1='jsons/'+name
        name2='jsons/'+name[:-5]+'_good.json'
        print('Filtering ' + name1)
        f1=open(name1, 'r')
        out=json.loads(f1.read())
        out1=[x for x in out if good_channel(x[0], channelList)]
        f1.close()
        print('Writing ' + name2)
        f2=open(name2, 'w')
        f2.write(json.dumps(out1, default=np_encoder))
        f2.close()

if __name__ == '__main__':
    main(sys.argv[1])
    #filter(sys.argv[3], sys.argv[2])
    # convert(*sys.argv[1:], excluded_channels=_excluded_channels, std_threshold = 4)
