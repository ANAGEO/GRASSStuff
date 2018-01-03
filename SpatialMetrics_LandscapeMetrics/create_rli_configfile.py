##### Function that create the r.li configuration file for a list of landcover raster.
### It enable to create in one function as many configuration file as the number of raster provided in 'listoflandcoverraster'.
### It could be use only in case study with a several landcover raster and only one landscape unit layer.
### So, the landscape unit layer if fixed and there are the landcover raster which change. 
# 'listoflandcoverraster' wait for a list with the name (string) of landcover rasters.
# 'landscape_polygons' wait for the name (string) of the vector layer containing the polygons to be used as landscape units.
# 'returnlistpath' wait for a boolean value (True/False) according to the fact that a list containing the path to the configuration files is desired.
# 'ncores' wait for a integer corresponding to the number of desired cores to be used for parallelization.

# Import libraries for multiprocessing 
import multiprocessing
from multiprocessing import Pool
from functools import partial 

# Function that copy the landscape unit raster masks on a new layer with name corresponding to the current 'landcover_raster'
def copy_landscapeunitmasks(current_landcover_raster,base_landcover_raster,landscape_polygons,landscapeunit_bbox,cat):
    ### Copy the landscape units mask for the current 'cat'
    # Define the name of the current "current_landscapeunit_rast" layer
    current_landscapeunit_rast=current_landcover_raster.split("@")[0]+"_"+landscape_polygons.split("@")[0]+"_"+str(cat)          
    base_landscapeunit_rast=base_landcover_raster.split("@")[0]+"_"+landscape_polygons.split("@")[0]+"_"+str(cat)          
    # Copy the the landscape unit created for the first landcover map in order to match the name of the current landcover map
    gscript.run_command('g.copy', overwrite=True, quiet=True, raster=(base_landscapeunit_rast,current_landscapeunit_rast))
    # Add the line to the maskedoverlayarea variable
    maskedoverlayarea="MASKEDOVERLAYAREA "+current_landscapeunit_rast+"|"+landscapeunit_bbox[cat]
    return maskedoverlayarea

