#Adapted from 
#@author  Yun-Pang Wang
#@author  Michael Behrisch

import xmltodict, json
from lxml import etree
from xml.sax import saxutils, make_parser, handler
import io
from app.database import DB
# import helperClasses as helperc
# mpl.use('agg')
class TripStatistics():
    def __init__(self, tripsfile):
        self.tripsfile = tripsfile
        self.generate_statistics()


    def getBasicStats(self, method, vehicles, assignments):
        totalVeh = 0.
        totalTravelTime = 0.
        totalTravelLength = 0.
        totalTravelSpeed = 0.
        totalWaitTime = 0.
        totalDiffTime = 0.
        totalDiffSpeed = 0.
        totalDiffLength = 0.
        totalDiffWaitTime = 0.
        totalDiffTravelTime = 0.
        totalDepartDelay = 0.
        totalDuration = 0.
        simulation_id = ''
        scenario_id = ''
        scenario_description = ''
        waiting_time_of_vehicles = []
        speeds_of_vehicles = []
        for veh in vehicles:
            # print(veh.)
            totalVeh += 1
            veh.method = method
            # unit: speed - km/h; traveltime - minutes; travel length - meters
            veh.speed = (veh.travellength / veh.traveltime)*3.6
            totalTravelTime += veh.traveltime / 60.0
            totalTravelLength += round(veh.travellength/1000.0)
            totalWaitTime += round(veh.waittime/60.0)
            time_of_wait = round(veh.waittime / 60.0)
            waiting_time_of_vehicles.append(time_of_wait)
            totalTravelSpeed += veh.speed
            speeds_of_vehicles.append(veh.speed)
            totalDepartDelay += round(veh.departdelay / 60.0)
            totalDuration += veh.durationtime / 60.0
            simulation_id = veh.simul_id
            scenario_id = veh.scen_id
            scenario_description = veh.scen_description

        # print('speeds', speeds_of_vehicles)
        # print(waiting_time_of_vehicles)
        # Create a figure instance
        # print(waiting_time_of_vehicles)

        avgTravelTime = round(totalTravelTime / totalVeh)
        avgTravelLength = totalTravelLength / totalVeh
        avgTravelSpeed = totalTravelSpeed / totalVeh
        avgWaitTime = totalWaitTime / totalVeh
        avgDepartDelay = round(totalDepartDelay / totalVeh)
        avgDuration = round(totalDuration / totalVeh)
        for veh in vehicles:
            totalDiffTravelTime += (veh.traveltime - avgTravelTime) ** 2
            totalDiffSpeed += (veh.speed - avgTravelSpeed) ** 2
            totalDiffLength += (veh.travellength - avgTravelLength) ** 2
            totalDiffWaitTime += (veh.waittime - avgWaitTime) ** 2

        # SD: standard deviation
        SDTravelTime = (totalDiffTravelTime / totalVeh) ** (0.5)
        SDLength = (totalDiffLength / totalVeh) ** (0.5)
        SDSpeed = (totalDiffSpeed / totalVeh) ** (0.5)
        SDWaitTime = (totalDiffWaitTime / totalVeh) ** (0.5)

        assignments[method] = Assign(method, totalVeh, totalTravelTime, totalTravelLength,
                                     totalDepartDelay, totalWaitTime, avgTravelTime,
                                     avgTravelLength, avgTravelSpeed, avgDepartDelay,
                                     avgWaitTime, SDTravelTime, SDLength, SDSpeed, SDWaitTime, waiting_time_of_vehicles, speeds_of_vehicles, totalDuration, avgDuration, simulation_id, scenario_id, scenario_description)

    def getStatisticsOutput(self, assignments, outputfile=None):
        wantedOutputTypes = ["totalNumberOfVehicles", "totalDepartureDelay", "averageDepartureDelay", "totalWaitingTime","averageVehicularWaitingTime",
                             "averageVehicularTravelTime", "totalTravelTime", "averageVehicularTravelLength","averageVehicularTravelSpeed"
                             ]
        statsJSONFormat = ""
        for method in assignments.values():
            statsJSONFormat = statsJSONFormat + "{"
            statsJSONFormat = statsJSONFormat + '\n\t\t"totalNumberOfVehicles":{}'.format(method.totalVeh) + ","
            statsJSONFormat = statsJSONFormat + '\n\t\t"totalDepartureDelay":{}'.format(method.totalDepartDelay) + ","
            statsJSONFormat = statsJSONFormat + '\n\t\t"averageDepartureDelay":{}'.format(method.avgDepartDelay) + ","
            statsJSONFormat = statsJSONFormat + '\n\t\t"totalWaitingTime":{}'.format(method.totalWaitTime) + ","
            statsJSONFormat = statsJSONFormat + '\n\t\t"averageVehicularWaitingTime":{}'.format(method.avgWaitTime) + ","
            statsJSONFormat = statsJSONFormat + '\n\t\t"totalTravelTime":{}'.format(method.totalTravelTime) + ","
            statsJSONFormat = statsJSONFormat + '\n\t\t"averageVehicularTravelTime":{}'.format(method.avgTravelTime) + ","
            statsJSONFormat = statsJSONFormat + '\n\t\t"totalTravelLength":{}'.format(method.totalTravelLength) + ","
            statsJSONFormat = statsJSONFormat + '\n\t\t"averageVehicularTravelLength":{}'.format(method.avgTravelLength) + ","
            statsJSONFormat = statsJSONFormat + '\n\t\t"waitingTimesOfVehicles":{}'.format(method.waiting_time_of_vehicles) + ","
            statsJSONFormat = statsJSONFormat + '\n\t\t"speedsOfVehicles":{}'.format(method.speeds_of_vehicles) + ","
            statsJSONFormat = statsJSONFormat + '\n\t\t"averageVehicularTravelSpeed":{}'.format(method.avgTravelSpeed) + ","
            statsJSONFormat = statsJSONFormat + '\n\t\t"totalDurationofTraveling":{}'.format(method.totalDuration) + ","
            statsJSONFormat = statsJSONFormat + '\n\t\t"averageDurationOfTraveling":{}'.format(method.avgDuration) + ","
            statsJSONFormat = statsJSONFormat + '\n\t\t"simulation_id":\"{}\"'.format(method.simul_id) + ","
            statsJSONFormat = statsJSONFormat + '\n\t\t"scenario_id":\"{}\"'.format(method.scen_id) + ","
            statsJSONFormat = statsJSONFormat + '\n\t\t"scenario_description":\"{}\"'.format(method.scen_description)
            statsJSONFormat = statsJSONFormat + "\n}"
        self.save(statsJSONFormat)

        def __repr__(self):
            return "%s_%s_%s_%s_%s_%s<%s>" % (self.label, self.depart, self.arrival, self.speed, self.traveltime, self.travellength, self.route)

    def save(self, statsJSONFormat):
        # print(statsJSONFormat)
        dbStats = json.loads(statsJSONFormat)
        collection = DB.DATABASE['trip_statistics']
        new_result = collection.insert_one(dbStats)
        print('One post with statistics:{0}'.format(new_result.inserted_id))
        # doc_returned = collection.find_one({'simulationID': statistics})
        # print(doc_returned)

    def xml2dict(self, element):
        string_element = etree.tostring(element, encoding='utf8').decode('utf8')
        output = xmltodict.parse(string_element)
        # output['edge'].pop('@xmlns:xsi')
        output_final = json.dumps(output)
        return output_final + ','

    def generate_statistics(self):
        parser = make_parser()
        allvehicles = {}
        allvehicles[self.tripsfile] = []
        parser.setContentHandler(VehInformationReader(allvehicles[self.tripsfile]))
        parser.parse(self.tripsfile)

        assignments = {}
        for method, vehicles in allvehicles.items():
            self.getBasicStats(method, vehicles, assignments)

        self.getStatisticsOutput(assignments)
        print('The calculation of network statistics is done!')

    # def plotStatistics(self, assignments):
    #     for method in assignments.values():
    #         #Create a density plot from the list of waiting times of vehicles
    #         # This will show the trend of the waiting time increase
    #         from scipy.stats import gaussian_kde
    #         # import numpy as np
    #         # import matplotlib.pyplot as plt
    #         # data = method.waiting_time_of_vehicles
    #         # print(data)
    #         # density = gaussian_kde(data)
    #         # xs = np.linspace(0, 8, 200)
    #         # density.covariance_factor = lambda: .25
    #         # density._compute_covariance()
    #         # plt.plot(xs, density(xs))
    #         # plt.title('Density plot of waiting time of vehicles')
    #         # plt.show()
    #         # #
    #         # # # # It shows a boxplot for the speeds of the vehicles
    #         # fig = plt.figure(1, figsize=(9, 6))
    #         # # Create an axes instance
    #         # ax = fig.add_subplot(111)
    #         # # Create the boxplot
    #         # bp = ax.boxplot(method.speeds_of_vehicles)
    #         # # Save the figure
    #         # # fig.savefig('fig1.png', bbox_inches='tight')
    #         # plt.title('Box plot of speeds of vehicles')
    #         # plt.show()

