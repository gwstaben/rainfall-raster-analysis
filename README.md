# rainfall-raster-analysis
## This repo contains a number of scripts and notebooks to pre-process and undertake analysis of the monthly rainfall raster layers and produce percentile and decile raster layers for a given year. 

#### The monthly rainfall raster grids are interpolated from BOM rainfall stations across Australia; produced by the QLD Government, further details can be found here:
https://www.longpaddock.qld.gov.au/silo/ 

https://www.longpaddock.qld.gov.au/silo/about/publications-references/

The gridded monthly rainfall rasters can be downloaded from: https://www.longpaddock.qld.gov.au/silo/gridded-data/ 
<p align="center">
<img src="https://github.com/gwstaben/rainfall-raster-analysis/blob/main/png/month_rainfall.png" width="485" height="400">
</p>

#### The first step is to produce the seasonal rainfall total layers for a given period (e.g. NT wetseason = October 2021 to April 2022) going back to the 1800's using the notebook: "Multi seasonal rainfall - workflow.ipynb" this notebook details the workflow which calculates the seasonal total for each year, reprojects the raster layer and clips it the NT boundary.   

#### Once the seasonal total rainfall layers are produced you can then compare the current seasons total (2021-2022 wet season) against previous seasons back in time by caluclating the percentile of score (see https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.percentileofscore.html). The precentile of score layer is then coverted to a decile ranked layer. The notebook: "run_rainfall_seasonal_workflow.ipynb" detials the workflow to undertake the analysis.     

