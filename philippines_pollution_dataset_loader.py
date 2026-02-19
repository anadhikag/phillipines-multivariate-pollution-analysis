# -*- coding: utf-8 -*-
"""
Philippines Pollution Dataset Loading Script
Originally exported from Google Colab.

This script:
- Authenticates with Earthdata and Google Earth Engine
- Streams and subsets satellite datasets over the Philippines
- Loads NO2, AOD, LST, ERA5 Skin Temperature, and Nighttime Lights
- Interpolates to common grid
- Exports final merged dataset
"""

# ============================================================
# Environment Setup
# ============================================================

!pip install -q earthaccess xarray netCDF4 h5netcdf dask rioxarray \
               scikit-learn cartopy matplotlib seaborn pyhdf \
               cdsapi earthengine-api geemap

import os
import shutil
import zipfile
import re

import earthaccess
import xarray as xr
import numpy as np
import pandas as pd
import dask
import rioxarray as rxr
import cdsapi
import ee

# Optimize Dask slicing
dask.config.set({"array.slicing.split_large_chunks": True})

# ============================================================
# Authentication
# ============================================================

earthaccess.login()

ee.Authenticate()
ee.Initialize(project="learned-fusion-487816-n2")

# ============================================================
# Study Region Definition (Philippines)
# ============================================================

LAT_MIN, LAT_MAX = 4, 21
LON_MIN, LON_MAX = 116, 127

TIME_START = "2019-01-01"
TIME_END   = "2024-12-31"

# ============================================================
# Utility Functions
# ============================================================

def normalize_longitude(ds, lon_name):
    """Convert 0–360 longitude to -180–180 if necessary."""
    lon = ds[lon_name]
    if lon.max() > 180:
        ds = ds.assign_coords({lon_name: (((lon + 180) % 360) - 180)})
        ds = ds.sortby(lon_name)
    return ds


def detect_spatial_coords(ds):
    """Detect latitude and longitude coordinate names."""
    lat_candidates = ["lat", "latitude", "Latitude", "LATITUDE"]
    lon_candidates = ["lon", "longitude", "Longitude", "LONGITUDE"]

    lat_name = next((c for c in lat_candidates if c in ds.coords), None)
    lon_name = next((c for c in lon_candidates if c in ds.coords), None)

    if lat_name is None or lon_name is None:
        raise ValueError("Latitude/Longitude coordinates not found.")

    return lat_name, lon_name


def spatial_subset(ds, lat_min, lat_max, lon_min, lon_max):
    """Spatially subset dataset safely."""
    lat_name, lon_name = detect_spatial_coords(ds)
    ds = normalize_longitude(ds, lon_name)

    if ds[lat_name][0] > ds[lat_name][-1]:
        ds = ds.sortby(lat_name)

    return ds.sel({
        lat_name: slice(lat_min, lat_max),
        lon_name: slice(lon_min, lon_max)
    })


def temporal_subset(ds, start, end):
    """Temporal subset."""
    if "time" not in ds.coords:
        raise ValueError("Time coordinate not found.")
    return ds.sel(time=slice(start, end))


def extract_time_from_dataset(ds):
    """Extract time from dataset metadata."""
    if "time" in ds.coords:
        return pd.to_datetime(ds["time"].values)

    if "time_coverage_start" in ds.attrs:
        return pd.to_datetime(ds.attrs["time_coverage_start"])

    if "RangeBeginningDate" in ds.attrs:
        return pd.to_datetime(ds.attrs["RangeBeginningDate"])

    if "GranuleID" in ds.attrs:
        match = re.search(r'_(\d{6})_', ds.attrs["GranuleID"])
        if match:
            return pd.to_datetime(match.group(1), format="%m%Y")

    raise ValueError("Could not determine time from dataset.")


def stream_dataset(short_name, start, end, chunks={}):
    """Search, download, and concatenate dataset over time."""
    results = earthaccess.search_data(
        short_name=short_name,
        temporal=(start, end)
    )

    local_files = earthaccess.download(results)

    datasets = []
    for f in sorted(local_files):
        ds = xr.open_dataset(f, chunks=chunks)
        time_value = extract_time_from_dataset(ds)
        ds = ds.expand_dims({"time": [time_value]})
        datasets.append(ds)

    ds_combined = xr.concat(datasets, dim="time")
    return ds_combined.sortby("time")


def load_subset_dataset(short_name, variable_name):
    """Full loading pipeline."""
    ds = stream_dataset(short_name, TIME_START, TIME_END)
    ds = spatial_subset(ds, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX)
    ds = temporal_subset(ds, TIME_START, TIME_END)

    if variable_name not in ds.variables:
        raise ValueError(f"{variable_name} not found.")

    return ds[variable_name]


