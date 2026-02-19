# 🇵🇭 Multivariate Satellite-Based Pollution Analysis of the Philippines (2019–2024)

## Overview

This project performs a **multivariate spatiotemporal analysis** of environmental pollution patterns in the Philippines using satellite-derived datasets (2019–2024).

The study integrates multiple environmental indicators to examine:

- Spatial pollution intensity patterns  
- Temporal trends (including COVID-era shifts)  
- Principal pollution components  
- Urbanization–pollution relationships  
- Regional clustering of pollution signatures  

---

## Datasets Used

| Variable | Dataset | Resolution | Source |
|----------|----------|------------|--------|
| **NO₂** | TROPOMI Level 3 (QA75) | 0.1° | NASA GES DISC |
| **AOD** | MODIS Aqua Level 3 | 0.1° | NASA GES DISC |
| **LST** | ERA5-Land Skin Temperature | 0.1° | Copernicus CDS |
| **Nighttime Lights** | VIIRS Black Marble Monthly | ~0.1° aggregated | Google Earth Engine |

All datasets are harmonized to a common **0.1° × 0.1° grid**.

---

## Study Region

Philippines bounding box:

- Latitude: **4°N – 21°N**
- Longitude: **116°E – 127°E**

Time range:

- **January 2019 – December 2024**

---

## Methodology

### 1. Data Processing
- Earthdata streaming & subsetting
- ERA5 retrieval via CDS API
- VIIRS aggregation via Google Earth Engine
- Spatial harmonization to common grid
- Unit conversions (Kelvin → °C)
- Quality filtering
- Missing value handling

### 2. Multivariate Analysis
- Standardization
- Correlation matrix
- Principal Component Analysis (PCA)
- KMeans clustering
- Temporal trend analysis

---

## Output

- Harmonized multivariate dataset  
- Spatial pollution intensity maps  
- PCA component interpretation  
- Cluster classification maps  
- Time-series trends (2019–2024)

---

## Setup

### 1️. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️. Authenticate

NASA Earthdata login required

Copernicus CDS API configured

Google Earth Engine authenticated

### 3. Run
python philippines_pollution_pipeline.py

## Notes

Satellite-derived measurements represent atmospheric column or surface proxies.

Nighttime lights are used as an urbanization proxy.

All analysis conducted at monthly temporal resolution.
