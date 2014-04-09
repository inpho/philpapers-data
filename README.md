Loran Saggu

First push 1/29/2014 at 2:30 PM

fileExplorer - Used to add philpapers on inphodata to local couchdb on 1/30/2014

2/5/2014 - fileExplorer updated - checks when files were last updated and is able to replace any old files with new versions
2/12/2014 - fileExplorer updated - updates old files more efficiently: not necessary to delete file then replace it
2/12/2014 - updateCouchDB updated - reflects changes that handle existing files in the DB and updates similarly to fileExplorer

2/12/2014 - fileExplorer updated - Includes argparse arguments: configuration may be automatic or manual

2/17/2014 - fileExplorer updated - Added argparse functionality!

3/14/2014 - fileExplorer updated - Cleaned up, able to descend file trees, new authentication ability for CouchDB Databases.

3/26/2014 - Fixed AttributeError issue with fileExplorer by adding json import to if __name__ == "__main__" section
3/26/2014 - Also adjusted code to handle json docs without 'id' field - Needs to be fixed!

4/2/2014 - fileExplorer updated - Improved Command Line Control, see "fileExplorer.py -h" for more information

4/9/2-14 - fileExplorer updated - More efficient opening of CouchDB and directoryDelve()

