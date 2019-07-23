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

def saveToDB(filepath):
    # entries_to_keep = {'id', 'maxspeed', 'meanspeed', 'occupancy', 'vehicle_count', 'shape'}
    entries_to_keep = {'id', 'traveltime', 'density', 'occupancy', 'waitingTime', 'speed'}
    lane_ids = {}
    for event, elem in etree.iterparse(filepath, events=('end',), tag='edge'):
        parent = elem.getparent()
        latest_timestep = parent.attrib['end']
        edgeid = elem.attrib['id']
        # if edgeid == ':1833998204_3':
        # string_element = etree.tostring(elem, encoding='utf8').decode('utf8')
        # print(string_element)
        # print(edgeid)
        # elem.attrib.pop('xmlns', None)
        # print('timestep', latest_timestep)
        elem.set('end', latest_timestep)
        num_attributes = 0
        keys = []
        parse = False
        for j in elem.iterfind("lane"):
            lane_id = j.attrib['id']
            # print(lane_id)
            # lon_lat_array = findLonLat(lane_id)
            # if edgeid == ':1833998204_3':
            #     # print(lon_lat_array)
            # j.set('shape', str(lon_lat_array))

            attributes = j.attrib
            for attribute in attributes.keys():
                if attribute not in entries_to_keep:
                    j.attrib.pop(attribute, None)
            attributes2 = j.attrib
            num_attributes = len(attributes2)
            # if (num_attributes > 1):
            #     print(latest_timestep)
            #     if lane_id in keys:
            #         lon_lat_array = lane_ids[lane_id]
            #         j.set('shape', str(lon_lat_array))
            #     else:
            #         lon_lat_array = findLonLat(lane_id)
            #         lane_ids[lane_id] = lon_lat_array
            #         j.set('shape', str(lon_lat_array))
            #         keys = lane_ids.keys()
            if (num_attributes <= 2):
                elem.remove(j)
            else:
                parse = True
            # j.set('date', '02/04/2019')
        if(parse):
            json_result = xml2dict(elem)  # string
            new_result = flows.insert_one(json_result)
            # doc_returned = flows.find_one({'edge.@id':edgeid})
            # print(json.dumps(doc_returned['edge']))
        # print(type(json_result))
        # print(json.dumps(json_result))


        if event == 'end':
            elem.clear()
            # print('cleared')

def findLonLat(laneid):
    query_string = "//lane[@id=" + "'" + laneid +  "'" + "]/@shape"
    shape = doc.xpath(query_string)
    list_shape = shape[0].split(' ')
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

def xml2dict(element):
    string_element = etree.tostring(element, encoding='utf8').decode('utf8')
    output = xmltodict.parse(string_element)
    output['edge'].pop('@xmlns:xsi')
    output_final = json.dumps(output)
    # print(output_final)
    return output

def testDocumentInsertion():
    doc_returned = flows.find_one({ 'edge.@id': ":3330548807_1" })
    print(json.dumps(doc_returned['edge']))


#Call example
database = hc.Database()
flows = database._db.flows8
readInputNet('../data/input-simulation/kirchheim.net.xml')
saveToDB('../data/input-simulation/edgelane3.xml')
# testDocumentInsertion()