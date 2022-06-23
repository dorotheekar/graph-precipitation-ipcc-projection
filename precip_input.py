import xarray as xr
import pandas as pd
import netCDF4
from matplotlib import pyplot as plt
import numpy as np
import geopandas as gpd
from geopandas import GeoDataFrame
from matplotlib import font_manager

from shapely.geometry import Point, MultiPoint
from geopandas import GeoDataFrame


from precip_main import precipitation_graph


################################################################
# Select historical period
# Outputs : histo_start_date, histo_end_date, histo_years_number

while True :
    histo_start_year = input(f">>> Start year of historical period studied ? (Between 2006 and 2019) = ")
    
    if int(histo_start_year) >= 2006 and int(histo_start_year) <= 2019 :
        histo_start_date = histo_start_year + "0101"
        
        while True :
            histo_end_year = input(f">>> End year of historical period studied ? (Between {histo_start_year} and 2020) = ")

            if int(histo_end_year) > int(histo_start_year) and int(histo_end_year) <= 2020:
                histo_end_date = histo_end_year + "0101"
                histo_years_number = int(histo_end_year) - int(histo_start_year)

                break

            else : 
                print(f"Please enter a year between {histo_start_year} and 2020 ")

        break            
    else :
        print(f"Please enter a year between 2006 and 2019 ")

################################################################
# Select projection period
# Outputs : projec_start_date, projec_end_date, RCP, projec_years_number

while True :
    projec_start_year = input(f">>> Start year of projection period studied ? (Between 2036 and 2059) = ")

    if int(projec_start_year) >= 2036 and int(projec_start_year) <= 2059 :
        projec_start_date = projec_start_year + '0101'

        while True :
            projec_end_year = input(f">>> End year of projection period studied ? (Between {projec_start_year} and 2060) =  ")

            if int(projec_end_year) > int(projec_start_year) and int(projec_end_year) <= 2060:
                projec_end_date = projec_end_year + '0101'
                projec_years_number = int(projec_end_year) - int(projec_start_year)
                RCP = input('>> For what projection ? (RCP26, RCP45, RCP85) = ')

                break
            else :
                print(f"Please enter a year between {projec_start_year} and 2060 ")

        break

    else : 
        print(f"Please enter a year between 2036 and 2059 ")



################################################################
# User choices for precipitation_graph class

user_choice = precipitation_graph(

    histo_start_date, histo_end_date,
    projec_start_date, projec_end_date, RCP,
    histo_years_number, projec_years_number

	)

# Apply map_division function to finish user choices. See function to get details
geo_data_used, geo_data_used_without_index, chosen_name, chosen_name_index = user_choice.map_division()


# Customed title considering chosen variable
title = f'Cumul de pluie sur {chosen_name} (Projection {RCP} = {projec_years_number} ans, Historique = {histo_years_number} ans)'


print('*** All choices have been saved. Beginning of the process ... ***')

################################################################

histo, projec = user_choice.open_files()

print('Extracting location points from files ...')
df_histo = user_choice.files_location_points(histo)
df_projec = user_choice.files_location_points(projec)
print('End of location points extraction.')

print('Selecting of french area ...')
histo_initial_data = user_choice.french_area(df_histo)
projec_initial_data = user_choice.french_area(df_projec)
print('End of french area selection.')

print('Extracting precipitation and time  ...')
histo_initial_data = user_choice.extract_precip_and_time(histo_initial_data, histo)
projec_initial_data = user_choice.extract_precip_and_time(projec_initial_data, projec)
print('End of precipitation and time extraction.')

################################################################
# Quick remark : could define those functions into main without errors. 
# I managed to define functions here to get declinasion of precipitation data for each dates
print( 'Giving corresponding precipitation to time data ...')

#######################################
def histo_giving_precip_and_time(row):

    precip = row.prAdjust
    times = row.time
        
    histo_index_list.extend([row.geometry] * len(times))
    histo_precip_list.extend(precip)
    histo_times_list.extend(times)
######################################

histo_index_list = []
histo_precip_list = []
histo_times_list = []

histo_initial_data.apply(histo_giving_precip_and_time, axis = 1)

histo_intermediate_dataframe = pd.DataFrame({
    "geometry": histo_index_list,
    'precip' : histo_precip_list,
    "time": histo_times_list
})


histo_intermediate_data = GeoDataFrame(histo_intermediate_dataframe, crs = "EPSG:4326", geometry = histo_index_list)

########################################
def projec_giving_precip_and_time(row):

    precip = row.prAdjust
    times = row.time
        
    projec_index_list.extend([row.geometry] * len(times))
    projec_precip_list.extend(precip)
    projec_times_list.extend(times)

######################################

projec_index_list = []
projec_precip_list = []
projec_times_list = []


projec_initial_data.apply(projec_giving_precip_and_time, axis = 1)

projec_intermediate_dataframe = pd.DataFrame({
    "geometry": projec_index_list,
    'precip' : projec_precip_list,
    "time": projec_times_list
})

projec_intermediate_data = GeoDataFrame(projec_intermediate_dataframe, crs = "EPSG:4326", geometry = projec_index_list)

print( 'End of giving corresponding precipitation to time data.')

################################################################
print('Scaling data on chosen region...')
histo_data_scaled = user_choice.data_scaled_on_region(histo_intermediate_data, geo_data_used_without_index, chosen_name_index)
projec_data_scaled = user_choice.data_scaled_on_region(projec_intermediate_data, geo_data_used_without_index, chosen_name_index)
print('End of data on chosen region scaling.')

print('Grouping data by week...')
histo_time_grouping_by_week = user_choice.grouping_by_week(histo_data_scaled)
projec_time_grouping_by_week = user_choice.grouping_by_week(projec_data_scaled)
print('End of data by week grouping.')


print('Computing precipitation mean on weeks ...')
histo_weekly_data = user_choice.weekly_accumulated(histo_time_grouping_by_week)
projec_weekly_data = user_choice.weekly_accumulated(projec_time_grouping_by_week)
print('End of precipitation mean on weeks computing')

# Getting path for custom font
path = 'C:\\Windows\\Fonts\\FontFont - Daxline Offc Light.ttf'
prop = font_manager.FontProperties(fname = path)
plt.rcParams['font.family'] = prop.get_name()

# Applying function to get precipitation graph
user_choice.get_precip_graph(histo_weekly_data, projec_weekly_data, title, prop)

print('*** Process successfully executed. Check folders to see output. ***')