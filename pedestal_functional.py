import h5py
import numpy as np
import sys
import json
from functools import reduce
from collections import defaultdict

#_excluded_channels = [6,7,8,9,22,23,24,25,38,39,40,54,55,56,57]
_excluded_uniques = []
_excluded_channels = []

def unique_channel_id(io_group, io_channel, chip_id, channel_id):
    return channel_id + 64*(chip_id + 256*(io_channel + 256*(io_group)))

def getKey(item):
    return item[0]

def np_encoder(object):
    if isinstance(object, np.generic):
        return object.item()

def convert(filename, excluded_uniques=None, excluded_channels=None):

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
    
    if excluded_uniques:
        for x in out:
            if x[0] in excluded_uniques:
                out.remove(x)
    if excluded_channels:
        for x in out:
            if x[0]%64 in excluded_channels:
                out.remove(x)
    f.close()
    return out

def main(dataFileList, channelFileList):
    
    g = open(channelFileList, 'r')
    for file in g:
        f1=open('bad_channel_files/'+file.strip(), 'r')
        out=json.loads(f1.read())
        for x in out:
            if x!='All':
                io_group, io_channel, chip_id = [int(y) for y in x.split('-')]
                for channel_id in out[x]:
                    _excluded_uniques.append(unique_channel_id(io_group, io_channel, chip_id, channel_id))
        for x in out['All']:
            if x not in _excluded_channels:
                _excluded_channels.append(x)
                        
    f = open(dataFileList, "r")

    for file in f:
        f1 = open('jsons/'+file.strip()[:-3]+"-summary.json", "w+")
        f1.write(json.dumps(convert('datalogs/'+file.strip(), _excluded_uniques, _excluded_channels), default=np_encoder))
        f1.close()

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
    # convert(*sys.argv[1:], excluded_channels=_excluded_channels, std_threshold = 4)
