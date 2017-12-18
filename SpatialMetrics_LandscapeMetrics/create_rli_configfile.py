######## FUNCTION CREATING THE CONFIGURATION FILE FOR R.LI GRASS GIS'S MODULE.
#### Create the configuration file for r.li using landscape units defined by vector layer polygons. 
#### The script will create several configuration corresponding to the different landcover where spatial metrics have to be computed in the same landscape units
## 'listoflandcoverraster' wait for a list containing the name of landcover raster to be used
## 'landscape_polygons' wait for a vector layer of polygons that correspond to the landscape units to be used for analysis 
## 'returnlistpath' wait for a boolean value (True or False) depending if the list of path to the configuration file is desired as return of the function

####### TODO: Add check if raster provided in 'listoflandcoverraster' exists
####### TODO: Add check of same spatial resolution (and extend) between the different landcover raster in the list

import sys,os
import grass.script as gscript
from grass.script import core as grass

def create_rli_configfile(listoflandcoverraster,landscape_polygons,returnlistpath=False):
    # Check if 'listoflandcoverraster' is not empty
    if len(listoflandcoverraster)==0:
        sys.exit("The list of landcover raster is empty and should contain at least one raster name")
    
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
        # Loop trough the landscape units
        for cat in list_cat:
            # Define the name of the current "current_landscapeunit_rast" layer
            current_landscapeunit_rast=current_landcover_raster.split("@")[0]+"_"+landscape_polygons.split("@")[0]+"_"+str(cat)          
            base_landscapeunit_rast=base_landcover_raster.split("@")[0]+"_"+landscape_polygons.split("@")[0]+"_"+str(cat)          
            # Copy the the landscape unit created for the first landcover map in order to match the name of the current landcover map
            gscript.run_command('g.copy', overwrite=True, quiet=True, raster=(base_landscapeunit_rast,current_landscapeunit_rast))
            # Add the line to the maskedoverlayarea variable
            maskedoverlayarea+="MASKEDOVERLAYAREA "+current_landscapeunit_rast+"|"+landscapeunit_bbox[cat]+"\n"
        # Compile the content of the r.li configuration file
        config_file_content="SAMPLINGFRAME 0|0|1|1\n"
        config_file_content+=maskedoverlayarea
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