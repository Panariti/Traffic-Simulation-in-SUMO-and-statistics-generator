import string
from xml.sax import saxutils, make_parser, handler


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

    def __repr__(self):
        return "%s_%s_%s_%s_%s_%s<%s>" % (
        self.label, self.depart, self.arrival, self.speed, self.traveltime, self.travellength, self.route)


# This class is used in the significance test.
class Assign:
    def __init__(self, method, totalVeh, totalTravelTime, totalTravelLength, totalDepartDelay, totalWaitTime,
                 avgTravelTime, avgTravelLength, avgTravelSpeed, avgDepartDelay, avgWaitTime, SDTravelTime, SDLength,
                 SDSpeed, SDWaitTime, waiting_time_of_vehicles, speeds_of_vehicles, totalDuration, avgDuration):
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
        if name == 'tripinfo':
            self._Vehicle = Vehicle(attrs['id'])
            self._Vehicle.traveltime = float(attrs['duration'])
            self._Vehicle.travellength = float(attrs['routeLength'])
            self._Vehicle.departdelay = float(attrs['departDelay'])
            self._Vehicle.waittime = float(attrs['departDelay'])
            self._Vehicle.durationtime = float(attrs['duration'])
            self._vehList.append(self._Vehicle)


# output the network statistics based on the sumo-simulation results
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