# Function that create the r.li configuration file for the base landcover raster and then for all the binary rasters
def create_rli_configfile(listoflandcoverraster,landscape_polygons,returnlistpath=True,ncores=2):
    # Check if 'listoflandcoverraster' is not empty
    if len(listoflandcoverraster)==0:
        sys.exit("The list of landcover raster is empty and should contain at least one raster name")
    # Check if rasters provided in 'listoflandcoverraster' exists to avoid error in mutliprocessing 
    for cur_rast in listoflandcoverraster:
        try:
            mpset=cur_rast.split("@")[1]
        except:
            mpset=""
        if cur_rast not in gscript.list_strings(type='raster',mapset=mpset):
            sys.exit('Raster <%s> not found' %categorical_raster)
    # Check if rasters provided in 'listoflandcoverraster' have the same extend and spatial resolution 
    raster={}
    for x, rast in enumerate(raster_list):
        raster[x]=gscript.raster_info(rast)
    key_list=raster.keys()
    for x in key_list[1:]:
        for info in ('north','south','east','west','ewres','nsres'):
            if not raster[0][info]==raster[x][info]:
                sys.exit("Some raster provided in the list have different spatial resolution or extend, please check")    
    # Get the version of GRASS GIS 
    version=grass.version()['version'].split('.')[0]
    # Define the folder to save the r.li configuration files
    if sys.platform=="win32":
        rli_dir=os.path.join(os.environ['APPDATA'],"GRASS"+version,"r.li")
    else: 
        rli_dir=os.path.join(os.environ['HOME'],".grass"+version,"r.li")
    if not os.path.exists(rli_dir):
        os.makedirs(rli_dir)
    ## Create an ordered list with the 'cat' value of landscape units to be processed.
    list_cat=[int(x) for x in gscript.parse_command('v.db.select', quiet=True, map=landscape_polygons, column='cat', flags='c')]
    list_cat.sort()
    # Declare a empty dictionnary which will contains the north, south, east, west values for each landscape unit
    landscapeunit_bbox={}
    # Declare a empty list which will contain the path of the configation files created
    listpath=[]
    # Declare a empty string variable which will contains the core part of the r.li configuration file
    maskedoverlayarea=""
    # Duplicate 'listoflandcoverraster' in a new variable called 'tmp_list'
    tmp_list=list(listoflandcoverraster)
    # Set the current landcover raster as the first of the list
    base_landcover_raster=tmp_list.pop(0) #The pop function return the first item of the list and delete it from the list at the same time
    # Loop trough the landscape units
    for cat in list_cat:
        # Extract the current landscape unit polygon as temporary vector
        tmp_vect="tmp_"+base_landcover_raster.split("@")[0]+"_"+landscape_polygons.split("@")[0]+"_"+str(cat)
        gscript.run_command('v.extract', overwrite=True, quiet=True, input=landscape_polygons, cats=cat, output=tmp_vect)
        # Set region to match the extent of the current landscape polygon, with resolution and alignement matching the landcover raster
        gscript.run_command('g.region', vector=tmp_vect, align=base_landcover_raster)
        # Rasterize the landscape unit polygon
        landscapeunit_rast=tmp_vect[4:]
        gscript.run_command('v.to.rast', overwrite=True, quiet=True, input=tmp_vect, output=landscapeunit_rast, use='cat', memory='3000')
        # Remove temporary vector
        gscript.run_command('g.remove', quiet=True, flags="f", type='vector', name=tmp_vect)
        # Set the region to match the raster landscape unit extent and save the region info in a dictionary
        region_info=gscript.parse_command('g.region', raster=landscapeunit_rast, flags='g')
        n=str(round(float(region_info['n']),5)) #the config file need 5 decimal for north and south
        s=str(round(float(region_info['s']),5))
        e=str(round(float(region_info['e']),6)) #the config file need 6 decimal for east and west
        w=str(round(float(region_info['w']),6))
        # Save the coordinates of the bbox in the dictionary (n,s,e,w)
        landscapeunit_bbox[cat]=n+"|"+s+"|"+e+"|"+w
        # Add the line to the maskedoverlayarea variable
        maskedoverlayarea+="MASKEDOVERLAYAREA "+landscapeunit_rast+"|"+landscapeunit_bbox[cat]+"\n"

    # Compile the content of the r.li configuration file
    config_file_content="SAMPLINGFRAME 0|0|1|1\n"
    config_file_content+=maskedoverlayarea
    config_file_content+="RASTERMAP "+base_landcover_raster+"\n"
    config_file_content+="VECTORMAP "+landscape_polygons+"\n"

    # Create a new file and save the content
    configfilename=base_landcover_raster.split("@")[0]+"_"+landscape_polygons.split("@")[0]
    path=os.path.join(rli_dir,configfilename)
    listpath.append(path)
    f=open(path, 'w')
    f.write(config_file_content)
    f.close()
    
    # Continue creation of r.li configuration file and landscape unit raster the rest of the landcover raster provided
    while len(tmp_list)>0:
        # Reinitialize 'maskedoverlayarea' variable as an empty string
        maskedoverlayarea=""
        # Set the current landcover raster as the first of the list
        current_landcover_raster=tmp_list.pop(0) #The pop function return the first item of the list and delete it from the list at the same time
        # Copy all the landscape units masks for the current landcover raster
        p=Pool(ncores) #Create a pool of processes and launch them using 'map' function
        func=partial(copy_landscapeunitmasks,current_landcover_raster,base_landcover_raster,landscape_polygons,landscapeunit_bbox) # Set fixed argument of the function
        maskedoverlayarea=p.map(func,list_cat) # Launch the processes for as many items in the list and get the ordered results using map function
        p.close()
        p.join()
        # Compile the content of the r.li configuration file
        config_file_content="SAMPLINGFRAME 0|0|1|1\n"
        config_file_content+="\n".join(maskedoverlayarea)+"\n"
        config_file_content+="RASTERMAP "+current_landcover_raster+"\n"
        config_file_content+="VECTORMAP "+landscape_polygons+"\n"
        # Create a new file and save the content
        configfilename=current_landcover_raster.split("@")[0]+"_"+landscape_polygons.split("@")[0]
        path=os.path.join(rli_dir,configfilename)
        listpath.append(path)
        f=open(path, 'w')
        f.write(config_file_content)
        f.close()
    
    # Return a list of path of configuration files creates if option actived
    if returnlistpath:
        return listpath