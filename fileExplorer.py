import os
import sys
import couchdb
from couchdb import *
import json
from glob import iglob as glob

#import webbrowser
#import Tkinter, tkFileDialog as tk

class fileExplorer:
#    Class that represents a file folder

    fileFolder = "empty"

    def getFileFolder(self):
        global fileFolder
        fileFolder = raw_input("Enter file folder path: ")
        return fileFolder

    def printFiles(self, filePath): #TEST METHOD
        x = 0
        for file in os.listdir(filePath): #Lists names of items in directory - does not give actual items
            x += 1
        y = 0
        for file in os.listdir(filePath):
            y += 1
            print "\rStatus __________ %d" %(y/x * 100) + "%",

        print ("\n")

    #SETUP Database - CouchDB and ADD JSON FILES TO COUCH 
    def setupDB(self, path):
        print "Wait...\n...\n..."

        x = 0
        for file in glob(path):
            x += 1

#        dbLocation = raw_input("Enter CouchDB Location: ")
        couch = couchdb.Server()
        
        print "Connected to local database."

        database = raw_input("Enter Database: ")
        if database in couch: #Checks if entered db exists on server
            db = couch[database]
        else:
            db = couch.create(database)

        print database + " database opened.\n"

	#CHECK IF READY TO CONTINUE
	response = raw_input("Continue <y/n> ")
	if response == "y":
	        print "\nAdding files to " + database + "\n"
		# Add json files to couchDB db
	        y = 0
	        for file in glob(path):
	            # Load file as json, add _id element, add file to couchdb
	            if (file.endswith(".json")):
	                document = json.load(file)
	                document["_id"] = document.get("id")
	                db.save(document)

	            y += 1
	            print "\r Status ___________ %d" %(y/x * 100) + "%",
        
	        print "\n"


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
    print "Hello. Prepare to move jSON files from one directory to a couchDB database!"
    print "..."
    print "...\n"

    fileEx = fileExplorer()
    data_path = fileEx.getFileFolder()

#    fileEx.printFiles(data_path)

    fileEx.setupDB(data_path)

#    fileExplorer.testProgress()

    print "Complete."


if __name__ == "__main__":
    main()

#    folder = tk.askopenfile()
#    print folder
#    Tkinter._test()


#SOURCES
# Stack Overflow
# Python Documentation