# ============================================================
# Dataset Loaders
# ============================================================

def load_no2():
    """Load TROPOMI NO2."""
    no2 = load_subset_dataset(
        "HAQ_TROPOMI_NO2_GLOBAL_M_L3",
        "Tropospheric_NO2"
    )

    fill_value = no2.attrs.get("_FillValue")
    if fill_value is not None:
        no2 = no2.where(no2 != fill_value)

    return no2


def load_aod():
    """Load MODIS Aqua AOD."""
    results = earthaccess.search_data(
        short_name="AER_DBDT_M10KM_L3_MODIS_AQUA",
        temporal=(TIME_START, TIME_END)
    )

    local_files = earthaccess.download(results)

    datasets = []
    for f in sorted(local_files):
        ds = xr.open_dataset(f)
        ds = ds.sel(
            Latitude=slice(LAT_MIN, LAT_MAX),
            Longitude=slice(LON_MIN, LON_MAX)
        )
        ds = ds[["COMBINE_AOD_550_AVG"]]
        datasets.append(ds)

    ds_combined = xr.concat(datasets, dim="Time").sortby("Time")
    aod = ds_combined["COMBINE_AOD_550_AVG"]

    return aod.rename({"Time": "time"}).transpose(
        "time", "Latitude", "Longitude"
    )


def load_lst():
    """Load MODIS Land Surface Temperature."""
    ds = stream_dataset("MOD11C3", TIME_START, TIME_END)
    ds = spatial_subset(ds, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX)

    lst = ds["LST_Day_CMG"] * 0.02 - 273.15
    qc = ds["QC_Day"]

    lst = lst.where(qc == 0)

    fill_value = lst.attrs.get("_FillValue")
    if fill_value is not None:
        lst = lst.where(lst != fill_value)

    return lst


# ============================================================
# ERA5 Land Skin Temperature
# ============================================================

cds_content = """url: https://cds.climate.copernicus.eu/api
key: YOUR_CDS_API_KEY
"""

with open(os.path.expanduser("~/.cdsapirc"), "w") as f:
    f.write(cds_content)

c = cdsapi.Client()

c.retrieve(
    "reanalysis-era5-land-monthly-means",
    {
        "format": "netcdf",
        "product_type": "monthly_averaged_reanalysis",
        "variable": "skin_temperature",
        "year": [str(y) for y in range(2019, 2025)],
        "month": [f"{m:02d}" for m in range(1, 13)],
        "time": "00:00",
        "area": [21, 116, 4, 127],
    },
    "ERA5_PH.nc"
)

era = xr.open_dataset("ERA5_PH.nc")

era = era.rename({
    "valid_time": "time",
    "latitude": "Latitude",
    "longitude": "Longitude"
})

era["skt"] = era["skt"] - 273.15
era = era.sortby("Latitude")
era = era.transpose("time", "Latitude", "Longitude")

# ============================================================
# Nighttime Lights (Google Earth Engine)
# ============================================================

philippines = ee.Geometry.Rectangle([116, 4, 127, 21])

ntl_collection = (
    ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG")
    .filterDate(TIME_START, "2025-01-01")
    .select("avg_rad")
)

def resample_to_01deg(image):
    return (
        image
        .reduceResolution(ee.Reducer.mean(), maxPixels=1024)
        .reproject(crs="EPSG:4326", scale=10000)
        .clip(philippines)
        .set("system:time_start", image.get("system:time_start"))
    )

ntl_stack = ntl_collection.map(resample_to_01deg).toBands()

task = ee.batch.Export.image.toDrive(
    image=ntl_stack,
    description="NTL_PH_2019_2024",
    folder="EarthEngineExports",
    fileNamePrefix="NTL_PH_2019_2024",
    region=philippines,
    scale=10000,
    crs="EPSG:4326",
    maxPixels=1e13
)

task.start()

# ============================================================
# Load All Datasets
# ============================================================

no2 = load_no2()
aod = load_aod()
lst = load_lst()

# Interpolate to ERA5 grid
target_lat = era["Latitude"]
target_lon = era["Longitude"]

no2_interp = no2.interp(Latitude=target_lat, Longitude=target_lon)
aod_interp = aod.interp(Latitude=target_lat, Longitude=target_lon)

# Final merged dataset
final_ds = xr.Dataset({
    "NO2": no2_interp,
    "AOD": aod_interp,
    "LST": era["skt"]
}).compute()

final_ds.to_netcdf("MASTER_PH_Pollution_2019_2024.nc")
