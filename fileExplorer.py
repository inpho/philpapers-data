#README: So, I did a bad job of naming this program. 
# fileExplorer.py enters a specified folder and uploads .json documents into a specified CouchDB database.

import datetime
from glob import iglob, glob
import json
import os
import os.path
import sys

import couchdb

#import webbrowser
#import Tkinter, tkFileDialog as tk

class fileExplorer(object):
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

    #SETUP Database - CouchDB    
    #path is file path of .json documents
    def setupDB(self, path, database=None, username=None, password=None, host=None, auto=False, silent=False):
        
        if not silent:             
            print "Wait...\n...\n..."
#        os.chdir(path) #MAKE 'path' CURRENT WORKING DIRECTORY
        
#        x = 0
#        for file in iglob("*.*"):
#            x += 1  
#        if not silent:
#            print "\nItems in directory: " + str(x) + "\n"

        if not username == None:
            couch = couchdb.Server("http://"+username+":"+password+"@"+host)
        else:
            couch = couchdb.Server("http://"+host)
        
        if not silent:
            print "Connected to local database."
        if auto == False:
            response = raw_input("Continue <y/n> ")
            if response != "y":
                return;

        if database in couch: #Checks if entered db exists on server
            db = couch[database]
        else:
            try:
                db = couch.create(database)
            except couchdb.Unauthorized:
                sys.exit("No or improper credentials given.")
        
        if not silent:
            print database + " database opened.\n"
            #CHECK IF READY TO CONTINUE if an explicit run
        if auto == False:
            response = raw_input("Continue <y/n> ")
            if response != "y":
                return;
        print "\nAdding files to " + database + "\n"

        return db

    def fillDB(self, path, db, silent=False):
        """Copy JSON files from given 'path' to given couchDB db"""
        # DB refers to instance of CouchDB database

        # Add json files to couchDB db --------->

        os.chdir(path) #MAKE 'path' CURRENT WORKING DIRECTORY

        #FIRST: obtain time of last update
        lastSync = self.getLastSync(path)
#        y = 0
        for file in iglob("*.json"): #Only worries about .json files
            skip=False
            # Load file as json, add _id element, add file to couchdb
            with open(file) as temp: #File is automatically CLOSED with 'with'
                document = json.load(temp)
                if document.get("id") is not None:
                    id = document.get("id") #THIS PROGRAM ASSUMES jSON HAS id FIELD!
                    document["_id"] = id #Set Document _id field
                    if id in db: # Check if file is already in database
                        if lastSync < datetime.datetime.fromtimestamp(os.path.getmtime(file)):
                            #del db[id] # Delete existing doc in database
                            document["_rev"] = db[document["_id"]].get("_rev") 
                            # Pull _rev from existing doc on db and add it to updated doc to avoid conflict error
                        else:
                            skip=True
                if not skip:
                    try:
                        db.save(document)
                    except couchdb.Unauthorized:
                        sys.exit("No or improper credentials given.")
                    
#            y += 1
#            print "\r Status ___________ %f" %(y/x * 100) + "%",
        
        if not silent:
            print "\n"

        db.commit() # Ensure changes are physically stored

        self.updateLastSync(path) # UPDATE TIME OF LAST SYNC

    def directoryDelve(self, path, cdb, silent, explicit):
        """Search through a given directory and all internal directories for 
            .json documents and copy them to specified database"""

        self.fillDB(path, cdb, silent=silent)

        if not explicit: # Remember, explicit means only given directory is of any
                         # concern, subdirectories are not searched.
            for thing in iglob(os.path.join(path, "*")):
                if os.path.isdir(thing):
                    self.directoryDelve(path, cdb, silent, explicit)


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
        for file in os.listdir(filePath): #Lists names of items in directory - does not give actual items
            print file

        print ("\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="""
        Transfer and/or update JSON files from select directory into select CouchDB
        database.""")
    
    # Positional argument, directory to search.
    parser.add_argument("directory", type=str, default=None, help="""Used to provide
        name of directory in which JSON files are located""")

    # JSON file copying functions
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-l", "--loud", action="store_const", const="loud", dest="mode",
        help="""Use to deliver all .json files within a directory and its internal 
            directories to a single specified database""")
    group.add_argument("-q", "--quiet", action="store_const", const="quiet",
        help="""Performs same task as 'tree' but with no text printed to screen""", 
        dest="mode")

    # For Explicit addition of JSON documents within a directory into a CouchDB without
    # sifting through subdirectories
    group.add_argument("-e", "--explicit", action="store_const", const="explicit",
        help="""Use to explicity choose directory and database. Adds only json files 
            in specified directory, not in subdirectories""", dest="mode")
#    group.add_argument("-a", "--auto", action="store_true", dest="mode",
#        help="Use for automated delivery of philpapers to philpapers database")

    # Database and Directory Information
    parser.add_argument("-s", "--server", type=str, default="127.0.0.1:5984", help="""
        Used to specify a CouchDB server if it is not local""")
    parser.add_argument("-u", "--username", type=str, help="""Used to provide username
        for CouchDB if one exits""")
    parser.add_argument("-p", "--password", type=str, help="""Used to provide password
        for CouchDB if one exits""")
    parser.add_argument("-db", "--database", type=str, help="""Used to provide name of
        CouchDB database to which files will be transfered""")

    # Debugging flags
    parser.add_argument("-nf", "--numFiles", action="store_true",
        help="Print the number of items within a specified directory")
    parser.add_argument("-nj", "--numJson", action="store_true", 
        help="Print the number of JSON files within a specified directory")
    parser.add_argument("-pf", "--printFiles", action="store_true", 
        help="Print the names of items within a specified directory")
    parser.add_argument("-ls", "--lastSync", action="store_true", 
        help="Print the time when directory was last synced with database or false if none")
    args = parser.parse_args()

    if not (args.numFiles or args.numJson or args.printFiles or args.lastSync):
        if not args.mode:
            args.mode = "loud"
    
    print "\nHello. Prepare to move jSON files from one directory to a CouchDB database!"
    print "...\n"

    fileEx = fileExplorer() #Create instance of fileExplorer
    
    database = args.database
    data_path = args.directory
    host = args.server
    username = args.username
    password = args.password

    if args.mode:
        # If no database or data_path given, ask for them!
        if data_path is None:
            data_path = fileEx.getFileFolder()
        if database is None:
            database = raw_input("Enter CouchDB databse to write .json files to: ")

    if args.mode == "loud":
        print "sweet."
        # cdb is the CouchDB database to be modified/created/filled
        cdb = fileEx.setupDB(path, database=database, username=username, password=password, host=host, auto=auto, silent=silent)
        fileEx.directoryDelve(data_path, cdb, False, False)

    if args.mode == "quiet":
        print "..."
        # cdb is the CouchDB database to be modified/created/filled
        cdb = fileEx.setupDB(path, database=database, username=username, password=password, host=host, auto=auto, silent=silent)
        fileEx.directoryDelve(data_path, cdb, True, False)

    if args.mode == "explicit":
        cdb = fileEx.setupDB(data_path, database=database, username=username, password=password, host=host, auto=False, silent=False)
        fileEx.directoryDelve(data_path, cdb, False, True)

#    if args.auto: #Run auto code
#        data_path = "/var/inphosemantics/data/20130522/philpapers/raw"
#        database = "philpapers"
#        fileEx.setupDB(data_path, database=database, username=None, password=None, host=None, auto=True)

    # DEBUGGING FLAGS
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

    
    print "Complete."


#SOURCES
# Stack Overflow
# Python Documentation

