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

#import webbrowser
#import Tkinter, tkFileDialog as tk

class fileExplorer:
#    Class that represents a file folder

    fileFolder = "empty"

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
    def setupDB(self, path):
        print "Wait...\n...\n..."
        os.chdir(path) #MAKE 'path' CURRENT WORKING DIRECTORY
        
        x = 0
        for file in iglob("*.*"):
            x += 1  
        print "\nItems in directory: " + str(x) + "\n"

#        dbLocation = raw_input("Enter CouchDB Location: ")
        couch = couchdb.Server()
        
        print "Connected to local database."
        response = raw_input("Continue <y/n> ")
        if response != "y":
            return;

        database = raw_input("Enter Database: ")
        if database in couch: #Checks if entered db exists on server
            db = couch[database]
        else:
            db = couch.create(database)
        print database + " database opened.\n"
        
        #CHECK IF READY TO CONTINUE
        response = raw_input("Continue <y/n> ")
        if response != "y":
            return
        else:
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
                    if id in db: # Check if file is already in database
                        if lastSync < datetime.datetime.fromtimestamp(os.path.getmtime(file)):
                            del db[id] # Delete existing doc in database
                            document["_id"] = id # Make sure '_id' field exists within document
                            db.save(document) # Add updated doc to database with same id
                    else:
                        document["_id"] = id
                        db.save(document)
                    
                y += 1
                print "\r Status ___________ %f" %(y/x * 100) + "%",
        
            print "\n"

            self.updateLastSync(path) # UPDATE TIME OF LAST SYNC


    def getNoJson(self, path): #Return any files that are not json files
        x = 0
        os.chdir(path)
        for file in iglob("*.*"):
            if file.endswith(".json"):
                x += 1
            else:
                print file
        print "\n" + str(x) + " files are json files"

    def printFiles(self, filePath): #TEST METHOD: Print files within filePath
        x = 0
        for file in os.listdir(filePath): #Lists names of items in directory - does not give actual items
            x += 1
            print file

        y = 0
        for file in os.listdir(filePath):
            y += 1
            print "\rStatus __________ %d" %(y/x * 100) + "%",

        print ("\n")

    def sayHi(self):    #Test Method
        print "Hi"
    
    @staticmethod   # Test Method: Static Method
    def sayHey():
        print "Hey"

    @staticmethod
    def testProgress():
        x = 0
        while x <= 1000:
            y = x/1000 * 100
            print "\r Status __________________ %d" %y + "%",
            x += 1

def main():
    print "\nHello. Prepare to move jSON files from one directory to a couchDB database!"
    print "...\n"

    fileEx = fileExplorer()
    data_path = fileEx.getFileFolder()

#    fileEx.printFiles(data_path)
#    fileEx.setupDB(data_path)
#    fileExplorer.testProgress()
#    fileEx.getNoJson(data_path)

    print "Complete."


if __name__ == "__main__":
    main()

#    folder = tk.askopenfile()
#    print folder
#    Tkinter._test()


#SOURCES
# Stack Overflow
# Python Documentation

