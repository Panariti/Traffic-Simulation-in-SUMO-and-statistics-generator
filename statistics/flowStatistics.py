import pandas as pd
from bson.json_util import dumps
from bson.json_util import loads
import numpy as np
from pandas.io.json import json_normalize
import xmltodict, json
# from pymongo import MongoClient

import sys
sys.path.append('C:\\Users\panar\PycharmProjects\Kirchheim4\ios19kirch-server\\flask\\app')
from app.database import DB

def generate_save_statistics(simulation_id, scenario_id, scenario_description):
    # client = MongoClient('mongodb://localhost:27017')
    # db = client['mongo-db']
    # collection = db.traffic_flow3
    # statistics = db.flow_statistics
    # print(simulation_id)
    collection = DB.DATABASE['traffic_flow']
    statistics = DB.DATABASE['flow_statistics']
    # test = db.test
    json = list(collection.find({"edge.@simulation_id": simulation_id}))
    def ensure_list(obj):
        if isinstance(obj, list):
            return obj
        else:
            return [obj]

    json_transformed = []

    for record in json:
        try:
            for lane in ensure_list(record['edge']['lane']):
                keys = list(lane.keys())
                non_at_keys = [s[1:] for s in keys]
                dicti = {}
                dicti['edge_id'] = record['edge']['@id']
                dicti['end'] = record['edge']['@end']
                for idx, element in enumerate(non_at_keys):
                    #                 print(element)
                    dicti[element] = lane[keys[idx]]
                json_transformed.append(dicti)
        except:
            i = i + 1
            print(record)

    df = pd.DataFrame(json_transformed)
    df.speed = df.speed.astype(np.float64)
    df.density = df.density.astype(np.float64)
    df.occupancy = df.occupancy.astype(np.float64)
    df.traveltime = df.traveltime.astype(np.float64)
    df.waitingTime = df.waitingTime.astype(np.float64)
    # print(df.head())
    #occupancy bigger than 0
    dt = df.loc[df['occupancy'] > 0]
    #averages for each lane by taking into account only the records where occupancy > 0
    dt1 = dt.groupby(['id']).mean()
    mean_values_over_time_per_lane = dt1[['density', 'occupancy', 'waitingTime']]
    mean_values_over_time_per_lane.columns = ['density', 'occupancy', 'waitingTime']

    # #take the lane_id of the lane with the highest average occupancy
    dt2 = dt1.loc[dt1['occupancy'].idxmax()]
    # print(dt2)
    # #take the shape of the lane above
    # dt3 = df.loc[df['lane_id'] == dt2.name].iloc[0]['shape']
    #save in MongoDB
    jsonFormatData = mean_values_over_time_per_lane.to_json(orient='index')
    json_loads = loads(jsonFormatData)
    json_loads['simulation_id'] = simulation_id
    json_loads['scenario_id'] = scenario_id
    json_loads['scenario_description'] = scenario_description
    json_loads['type'] = 'edge_statistics'
    # print(dumps(json_loads))
    # for key in json_loads.keys():
    #     print(key)
    statistics.insert_one(json_loads)
    # mean_values_over_time_per_lane

    #statistics regarding the entire statistics
    #it also contains the quartiles for each column, making it possible to create boxplots for each column.
    t = df.describe()
    list_names = [1, 2, 3, 4, 5, 6, 7, 8]
    list_names[0] = 'count'
    list_names[1] = 'mean'
    list_names[2] = 'std'
    list_names[3] = 'min'
    list_names[4] = 'quartileTwentyFive'
    list_names[5] = 'quartileFifty'
    list_names[6] = 'quartileSeventyFive'
    list_names[7] = 'max'
    t.index = list_names
    dfDataJSON = t.to_json()
    # dfDataJSON = df.describe().to_json()
    dfDataJSON_loads = loads(dfDataJSON)
    dfDataJSON_loads['simulation_id'] = simulation_id
    dfDataJSON_loads['scenario_id'] = scenario_id
    dfDataJSON_loads['scenario_description'] = scenario_description
    dfDataJSON_loads['type'] = 'summary'
    new_result = statistics.insert_one(dfDataJSON_loads)
    # print(t)
    # df.describe()
    # print(dumps(dfDataJSON_loads))

# generate_save_statistics("2019-07-07-18-39-32-6caf1b81-b563-44a6-ab53-1f345eb59852")
