# Problem Set 4: Working With Landsat Data

## Download Landsat Data

Downloaded from Landsat for the 20170310 period.

## Code from Class

```python

from osgeo import gdal
import matplotlib.pyplot as plt
import numpy as np
import os
%matplotlib inline


def process_string (st):
    """
    Parses Landsat metadata
    """
    return float(st.split(' = ')[1].strip('\n'))

def ndvi_calc(red, nir):
    """
    Calculate NDVI
    """
    return (nir - red) / (nir + red)

def emissivity_calc (pv, ndvi):
    """
    Calculates an estimate of emissivity
    """
    ndvi_dest = ndvi.copy()
    ndvi_dest[np.where(ndvi < 0)] = 0.991
    ndvi_dest[np.where((0 <= ndvi) & (ndvi < 0.2)) ] = 0.966
    ndvi_dest[np.where((0.2 <= ndvi) & (ndvi < 0.5)) ] = (0.973 * pv[np.where((0.2 <= ndvi) & (ndvi < 0.5)) ]) + (0.966 * (1 - pv[np.where((0.2 <= ndvi) & (ndvi < 0.5)) ]) + 0.005)
    ndvi_dest[np.where(ndvi >= 0.5)] = 0.973
    return ndvi_dest

def array2tif(raster_file, new_raster_file, array):
    """
    Writes 'array' to a new tif, 'new_raster_file',
    whose properties are given by a reference tif,
    here called 'raster_file.'
    """
    # Invoke the GDAL Geotiff driver
    raster = gdal.Open(raster_file)

    driver = gdal.GetDriverByName('GTiff')
    out_raster = driver.Create(new_raster_file,
                        raster.RasterXSize,
                        raster.RasterYSize,
                        1,
                        gdal.GDT_Float32)
    out_raster.SetProjection(raster.GetProjection())
    # Set transformation - same logic as above.
    out_raster.SetGeoTransform(raster.GetGeoTransform())
    # Set up a new band.
    out_band = out_raster.GetRasterBand(1)
    # Set NoData Value
    out_band.SetNoDataValue(-1)
    # Write our Numpy array to the new band!
    out_band.WriteArray(array)

```
Functions to retrieve location, process metadata, calculate brightness temperature, calculate proportional vegetstion, and land surface temperature!

# Retrieve location

```python
import sys
sys.path.insert(0,'/Library/Frameworks/GDAL.framework/Versions/2.2/Python/3.6/site-packages')
DATA = "/Users/arianna/Desktop/github/big-data-spring2018/week-05/ws05_materials/"
location = os.path.join(DATA, 'B10.TIF')

def tif2array(location):
    raster = gdal.Open(location)
    myarray = np.array(raster.GetRasterBand(1).ReadAsArray())
    myarray = myarray.astype(np.float32)
    #myarray
    return myarray

```
# Read and process metadata stored in text file
```python
    meta_text = '/Users/arianna/Desktop/github/big-data-spring2018/week-05/ws05_materials/MTL.txt'

    def retrieve_meta(meta_text):

       with open(meta_text) as f:
           meta = f.readlines()
           # Define terms to match
       matchers = ['RADIANCE_MULT_BAND_10', 'RADIANCE_ADD_BAND_10', 'K1_CONSTANT_BAND_10', 'K2_CONSTANT_BAND_10']

       [s for s in meta if any(xs in s for xs in matchers)]

       def process_string (st):

           return float(st.split(' = ')[1].strip('\n'))
       matching = [process_string(s) for s in meta if any(xs in s for xs in matchers)]

       rad_mult_b10, rad_add_b10, k1_b10, k2_b10 = matching
       return matching

    retrieve_meta(meta_text)
```
#Calculate Top of Atmosphere Spectral Radiance
#TIRS Band (thermal imaging) Temperature
#Calculate Brightness Temperature
#Calculate Top of Atmosphere Spectral Radiance

```python
def rad_calc(tirs, var_list):
  rad = var_list[0] * tirs + var_list[1]
  #plt.imshow(rad, cmap='RdYlGn')
  return rad

def bt_calc(rad, var_list):
  bt = var_list[3] / np.log((var_list[2]/rad) + 1) - 273.15
  #plt.imshow(bt, cmap='RdYlGn')
  return bt
```

#Calculate Proportional Vegetation
```python
def ndvi_calc(red, nir):
    """ Calculate NDVI"""
    return (nir - red) / (nir + red)

def pv_calc(ndvi, ndvi_s, ndvi_v):
  pv = (ndvi - ndvi_s ) / (ndvi_v - ndvi_s ) ** 2
  return pv
```

#Calculate Estimate of Land Surface Temperature

```python
def lst_calc(location):
  red_path = tif2array(os.path.join(location, 'B4.TIF'))
  nir_path = tif2array(os.path.join(location, 'B5.TIF'))
  tirs_path = tif2array(os.path.join(location, 'B10.TIF'))
  var_list = retrieve_meta(os.path.join(location, 'MTL.TXT'))
  getrad = rad_calc(tirs_path, var_list)
  bt = bt_calc(getrad, var_list)

  ndvi_s = 0.2
  ndvi_v = 0.5
  ndvi = ndvi_calc(red_path, nir_path)
  pvcalc = pv_calc(ndvi, ndvi_s, ndvi_v)
  emis = emissivity_calc (pvcalc, ndvi)
  wave = 10.8E-06
  # PLANCK'S CONSTANT
  h = 6.626e-34
  # SPEED OF LIGHT
  c = 2.998e8
  # BOLTZMANN's CONSTANT
  s = 1.38e-23
  p = h * c / s
  lst = bt / (1 + (wave * bt / p) * np.log(emis))
  return lst
  #plt.imshow(lst, cmap='RdYlGn')

```

#clean clouds
```python
def tif2array(location):

   tirs_path = os.path.join(location, 'BQA.TIF')

   tirs_data = gdal.Open(tirs_path)
   tirs_band = tirs_data.GetRasterBand(1)
   tirs = tirs_band.ReadAsArray()
   tirs = tirs.astype(np.float32)
   return tirs
bqa=tif2array(location)

array = lst

def cloud_filter(array, bqa):
   array_dest = array.copy()
   array_dest[np.where((bqa != 2720) & (bqa != 2724) & (bqa != 2728) & (bqa != 2732)) ] = 'nan'
   return array_dest
lst_filter = cloud_filter(array, bqa)
plt.imshow(lst_filter, cmap='RdYlGn')
plt.colorbar()

```

#Export Filtered Arrays as TIFF
```python
tirs_path = os.path.join(DATA, 'B10.TIF')
out_path = os.path.join(DATA, 'salazar_lst_20170310.tif')
array2tif(tirs_path, out_path, lst_filter)


out_path = os.path.join(DATA, 'salazar_ndvi_20170310.tif')
array2tif(tirs_path, out_path, ndvi)
```
