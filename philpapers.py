import argparse
from glob import iglob as glob
import json
import os.path
import tarfile

def create_sample(data_path, N=20):
    tar = tarfile.open("sample.tar", "w")
    data_path = os.path.join(data_path, '*.json')
    for i,filename in enumerate(glob(data_path)):
        tar.add(filename, arcname=os.path.basename(filename))
        if i > N:
            break
    tar.close()
    


def print_titles(data_path):
    ''' Takes a Philpapers data path, iterates through all JSON records in that
    folder, parses each and prints the title'''
    # search for all json files - the glob function iterates through a folder
    data_path = os.path.join(data_path, '*.json')
    for i,filename in enumerate(glob(data_path)):
        # open the file, parse the json, print the title, close the file
        with open(filename) as jsonfile:
            record = json.load(jsonfile)
            print record['title']

def valid_dir(path):
    ''' helper function for argparse module '''
    if not os.path.isdir(path):
        msg = "%r is not a valid directory" & path
        raise argparse.ArgumentTypeError(msg)
    return path

if __name__ == '__main__':
    import sys
    parser = argparse.ArgumentParser(description='Process PhilPapers Data Files')
    parser.add_argument('data_path', type=valid_dir, default=None)
    parser.add_argument('-c', dest='categories', nargs='*', type=str)
    args = parser.parse_args()

    # if a data path is manually specified, use it
    if args.data_path is None:
        # if not go with the inpho config file defaults
        data_path = config.get('general', 'data_path')
        philpapers_data_path = os.path.join(data_path, 'philpapers')

    print args.categories

    # TODO: Create print_filtered_categories function
    #print_filtered_categories(args.data_path, args.categories)

    create_sample(args.data_path, 20)
