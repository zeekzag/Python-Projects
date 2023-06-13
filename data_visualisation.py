import urllib.request, urllib
import numpy as np
import matplotlib.pyplot as pp
import pandas as pd

# To alternate different station_ids with changing only station_id
station_id = 'USW00093134'
urllib.request.urlretrieve(f'https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/all/{station_id}.dly', f'{station_id}.txt')

# create numpy array for downtown los angeles station
la_station = np.genfromtxt(f"{station_id}.txt",
                          delimiter = [11, 4, 2, 4] + [5, 1, 1, 1]*31,
                          # showing columns 0-3 and column4 to 4*31 days, by steps of 4 to remove flags in the data
                          usecols = [0, 1, 2, 3] + list(range(4, 4*32, 4)),
                          names = ['id', 'year', 'month', 'element'] + [f'day{i}' for i in range(1, 32)],
                          dtype = ['U11', 'i', 'i', 'U4'] + ['i']*31,
                          autostrip = True)


#plot average degree in tenths of degree from 1925 to 2022
#getting values from years 1925 to 2022 that has element TMIN and TMAX and store to min/max_temp_yearly
years = np.arange(1925,2023)
days = np.arange(1,32)
tmin = la_station[la_station['element'] == 'TMIN']
tmax = la_station[la_station['element'] == 'TMAX']

min_temp_yearly = []
max_temp_yearly = []


for year in years:
    yearly_min = []
    yearly_max = []
    #index and loop tmin using enumerate function
    for i, v_min in enumerate(tmin):
        v_max = tmax[i]
        if v_min['year'] == year and v_max['year'] == year:
            for day in days:
                if v_min[f'day{day}'] != -9999 and v_max[f'day{day}'] != -9999:
                    yearly_min.append(v_min[f'day{day}'])
                    yearly_max.append(v_max[f'day{day}'])
    min_temp_yearly.append(np.nanmean(yearly_min))
    max_temp_yearly.append(np.nanmean(yearly_max))

#convert list into a numpy array for handling big datasets
min_temp_yearly = np.array(min_temp_yearly)
max_temp_yearly = np.array(max_temp_yearly)

fig, ax = pp.subplots()
ax.plot(years, min_temp_yearly, label='Min Temp')
ax.plot(years, max_temp_yearly, label='Max Temp')
ax.set_xlabel('Year 1925 to 2022')
ax.set_ylabel('Temperature (tenths of degree C)')
ax.set_title('Temperature for Downtown Los Angeles')
ax.legend()
pp.savefig('avg_min_max_downtownLA.png')

#using pandas to plot graph and smooth values and reduce impact of outliers in data
temp_data = pd.DataFrame({
    'year': years,
    'min_temp': min_temp_yearly,
    'max_temp': max_temp_yearly
})

# Calculate rolling average with a window size of 10 years
temp_data = temp_data.rolling(window=5, center=True).mean()

# Plot the smoothed data
fig, ax = pp.subplots()
ax.plot(temp_data['year'], temp_data['min_temp'], label='Min Temp')
ax.plot(temp_data['year'], temp_data['max_temp'], label='Max Temp')
ax.set_xlabel('Year 1925 to 2022')
ax.set_ylabel('Temperature (tenths of degree C)')
ax.set_title('Temperature in Downtown Los Angeles')
ax.legend()
pp.savefig('pandas_smoothedgraph.png')