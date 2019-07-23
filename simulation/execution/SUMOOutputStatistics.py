import pandas as pd
from bson.json_util import dumps
from bson.json_util import loads
import numpy as np
from pandas.io.json import json_normalize
import xmltodict, json
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017')
db = client.kirchheim
flows = db.flows8
statistics = db.statistics
# test = db.test
json = list(flows.find({}))

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
print(df.head())

#occupancy bigger than 0
dt = df.loc[df['occupancy'] > 0]
#averages for each lane by taking into account only the records where occupancy > 0
dt1 = dt.groupby(['id']).mean()
mean_values_over_time_per_lane = dt1[['density', 'occupancy', 'waitingTime']]
mean_values_over_time_per_lane.columns = ['density', 'occupancy', 'waitingTime']

# #take the lane_id of the lane with the highest average occupancy
dt2 = dt1.loc[dt1['occupancy'].idxmax()]
print(dt2)
# #take the shape of the lane above
# dt3 = df.loc[df['lane_id'] == dt2.name].iloc[0]['shape']
#save in MongoDB
jsonFormatData = mean_values_over_time_per_lane.to_json(orient='index')
statistics.insert_one(loads(jsonFormatData))
# mean_values_over_time_per_lane

#statistics regarding the entire simulation
#it also contains the quartiles for each column, making it possible to create boxplots for each column.
dfDataJSON = df.describe().to_json()
new_result = statistics.insert_one(loads(dfDataJSON))
df.describe()