import pymongo
          

class DB(object):
          
    URI = "mongodb://root:example@rmmm_mongo_1:27017"
    # URI = "mongodb://localhost:27017/rmmm_mongo_1"
    @staticmethod
    def init():
        client = pymongo.MongoClient(DB.URI)
        DB.DATABASE = client['mongo-db']
          
    @staticmethod
    def insert(collection, data):
        DB.DATABASE[collection].insert(data)
          
    @staticmethod
    def find_one(collection, query):
        return DB.DATABASE[collection].find_one(query)
