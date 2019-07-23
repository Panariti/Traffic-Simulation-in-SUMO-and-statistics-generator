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
    entries_to_keep = {'id', 'maxspeed', 'meanspeed', 'occupancy', 'vehicle_count', 'shape'}
    for event, elem in etree.iterparse(filepath, events=('end',), tag = 'edge'):
        if elem.tag == 'data':
            latest_timestep = elem.attrib['timestep']
            elem.clear()
            # print('clear')
        if event == 'end':
            if elem.tag == 'edge':
                parent = elem.getparent()
                parent2 = parent.getparent()
                latest_timestep = parent2.attrib['timestep']
                if float(latest_timestep) % 600 == 0.0:
                    edgeid = elem.attrib['id']
                    # if edgeid == ':1833998204_3':
                    # string_element = etree.tostring(elem, encoding='utf8').decode('utf8')
                    # print(string_element)
                    # print(edgeid)
                    elem.attrib.pop('xmlns', None)
                    # print('timestep', latest_timestep)
                    elem.set('timestep', latest_timestep)
                    for j in elem.iterfind("lane"):
                        lane_id = j.attrib['id']
                        lon_lat_array = findLonLat(lane_id)
                        # if edgeid == ':1833998204_3':
                        #     # print(lon_lat_array)
                        j.set('shape', str(lon_lat_array))
                        attributes = j.attrib
                        for attribute in attributes.keys():
                            if attribute not in entries_to_keep:
                                j.attrib.pop(attribute, None)
                        # if edgeid == ':1833998204_3':
                        #     string_element = etree.tostring(elem, encoding='utf8').decode('utf8')
                        #     print('the end', string_element)
                    json_result = xml2dict(elem)  # string
                    # print(type(json_result))
                    # print(json_result)

                    new_result = flows.insert_one(json_result)
                    # doc_returned = flows.find_one({'edge.@id':edgeid})
                    # print(json.dumps(doc_returned['edge']))

                    # print('One post: {0}'.format(new_result.inserted_id))
                    # fb.write(json_result)
                elem.clear()
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
flows = database._db.flows4
readInputNet('../data/input-simulation/small-extract-for-testing/net.net.xml')
saveToDB('C:\\Users\panar\Desktop\sumodatatesting\small-extract-for-testing\\therealfulloutput.xml')
# testDocumentInsertion()