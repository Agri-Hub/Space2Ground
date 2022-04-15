# Space2Ground


### Towards Space-to-Ground Data Availability for the Monitoring of the Common Agricultural Policy



## Available Data

This dataset constists of 

* Sentinel-1 monthly mean time-series 
* Sentinel-2 time-series  
* Street level image patches from Mapillary  

## Getting started


### Python Dependencies

Anaconda environment
```
conda create -n space2ground python=3.7.3 pip
conda activate space2ground
pip install -r requirements.txt (to be added)
```


### Download Dataset

download Sentinel data to `data/`
```bash
bash download.sh sentinel
```
download Streetl level patches to `data/streetLevel_patches`
```bash
bash download.sh imagepatches
```
download Streetl level raw images to `data/Mapillary`
```bash
bash download.sh mapillary
```
or everything with `bash download.sh all`


## External Code

* Download street level images from Mapillary and annotate them with labels from LPIS

https://github.com/Agri-Hub/Callisto/tree/main/Mapillary

* Download and pre-process Sentinel-1 and Senintel-2 data:

https://github.com/Agri-Hub/ADC
