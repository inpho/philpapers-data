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
        if fileFolder == "":
            return self.getFileFolder()
        else:
            return fileFolder

    def printFiles(self, filePath): #TEST METHOD
        os.chdir(filePath)
        files = glob("*.*") #Lists names of items in directory - does not give actual items
        for file in files:
            print file

        print "\nMade it...\n"

        for file in os.listdir(filePath):
            print file
#            y += 1
#            print "\rStatus __________ %d" %(y/x * 100) + "%",

        print ("\n")

    #SETUP Database - CouchDB and ADD JSON FILES TO COUCH 
    def setupDB(self, path):
        print "Wait...\n...\n..."

        x = 0
        os.chdir(path)
        for file in glob("*.*"):
            if file.endswith(".docx"):
                print file
                x += 1

        print "\n" + str(x) + "\n"

#        dbLocation = raw_input("Enter CouchDB Location: ")
        couch = couchdb.Server()
        
        print "Connected to local database.\n"
        response = raw_input("Continue? <y/n> ")
        if response != "y":
            return

        database = raw_input("Enter Database: ")
        if database in couch: #Checks if entered db exists on server
            db = couch[database]
        else:
            db = couch.create(database)

        print database + " database opened.\n"

        #CHECK IF READY TO CONTINUE
        response = raw_input("Continue <y/n> ")
        if response != "y":
            return;

        print "\nAdding files to " + database + "\n"
        # Add json files to couchDB db
        y = 0
        for file in glob("*.*"):
            # Load file as json, add _id element, add file to couchdb
            if (file.endswith(".json")):
                temp = open(file)
                document = json.load(temp)
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


