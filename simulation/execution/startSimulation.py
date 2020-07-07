import os
import sys
import argparse
import uuid
import datetime
import requests
from lxml import etree
import input_preprocessing as ip
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
import traci
# tripInfo = "../data/input-statistics/tripinfo.xml"
# edgeLane = "../data/input-statistics/edgelane.xml"
simulation_id = ""
scenario_id = ""
scenario_description = ""
# contains TraCI control loop
def run():
    # step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        # print(step)
        # step += 1
    traci.close()
    sys.stdout.flush()

def create_simulation_id():
    global simulation_id
    # simulation_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-") + str(uuid.uuid4())
    simulation_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    simulation_id = "2054-07-19-19-35-29"

def get_scenario_id(filepath):
    tree = etree.parse(filepath)
    root = tree.getroot()
    global scenario_id
    global scenario_description
    for elem in root.iter('scenario'):
        scenario_id = elem.attrib['id']
    if scenario_id == '1':
        scenario_description = "morning rush hour"
    elif scenario_id == '2':
        scenario_description = "noon"
    else:
        scenario_description = "afternoon rush hour"

def add_id_to_tripinfo(filepath):
    path = filepath + "tripinfo.xml"
    tree = etree.parse(path)
    root = tree.getroot()
    for elem in root.iter('tripinfos'):
        elem.set('id', simulation_id)
        elem.set('scenario_id', scenario_id)
        elem.set('scenario_description', scenario_description)
    tree.write(path)
    print('The statistics id was added', simulation_id)

def add_scenario_to_edge_file(filepath, type_of_file='edgelane'):
    if type_of_file == 'edge':
        path = filepath + "edge.xml"
    else:
        path = filepath + "edgelane.xml"
    tree = etree.parse(path)
    root = tree.getroot()
    for elem in root.iter('meandata'):
        elem.set('scenario_id', scenario_id)
        elem.set('scenario_description', scenario_description)
    tree.write(path)
    print('The scenario id and description are added' + " to " + type_of_file, scenario_id + ' and' + scenario_description)


def create_xml_file(filepath, freq, sim_id):
    path = filepath + "additional.xml"
    # print(path)
    with open(path, 'w') as fb:
        fb.write('<additional>')
        lane = "<laneData "
        id = "id=" + "\"" + sim_id + "\" "
        file = "file=" + "\"" + "edgelane.xml" + "\" "
        frequency = "freq=\"" + str(freq) + "\"" + "/>"
        element = lane + id + file + frequency

        edge = "<edgeData "
        id = "id=" + "\"" + sim_id + "\" "
        file = "file=" + "\"" + "edge.xml" + "\" "
        frequency2 =  "/>"
        element = element + edge + id + file + frequency2
        fb.write(element)
        fb.write('</additional>')
    return path

def Main():
    create_simulation_id()
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default="../data/input-simulation/scenario2.sumocfg", type=str, help='Give the path to the sumocfg file')
    # parser.add_argument('--additional', default="../data/input-statistics/additional.xml", type=str, help = 'Give the path to the additional file for tripinfo output')
    parser.add_argument('--lanepath', default="../data/output-simulation/", type=str,
                        help='Give the filepath where you want the lanepath to be saved..')
    parser.add_argument('--edgepath', default="../data/output-simulation/", type=str,
                        help='Give the filepath where you want the lanepath to be saved..')
    parser.add_argument('--trippath', default="../data/output-simulation/", type=str,
                        help='Give the filepath where you want the tripinfo to be saved.')
    parser.add_argument('--color', default="origin", type=str,
                        help='Type whether you want cars to be colored based on origin (default) or destination.')
    parser.add_argument('--freq', default=600, type=int)

    args = parser.parse_args()
    success = ip.set_origin_dest_veh_color(args.color)
    sumoBinary = "sumo-gui"
    get_scenario_id(args.config)
    print(scenario_id, scenario_description)
    # # traci starts sumo as a subprocess and then this script connects and runs
    sumoCMD = [sumoBinary, "-c", args.config,
               "--additional-files", create_xml_file(args.lanepath, args.freq, simulation_id), "--tripinfo-output",
               args.trippath + 'tripinfo.xml']
    print(sumoCMD)
    traci.start(sumoCMD)
    run()
    add_id_to_tripinfo(args.trippath)
    add_scenario_to_edge_file(args.edgepath, 'edge')
    add_scenario_to_edge_file(args.edgepath)

    # # make post request
    # # Set the name of the XML file.
    #
    # trips_xml = "../data/output-simulation/" + "tripinfo.xml"
    # url_trips = "http://base/api/simulation/input/trip"
    #
    # edge_lane_xml = "../data/output-simulation/" + "edgelane.xml"
    # url_edge_lane = "http://base/api/simulation/input/flow"
    #
    # edges_xml = "../data/output-simulation/" + "edge.xml"
    # url_edges = "http://base/api/simulation/input/mainroads"
    #
    # headers = {
    #     'Content-Type': 'text/xml'
    #     }
    #
    # with open(trips_xml, 'r') as xml:
    #     # Give the object representing the XML file to requests.post.
    #     the_data = xml.read()
    #     r = requests.post(url_trips, data=the_data)
    #     print(r.content)
    #
    # with open(edge_lane_xml, 'r') as xml:
    #     # Give the object representing the XML file to requests.post.
    #     the_data = xml.read()
    #     r = requests.post(url_edge_lane, data=the_data)
    #     print(r.content)
    #
    # with open(edges_xml, 'r') as xml:
    #     # Give the object representing the XML file to requests.post.
    #     the_data = xml.read()
    #     r = requests.post(url_edges, data=the_data)
    #     print(r.content)

if __name__ == "__main__":
    Main()
