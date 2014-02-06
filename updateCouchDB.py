import couchdb
from couchdb import *
import json
import tarfile

from fileExplorer import fileExplorer


# Provide commentary!

def updateDB():
#   Connect to server - no args means local connection
    couch = couchdb.Server()
#   Commentary:
    print "Connected to CouchDB"
#   Ask for database to connect to or create:
    userInput = raw_input("Enter Database: ")
    if userInput in couch: #Checks if entered db exists on server
        db = couch[userInput]
    else:
        db = couch.create(userInput)
    print userInput + " database opened."
    
    sample = tarfile.open("C://Users/Saggu/Downloads/sample.tar")
    sampleFiles = sample.getmembers()

    for file in sampleFiles:
        #Extract file from tarfile
        exFile = sample.extractfile(file)
        #Deserialize the extracted ExFileObject into JSON object
        document = json.load(exFile)

        print "Adding document " + document.get("id")
        
        #Create '_id' field and set it equal to 'id' field in json document
        document["_id"] = document.get("id")
        document["testerspace"] = "WAZZUP"
        #Add document to specified CouchDB db
        if document["_id"] not in db:
            _id, _rev = db.save(document)
        else:
            del db[document.get("id")]
            db.save(document)
            _id = document.get("id")
        print "Document %s added succesfully" %_id

#   Useful for parsing through JSON docs
#    for key, value in doc.iteritems():
#        print key, value

    print "Success"


def main():
    updateDB()

#    print "Sup?"

    
if __name__ == "__main__":
    main()


#SOURCES
    #docs.python.org
    #philpapers.py by Jaimie Murdock
    #StackOverflow