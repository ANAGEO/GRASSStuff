##### Function that compute different landscape metrics (spatial metrics) at landscape level. 
### The metric computed are "dominance","pielou","renyi","richness","shannon","simpson".
### It is important to set the computation region before runing this script so that it match the extent of the 'raster' layer.
# 'configfile' wait for the path (string) to the configuration file corresponding to the 'raster' layer.
# 'raster' wait for the name (string) of the landcover map on which landscape metrics will be computed.
# 'returnlistresult' wait for a boolean value (True/False) according to the fact that a list containing the path to the result files is desired.
# 'ncores' wait for a integer corresponding to the number of desired cores to be used for parallelization.

# Import libraries for multiprocessing 
import multiprocessing
from multiprocessing import Pool
from functools import partial   

def compute_landscapelevel_metrics(configfile, raster, spatial_metric):
    if spatial_metric=='dominance':
        filename=raster.split("@")[0]+"_dominance"
        gscript.run_command('r.li.dominance', overwrite=True,
                            input=raster,config=configfile,output=filename)
        outputfile=os.path.join(os.path.split(configfile)[0],"output",filename)
        return outputfile
    if spatial_metric=='pielou':
        filename=raster.split("@")[0]+"_pielou"
        gscript.run_command('r.li.pielou', overwrite=True,
                            input=raster,config=configfile,output=filename)
        outputfile=os.path.join(os.path.split(configfile)[0],"output",filename)
        return outputfile
    if spatial_metric=='renyi': # The alpha parameter was set to 2 as in https://en.wikipedia.org/wiki/R%C3%A9nyi_entropy
        filename=raster.split("@")[0]+"_renyi"
        gscript.run_command('r.li.renyi', overwrite=True,
                            input=raster,config=configfile,alpha='2', output=filename)
        outputfile=os.path.join(os.path.split(configfile)[0],"output",filename)
        return outputfile
    if spatial_metric=='richness':
        filename=raster.split("@")[0]+"_richness"
        gscript.run_command('r.li.richness', overwrite=True,
                            input=raster,config=configfile,output=filename)
        outputfile=os.path.join(os.path.split(configfile)[0],"output",filename)
        return outputfile
    if spatial_metric=='shannon':
        filename=raster.split("@")[0]+"_shannon"
        gscript.run_command('r.li.shannon', overwrite=True,
                            input=raster,config=configfile,output=filename)
        outputfile=os.path.join(os.path.split(configfile)[0],"output",filename)
        return outputfile
    if spatial_metric=='simpson':
        filename=raster.split("@")[0]+"_simpson"
        gscript.run_command('r.li.simpson', overwrite=True,
                            input=raster,config=configfile,output=filename)
        outputfile=os.path.join(os.path.split(configfile)[0],"output",filename)
        return outputfile
    
def get_landscapelevel_metrics(configfile, raster, returnlistresult=True, ncores=2):
    # Check if raster exists to avoid error in mutliprocessing 
    try:
        mpset=raster.split("@")[1]
    except:
        mpset=""
    if raster not in gscript.list_strings(type='raster',mapset=mpset):
        sys.exit('Raster <%s> not found' %raster)
    # Check if configfile exists to avoid error in mutliprocessing 
    if not os.path.exists(configfile):
        sys.exit('Configuration file <%s> not found' %configfile)
    # Check for number of cores doesnt exceed available
    nbcpu=multiprocessing.cpu_count()
    if ncores>=nbcpu:
        ncores=nbcpu-1
    # List of metrics to be computed
    spatial_metric_list=["dominance","pielou","renyi","richness","shannon","simpson"]
    #Declare empty list for return
    returnlist=[] 
    # Create a new pool
    p=Pool(ncores)
    # Set the two fixed argument of the 'compute_landscapelevel_metrics' function
    func=partial(compute_landscapelevel_metrics,configfile, raster)
    # Launch the processes for as many items in the 'functions_name' list and get the ordered results using map function
    returnlist=p.map(func,spatial_metric_list)
    p.close()
    p.join()
    # Return list of paths to result files
    if returnlistresult:
        return returnlist