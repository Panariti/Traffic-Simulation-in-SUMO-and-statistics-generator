import sys
import random
from subprocess import call

tripInfoFile = "../data/input-simulation/small-extract-for-testing/trips.xml"
statisticsFile = "../data/output-simulation/stats.xml"

retcode = call(['python', 'TripStatistics.py',
				'-t', tripInfoFile], stdout=sys.stdout, stderr=sys.stderr)

# retcode = call(['python', 'TripStatistics.py',
# 				'-t', tripInfoFile,
# 				'-o', statisticsFile], stdout=sys.stdout, stderr=sys.stderr)

