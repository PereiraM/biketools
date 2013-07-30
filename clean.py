from __future__ import print_function, division
import os, json, time
from datetime import datetime, timedelta

from pprint import pprint

# data cleaning utility functions
# strip seconds from a datetime
def desecond(dt): return datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute)
# convert a datetime to a float which can be parsed in JS with new Date(jsTime)
def to_js_time(dt): return time.mktime(dt.timetuple())
# parse a raw file name into a datetime
def parse_file_time(time_str): 
    return datetime.strptime(time_str, '%Y-%m-%d %I:%M:%S %p')
# turn a datetime back into a filename
def unparse_file_time(file_time):
    return file_time.strftime('%Y-%m-%d %I:%M:%S %p')
# round a number to nearest n - eg. round_to(28, 10) returns 30
def round_to(x, base=1): return int(base * round(float(x)/base))
# round a datetime to nearest n minutes - round_time_to(9:12:42, 10) returns 9:10:00
def round_time_to(orig_time, base=1):
    ot = orig_time
    rhour = ot.hour
    rminute = round_to(ot.minute, base)
    round_delta = timedelta(minutes=(rminute - ot.minute))
    return desecond(orig_time + round_delta)

# parsing functions
# make station bike data point from a single full station's raw data point
def make_station_data(station_full):
    station_data = {}
    station_data['aDocks'] = station_full['availableDocks']
    station_data['aBikes'] = station_full['availableBikes']
    try:
        station_data['pFull'] = ((station_full['totalDocks'] - station_full['availableDocks']) / station_full['totalDocks'])
    except:
        station_data['pFull'] = 1.0
        
#     try:
#         station_data['pBroken'] = ((station_full['totalDocks'] - (station_full['availableDocks'] + station_full['availableBikes'])) / station_full['totalDocks'])
#     except:
#         station_data['pBroken'] = 1.0
    
    return station_data
# make a data object representing all bike data for all stations at a given time from a raw data file name
def make_stations_data(file_name, rounded_time):
    if rounded_time == None: rounded_time = parse_file_time(file_name)
    
    data_file = open('data_raw/' + file_name, 'r')
    stations_raw = json.loads(data_file.read())
    data_file.close()
    stations_full = stations_raw['stationBeanList']
    
    stations_data = {}
    stations_data['datetime'] = unparse_file_time(rounded_time)
    stations_data['jsTime'] = to_js_time(rounded_time)
    stations_data['bikeData'] = {}
    for station_full in stations_full:
        stations_data['bikeData'][station_full['id']] = make_station_data(station_full)
    return stations_data
    
def filter_interval(file_names, minutes):
    # this function takes a raw data timeseries (of whatever interval)
    # and returns another timeseries with one data point every n minutes.
    # if a data point is missing, another will be rounded to fill it if possible
    # (eg. if 9:05 is missing, 9:06's data will be used to fill the gap)
    
    data_times = map(parse_file_time, file_names)
    
    def make_time_map(data_time, minutes):
        rtime = rounded_time = round_time_to(data_time, base=minutes)
        error = abs(rounded_time - data_time)
        return {'data_time': data_time, 'rounded_time': rtime, 'error': str(error)}
    
    data_time_maps = [make_time_map(data_times[0], minutes)]
    for data_time in data_times:
        last_tmap = data_time_maps[-1]
        cur_tmap = make_time_map(data_time, minutes)
        if cur_tmap['rounded_time'] == last_tmap['rounded_time']:
            if cur_tmap['error'] < last_tmap['error']:
                data_time_maps[-1] = cur_tmap
        else:
            data_time_maps.append(cur_tmap)
    #return data_time_maps
    
    def make_data_point(time_map):
        file_name = unparse_file_time(time_map['data_time'])
        rounded_time = time_map['rounded_time']
        return make_stations_data(file_name, rounded_time)
    
    interval_data = map(make_data_point, data_time_maps)
    return interval_data

def make_data_day_files():
    data_files = os.listdir('data_raw')
    data_files = filter(lambda file_name: file_name != '.gitignore', data_files)
    data_files.sort(key=parse_file_time)
    
    def group_by_day(files_by_day, file_name):
        day_str = file_name[:10]
        if day_str in files_by_day:
            files_by_day[day_str].append(file_name)
        else:
            files_by_day[day_str] = [file_name]
        return files_by_day
    
    files_by_day = reduce(group_by_day, data_files, {})
    json.encoder.FLOAT_REPR = lambda f: ("%.3f" % f)
    i = 1
    for date_str in files_by_day:
        print('making day file', date_str, '(', i, 'of', len(files_by_day.keys()), ')')
        interval_data = filter_interval(files_by_day[date_str], 15)
        day_file = open('data/history/' + date_str + '.js', 'w')
        day_file.write(json.dumps(interval_data))
        day_file.close()
        i+=1

make_data_day_files()
data_files = os.listdir('data_raw')
data_files = filter(lambda file_name: file_name != '.gitignore', data_files)
data_files.sort(key=parse_file_time)

# find gaps in data bigger than # mins and show them
last_file_time = parse_file_time(data_files[0])
for file_name in data_files:
    file_time = parse_file_time(file_name)
    gap = file_time - last_file_time
    if gap.seconds > 180:
        print('data gap: ', str(gap), 'missing from', str(last_file_time), 'to', str(file_time))
    last_file_time = file_time

# make stations.js - a list of all stations
last_file_name = data_files[-1]
last_file = open('data_raw/' + last_file_name, 'r')
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

json.encoder.FLOAT_REPR = lambda f: ("%.10f" % f)
stations_file = open('data/stations.js', 'w')
stations_file.write(json.dumps(stations))
stations_file.close()



# make current.js - file of most recent bike data points
current_data = make_stations_data(last_file_name, None)
current_file = open('data/current.js', 'w')
current_file.write(json.dumps(current_data))
current_file.close()
