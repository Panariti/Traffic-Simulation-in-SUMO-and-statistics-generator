from pymongo import MongoClient
class Database(object):

    _db = None

    def __init__(self):
        '''Create connection with MongoDB database'''
        client = MongoClient('mongodb://localhost:27017')
        self._db = client.kirchheim #The name of the database. If it is not created yet, then this command also creates it.
        # flows = db.flows