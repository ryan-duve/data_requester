#!/usr/bin/python3
import mysql.connector
import datetime
import os #for current working directory
import sys #for error catching

#DataFileCreator
#receives device set and date/time range and creates file of DB query results

class DataFileCreator:

    #if device_set and timestamps are valid, save as class data attributes
    def __init__(self,device_set,timestamps):

        #make sure there are devices and timestamps
        if not device_set or not timestamps:
            print("Empty submitted field\ndevices:", device_set,"\ntimestamps:",timestamps)
            exit()

        #get all valid devices from DB
        cur = self.dbCursor()
        cur.execute("SELECT DISTINCT device FROM slowcontrolreadings")

        #flatten valid devices: [['d1'],['d2'],['d3]] => ['d1','d2','d3']
        valid_devices = set([d for a in cur.fetchall() for d in a])

        #check if all requested devices in set are valid
        invalid_devices = device_set.difference(valid_devices)
        if invalid_devices:
            print("Requested devices",invalid_devices,"not in database.")
            exit()

        #build and order device list from device set
        #list is ordered so data file name is uniquely determined
        device_list = [i for i in device_set]
        device_list.sort()

        #enforce exactly two timestamps
        if len(timestamps) != 2:
            print(timestamps,"must have exactly two timestamps")
            exit()

        #try turning timestamps into datetime objects
        try:
            datetimes = [datetime.datetime.strptime(ts,'%Y-%m-%d %H:%M:%S') for ts in timestamps]
        except ValueError:
            print("Timestamps",timestamps,"do not have the form 'YYYY-MM-DD HH:MM:SS'")
            exit()

        #set begTime and endTime
        datetimes.sort()
        begTime=datetimes[0]
        endTime=datetimes[1]

        #reject identical datetimes
        if begTime==endTime:
            print("The two times",[i.isoformat(sep=" ") for i in (begTime,endTime)],"must be different.")
            exit()

        #build filename with format: CURRENT_TIME-DEV_LIST-BEG_TIME-END_TIME.dat
        #e.g., 20150120_120000-dev1_dev2_dev3-20150101_000000-to-20150101_235959.dat
        device_string = "_".join(device_list) #dev1_dev2_dev3
        nowTime = datetime.datetime.now()
        file_times = [t.strftime("%Y%m%d_%H%M%S") for t in (nowTime,begTime,endTime)]
        filename = "-".join([file_times[0],device_string,file_times[1],"to",file_times[2]])+".dat"

        #set class attributes
        self.devices = device_list
        self.begTime = datetimes[0]
        self.endTime = datetimes[1]
        self.filename = filename
        cwd = os.getcwd() #no trailing slash
        #self.filepath = os.path.join(cwd,'dat','')#adds trailing slash
        self.filepath = '/tmp/dat/' #can't get file perms to work with above

        #make the file, return number of lines written
        return self.executeQuery()

    #returns cursor to MySQL database
    def dbCursor(self):
        #return cursor if already existing
        if not hasattr(self,'con'):
            #get all valid devices from DB
            self.con = mysql.connector.connect(
                    host = "localhost",
                    user = "dnp",
                    database = "slowcontrols")
        return self.con.cursor()

    #stores data in file and returns number of data points
    def executeQuery(self):

        output = self.filepath+self.filename
        print(output)
        begTimeSQL = self.begTime.strftime('%Y-%m-%d %H:%M:%S')
        endTimeSQL = self.endTime.strftime('%Y-%m-%d %H:%M:%S')

        #submit query
        cur = self.dbCursor()
        placeholders = ','.join('%s' for d in self.devices) # makes => %s,%s,%s,..
        query = """
            SELECT 'device', 'measurement_reading', 'created_at'
            UNION ALL
            SELECT device, measurement_reading, created_at
            FROM slowcontrolreadings
            WHERE device IN (%s)
            AND (created_at BETWEEN '%s' AND '%s')
            ORDER BY created_at DESC
            INTO OUTFILE '%s'
            FIELDS TERMINATED BY ','
            LINES TERMINATED BY '\\n';
            """ % (placeholders,begTimeSQL,endTimeSQL,output)
        try:
            cur.execute(query,self.devices)
            self.nLines = cur.rowcount
        except:#generic error catcher:https://wiki.python.org/moin/HandlingExceptions
            e = sys.exc_info()[0]
            print("Failed to execute query: %s\n\nError Message:%s",(query,e))
            exit()

    def getNLines(self):
        return self.nLines

    def getFilePath(self):
        return self.filepath

    def getFileName(self):
        return self.filename

    def cleanUp(self):
        if self.con:
            self.con.close()

if __name__ == "__main__":
    device_set = set(['dev1','dev3'])
    timestamps = ['2015-01-25 00:00:01','2016-01-25 09:38:00']
    file_creator = DataFileCreator(device_set,timestamps)
    print(file_creator.getFileName())
    print(file_creator.getNLines())
    file_creator.cleanUp() #delete MySQL connection