# This class is for storing vehicle information, such as departure time, route and travel time.
class Vehicle:
    def __init__(self, label):
        self.label = label
        self.method = None
        self.depart = 0.
        self.arrival = 0.
        self.speed = 0.
        self.route = []
        self.traveltime = 0.
        self.travellength = 0.
        self.departdelay = 0.
        self.waittime = 0.
        self.rank = 0.
        self.simul_id = ''
        self.scen_id = ''
        self.scen_description = ''

    def __repr__(self):
        return "%s_%s_%s_%s_%s_%s<%s>" % (
        self.label, self.depart, self.arrival, self.speed, self.traveltime, self.travellength, self.route)


class Assign:
    def __init__(self, method, totalVeh, totalTravelTime, totalTravelLength, totalDepartDelay, totalWaitTime,
                 avgTravelTime, avgTravelLength, avgTravelSpeed, avgDepartDelay, avgWaitTime, SDTravelTime, SDLength,
                 SDSpeed, SDWaitTime, waiting_time_of_vehicles, speeds_of_vehicles, totalDuration, avgDuration, simul_id, scen_id, scen_description):
        self.label = method
        self.totalVeh = totalVeh
        self.totalTravelTime = totalTravelTime
        self.totalTravelLength = totalTravelLength
        self.totalDepartDelay = totalDepartDelay
        self.totalWaitTime = totalWaitTime
        self.avgTravelTime = avgTravelTime
        self.avgTravelLength = avgTravelLength
        self.avgTravelSpeed = avgTravelSpeed
        self.avgDepartDelay = avgDepartDelay
        self.avgWaitTime = avgWaitTime
        self.SDTravelTime = SDTravelTime
        self.SDLength = SDLength
        self.SDSpeed = SDSpeed
        self.SDWaitTime = SDWaitTime
        self.waiting_time_of_vehicles = waiting_time_of_vehicles
        self.speeds_of_vehicles = speeds_of_vehicles
        self.totalDuration = totalDuration
        self.avgDuration = avgDuration
        self.sumrank = 0.
        self.simul_id = simul_id
        self.scen_id = scen_id
        self.scen_description = scen_description

    def __repr__(self):
        return "%s_<%s|%s|%s|%s|%s|%s|%s|%s|%s>" % (
        self.label, self.totalVeh, self.avgTravelTime, self.avgTravelLength, self.avgTravelSpeed,
        self.avgWaitTime, self.SDTravelTime, self.SDLength, self.SDSpeed, self.SDWaitTime)


