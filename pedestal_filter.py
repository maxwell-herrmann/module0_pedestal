import sys
import json
import re
import numpy as np

def np_encoder(object):
    if isinstance(object, np.generic):
        return object.item()

def unique2key(unique):
    channel_id=unique%64
    chip_id = (unique//64) % 256
    io_channel = (unique //(64*256))%256
    io_group = (unique // (64*256*256)) %256
    return channel_id, chip_id, io_channel, io_group

def good_channel(unique, channelList):
    outs=[]
    good=True
    f=open(channelList, 'r')
    channel_id, chip_id, io_channel, io_group = unique2key(unique)
    for file in f:
        f1=open('bad_channel_files/'+file.strip(), 'r')
        out=json.loads(f1.read())
        if str(io_group)+'-'+str(io_channel)+'-'+str(chip_id) in out:
            if channel_id in out[str(io_group)+'-'+str(io_channel)+'-'+str(chip_id)]:
                good=False
                #print('Bad one!')
            if channel_id in out['All']:
                good=False
        if channel_id in out['All']:
            good=False
            #print('Bad one!')
            f1.close()
    f.close()
    return good

def good_channel_jsons(jsonList, channelList):
    f=open(jsonList, 'r')
    lines=f.readlines()
    f.close()
    for file in lines:
        name=file.strip()
        print('Opening ' + name)
        name1='jsons/'+name
        name2='good_jsons/'+name[:-5]+'_good.json'
        f1=open(name1, 'r')
        out=json.loads(f1.read())
        out1=[x for x in out if good_channel(x[0], channelList)]
        f1.close()
        print('Writing ' + name2)
        f2=open(name2, 'w')
        f2.write(json.dumps(out1, default=np_encoder))
        f2.close()
good_channel_jsons(sys.argv[1], sys.argv[2]) 
