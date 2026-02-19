# 🇵🇭 Multivariate Statistical Analysis of Air Pollution Drivers in the Philippines (2019–2024)

## Overview

This project performs a **multivariate statistical analysis** of satellite-derived environmental indicators across the Philippines from **January 2019 to December 2024**.

The objective is to examine how pollution indicators co-vary over time and to evaluate whether anthropogenic activity proxies statistically explain national NO₂ variability.

The study integrates multiple remote sensing datasets and applies:

- Correlation analysis  
- Principal Component Analysis (PCA)  
- K-means clustering  
- Linear trend testing  
- Multiple regression modeling  
- Model diagnostics and robustness checks  

This project was developed as part of a Statistical Foundations for Data Science course and emphasizes **interpretability, validation, and methodological rigor**.

---

## Study Region

**Philippines Bounding Box**

- Latitude: 4°N – 21°N  
- Longitude: 116°E – 127°E  

**Time Range**

- January 2019 – December 2024  
- Monthly resolution (72–73 time steps)

---

## Datasets Used

| Variable | Dataset | Resolution | Source |
|----------|----------|------------|--------|
| **Tropospheric NO₂** | TROPOMI Level 3 (QA75) | 0.1° | NASA GES DISC |
| **Aerosol Optical Depth (AOD)** | MODIS Aqua Level 3 | 0.1° | NASA GES DISC |
| **Skin Temperature (SKT)** | ERA5-Land Monthly Mean | 0.1° | Copernicus CDS |
| **Nighttime Lights (NTL)** | VIIRS Black Marble Monthly | ~0.1° (aggregated) | Google Earth Engine |

All datasets were harmonized to a common **0.1° × 0.1° spatial grid**.

---

## Data Processing

### 1. Harmonization

- Spatial subsetting to Philippines
- Regridding to common resolution
- Unit conversions (Kelvin → °C)
- Quality filtering
- Handling of fill values
- Temporal alignment

Due to differences in satellite coverage and masking, spatial overlap was sparse at pixel level. Therefore, analysis was conducted primarily at the **national aggregate monthly scale**.

---

### 2. Preprocessing

- Outlier filtering using Z-score thresholds  
- Temporal interpolation  
- Log transformation of NO₂ (after clipping negative values)  
- Z-score standardization for multivariate comparability  

---

## Statistical Methods

### 1. Correlation Analysis

Pearson correlation was computed using national monthly means.

**Finding:**
- Moderate positive association between NO₂ and Nighttime Lights.
- Moderate association between NO₂ and AOD.
- Weak direct association between NO₂ and temperature.

---

### 2. Principal Component Analysis (PCA)

PCA was applied to standardized national monthly means.

**Result:**
- PC1 explains ~51% of total variance.
- PC1 represents a shared pollution/activity intensity component.

This indicates partially coupled environmental variability.

---

### 3. Emission Regime Classification (K-Means)

K-means clustering (k=3) identified statistically distinct monthly regimes.

**ANOVA p-value < 1e-10**

Regimes correspond to:
- High-emission months
- Low-emission months
- Transitional months

---

### 4. Trend Analysis

Linear regression testing found:

- No statistically significant long-term national NO₂ trend (p > 0.05)

Variability appears episodic rather than monotonic.

---

### 5. Multiple Linear Regression

Model:

\[
NO₂ ~ AOD + SKT + NTL
\]

**Key Results:**

- R² ≈ 0.18 (modest explanatory power)
- Nighttime Lights: statistically significant predictor
- AOD: moderate influence
- Temperature: not independently significant
- VIF < 2 (low multicollinearity)
- Durbin–Watson ≈ 1.07 (mild positive autocorrelation)

---

### 6. Model Validation & Robustness

- **Train–Test Split (2019–2023 vs 2024):**
  - Test R² ≈ -0.02  
  - Indicates weak predictive generalization  
  - Model is explanatory rather than forecasting

- **Removing 2020 (COVID shock):**
  - Slight increase in R²
  - NTL remains significant
  - Core conclusions remain stable

---

## Key Conclusions

1. Pollution indicators exhibit moderate national co-variation.
2. A dominant latent pollution/activity factor explains over 50% of variance.
3. Monthly pollution regimes are statistically distinct.
4. No significant long-term NO₂ trend detected (2019–2024).
5. Nighttime Lights (urban activity proxy) is the strongest predictor of NO₂ variability.
6. Temperature contributes minimal independent explanatory power.
7. Predictive generalization is limited — the model is primarily explanatory.
8. Pixel-level multivariate correlation was not reliable due to sparse spatial overlap.

Overall, anthropogenic activity proxies appear more strongly associated with national NO₂ variability than meteorological temperature at monthly scale.

---

## Repository Structure

.
├── Final_PH_Analysis.ipynb
├── MASTER_PH_Pollution_2019_2024.nc
├── figures/
├── requirements.txt
└── README.md


---

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```
<<<<<<< HEAD
=======
### 2. Authentication Required
>>>>>>> 9264e6a (Added Analysis)

NASA Earthdata Login

Copernicus CDS API

Google Earth Engine

### 3. Run Analysis

Open the Jupyter Notebook:

> jupyter notebook Final_PH_Analysis.ipynb

## Limitations

- High spatial sparsity after harmonization

- Pixel-level temporal overlap limited

- Modest explanatory power (R² ≈ 0.18)

- Weak out-of-sample predictive performance

This study emphasizes statistical structure and interpretation rather than forecasting accuracy.

## Academic Context

### Developed for:

**Statistical Foundations for Data Science**

### Focus areas:

- Multivariate structure

- Dimensionality reduction

- Regression modeling

- Assumption testing

- Model validation

- Robustness analysis
