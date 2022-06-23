###########################################################
# IMPORTATION DES LIBRAIRIES
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


######################################################################
class precipitation_graph:
# Precipitation graph class

    ######################################################################
    def __init__(self,
    histo_start_date, histo_end_date,  # start and end date of historical period chosen by user
    projec_start_date, projec_end_date, RCP, # start and end date of projection period chosen by user + RCP projection name
    histo_years_number, projec_years_number) :  # computation of historical and projection period
    # Variables will be chosen by the user in the input file

        self.histo_start_date = histo_start_date
        self.histo_end_date = histo_end_date
        self.projec_start_date = projec_start_date
        self.projec_end_date = projec_end_date
        self.RCP = RCP
        self.histo_years_number = histo_years_number
        self.projec_years_number = projec_years_number

    ######################################################################        
    def map_division(self):
    # Map division choice : french départements or french régions 

        while True:
            geo_data = input("Choose a french map divison: D (Départements) or R (Région) = ")
            # User is choosing between 2 given choice of map division
            chosen_name = input(" Enter the name of Région/Département chosen = ")
            # User is choosing a name of département/région

            if geo_data == 'D': 
                # French "départements"

                geo_data_used = gpd.read_file('departements.geojson') # Loading geojson of departements
                geo_data_used = geo_data_used.sort_values(by = ['code']).set_index(['code'])
                geo_data_used_without_index = geo_data_used.reset_index() # Loading geojson of departements without indexes

                chosen_name_index = np.where(geo_data_used_without_index["nom"] == chosen_name)[0][0] # Path to departement with name (just to select later POINTS in POLYGONS)

                print("Your choice has been successfully saved.")

                return geo_data_used, geo_data_used_without_index, chosen_name_index

            if geo_data == 'R':
                # French "régions"

                geo_data_used = gpd.read_file('regions.geojson') # Loading geojson of regions
                geo_data_used = geo_data_used.sort_values(by = ['code']).set_index(['code'])
                geo_data_used_without_index = geo_data_used.reset_index() # Loading geojson of regions without indexes

                chosen_name_index = np.where(geo_data_used_without_index["nom"] == chosen_name)[0][0]  # Path to region with name (just to select later POINTS in POLYGONS)

                print("Your choice has been successfully saved.")
                return geo_data_used, geo_data_used_without_index, chosen_name,chosen_name_index


            else :
                print('Error: Please answer D or R to the previous question.')

    ######################################################################
    def open_files(self):
    # NetCDF Files opening sliced by start date, end date,  latitude and longitude

        print("> Files opening in progress...")

        ds = xr.open_mfdataset("./prAdjust/*.nc",  autoclose=True, engine = 'netcdf4')
        ds = ds.sel(rlat = slice(-9, 2), rlon = slice(-15, -6))

        ########################
        # GENERAL DATASET 
        ds['prAdjust'] = ds['prAdjust']*86400 # 1kg m²/s = 86 400 mm/day > conversion needed to have values per day
        ds.attrs['units'] = 'mm/day' # changing units' name

        ########################
        # HISTORICAL DATA SET  
        histo = ds.sel(time = slice(self.histo_start_date, self.histo_end_date)) # selected data over historical period
        histo = histo.resample(time = '7D').sum() # as we decided to have a cumulation on a week, need to sum on 7 days

        ########################
        # DATA SET PROJECTION
        projec = ds.sel(time = slice(self.projec_start_date, self.projec_end_date)) # selected data over projection period
        projec = projec.resample(time = '7D').sum() # as we decided to have a cumulation on a week, need to sum on 7 days

        histo = histo.load() # loading data in RAM will allow us to go faster (Warning : sometimes can causes bugs)
        projec = projec.load()  # loading data in RAM will allow us to go faster (Warning : sometimes can causes bugs)


        print("> Files successfully opened.")

        return histo, projec

    ######################################################################
    def files_location_points(self, dataset):
        # Extracting latitude and longitude on dataset

        df = pd.DataFrame()
        lon = dataset.lon.values
        lat = dataset.lat.values
        rlat_list, rlon_list, lat_list, lon_list =[], [], [], []

        for x, y in [(x,y) for x in dataset.rlat.values for y in dataset.rlon.values]:
            rlat_list.append(x)
            rlon_list.append(y)

            local_ds = dataset.sel(rlat = x, rlon = y)
            lat_list.append(local_ds.lat.values)
            lon_list.append(local_ds.lon.values)

        df = pd.DataFrame({
            "lat": lat_list,
            "lon": lon_list,
            "rlat": rlat_list,
            "rlon" : rlon_list})

        return df

    ######################################################################
    def french_area(self, df):
        # Selecting only french POINTS

        geometry = [Point(xy) for xy in zip(df.lon, df.lat)]
        df_tmp = df.drop(['rlon', 'rlat', 'lon', 'lat'], axis = 1)
        gdf = GeoDataFrame(df, crs = "EPSG:4326", geometry = geometry)

        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))    
        france = world.query('name == "France"')

        initial_data = gpd.sjoin(gdf, france, op = "within")
        initial_data = initial_data.drop(['index_right', 'continent', 'pop_est', 'iso_a3', 'gdp_md_est', 'name'], axis = 1)
        
        return initial_data

    ######################################################################
    def extract_precip_and_time(self, initial_data, dataset):    
        # Extracting precipitation and time data associated to each points

        PrecipList = []
        TimeList = []
        PointList = []

        for x in range(len(initial_data)):
            dataset_sel = dataset.sel(rlat = initial_data['rlat'].iloc[x], rlon = initial_data['rlon'].iloc[x])

            PointList.append(initial_data['geometry'].iloc[x])
            PrecipList.append(dataset_sel['prAdjust'].values.tolist())
            TimeList.append(dataset_sel['time'].values.tolist())


        initial_data['prAdjust'] = PrecipList
        initial_data['time'] = TimeList

        return initial_data

    ######################################################################
    def data_scaled_on_region(self, intermediate_data, geo_data_used_without_index, chosen_name_index) :
        # Get data on a selected région/département, considering variable chosen_name_index

        search_in = intermediate_data.within(geo_data_used_without_index.iloc[chosen_name_index]['geometry'])
        search_out = intermediate_data.loc[search_in]
        
        data_scaled = GeoDataFrame(search_out, crs = "EPSG:4326", geometry = search_out['geometry'] )
        data_scaled = data_scaled.reset_index(drop = True)

        return data_scaled


    ######################################################################
    def grouping_by_week(self, data_scaled):
        # Precipitation mean on weeks

        time_grouping_by_week = data_scaled.groupby('time').agg(list).reset_index()
        # Grouping data by dates (DD/MM/YYYY)

        for row in range(len(time_grouping_by_week)):
            time_grouping_by_week['time'].iloc[row] = time_grouping_by_week['time'].iloc[row].strftime('%V')
            # %V keep number of week of each dates (in range 1 to 53 according to documentation of .strftime)

            time_grouping_by_week['precip'].iloc[row] = (sum(time_grouping_by_week['precip'].iloc[row]) / len(time_grouping_by_week['precip'].iloc[row]))
            # Computation of mean for each dates

        time_grouping_by_week =  time_grouping_by_week.sort_values(by = 'time').reset_index(drop = True)

        return time_grouping_by_week
    ######################################################################
    def weekly_accumulated(self, time_grouping_by_week):    

        weekly_data = time_grouping_by_week.groupby('time').agg(list).reset_index().drop(['geometry'], axis = 1)
        # Grouping each week 

        for row in range(len(weekly_data)):
            weekly_data['precip'].iloc[row] = (sum(weekly_data.iloc[row]['precip']) / len(weekly_data.iloc[row]['precip']))
            # Mean of each week

        weekly_data['precip'] = weekly_data['precip'].cumsum()
        # Accumulation sum 

        return weekly_data
    ######################################################################
    def get_precip_graph(self, histo_weekly_data, projec_weekly_data, title, prop):
        # Graph with two axes : projection and historical precipitation accumulation sum on each week 
        # Note that it's a mean on each week 

        ################################
        x = projec_weekly_data['time'] # In range 0 to 53

        ya = histo_weekly_data['precip'] # Historical data
        yb = projec_weekly_data['precip'] # Projection data

        ################################
        fig = plt.figure()
         
        ax = fig.add_axes([1, 1, 1, 1]) 
        # Size of figure

        ax.plot(x, ya)
        # Historical plot

        ax.plot(x, yb)
        # Projection plot


        ticks = [0,100,200,300,400,500,600,700,800,900, 1000]
        ax.set_yticks(ticks)
        # Custom y tick labels

        xs = [4.34524, 8.34524, 12.34524, 16.34524, 20.34524, 24.34524, 28.34524, 32.34524 , 36.34524, 40.34524, 44.34524, 48.34524] # 1 month = 4.34524 weeks
        labels = ['jan','fév','mar','apr','mai','juin','jul','août','sept','oct','nov','déc']
        plt.xticks(xs, labels, fontname = prop.get_name())
        # Custom x tick labels

        ax.set_title(title, fontproperties = prop)
        # Title of customized font

        ax.legend(['Historique', self.RCP], prop = prop)
        # Simple legend

        #fig.set_facecolor("w")

        fig.savefig("output.svg", bbox_inches = 'tight', dpi = 150)
