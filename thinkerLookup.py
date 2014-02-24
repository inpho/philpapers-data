from collections import defaultdict
import couchdb

from inpho.model import Session, Thinker

# some stuff to connect to the couchDB

results = defaultdict(dict)

for thinker in Session.query(Thinker).all():
    pass
    # something to query the couch db, return counts of each field type
    results[thinker.ID]['title'] = ???query???

# return results or write to a csv
