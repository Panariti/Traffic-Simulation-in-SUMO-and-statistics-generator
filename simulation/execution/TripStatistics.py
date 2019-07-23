import os, sys, datetime, math, operator
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import xmltodict, json
from lxml import etree
from xml.sax import saxutils, make_parser, handler
from optparse import OptionParser
import DatabaseClasses as hc
import helperClasses as helperc
# mpl.use('agg')
def getBasicStats(verbose, method, vehicles, assignments):
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
    waiting_time_of_vehicles = []
    speeds_of_vehicles = []
    for veh in vehicles:
        # print(veh.)
        totalVeh += 1
        veh.method = method
        # unit: speed - m/s; traveltime - s; travel length - m
        veh.speed = veh.travellength / veh.traveltime
        totalTravelTime += veh.traveltime / 60.0
        totalTravelLength += veh.travellength
        totalWaitTime += veh.waittime / 60.0
        waiting_time_of_vehicles.append(veh.waittime / 60.0)
        totalTravelSpeed += veh.speed
        speeds_of_vehicles.append(veh.speed)
        totalDepartDelay += veh.departdelay / 60.0
        totalDuration += veh.durationtime / 60.0

    # print('speeds', speeds_of_vehicles)
    # print(waiting_time_of_vehicles)
    # Create a figure instance
    # print(waiting_time_of_vehicles)

    if verbose:
        print('totalVeh:', totalVeh)
    avgTravelTime = totalTravelTime / totalVeh
    avgTravelLength = totalTravelLength / totalVeh
    avgTravelSpeed = totalTravelSpeed / totalVeh
    avgWaitTime = totalWaitTime / totalVeh
    avgDepartDelay = totalDepartDelay / totalVeh
    avgDuration = totalDuration / totalVeh
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

    assignments[method] = helperc.Assign(method, totalVeh, totalTravelTime, totalTravelLength,
                                 totalDepartDelay, totalWaitTime, avgTravelTime,
                                 avgTravelLength, avgTravelSpeed, avgDepartDelay,
                                 avgWaitTime, SDTravelTime, SDLength, SDSpeed, SDWaitTime, waiting_time_of_vehicles, speeds_of_vehicles, totalDuration, avgDuration)

def getStatisticsOutput(assignments, outputfile=None):
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
        statsJSONFormat = statsJSONFormat + '\n\t\t"averageDurationOfTraveling":{}'.format(method.avgDuration)
        statsJSONFormat = statsJSONFormat + "\n}"
    print(statsJSONFormat)
    dbStats = json.loads(statsJSONFormat)
    new_result = statistics.insert_one(dbStats)
    # print(dbStats)
    print('One post with statistics:{0}'.format(new_result.inserted_id))

    def __repr__(self):
        return "%s_%s_%s_%s_%s_%s<%s>" % (self.label, self.depart, self.arrival, self.speed, self.traveltime, self.travellength, self.route)

def plotStatistics(assignments):
    for method in assignments.values():
        #Create a density plot from the list of waiting times of vehicles
        # This will show the trend of the waiting time increase
        from scipy.stats import gaussian_kde
        # data = waiting_time_of_vehicles
        # data = method.waiting_time_of_vehicles
        # density = gaussian_kde(data)
        # xs = np.linspace(0, 8, 200)
        # density.covariance_factor = lambda: .25
        # density._compute_covariance()
        # plt.plot(xs, density(xs))
        # plt.title('Density plot of waiting time of vehicles')
        # plt.show()

        # # It shows a boxplot for the speeds of the vehicles
        # fig = plt.figure(1, figsize=(9, 6))
        # # Create an axes instance
        # ax = fig.add_subplot(111)
        # # Create the boxplot
        # bp = ax.boxplot(method.speeds_of_vehicles)
        # # Save the figure
        # # fig.savefig('fig1.png', bbox_inches='tight')
        # plt.title('Box plot of speeds of vehicles')
        # plt.show()



def xml2dict(element):
    string_element = etree.tostring(element, encoding='utf8').decode('utf8')
    output = xmltodict.parse(string_element)
    # output['edge'].pop('@xmlns:xsi')
    output_final = json.dumps(output)
    return output_final + ','

optParser = OptionParser()
optParser.add_option("-t", "--tripinform-file", dest="vehfile",
                     help="read vehicle information generated by the DUA assignment from FILE (mandatory)",
                     metavar="FILE")
# optParser.add_option("-o", "--output-file", dest="outputfile", default="Global_MOE.txt",
#                      help="write output to FILE", metavar="FILE")
# optParser.add_option("-g", "--SGToutput-file", dest="sgtoutputfile", default="significanceTest.txt",
#                      help="write output to FILE", metavar="FILE")
optParser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                     default=False, help="tell me what you are doing")

(options, args) = optParser.parse_args()
# print(options, args)
if not options.vehfile:
    optParser.print_help()
    sys.exit()
parser = make_parser()

allvehicles = {}
for filename in options.vehfile.split(","):
    allvehicles[filename] = []
    parser.setContentHandler(helperc.VehInformationReader(allvehicles[filename]))
    parser.parse(filename)

# print('all_vehicles', allvehicles.items())
# Vehicles from dua, incremental, clogit and oneshot are in included in the allvehlist.

# intitalization
combilabel = ''

assignments = {}
# calculate/read the basic statistics
database = hc.Database()
statistics = database._db.statistics
for method, vehicles in allvehicles.items():
    getBasicStats(options.verbose, method, vehicles, assignments)

getStatisticsOutput(assignments)
plotStatistics(assignments)
print('The calculation of network statistics is done!')