from database import DB
import json
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

def get_last_simulations_main_road(num):
    collection = DB.DATABASE['main_roads']
    # .SetFields(Fields.Include("oneField", "anotherField").Exclude("_id"))
    documents = list(collection.find({},{"_id":0}).sort([("simulation_id", -1)]).limit(num))
    # json_result = JSONEncoder().encode(documents)
    # python_dict = literal_eval(json_result)
    # for elem in documents:
    #     print(elem)
    return documents

def get_last_statistics(num, type):
    if type == 'trip':
        collection = DB.DATABASE['trip_statistics']
        documents = list(collection.find({}, {"_id": 0}).sort([("simulation_id", -1)]).limit(num))
        return documents
    else:
        collection = DB.DATABASE['flow_statistics']
        documents = list(collection.find({'type': type}, {"_id": 0}).sort([("simulation_id", -1)]).limit(num))
        return documents

def get_latest_traffic():
    collection = DB.DATABASE["traffic"]
    cursor = list(collection.find({}, {"_id": False}).sort([("created_at", -1)]).limit(1))
    data = cursor[0]
    data["created_at"] = str(data["created_at"])
    return data

def get_latest_driver_recommendations():
    collection = DB.DATABASE["driving_recommendations"]
    cursor = collection.find({}, {"_id": False}).sort([("created_at", -1)]).limit(1)
    return cursor[0]["data"]

def get_scenario_heatmap_data_with_id(id):
    collection = DB.DATABASE["simulation_heatmap"]
    cursor = list(collection.find({"scenario_id": id}, {"_id": False}).limit(1))
    return cursor[0]["data"]

def get_all_simulation_scenarios():
    collection = DB.DATABASE["simulation_scenarios"]
    cursor = list(collection.find({}, {"_id": False}).limit(1))
    return cursor[0]["data"]



# def get_boxplot_data():
#     collection = DB.DATABASE["boxplot"]
#     return list(collection.find({}, {"_id": False}))

# def get_summary_data():
#     collection = DB.DATABASE["scen_summary"]
#     return list(collection.find({}, {"_id": False}))

# def get_road_data():
#     collection = DB.DATABASE["main_roads"]
#     return list(collection.find({}, {"_id": False}))
