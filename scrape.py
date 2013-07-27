import urllib2, json, os, time, sys

while True:
    try:
        print 'requesting data...'
        stations_data_str = urllib2.urlopen('http://citibikenyc.com/stations/json').read()
        stations_data = json.loads(stations_data_str)
        data_time = stations_data['executionTime']
        data_files = os.listdir('data')
        
        if data_time not in data_files:
            data_file = open('data_raw/' + data_time, 'w')
            data_file.write(stations_data_str)
            data_file.close()
            
            print data_time
            stations = stations_data['stationBeanList']
            in_service = 0
            
            for station in stations:
                #if station['id'] in [150, 250, 251, 266, 301, 303, 317, 326, 339, 375, 393, 394, 432, 433, 445]:
                if station['id'] in [250, 251, 303, 317, 326, 394, 432, 445]:
                    print station['id'], '\t', station['stationName'][0:22], '\t- ',
                    print station['availableBikes'], '/', station['totalDocks'], ' bikes (', station['statusValue'], ')'
                if station['statusKey'] == 1:
                    in_service += 1
                    
            print in_service, '/', len(stations), 'stations in service'
        else:
            print "already got", data_time
    except:
        print "error:", sys.exc_info()[1].message
    
    time.sleep(30)
