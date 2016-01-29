#!/usr/bin/python3
#DataRequestHandler.py

import os.path
from DataFileCreator import DataFileCreator
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import matplotlib.pyplot as plt 
import matplotlib.dates as md
import csv
import json
import datetime

# A Python script called by PHP with data request variables instantiates this
# class.  DataRequestHandler is responsible for managing the user's data
# request preferences/parameters and returning server resources to the web
# browser.

#create device_set (set) and timestamps (list) from user input

class DataRequestHandler:

    #prefix user_ denotes unsanitized string from user
    def __init__(self,user_device_set,user_timestamps):
        self.fc = DataFileCreator(user_device_set, user_timestamps)
        print("Created %s with %s lines of data\n",(self.fc.getFileName(),self.fc.getNLines()))
        self.fc.cleanUp()

    def makeDataPreview(self):
        data_filename = self.fc.getFilePath()+self.fc.getFileName()
        print('data_filename=%s'%data_filename)
        #check existence of data file
        if not os.path.isfile(data_filename):
            print("File not found: '%s'\n" % data_filename)
            exit()

        #check if nLines > 1
        if self.fc.getNLines() == 1:
            print("No data points in file: '%s'\n" % data_filename)
            exit()

        #create dict for matplotlib
        readings = self.makeDictFromFile(data_filename)
        d1Data = list(zip(*readings["dev1"]))
        #print(d1Data)
        ts_format = '%Y-%m-%d %H:%M:%S'
        times = [datetime.datetime.strptime(ts,ts_format) for ts in d1Data[0]]
        print(times)


        #----------begin making the plot----------
        
        print("Begin making plot\n")
        nDev = len(self.fc.devices)

        host = host_subplot(111,axes_class = AA.Axes)

        host.set_xlabel("Time",labelpad=20)
        ax = plt.gca()
        #http://stackoverflow.com/a/4091264/1717828
        xfmt = md.DateFormatter('\n\n%m-%d\n%H:%M:%S')
        ax.xaxis.set_major_formatter(xfmt)

        host.set_ylabel(self.fc.devices[0])

        plot0, = host.plot(times,d1Data[1],marker='o')

        plt.draw()
        plt.show()
        #----------plot drawing finished----------

    def makeDictFromFile(self,data_filename):
        #make dictionary of readings
        #{
        #    "evapSi":[
        #        ['2016-01-29 00:00:00','3'],
        #        ['2016-01-29 00:00:01','4']
        #        ],
        #    "he3Flow"[
        #        ['2016-01-29 00:00:00','3'],
        #        ['2016-01-29 00:00:01','4']
        #        ],        
        #    "evapPress"[
        #        ['2016-01-29 00:00:00','3'],
        #        ['2016-01-29 00:00:01','4']
        #        ['2016-01-29 00:00:02','8']
        #        ],        
        #    ]
        #}
        dev_list = self.fc.devices

        readings = {device:[] for device in dev_list}
        with open(data_filename, mode='r') as infile:
            reader = csv.reader(infile)
            next(reader,None) #skip header
            for d,v,t in reader:
                readings[d].append([t,v])

        #print(json.dumps(readings,sort_keys=True,indent=2))
        return readings



        

if __name__ == "__main__":
    create_data_preview = True
    drh = DataRequestHandler(set(['dev1','dev2','dev3']),['2016-01-24 00:00:01','2016-01-27 10:52:00'])
    if create_data_preview:
        print("creating data preview")
        drh.makeDataPreview()
