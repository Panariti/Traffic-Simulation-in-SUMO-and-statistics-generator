from lxml import etree
import xmltodict, json
import os, sys, sumolib
from pymongo import MongoClient
# from execution import HelpClasses as hc
import DatabaseClasses as hc
'''Needed dependencies are SUMO, matplotlib and pyproj'''

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

net = None
doc = None

def readInputNet(filepath):
    global net
    net = sumolib.net.readNet(filepath)
    global doc
    doc = etree.parse(filepath)

def getLaneShapes():
    for lane in doc.iter(tag = 'lane'):
        statsJSONFormat = ""
        # edge_parent = lane.getparent()
        # edge_id = edge_parent.attrib['id']
        shape = lane.attrib['shape']
        lat_lon = findLonLat(shape)
        statsJSONFormat = statsJSONFormat + "{\"lane\":{"
        statsJSONFormat = statsJSONFormat + '\n\t\t"@id":\"{}'.format(lane.attrib['id']) + "\","
        statsJSONFormat = statsJSONFormat + '\n\t\t"@shape":{}'.format(lat_lon)
        statsJSONFormat = statsJSONFormat + "\n}"
        statsJSONFormat = statsJSONFormat + "\n}"
        dbJSON = json.loads(statsJSONFormat)
        new_result = flows.insert_one(dbJSON)
        # doc_returned = flows.find_one({'lane.@id':lane.attrib['id']})
        # print(json.dumps(doc_returned['lane']))

def findLonLat(shape):
    list_shape = shape.split(' ')
    list_of_number_arrays = []
    number_array = []
    for coor in list_shape:
        coordinates = coor.split(',')
        lon, lat = net.convertXY2LonLat(float(coordinates[0]), float(coordinates[1]))
        number_array.append(lon)
        number_array.append(lat)
        list_of_number_arrays.append(number_array)
        number_array = []
    # print(list_of_number_arrays)
    # str_shape = ','.join(map(str, number_array))
    # print(number_array)
    return list_of_number_arrays

database = hc.Database()
flows = database._db.lanes
readInputNet('../data/input-simulation/kirchheim.net.xml')
getLaneShapes()




