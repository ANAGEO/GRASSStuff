###### Function creating a binary raster for each category of a base raster. 
### The function run within the current region. If a category do not exists in the current region, no binary map will be produce
# 'categorical_raster' wait for the name of the base raster to be used. It is the one from which one binary raster will be produced for each category value
# 'prefix' wait for a string corresponding to the prefix of the name of the binary raster which will be produced
# 'setnull' wait for a boolean value (True, False) according to the fact that the output binary should be 1/0 or 1/null
# 'returnlist' wait for a boolean value (True, False) regarding to the fact that a list containing the name of binary raster is desired as return of the function
# 'category_list' wait for a list of interger corresponding to specific category of the base raster to be used 

def create_binary_raster(categorical_raster,prefix="binary",setnull=False,returnlist=False,category_list=None):
    returnlist=[] #Declare empty list for return
    #gscript.run_command('g.region', raster=categorical_raster, quiet=True) #Set the region
    null='null()' if setnull else '0' #Set the value for r.mapcalc
    minclass=1 if setnull else 2 #Set the value to check if the binary raster is empty
    if category_list == None: #If no category_list provided
        category_list=[cl for cl in gscript.parse_command('r.category',map=categorical_raster,quiet=True)]
    for i,x in enumerate(category_list):  #Make sure the format is UTF8 and not Unicode
        category_list[i]=x.encode('UTF8')
    category_list.sort(key=float) #Sort the raster categories in ascending.
    #Create a binary raster for the current class
    for cl in category_list:
        binary_class=prefix+"_"+cl
        gscript.run_command('r.mapcalc', expression=binary_class+'=if('+categorical_raster+'=='+str(cl)+',1,'+null+')',overwrite=True, quiet=True)
        if len(gscript.parse_command('r.category',map=binary_class,quiet=True))>=minclass:  #Check if created binary is not empty
            returnlist.append(binary_class)
        else:
            gscript.run_command('g.remove', quiet=True, flags="f", type='raster', name=binary_class)
    if returnlist:
        return returnlist