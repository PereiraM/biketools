from __future__ import print_function, division
import os, json, time
from datetime import datetime

def desecond(date_str): return date_str[0:-6] + ' ' + date_str[-2:]
def to_js_time(dt): return time.mktime(dt.timetuple())
def parse_time(time_str): return datetime.strptime(desecond(time_str), '%Y-%m-%d %I:%M %p')

data_files = os.listdir('data_old')

# find gaps in data bigger than # mins and show them
data_files.sort(key=parse_time)
last_file_time = parse_time(data_files[0])
for file_name in data_files:
    file_time = parse_time(file_name)
    file_time
    gap = file_time - last_file_time
    if gap.seconds > 180:
        print('data gap: ', str(gap), 'missing from', str(last_file_time), 'to', str(file_time))
    last_file_time = file_time

# make stations.js - a list of all stations
last_file_name = data_files[-1]
last_file = open('data_old/' + last_file_name, 'r')
last_data = json.loads(last_file.read())
last_file.close()

stations_full = last_data['stationBeanList']
stations = []
for station_full in stations_full:
    station = {}
    station['id'] = station_full['id']
    station['stationName'] = station_full['stationName']
    station['totalDocks'] = station_full['totalDocks']
    station['latitude'] = station_full['latitude']
    station['longitude'] = station_full['longitude']
    station['stAddress1'] = station_full['stAddress1']
    stations.append(station)
    
stations_file = open('data/stations.js', 'w')
stations_file.write(json.dumps(stations))
stations_file.close()

# make current.js - file of most recent bike data points
current_data = {}
current_data['datetime'] = last_file_name
current_data['jsTime'] = to_js_time(parse_time(last_file_name))
for station_full in stations_full:
    station_data = {}
    station_data['availableDocks'] = station_full['availableDocks']
    station_data['availableBikes'] = station_full['availableBikes']
    station_data['pFull'] = ((station_full['totalDocks'] - station_full['availableDocks']) / station_full['totalDocks'])
    station_data['pBroken'] = ((station_full['totalDocks'] - (station_full['availableDocks'] + station_full['availableBikes'])) / station_full['totalDocks'])
    current_data[station_full['id']] = station_data

current_file = open('data/current.js', 'w')
current_file.write(json.dumps(current_data))
current_file.close()
