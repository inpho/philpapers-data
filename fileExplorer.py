#README: So, I did a bad job of naming this program. 
# fileExplorer.py enters a specified folder and uploads .json documents into a specified CouchDB database.
# Currently, the local CouchDB is the server to which fileExplorer sends data

import datetime
from glob import iglob, glob
import json
import os
import os.path
import sys

import couchdb
from couchdb import *

#import webbrowser
#import Tkinter, tkFileDialog as tk

class fileExplorer:
#    Class that represents a file folder containing JSON documents

    fileFolder = None #Path of file folder

    #Obtain path to folder in which .json documents are located
    def getFileFolder(self):
        global fileFolder
        fileFolder = raw_input("Enter file folder path: ")
        if fileFolder == "":
            return self.getFileFolder()
        else:
        	return fileFolder

    #getLastSync returns the time when documents were last updated according to lastSync.txt
    # if lastSync.txt does not exist return 0
    def getLastSync(self, path):
        lastSyncFile = os.path.join(path, "lastSync.txt")
        if os.path.isfile(lastSyncFile):
            with open(lastSyncFile) as file:
                lastSync = datetime.datetime.strptime(file.read(), "%Y-%m-%d %H:%M:%S.%f") 
                    #Read file containing string representation of last update time and convert it to timedate object
                return lastSync
        else:
            return datetime.datetime.min

    #updateLastSync updates the lastSync.txt file with the current time - the time of the most recent update.
    def updateLastSync(self, path):
        lastSyncFile = os.path.join(path, "lastSync.txt")
        with open(lastSyncFile, "w+") as file:
            file.write(str(datetime.datetime.now())) #Write Current time to file - overwrite any current time or contents

    #SETUP Database - CouchDB and ADD JSON FILES TO COUCH 
    #path is file path of .json documents
    def setupDB(self, path, database=None, username=None, password=None, host=None, auto=False):
             
        print "Wait...\n...\n..."
        os.chdir(path) #MAKE 'path' CURRENT WORKING DIRECTORY
        
        x = 0
        for file in iglob("*.*"):
            x += 1  
        print "\nItems in directory: " + str(x) + "\n"

        if not host == None and not username == None:
            couch = couchdb.Server("http://"+username+":"+password+"@"+host+":5984")
        elif not host == None:
            couch = couchdb.Server("http://"+host+":5984")
        elif username == None and password == None:
            couch = couchdb.Server()
        else:
            couch = couchdb.Server("http://"+username+":"+password+"@127.0.0.1:5984")
        
        print "Connected to local database."
        if auto == False:
            response = raw_input("Continue <y/n> ")
            if response != "y":
                return;

        if database in couch: #Checks if entered db exists on server
            db = couch[database]
        else:
            db = couch.create(database)
        print database + " database opened.\n"
        
        #CHECK IF READY TO CONTINUE if an explicit run
        if auto == False:
            response = raw_input("Continue <y/n> ")
            if response != "y":
                return;

        print "\nAdding files to " + database + "\n"
        # Add json files to couchDB db --------->

        #FIRST: obtain time of last update
        lastSync = self.getLastSync(path)
        y = 0
        for file in iglob("*.json"): #Only worries about .json files
            # Load file as json, add _id element, add file to couchdb
            with open(file) as temp: #File is automatically CLOSED with 'with'
                document = json.load(temp)
		if document.get("id") is not None:
                    id = document.get("id") #THIS PROGRAM ASSUMES jSON HAS id FIELD!
                    document["_id"] = id #Set Document _id field
                    if id in db: # Check if file is already in database
                        if lastSync < datetime.datetime.fromtimestamp(os.path.getmtime(file)):
    #                       del db[id] # Delete existing doc in database
                            document["_rev"] = db[document["_id"]].get("_rev") # Pull _rev 
                           #from existing doc on db and add it to updated doc to avoid conflict error

                db.save(document)
                    
            y += 1
            print "\r Status ___________ %f" %(y/x * 100) + "%",
        
        print "\n"

        db.commit() # Ensure changes are physically stored

        self.updateLastSync(path) # UPDATE TIME OF LAST SYNC

    def directoryDelve(self, path, database, username, password, host, auto):
        """Search through a given directory and all internal directories for 
            .json documents and copy them to specified database"""
        
        for thing in iglob(os.path.join(path, "*")):
            if os.path.isdir(thing):
                self.directoryDelve(thing, database, username, password, host, auto)

        self.setupDB(path, database=database, username=username, password=password, host=host, auto=auto)


    def getNumFiles(self, path):
        """ Return number of files within directory """
        return len(os.listdir(path))

    def getNumJson(self,path):
        return len(glob(os.path.join(path, "*.json")))

    def getNoJson(self, path): #Print any files that are not json files and print number of json files
        x = 0
        os.chdir(path)
        for file in iglob("*.json"):
            if file.endswith(".json"):
                x += 1
            else:
                print file
        print "\n" + str(x) + " files are json files"

    def printFiles(self, filePath): #Print files within filePath
