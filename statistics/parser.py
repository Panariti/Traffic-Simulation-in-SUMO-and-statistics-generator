from lxml import etree
import xmltodict, json
from app.database import DB

def parse_and_save(filepath):
    entries_to_keep = {'id', 'traveltime', 'density', 'occupancy', 'waitingTime', 'speed'}
    lane_ids = {}
    tree = etree.ElementTree(etree.fromstring(filepath))
    root = tree.getroot()
    simulation_id = ''
    scenario_id = ''
    i = 0
    for elem in root.iter('edge'):
        parent = elem.getparent()
        if i == 0:
            parent_meandata = parent.getparent()
            scenario_id = parent_meandata.attrib['scenario_id']
            scenario_description = parent_meandata.attrib['scenario_description']
            print('scenario id and description are:' + scenario_id + ", " + scenario_description)
        i = 1
        latest_timestep = parent.attrib['end']
        simulation_id = parent.attrib['id']
        edgeid = elem.attrib['id']
        elem.set('end', latest_timestep)
        elem.set('simulation_id', simulation_id)
        elem.set('scenario_id', scenario_id)
        elem.set('scenario_description', scenario_description)
        num_attributes = 0
        keys = []
        parse = False
        for j in elem.iterfind("lane"):
            lane_id = j.attrib['id']
            attributes = j.attrib
            for attribute in attributes.keys():
                if attribute not in entries_to_keep:
                    j.attrib.pop(attribute, None)
            attributes2 = j.attrib
            num_attributes = len(attributes2)
            if (num_attributes <= 2):
                elem.remove(j)
            else:
                parse = True
            # j.set('date', '02/04/2019')
        if(parse):
            json_result = xml2dict(elem)  # string
            # print(json_result)
            collection = DB.DATABASE['traffic_flow']
            new_result = collection.insert_one(json_result)
            # doc_returned = collection.find_one({'edge.@id':edgeid})
            # print(json.dumps(doc_returned['edge']))
            # print(type(json_result))
            # print(json.dumps(json_result))
    return (simulation_id, scenario_id, scenario_description)

def xml2dict(element):
    string_element = etree.tostring(element, encoding='utf8').decode('utf8')
    output = xmltodict.parse(string_element)
    output['edge'].pop('@xmlns:xsi')
    output_final = json.dumps(output)
    # print(output_final)
    return output
