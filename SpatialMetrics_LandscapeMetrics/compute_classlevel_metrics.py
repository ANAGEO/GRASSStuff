##### Function that compute different landscape metrics (spatial metrics) at class level. 
### The metric computed are "patch number (patchnum)","patch density (patchdensity)","mean patch size(mps)",
### "coefficient of variation of patch area (padcv)","range of patch area size (padrange)",
### "standard deviation of patch area (padsd)", "shape index (shape)", "edge density (edgedensity)".
### It is important to set the computation region before runing this script so that it match the extent of the 'raster' layer.
# 'configfile' wait for the path (string) to the configuration file corresponding to the 'raster' layer.
# 'raster' wait for the name (string) of the landcover map on which landscape metrics will be computed.
# 'returnlistresult' wait for a boolean value (True/False) according to the fact that a list containing the path to the result files is desired.
# 'ncores' wait for a integer corresponding to the number of desired cores to be used for parallelization.

# Import libraries for multiprocessing 
import multiprocessing
from multiprocessing import Pool
from functools import partial   

def compute_classlevel_metrics(configfile, raster, spatial_metric):
    filename=raster.split("@")[0]+"_%s" %spatial_metric
    gscript.run_command('r.li.%s' %spatial_metric, overwrite=True,
                        input=raster,config=configfile,output=filename)
    outputfile=os.path.join(os.path.split(configfile)[0],"output",filename)
    return outputfile
    
def get_classlevel_metrics(configfile, raster, returnlistresult=True, ncores=2):
    # Check if raster exists to avoid error in mutliprocessing 
    try:
        mpset=raster.split("@")[1]
    except:
        mpset=""
    if raster not in [x.split("@")[0] for x in gscript.list_strings(type='raster',mapset=mpset)]:
        sys.exit('Raster <%s> not found' %raster)
    # Check if configfile exists to avoid error in mutliprocessing 
    if not os.path.exists(configfile):
        sys.exit('Configuration file <%s> not found' %configfile)
    # List of metrics to be computed
    spatial_metric_list=["patchnum","patchdensity","mps","padcv","padrange","padsd","shape","edgedensity"]
    # Check for number of cores doesnt exceed available
    nbcpu=multiprocessing.cpu_count()
    if ncores>=nbcpu:
        ncores=nbcpu-1
        if ncores>len(spatial_metric_list):
            ncores=len(spatial_metric_list)  #Adapt number of cores to number of metrics to compute
    # Declare empty list for return
    returnlist=[] 
    # Create a new pool
    p=Pool(ncores)
    # Set the two fixed argument of the 'compute_classlevel_metrics' function
    func=partial(compute_classlevel_metrics,configfile, raster)
    # Launch the processes for as many items in the 'functions_name' list and get the ordered results using map function
    returnlist=p.map(func,spatial_metric_list)
    p.close()
    p.join()
    # Return list of paths to result files
    if returnlistresult:
        return returnlist