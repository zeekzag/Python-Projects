import urllib.request, urllib
import numpy as np

urllib.request.urlretrieve('https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt','stations.txt')
urllib.request.urlretrieve('https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt','readme.txt')

# IV. FORMAT OF "ghcnd-stations.txt"

# ------------------------------
# Variable   Columns   Type
# ------------------------------
# ID            1-11   Character
# LATITUDE     13-20   Real
# LONGITUDE    22-30   Real
# ELEVATION    32-37   Real
# STATE        39-40   Character
# NAME         42-71   Character
# GSN FLAG     73-75   Character
# HCN/CRN FLAG 77-79   Character
# WMO ID       81-85   Character
# ------------------------------

# create numpy array for stations 
'''stations = np.genfromtxt('stations.txt',
                          delimiter = [11, 9, 10, 7, 3, 31, 4, 4, 6],
                          names = ['id', 'latitude', 'longitude', 'elevation', 'state', 'name', 'gsn', 'hcn', 'wmo'],
                          dtype = ['U11', 'd', 'd', 'd', 'U3', 'U31', 'U4', 'U4', 'U6'],
                          autostrip = True)'''
# finding state CA and name with los angeles for ID
'''stations_ca = stations[stations['state'] == 'CA']
all_la_station = stations[np.char.find(stations['name'], 'LOS ANGELES') == 0]
print(stations_ca)
print(all_la_station)'''

# plot and check graph for state CA and name LOS ANGELES for visualisation.
'''pp.plot(stations_ca['longitude'], stations_ca['latitude'], '.', markersize = 1)
pp.plot(all_la_station['longitude'], all_la_station['latitude'], '.', markersize = 1)
pp.savefig('stations_ny.png')'''

# To alternate different station_ids with changing only station_id
station_id = 'USW00093134'
urllib.request.urlretrieve(f'https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/all/{station_id}.dly', f'{station_id}.txt')

# III. FORMAT OF DATA FILES (".dly" FILES)

# ------------------------------
# Variable   Columns   Type
# ------------------------------
# ID            1-11   Character
# YEAR         12-15   Integer
# MONTH        16-17   Integer
# ELEMENT      18-21   Character
# VALUE1       22-26   Integer
# MFLAG1       27-27   Character
# QFLAG1       28-28   Character
# SFLAG1       29-29   Character
# VALUE2       30-34   Integer
# MFLAG2       35-35   Character
# QFLAG2       36-36   Character
# SFLAG2       37-37   Character
#   .           .          .
#   .           .          .
#   .           .          .
# VALUE31    262-266   Integer
# MFLAG31    267-267   Character
# QFLAG31    268-268   Character
# SFLAG31    269-269   Character
# ------------------------------

# create numpy array for downtown los angeles station
la_station = np.genfromtxt(f"{station_id}.txt",
                          delimiter = [11, 4, 2, 4] + [5, 1, 1, 1]*31,
                          # showing columns 0-3 and column4 to 4*31 days, by steps of 4 to remove flags in the data
                          usecols = [0, 1, 2, 3] + list(range(4, 4*32, 4)),
                          names = ['id', 'year', 'month', 'element'] + [f'day{i}' for i in range(1, 32)],
                          dtype = ['U11', 'i', 'i', 'U4'] + ['i']*31,
                          autostrip = True)

#check total invalid numbers from day1 to 31 to determine reliability of data
invalid_counts = {'TMIN': [], 'TMAX': []}
for i in range(1, 32):
    for element in ['TMIN', 'TMAX']:
        invalid_nums = np.count_nonzero((la_station[f'element'] == element) & (la_station[f'day{i}'] == -9999))
        invalid_counts[element].append(invalid_nums)
#print(invalid_counts)

#variables to store temperature values
min_y1y2 = []
max_y1y2 = []
days = np.arange(1,32)

# function to get values from any 2 years for MIN and MAX and storing them into list
def get_average(y1, y2):
    for year in range(y1, y2):
        #storing data from year and element(TMIN and TMAX) into year_min and year_max
        year_min = la_station[(la_station['year'] == year) & (la_station['element'] == 'TMIN')]
        year_max = la_station[(la_station['year'] == year) & (la_station['element'] == 'TMAX')] 
        for i in year_min:
            for day in days:
                value = i[f'day{day}']
                # converting non-existent values into NaN (cleaning data)
                if value != -9999:
                    min_y1y2.append(value)
                else:
                    min_y1y2.append(np.nan)
        for j in year_max:
            for day in days:
                value = j[f'day{day}']   
                if value != -9999:
                    max_y1y2.append(value)
                else:
                    max_y1y2.append(np.nan)
# use get_value for year 1945 to 1955
get_average(1945, 1956)

year_minvalue = []
year_maxvalue = []

# function to get value for a year
def get_value(y):
    year_min = la_station[(la_station['year'] == y) & (la_station['element'] == 'TMIN')]
    year_max = la_station[(la_station['year'] == y) & (la_station['element'] == 'TMAX')]
    for v in year_min:
        for day in days:
            value = v[f'day{day}']
            if value != -9999:
                year_minvalue.append(value)
            else:
                year_minvalue.append(np.nan)
    for v2 in year_max:
        for day in days:
            value = v2[f'day{day}']
            if value != -9999:
                year_maxvalue.append(value)
            else:
                year_maxvalue.append(np.nan)
#use get_value for a year
get_value(2021)

# convert list into numpy array for arithmetic calculations
npmin_y1y2 = np.array(min_y1y2)
npmax_y1y2 = np.array(max_y1y2)
npmin_year = np.array(year_minvalue)
npmax_year = np.array(year_maxvalue)

# calculate weather anomalies by definition as year's average temperature - midcentury average
# midcentury average for year 1945 to 1955
average_y1y2 = np.nanmean(np.concatenate([npmin_y1y2, npmax_y1y2]))

#calculating a year average
average_year = np.nanmean(np.concatenate([npmin_year, npmax_year]))

#calculate weather anomaly
weather_anomaly = (average_year - average_y1y2)
print(f"anomaly from 2022 comparing to midcentury average is: {weather_anomaly} measured by tenths of degree C")