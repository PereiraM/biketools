from __future__ import print_function
import urllib2, json, os, time, sys

FAVORITE_STATIONS = []
#FAVORITE_STATIONS = [250, 251, 303, 317, 326, 394, 432, 445]
#FAVORITE_STATIONS = [150, 250, 251, 266, 301, 303, 317, 326, 339, 375, 393, 394, 432, 433, 445]

def colored(text, color):
    colors = {'red': '\033[91m', 'green': '\033[92m'}
    color_end = '\033[0m'
    if color in colors:
        return colors[color] + text + color_end
    else:
        return text

def print_header(data_time):
    print('CitiBike station data as of', data_time)
    if not len(FAVORITE_STATIONS):
        print('Favorite stations not set, showing all stations')
    print('LEGEND: ', colored("| broken bike ", 'red'), colored("| available bike ", 'green'), ": empty dock")

def main():
    try:
        stations_data_str = urllib2.urlopen('http://citibikenyc.com/stations/json').read()
        stations_data = json.loads(stations_data_str)
        data_time = stations_data['executionTime']
        stations = stations_data['stationBeanList']
        my_stations = filter(lambda station: station['id'] in FAVORITE_STATIONS or not len(FAVORITE_STATIONS), stations)
        max_docks = reduce(lambda max_docks, station: max(max_docks, station['totalDocks']), my_stations, 0)
        print(max_docks)
        print_header(data_time)
        
        for station in my_stations:
            if station['id'] in FAVORITE_STATIONS or not len(FAVORITE_STATIONS):
                station_name_trimmed = station['stationName'][0:22].ljust(25)
                print(station['id'], '\t', station_name_trimmed, end='  ')
                
                if(station['statusKey'] == 1):
                    total_docks = station['totalDocks']
                    available_docks = station['availableDocks']
                    available_bikes = station['availableBikes']
                    broken_bikes = total_docks - (available_bikes + available_docks)
                    
                    print(colored(broken_bikes * "|", 'red'), end='')
                    print(colored(available_bikes * "|", 'green'), end='')
                    print(available_docks * ":", end='   ')
                    
                    rjust_spaces = max_docks - total_docks
                    bikes_str_trimmed = ((" " * rjust_spaces) + str(available_bikes) + '/' + str(total_docks) + ' bikes ')
                    print(bikes_str_trimmed)
                    #print('(', station['availableBikes'], '/', station['totalDocks'], 'bikes)')
                else:
                    print(colored('STATION NOT IN SERVICE', 'red'))
    except:
        print("error:", sys.exc_info()[1].message)

if __name__ == '__main__':
    main()