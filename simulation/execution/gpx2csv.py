# from gpx_csv_converter import Converter
#
# my_gpx_string = "E:\heatmap-gpx\\myOutput1.gpx"
# string = '<?xml version="1.0" encoding="UTF-8"?><gpx version="1.0"><trk><name>1</name><trkseg><trkpt lon="11.769746" lat="48.156659"><time>2.0</time></trkpt><trkpt lon="11.769766" lat="48.156667"><time>3.0</time></trkpt><trkpt lon="11.769814" lat="48.156688"><time>4.0</time></trkpt><trkpt lon="11.769873" lat="48.156714"><time>5.0</time></trkpt><trkpt lon="11.769938" lat="48.156742"><time>6.0</time></trkpt><trkpt lon="11.769991" lat="48.156765"><time>7.0</time></trkpt><trkpt lon="11.770044" lat="48.156788"><time>8.0</time></trkpt><trkpt lon="11.770098" lat="48.156811"><time>9.0</time></trkpt><trkpt lon="11.770163" lat="48.15684"><time>10.0</time></trkpt><trkpt lon="11.770221" lat="48.156865"><time>11.0</time></trkpt><trkpt lon="11.770287" lat="48.156894"><time>12.0</time></trkpt><trkpt lon="11.770349" lat="48.15692"><time>13.0</time></trkpt><trkpt lon="11.770404" lat="48.156944"><time>14.0</time></trkpt><trkpt lon="11.730117" lat="48.166074"><time>15.0</time></trkpt><trkpt lon="11.730203" lat="48.166126"><time>16.0</time></trkpt></trkseg></trk></gpx>'
# with open(my_gpx_string, 'r') as file:
#     data = file.read()
#     Converter(my_gpx_string, 'E:\heatmap-gpx\csvtest.csv')
from lxml import etree

def parse_gpx_to_csv(filepath, save_to_filepath):
    i = 0
    with open(save_to_filepath, 'w') as fb:
        for event, elem in etree.iterparse(filepath, events=('end',), tag='trkpt'):
            lat = elem.attrib['lat']
            lon = elem.attrib['lon']
            fb.write(lat + ',' + lon + ',\n')
            i = i + 1
            if event == 'end':
                elem.clear()
        print(i)


# filepath = "E:\heatmap-gpx\\myOutput1.gpx"
# save_to_filepath = "E:\heatmap-gpx\\csv1.csv"
# parse_gpx_to_csv(filepath, save_to_filepath)