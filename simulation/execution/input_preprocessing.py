#Based on Nathalie's work
import os, sys
import subprocess
import xml.etree.ElementTree as ET
from lxml import etree

VALID_SCENARIO_IDS = {1, 2, 3}
VALID_AREA_IDS = {'aschheim_west',
                  'ebersberg_east',
                  'feldkirchen_west',
                  'heimstetten_industrial_1',
                  'heimstetten_industrial_2',
                  'heimstetten_residential',
                  'kirchheim_industrial_east',
                  'kirchheim_industrial_west',
                  'kirchheim_residential',
                  'unassigned_edges'}

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

def write_sumocfg_files():
    for scenario_id in VALID_SCENARIO_IDS:
        configuration_tag = ET.Element('configuration')
        scenario_id_tag = ET.SubElement(
            configuration_tag,
            'scenario',
            {'id': '{0}'.format(scenario_id)}
            )

        input_tag = ET.SubElement(
            configuration_tag,
            'input'
            )
        net_file_tag = ET.SubElement(
            input_tag,
            'net-file',
            {'value': 'kirchheim-street-names.net.xml'}
            )
        route_files_tag = ET.SubElement(
            input_tag,
            'route-files',
            {'value': 'scenario{0}.rou.xml'.format(scenario_id)}
            )
        gui_settings_file_tag = ET.SubElement(
            input_tag,
            'gui-settings-file',
            {'value': 'gui-settings-origin-dest-vehicles.cfg'}
            )

        time_tag = ET.SubElement(configuration_tag, 'time')
        begin_tag = ET.SubElement(time_tag, 'begin', {'value': '0'})
        end_tag = ET.SubElement(time_tag, 'end', {'value': '10800'})

        processing_tag = ET.SubElement(configuration_tag, 'processing')
        junction_blocker_ignore_tag = ET.SubElement(processing_tag, 'ignore-junction-blocker', {'value': '1'})

        configuration_file = ET.ElementTree(configuration_tag)
        configuration_file.write('../data/input-simulation/scenario{0}.sumocfg'.format(scenario_id))

        # pretty formatting
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse('../data/input-simulation/scenario{0}.sumocfg'.format(scenario_id), parser)
        tree.write('../data/input-simulation/scenario{0}.sumocfg'.format(scenario_id), pretty_print=True)

def write_taz_file(path_to_net, path_to_polygons, path_to_output):
    path_to_script = tools + '/edgesInDistricts.py'
    cmd = 'python {0} -n {1} -t {2} -o {3}'\
                .format(path_to_script, path_to_net, path_to_polygons, path_to_output)
    subprocess.call(cmd.split())

    # filter edges not in any other taz except total_area
    taz_tree = ET.parse(path_to_output)
    taz_root = taz_tree.getroot()

    total_area_edges = []
    unassigned_edges = []
    assigned_edges = set()
    assigned_edges_per_area = {}
    for taz in taz_root.iter('taz'):
        if (taz.get('id') == 'total_area'):
            total_area_edges = taz.get('edges').split()
        elif (taz.get('id') in VALID_AREA_IDS):
            assigned_edges.update(taz.get('edges').split())
            assigned_edges_per_area[taz.get('id')] = taz.get('edges').split()

    for edge in total_area_edges:
        if (edge not in assigned_edges):
            unassigned_edges.append(edge)

    assigned_edges_per_area['unassigned_edges'] = unassigned_edges

    # remove all edges which do not allow 'passenger' i.e. vehicles to drive on
    net_tree = ET.parse('../data/input-simulation/kirchheim-street-names.net.xml')
    net_root = net_tree.getroot()

    passenger_allowed_edges = set()
    for edge in net_root.iter('edge'):
        allowed = edge.find('lane').get('allow')
        disallowed = edge.find('lane').get('disallow')

        if (allowed is None and disallowed is None):
            passenger_allowed_edges.add(edge.get('id'))
        if (allowed is None):
            if ('passenger' not in disallowed):
                passenger_allowed_edges.add(edge.get('id'))
        if (disallowed is None):
            if ('passenger' in allowed):
                passenger_allowed_edges.add(edge.get('id'))

    for area_id, edges in assigned_edges_per_area.items():
        allowed_in_area = []
        for edge in edges:
            if (edge in passenger_allowed_edges):
                allowed_in_area.append(edge)
        assigned_edges_per_area[area_id] = allowed_in_area

    for taz in taz_root.iter('taz'):
        if (taz.get('id') in VALID_AREA_IDS):
            taz.set('edges', ' '.join(assigned_edges_per_area[taz.get('id')]))

    # create new taz with edges not in any other taz except total_area
    ET.SubElement(taz_root, 'taz', {'id': 'unassigned_edges', 'edges': ' '.join(unassigned_edges)})
    taz_tree.write(path_to_output)

