#README: So, I did a bad job of naming this program. 
# fileExplorer.py enters a specified folder and uploads .json documents into a specified CouchDB database.
# Currently, the local CouchDB is the server to which fileExplorer sends data

import os
import sys
import couchdb
from couchdb import *
import json
from glob import iglob
import datetime
import argparse

#import webbrowser
#import Tkinter, tkFileDialog as tk

parser = argparse.ArgumentParser(description="Transfer and/or update JSON files from select directory into select CouchDB database.")
parser.add_argument("-e", "--explicit", action="store_true", help="Use to explicity choose directory and database")
parser.add_argument("-a", "--auto", action="store_true", help="Use for automated delivery of philpapers to philpapers database")
parser.add_argument("-nf", "--numFiles", action="store_true", help="Get the number of items within a specified directory")
parser.add_argument("-nj", "--numJson", action="store_true", help="Get the number of JSON files within a specified directory")
parser.add_argument("-pf", "--printFiles", action="store_true", help="Print the names of items within a specified directory")
parser.add_argument("-ls", "--lastSync", action="store_true", help="Get the time when directory was last synced with database or false if none")
args = parser.parse_args()

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
                lastSync = datetime.datetime.strptime(file.read(), "%Y-%m-%d %H:%M:%S.%f") #Read file containing string representation of last update time and convert it to timedate object
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
    def setupDB(self, path, database=None):
        auto = None
        if database == None: # If no database value, this is explicit run
            auto = False
        else:
            auto = True
        
        print "Wait...\n...\n..."
        os.chdir(path) #MAKE 'path' CURRENT WORKING DIRECTORY
        
        x = 0
        for file in iglob("*.*"):
            x += 1  
        print "\nItems in directory: " + str(x) + "\n"

#        dbLocation = raw_input("Enter CouchDB Location: ")
        couch = couchdb.Server()
        
        print "Connected to local database."
        if auto == False:
            response = raw_input("Continue <y/n> ")
            if response != "y":
                return;

        if database == None:
            database = raw_input("Enter Database: ")
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
                id = document.get("id") 
                document["_id"] = id #Set Document _id field
                if id in db: # Check if file is already in database
                    if lastSync < datetime.datetime.fromtimestamp(os.path.getmtime(file)):
#                            del db[id] # Delete existing doc in database
                        document["_rev"] = db[document["_id"]].get("_rev") # Pull _rev from existing doc on db and add it to updated doc to avoid conflict error
                        db.save(document) # Add updated doc to database with same id
                else:
                    db.save(document)
                    
            y += 1
            print "\r Status ___________ %f" %(y/x * 100) + "%",
        
        print "\n"

        db.commit() # Ensure changes are physically stored

        self.updateLastSync(path) # UPDATE TIME OF LAST SYNC



    def getNumFiles(self, path): #Return number of files within directory
        files = 0
        for thing in os.listdir(path):
            files += 1
        return files

    def getNumJson(self,path):
        jFiles = 0
        for file in os.listdir(path):
            if file.endswith(".json"):
                jFiles += 1
        return jFiles

    def getNoJson(self, path): #Print any files that are not json files and print number of json files
        x = 0
        os.chdir(path)
        for file in iglob("*.*"):
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


print "\nHello. Prepare to move jSON files from one directory to a couchDB database!"
print "...\n"

fileEx = fileExplorer() #Create instance of fileExplorer

if args.explicit:
    data_path = fileEx.getFileFolder()
    fileEx.setupDB(data_path)

elif args.auto:
#    data_path = "/var/inphosemantics/data/20130522/philpapers/raw"
    data_path = "/var/inphosemantics/data/20130522/philpapers/raw"
    database = "philpapers"
    fileEx.setupDB(data_path, database=database)

if args.numFiles:
    data_path = fileEx.getFileFolder()
    print "Files in %s: " %data_path + str(fileEx.getNumFiles(data_path))

if args.numJson:
    data_path = fileEx.getFileFolder()
    print "JSON files in %s: " %data_path + str(fileEx.getNumJson(data_path))

if args.printFiles:
    data_path = fileEx.getFileFolder()
    fileEx.printFiles(data_path)

if args.lastSync:
    data_path = fileEx.getFileFolder()
    lastSync = fileEx.getLastSync(data_path)
    if lastSync == datetime.datetime.min:
        print "No lastSync.txt file in %s" %data_path
    else:
        print "%s last synced " %data_path + str(lastSync)

else:
	print "Proper argument not given."

print "Complete."


#def main():
#    fileEx.printFiles(data_path)
#    fileEx.setupDB(data_path)
#    fileEx.getNoJson(data_path)

#if __name__ == "__main__":
#    main()


#SOURCES
# Stack Overflow
# Python Documentation

