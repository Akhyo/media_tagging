#!/usr/bin/env python3
import pickle
import magic
import filerecord

datafile='filedata.test'

loadfile = open(datafile,'rb') 
pickle.load(loadfile)
loadfile.close()

#Do stuff

dumpfile = open(datafile,'wb')  
pickle.dump(filerecord.all_data, dumpfile)
dumpfile.close()

