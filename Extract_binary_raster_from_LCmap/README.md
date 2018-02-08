# Create binary raster

This function creates a binary raster for each category of a base raster. The function run within the current region. If a category do not exists in the current region, no binary map will be produce.


#### Parameters:
- 'categorical_raster' wait for the name of the base raster to be used. It is the one from which one binary raster will be produced for each category value
- 'prefix' wait for a string corresponding to the prefix of the name of the binary raster which will be produced
- 'setnull' wait for a boolean value (True, False) according to the fact that the output binary should be 1/0 or 1/null
- 'returnlist' wait for a boolean value (True, False) regarding to the fact that a list containing the name of binary raster is desired as return of the function
- 'category_list' wait for a list of interger corresponding to specific category of the base raster to be used 

#### TODOs:
- Add option enabling the user to choose between r.mapcalc (creation of the binary as a 'hard copy') or r.reclass (simple reclassify of the original layer, enabling saving hard drive space)