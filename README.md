## Graph of IPCC precipitation projection and historical precipitation (on France : 'départements'/'régions')
### Introduction

> The provided graphs are based on Eurocordex NetCDF files on adjusted IPCC models (https://www.euro-cordex.net/060378/index.php.en) and display 
precipitation cumulation level on historical and projection models. The idea is to provide a comparision between historical and future annual cumulation of precipitation. Time intervall, IPCC projection and geographical french area are to be chosen by user. 
<!-- toc -->
### Table of contents
- [Technology](#technology)
- [Setup](#setup)
- [Folder structure](#folder-structure)
- [Files description](#files-description)
	* [Data](#data)
	* [Input](#input)
	* [Module](#module)
	* [Requirements](#requirements)
	* [Geographical Data](#geographical-data)

### Technology 

Project created with :
```Python 3.9.13```

### Setup

> Please note that geopandas module sometimes can't be just installed with pip install geopandas. This requires to download wheel dependecies such as : Fiona, DAL, pyproj, rtree, and shapely (provided here : https://www.lfd.uci.edu/~gohlke/pythonlibs/). It should match your architecture and python version. When each wheel is downloaded, please open a command prompt and change directories to the folder where they are located. Run for each one of them ```pip install wheel_filename.whl```. Then, run ```pip install geopandas```. When this process is complete, you can properly ```pip install -r requirements.txt``` in order to install all other necessary modules.
<!-- toc -->
### Folder structure
```
├── README.md          
├── prAdjust
│   └── *.nc 
├── precip_input.py              
├── recip_main.py 
├── locations.csv            
├── requirements.txt                                  
├── regions.json            
└── departements.geojson 
```
### Files description
#### Data : 

> Note that anyone could had  other files with other temporal range or other variables respecting folder structure below.
<!-- toc -->
- ```prAdjust``` : .nc files on temporal range 2006 to 2020 (historical) and 2036 to 2060 (RCP85)

#### Input :

- ```precip_input.py``` : list of variables chosen by user
	- ```histo_start_date``` : Start date of historical period studied.
	- ```histo_end_date``` : End date of historical period studied.
	- ```projec_start_date``` :  Start date of projection period studied
	- ```period``` : Name of the scenario projection (RCP26/RCP45/RCP85) if different to historical period. It will appear on the map. (The original project provides only RCP85 projection)
	- ```geo_data_used``` : Geographical data division chosen between 'départements' and 'régions'
	- ```chosen_name``` : Chosen name of 'départements' or 'régions'

#### Module :

- ```precip_main.py``` : contains all custom modules to provide choropleth map.

#### Output :

> Graphs provided in .svg depending on variables chosen by user.
<!-- toc -->

- ```graph_{chosen_name}.svg``` : Graph in .svg

#### Requirements : 


-  ```requirements.txt``` : All external modules needed to run code. Please make sure you've downloaded all geopandas dependencies ([see here](#setup)) 

	- ```pandas```
	- ```xarray```
	- ```numpy```
	- ```geopandas```
	- ```plotly```
	- ```shapely```
	- ```netCDF```
	- ```dask```

#### Geographical data : 

> Files used to parse data according to geographical division chosen by the user
<!-- toc -->

- ```departements.json``` : a .json file providing all 'départements'
- ```regions.json``` : a .json file providing all 'régions'


         
