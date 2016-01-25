#!/usr/bin/python3
#DataRequestHandler.py

import os.path
from DataFileCreator import DataFileCreator

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
        #check existence of data file
        if not os.path.isfile(data_filename):
            print("File not found: '%s'\n" % data_filename)
            exit()

        #check if nLines > 1
        if self.fc.getNLines() == 1:
            print("No data points in file: '%s'\n" % data_filename)

        #make graph

        

if __name__ == "__main__":
    create_data_preview = True
    drh = DataRequestHandler(set(['dev1','dev3']),['2015-01-19 00:00:01','2016-01-11 17:52:00'])
    if create_data_preview:
        print("creating data preview")
    drh.makeDataPreview()