def write_random_trips_and_routes(path_to_net,
                                  path_to_trip_output,
                                  path_to_route_output,
                                  path_to_weights,
                                  load_weights,
                                  fringe_factor=1,
                                  number_of_vehicles=9500):
    path_to_script = tools + '/randomTrips.py'
    cmd = 'python {0} -n {1} -e 10800 -o {2} --route-file {3} --validate --fringe-factor {4} -p {5}'\
          .format(path_to_script,
                  path_to_net,
                  path_to_trip_output,
                  path_to_route_output,
                  fringe_factor,
                  ((10800-0)/(number_of_vehicles * 1.0)))
    if (load_weights):
        cmd += ' --weights-prefix {0}'.format(path_to_weights)
    subprocess.call(cmd.split())

def set_up_weight_file(scenario_id, weight_type, edges_per_area):
    root = ET.Element('edgedata')
    interval = ET.SubElement(root, 'interval', {'begin': '0', 'end': '10800'})

    for area_id, edges in edges_per_area.items():
        for edge in edges:
            ET.SubElement(interval, 'edge', {'id': edge, 'value': '0'})

    tree = ET.ElementTree(root)
    tree.write('../data/input-simulation/scenario{0}.{1}.xml'\
                                .format(scenario_id, weight_type))

    #pretty formatting
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse('../data/input-simulation/scenario{0}.{1}.xml'\
                       .format(scenario_id, weight_type),
                       parser)
    tree.write('../data/input-simulation/scenario{0}.{1}.xml'\
               .format(scenario_id, weight_type),
               pretty_print=True)

# distributes probabilities equally over all edges in an area
def write_weight_file(weight_type,
                      weights_per_area={'aschheim_west': 0,
                                        'ebersberg_east': 0,
                                        'feldkirchen_west': 0,
                                        'heimstetten_industrial_1': 0.5,
                                        'heimstetten_industrial_2': 0.5,
                                        'heimstetten_residential': 0.5,
                                        'kirchheim_industrial_east': 0,
                                        'kirchheim_industrial_west': 0,
                                        'kirchheim_residential': 0,
                                        'unassigned_edges': 0},
                      scenario_id=0):
    weights_per_area_keys = set(weights_per_area.keys())

    if (weights_per_area_keys.symmetric_difference(VALID_AREA_IDS) != set()):
        raise ValueError('area_ids must only be exactly %r.' % VALID_AREA_IDS)
    if (scenario_id not in VALID_SCENARIO_IDS):
        raise ValueError("scenario_id must be one of %r." % VALID_SCENARIO_IDS)
    if (weight_type != 'src' and weight_type != 'dst'):
        raise ValueError("weight_type must be 'src' or 'dst'")

    edges_per_area = {}
    taz_tree = ET.parse('../data/input-simulation/areas-of-interest.taz.xml')
    taz_root = taz_tree.getroot()

    for taz in taz_root.iter('taz'):
        if (taz.get('id') in VALID_AREA_IDS):
            edges_per_area['{0}'.format(taz.get('id'))] = taz.get('edges').split()

    scenario_weights_tree = ET.parse('../data/input-simulation/scenario{0}.{1}.xml'\
                                     .format(scenario_id, weight_type))
    scenario_weights_root = scenario_weights_tree.getroot()

    for edge in scenario_weights_root.iter('edge'):
        edge_id = edge.get('id')
        if (edge_id in edges_per_area['aschheim_west']):
            edge.set('value', '{0}'\
            .format(weights_per_area['aschheim_west']/len(edges_per_area['aschheim_west'])))
        elif (edge_id in edges_per_area['ebersberg_east']):
            edge.set('value', '{0}'\
            .format(weights_per_area['ebersberg_east']/len(edges_per_area['ebersberg_east'])))
        elif (edge_id in edges_per_area['feldkirchen_west']):
            edge.set('value', '{0}'\
            .format(weights_per_area['feldkirchen_west']/len(edges_per_area['feldkirchen_west'])))
        elif (edge_id in edges_per_area['heimstetten_industrial_1']):
            edge.set('value', '{0}'\
            .format(weights_per_area['heimstetten_industrial_1']/len(edges_per_area['heimstetten_industrial_1'])))
        elif (edge_id in edges_per_area['heimstetten_industrial_2']):
            edge.set('value', '{0}'\
            .format(weights_per_area['heimstetten_industrial_2']/len(edges_per_area['heimstetten_industrial_2'])))
        elif (edge_id in edges_per_area['heimstetten_residential']):
            edge.set('value', '{0}'\
            .format(weights_per_area['heimstetten_residential']/len(edges_per_area['heimstetten_residential'])))
        elif (edge_id in edges_per_area['kirchheim_industrial_east']):
            edge.set('value', '{0}'\
            .format(weights_per_area['kirchheim_industrial_east']/len(edges_per_area['kirchheim_industrial_east'])))
        elif (edge_id in edges_per_area['kirchheim_industrial_west']):
            edge.set('value', '{0}'\
            .format(weights_per_area['kirchheim_industrial_west']/len(edges_per_area['kirchheim_industrial_west'])))
        elif (edge_id in edges_per_area['kirchheim_residential']):
            edge.set('value', '{0}'\
            .format(weights_per_area['kirchheim_residential']/len(edges_per_area['kirchheim_residential'])))
        elif (edge_id in edges_per_area['unassigned_edges']):
            edge.set('value', '{0}'\
            .format(weights_per_area['unassigned_edges']/len(edges_per_area['unassigned_edges'])))

    scenario_weights_tree.write('../data/input-simulation/scenario{0}.{1}.xml'\
                                .format(scenario_id, weight_type))

