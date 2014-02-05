import httplib
import json
import os
import os.path
import sys
import tarfile
from time import strftime, sleep

# import config file parser
try:
    from inpho import config
except ImportError:
    import config

#run as this on command line:
# >> nohup python philpapers.py

def pull_from_date(start_date, offset=0, data_path=None, log_path=None,
                   backup_path=None): 
    """
    Pulls and pickles all new or changed paper abstracts
    from start_date until there are no more and then records
    the date it ran.
    """
    # ensure data dir is proper
    if data_path is None:
        data_path = 'philpapers_data'

    if not os.path.isdir(data_path):
        os.makedirs(data_path)

    # ensure log dir is proper
    if log_path is None:
        log_path = 'philpapers_log'
    
    rundate = strftime("%Y-%m-%d")
    sys.stderr.write('Starting at ' + start_date + ' to ' + str(rundate) + '\n')

    if backup_path is not None:
        backup(data_path, backup_path, rundate)
    
    conn = httplib.HTTPConnection("philpapers.org")
    
    while(True):
        request_url= "/utils/export_contents.json?apiId=2956&apiKey=" +\
            config.get("philpapers", "apikey") +"&updated=" + str(start_date) + "T12:00:00&offset=" + str(offset)
        
        sys.stderr.write('requesting offset: ' + str(offset) + " from " + str(start_date) + " with offset " + str(offset) + '\n')
        conn.request("GET", request_url)
        result = conn.getresponse()
      
        data_pulled = result.read()
        
        try: # check for good data
            data = json.loads(data_pulled)
        except ValueError: # wait a bit and try again
            sleep(10) 
            conn.request("GET", request_url)
            result = conn.getresponse()
            data_pulled = result.read()
            try: # check new data
                data = json.loads(data_pulled)
            except ValueError: # two failures
                sys.stderr.write('terminated with ValueError on second attempt at offset' + str(offset) + '\n')
                break

        for entry in data['entries']:
            entry_file = os.path.join(data_path, entry['id'] + '.json')
            with open(entry_file, 'w') as f:
                f.write(json.dumps(entry))
                
        if not data['more']:
            sys.stderr.write('terminated successfully, no more data available\n')
            break

        offset += 100
        sleep(10)

    with open(log_path, 'a+') as log:
        log.write('Pulled: ' + str(rundate) + '\n')
    
def backup(data_path, backup_path, rundate):
    backup_path = os.path.join(backup_path, rundate + '.tar.gz')
    tar = tarfile.open(backup_path, 'w:gz')
    tar.add(data_path, arcname=os.path.basename(data_path))
    tar.close()
        
    

#start date 1970-01-01 for the first pull
#currently incremented manually for subsequent pulls, but should read log file
if __name__ == '__main__':
    import sys

    log_path = config.get('general', 'log_path')
    philpapers_log = os.path.join(log_path, 'philpapers')

    backup_path = config.get('general', 'backup_path')
    philpapers_backup_path = os.path.join(backup_path, 'philpapers')
    if not os.path.exists(philpapers_backup_path):
        os.mkdir(philpapers_backup_path)

    if os.path.exists(philpapers_log):
        with open(philpapers_log, 'r') as f:
            lineList = f.readlines()
            start_date = lineList[-1][8:].strip()
    else:
        start_date = "1970-01-01"

    if sys.argv[-1] != 'philpapers.py':
        philpapers_data_path = sys.argv[-1]
    else:
        data_path = config.get('general', 'data_path')
        philpapers_data_path = os.path.join(data_path, 'philpapers')

    print "DATA:", philpapers_data_path
    print "LOG:", philpapers_log
    print "BACKUP:", philpapers_backup_path
    pull_from_date(start_date, 
                   data_path=philpapers_data_path,
                   log_path=philpapers_log, 
                   backup_path=philpapers_backup_path)

