# create_rli_configfile.py

- **This script is dedicated to the creation of the configuration file for the r.li module of GRASS GIS.**
- It creates the configuration file for r.li using landscape units defined by vector layer polygons. 
- The script will create several configuration corresponding to the different landcover where spatial metrics have to be computed in the same landscape units

### Parameters:
- 'listoflandcoverraster' wait for a list containing the name of landcover raster to be used
- 'listoflandcoverraster' wait for a list containing the name of landcover raster to be used
- 'landscape_polygons' wait for a vector layer of polygons that correspond to the landscape units to be used for analysis 
- 'uniqueid' wait for the name of the 'landscape_polygons' layer's columns containing unique ID for each landscape unit polygon
- 'returnlistpath' wait for a boolean value (True or False) depending if the list of path to the configuration file is desired as return of the function

#### TODOs:
- Add check if raster provided in 'listoflandcoverraster' exists
- Add check of same spatial resolution (and extend) between the different landcover raster in the list



# compute_landscapelevel_metrics.py

- **Function that compute different landscape metrics (spatial metrics) at landscape level.**
- The metric computed are "dominance","pielou","renyi","richness","shannon","simpson".
- It is important to set the computation region before runing this script so that it match the extent of the 'raster' layer.

### Parameters:
- 'configfile' wait for the path (string) to the configuration file corresponding to the 'raster' layer.
- 'raster' wait for the name (string) of the landcover map on which landscape metrics will be computed.
- 'returnlistresult' wait for a boolean value (True/False) according to the fact that a list containing the path to the result files is desired.
- 'ncores' wait for a integer corresponding to the number of desired cores to be used for parallelization.



# compute_classlevel_metrics.py

- **Function that compute different landscape metrics (spatial metrics) at class level.**
- The metric computed are "patch number (patchnum)","patch density (patchdensity)","mean patch size(mps)", "coefficient of variation of patch area (padcv)","range of patch area size (padrange)", "standard deviation of patch area (padsd)", "shape index (shape)", "edge density (edgedensity)".
- It is important to set the computation region before runing this script so that it match the extent of the 'raster' layer.

### Parameters:
- 'configfile' wait for the path (string) to the configuration file corresponding to the 'raster' layer.
- 'raster' wait for the name (string) of the landcover map on which landscape metrics will be computed.
- 'returnlistresult' wait for a boolean value (True/False) according to the fact that a list containing the path to the result files is desired.
- 'ncores' wait for a integer corresponding to the number of desired cores to be used for parallelization.
