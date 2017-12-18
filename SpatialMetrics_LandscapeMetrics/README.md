# create_rli_configfile.py

- **This script is dedicated to the creation of the configuration file for the r.li module of GRASS GIS.**
- It creates the configuration file for r.li using landscape units defined by vector layer polygons. 
- The script will create several configuration corresponding to the different landcover where spatial metrics have to be computed in the same landscape units

### Parameters:
- 'listoflandcoverraster' wait for a list containing the name of landcover raster to be used
- 'listoflandcoverraster' wait for a list containing the name of landcover raster to be used
- 'landscape_polygons' wait for a vector layer of polygons that correspond to the landscape units to be used for analysis 
- 'returnlistpath' wait for a boolean value (True or False) depending if the list of path to the configuration file is desired as return of the function

#### TODOs:
- Add check if raster provided in 'listoflandcoverraster' exists
- Add check of same spatial resolution (and extend) between the different landcover raster in the list