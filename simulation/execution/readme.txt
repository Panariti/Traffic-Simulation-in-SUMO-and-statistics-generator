To use XMLtoMongoDB the following are required:
1. Have SUMO installed and have a path to the SUMO_HOME directory on the SUMO installation(This requirement at least holds in Windows).
2. Have MongoDB installed.
3. Run mongod from the command line.
4. Have the pacakged listed under requirements.txt installed. To install them just run: pip install -r /path/to/requirements.txt

To run the script for a test just use the provided data. The net.net.xml file contains the input of SUMO. This is where the (x,y) coordinates of the nodes are taken and are converted into latitude and longiture afterwards.
The data.xml is the actual sumo output(a smaller chunk of the real sumo output size(more than 7GB)) that is converted to json format and saved into the MongoDB database.

To use XML2JSON and SimVeh2TrafficFlow scripts:
1. There is not need to have MongoDB installed
2. There is no need to have PyMongo installed.

There are two scripts for producing statistics:
    -TripStatistics.py
    -SUMOOutputStatistics.py
To generate the statistics of the script TripStatistics.py just run the script generateStatistics.py
To generate the statistics of the script SUMOOutputStatistics.py just run this script(SUMOOutputStatistics.py)