#        x = 0
        for file in os.listdir(filePath): #Lists names of items in directory - does not give actual items
#            x += 1
            print file

#        y = 0
#        for file in os.listdir(filePath):
#            y += 1
#            print "\rStatus __________ %d" %(y/x * 100) + "%",

        print ("\n")


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="""
        Transfer and/or update JSON files from select directory into select CouchDB
        database.""")
    parser.add_argument("-e", "--explicit", action="store_true", 
        help="Use to explicity choose directory and database")
    parser.add_argument("-a", "--auto", action="store_true", 
        help="Use for automated delivery of philpapers to philpapers database")
    parser.add_argument("-t", "--tree", action="store_true",
        help="Use to deliver all .json files within a directory and its internal directories to a specified database")
    parser.add_argument("-nf", "--numFiles", action="store_true", 
        help="Print the number of items within a specified directory")
    parser.add_argument("-nj", "--numJson", action="store_true", 
        help="Print the number of JSON files within a specified directory")
    parser.add_argument("-pf", "--printFiles", action="store_true", 
        help="Print the names of items within a specified directory")
    parser.add_argument("-ls", "--lastSync", action="store_true", 
        help="Print the time when directory was last synced with database or false if none")
    args = parser.parse_args()
    
    print "\nHello. Prepare to move jSON files from one directory to a couchDB database!"
    print "...\n"
    
    fileEx = fileExplorer() #Create instance of fileExplorer
    
    if args.auto:
        data_path = "/var/inphosemantics/data/20130522/philpapers/raw"
        database = "philpapers"
        fileEx.setupDB(data_path, database=database, username=None, password=None, host=None, auto=True)
    else:
        data_path = fileEx.getFileFolder()
        host = raw_input("Enter CouchDB host (Hit Enter if local): ")
        if host == "":
            host = None
        username = raw_input("Enter CouchDB username (Hit Enter if none): ")
        if username == "":
            username = None
        password = raw_input("Enter CouchDB password (Hit Enter if none): ")
        if password == "":
            password = None

        database = raw_input("Enter CouchDB databse to write .json files to: ")

    if args.explicit:
        fileEx.setupDB(data_path, database=database, username=username, password=password, host=host, auto=False)

    if args.tree:
        fileEx.directoryDelve(data_path, database, username, password, host, True)

    # print the number of files
    if args.numFiles:
        print "Files in %s: " %data_path + str(fileEx.getNumFiles(data_path))
    
    if args.numJson:
        print "JSON files in %s: " %data_path + str(fileEx.getNumJson(data_path))
    
    if args.printFiles:
        fileEx.printFiles(data_path)
    
    if args.lastSync:
        lastSync = fileEx.getLastSync(data_path)
        if lastSync == datetime.datetime.min:
            print "No lastSync.txt file in %s" %data_path
        else:
            print "%s last synced " %data_path + str(lastSync)
    
    if not len(sys.argv) > 1:
        print "Proper argument not given."

    print "Complete."


#SOURCES
# Stack Overflow
# Python Documentation