# The class is for parsing the XML input file (vehicle information). This class is used for
# calculating the gloabal network performances, e.g. avg. travel time and avg. travel speed.
class VehInformationReader(handler.ContentHandler):
    def __init__(self, vehList):
        self._vehList = vehList
        self._Vehicle = None
        self._routeString = ''
    def startElement(self, name, attrs):
        if name == 'tripinfos':
            self._simulation_id = attrs['id']
            self._scenario_id = attrs['scenario_id']
            print(attrs['scenario_id'])
            print(attrs['scenario_description'])
            self._scenario_description = attrs['scenario_description']
        if name == 'tripinfo':
            self._Vehicle = Vehicle(attrs['id'])
            self._Vehicle.traveltime = float(attrs['duration'])
            self._Vehicle.travellength = float(attrs['routeLength'])
            self._Vehicle.departdelay = float(attrs['departDelay'])
            self._Vehicle.waittime = float(attrs['waitingTime'])
            self._Vehicle.durationtime = float(attrs['duration'])
            self._Vehicle.simul_id = self._simulation_id
            self._Vehicle.scen_id = self._scenario_id
            self._Vehicle.scen_description = self._scenario_description
            self._vehList.append(self._Vehicle)


# output the network statistics based on the sumo-statistics results
def getStatisticsOutput(assignments, outputfile):
    with open(outputfile, 'w') as foutveh:
        '''
        foutveh.write('average vehicular travel time(s) = the sum of all vehicular travel times / the number of vehicles\n')
        foutveh.write('average vehicular travel length(m) = the sum of all vehicular travel lengths / the number of vehicles\n')
        foutveh.write('average vehicular travel speed(m/s) = the sum of all vehicular travel speeds / the number of vehicles\n')
        for method in assignments.itervalues():
            foutveh.write('\nAssignment Method:%s\n' %method.label)
            foutveh.write('- total number of vehicles:%s\n' %method.totalVeh)
            foutveh.write('- total departure delay(s):%s, ' %method.totalDepartDelay)    
            foutveh.write('- average departure delay(s):%s\n' %method.avgDepartDelay)
            foutveh.write('- total waiting time(s):%s, ' %method.totalWaitTime)    
            foutveh.write('- average vehicular waiting time(s):%s\n' %method.avgWaitTime)
            foutveh.write('- total travel time(s):%s, ' % method.totalTravelTime)    
            foutveh.write('- average vehicular travel time(s):%s\n' %method.avgTravelTime)
            foutveh.write('- total travel length(m):%s, ' %method.totalTravelLength)
            foutveh.write('- average vehicular travel length(m):%s\n' %method.avgTravelLength)
            foutveh.write('- average vehicular travel speed(m/s):%s\n' %method.avgTravelSpeed)
        '''
        foutveh.write('<data>\n\t<items>')
        # foutveh.write('average vehicular travel length(m) = the sum of all vehicular travel lengths / the number of vehicles\n')
        for method in assignments.values():
            foutveh.write('\n\t\t<item name="totalNumberOfVehicles">%d' % method.totalVeh + '</item>')
            foutveh.write('\n\t\t<item name="totalDepartureDelay">%d' % method.totalDepartDelay + '</item>')
            foutveh.write('\n\t\t<item name="averageDepartureDelay">%d' % method.avgDepartDelay + '</item>')
            foutveh.write('\n\t\t<item name="totalWaitingTime">%d' % method.totalWaitTime + '</item>')
            foutveh.write('\n\t\t<item name="averageVehicularWaitingTime">%d' % method.avgWaitTime + '</item>')
            foutveh.write('\n\t\t<item name="totalTravelTime">%d' % method.totalTravelTime + '</item>')
            foutveh.write('\n\t\t<item name="averageVehicularTravelTime">%d' % method.avgTravelTime + '</item>')
            foutveh.write('\n\t\t<item name="totalTravelLength">%d' % method.totalTravelLength + '</item>')
            foutveh.write('\n\t\t<item name="averageVehicularTravelLength">%d' % method.avgTravelLength + '</item>')
            foutveh.write('\n\t\t<item name="averageVehicularTravelSpeed">%d' % method.avgTravelSpeed + '</item>')
        foutveh.write('\n\t</items>\n</data>')
        foutveh.close()
#
# def main():
#     # TripStatistics("../data/input-statistics/small-extract-for-testing/trips.xml")
#     t = io.StringIO('<tripinfos xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/tripinfo_file.xsd" id="2019-07-07-18-39-32-6caf1b81-b563-44a6-ab53-1f345eb59852"><tripinfo id="49" depart="50.00" departLane="180259843#2_0" departPos="0.20" departSpeed="0.00" departDelay="1.00" arrival="118.00" arrivalLane="-362226760#2_0" arrivalPos="11.16" arrivalSpeed="6.85" duration="68.00" routeLength="488.01" waitingTime="0.00" waitingCount="0" stopTime="0.00" timeLoss="9.47" rerouteNo="0" devices="tripinfo_49" vType="DEFAULT_VEHTYPE" speedFactor="0.85" vaporized=""/></tripinfos>')
#     TripStatistics(t)
#
#
# if __name__ == '__main__':
#     main()