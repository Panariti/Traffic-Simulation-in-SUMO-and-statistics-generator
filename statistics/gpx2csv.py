#Converts gpx data to csv with latitude and longitude data. Suitable for displaying traffic heatmaps. Works well with large files.

from lxml import etree

def parse_gpx_to_csv(filepath, save_to_filepath):
    with open(save_to_filepath, 'w') as fb:
        for event, elem in etree.iterparse(filepath, events=('end',), tag='trkpt'):
            lat = elem.attrib['lat']
            lon = elem.attrib['lon']
            fb.write(lat + ',' + lon + ',\n')
            if event == 'end':
                elem.clear()


# filepath = "E:\heatmap-gpx\\myOutput1.gpx"
# save_to_filepath = "E:\heatmap-gpx\\csv1.csv"
# parse_gpx_to_csv(filepath, save_to_filepath)