def set_default_veh_color():
    for scenario_id in VALID_SCENARIO_IDS:
        routes_tree = ET.parse('../data/input-simulation/scenario{0}.rou.xml'.format(scenario_id))
        root = routes_tree.getroot()
        for vehicle in root.iter('vehicle'):
            vehicle.set('color', '102, 179, 255') # light blue
        routes_tree.write('../data/input-simulation/scenario{0}.rou.xml'.format(scenario_id))

# if argument invalid: default color is set for all vehicles
def set_origin_dest_veh_color(color_by):
    set_default_veh_color()

    for scenario_id in VALID_SCENARIO_IDS:
        routes_tree = ET.parse('../data/input-simulation/scenario{0}.rou.xml'.format(scenario_id))
        routes_root = routes_tree.getroot()
        taz_tree = ET.parse('../data/input-simulation/areas-of-interest.taz.xml')
        taz_root = taz_tree.getroot()

        heimstetten_edges = str()
        kirchheim_edges = str()

        for taz in taz_root.iter('taz'):
            if (taz.get('id') == 'heimstetten_origin_dest' or taz.get('id') == 'heimstetten_industrial_origin_dest'):
                heimstetten_edges += taz.get('edges')
            elif (taz.get('id') == 'kirchheim_origin_dest'):
                kirchheim_edges += taz.get('edges')

        for vehicle in routes_root.iter('vehicle'):
            route_edges = vehicle.find('route').get('edges').split()

            idx = None
            if (color_by == 'origin'):
                idx = 0
            elif (color_by == 'destination'):
                idx = len(route_edges) - 1
            else:
                return

            if (route_edges[idx] in heimstetten_edges):
                vehicle.set('color', '255, 51, 153') # magenta
            elif (route_edges[idx] in kirchheim_edges):
                vehicle.set('color', '255, 153, 51') # orange

        routes_tree.write('../data/input-simulation/scenario{0}.rou.xml'.format(scenario_id))
    return True

# weights can only be adjusted one scenario and type at a time
def preprocess_simulation_input(
    color_by='origin',
    net_changed=False,
    alter_trips=False,
    alter_weights=False,
    load_weights=True,
    weight_type='src',
    weights_per_area={'aschheim_west': 0.1,
                      'ebersberg_east': 0.37,
                      'feldkirchen_west': 0.1,
                      'heimstetten_industrial_1': 0.01,
                      'heimstetten_industrial_2': 0.01,
                      'heimstetten_residential': 0.18,
                      'kirchheim_industrial_east': 0.1,
                      'kirchheim_industrial_west': 0.1,
                      'kirchheim_residential': 0.18,
                      'unassigned_edges': 0.05},
    fringe_factor=1,
    number_of_vehicles=9500,
    for_scenario_id=0
    ):

    if (net_changed):
        write_taz_file(
            '../data/input-simulation/kirchheim-street-names.net.xml',
            '../data/input-simulation/areas-of-interest.boundaries.xml',
            '../data/input-simulation/areas-of-interest.taz.xml'
            )

        if (alter_weights):
            write_weight_file(weight_type, weights_per_area, for_scenario_id)

        for scenario_id in VALID_SCENARIO_IDS:
            write_random_trips_and_routes(
                '../data/input-simulation/kirchheim-street-names.net.xml',
                '../data/input-simulation/scenario{0}.trips.xml'.format(scenario_id),
                '../data/input-simulation/scenario{0}.rou.xml'.format(scenario_id),
                '../data/input-simulation/scenario{0}'.format(scenario_id),
                load_weights,
                fringe_factor,
                number_of_vehicles
                )

    if (alter_trips):
        if for_scenario_id not in VALID_SCENARIO_IDS:
            raise ValueError("for_scenario_id must be one of %r." % VALID_SCENARIO_IDS)

        if (alter_weights):
            write_weight_file(weight_type, weights_per_area, for_scenario_id)

        write_random_trips_and_routes(
            '../data/input-simulation/kirchheim-street-names.net.xml',
            '../data/input-simulation/scenario{0}.trips.xml'.format(for_scenario_id),
            '../data/input-simulation/scenario{0}.rou.xml'.format(for_scenario_id),
            '../data/input-simulation/scenario{0}'.format(for_scenario_id),
            load_weights,
            fringe_factor,
            number_of_vehicles
            )

    if (alter_weights):
        write_weight_file(weight_type, weights_per_area, for_scenario_id)
        write_random_trips_and_routes(
            '../data/input-simulation/kirchheim-street-names.net.xml',
            '../data/input-simulation/scenario{0}.trips.xml'.format(for_scenario_id),
            '../data/input-simulation/scenario{0}.rou.xml'.format(for_scenario_id),
            '../data/input-simulation/scenario{0}'.format(for_scenario_id),
            load_weights,
            fringe_factor,
            number_of_vehicles
            )

    set_origin_dest_veh_color(color_by)

