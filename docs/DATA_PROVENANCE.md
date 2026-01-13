# Data Provenance / Procedencia de Datos

This document provides detailed source information for all datasets in the Puerto Rico Elections Platform.

Este documento proporciona informacion detallada sobre las fuentes de todos los conjuntos de datos en la Plataforma de Elecciones de Puerto Rico.

---

## Table of Contents / Tabla de Contenidos

1. [Electoral Data / Datos Electorales](#1-electoral-data--datos-electorales)
2. [Census Data / Datos Censales](#2-census-data--datos-censales)
3. [Geographic Boundaries / Limites Geograficos](#3-geographic-boundaries--limites-geograficos)
4. [Crosswalk Tables / Tablas de Referencia Cruzada](#4-crosswalk-tables--tablas-de-referencia-cruzada)

---

## 1. Electoral Data / Datos Electorales

### Source / Fuente

**Comision Estatal de Elecciones de Puerto Rico (CEE)**

| Attribute | Details |
|-----------|---------|
| **Organization** | Comision Estatal de Elecciones de Puerto Rico |
| **Website** | https://ww2.ceepur.org/ |
| **Events Page** | https://ww2.ceepur.org/Home/EventosElectorales |
| **Data Format** | HTML/XML (scraped and parsed) |
| **License** | Public government data |

### URL Patterns

| Event Type | URL Pattern |
|------------|-------------|
| Modern Events (2016+) | `https://elecciones{year}.ceepur.org/` |
| Legacy Events (2008-2012) | `http://168.62.166.179/reydi{year}/` |
| Special Elections | `https://{municipality}{year}.ceepur.org/` |

### Coverage

| Field | Value |
|-------|-------|
| **Time Period** | 2000-2025 |
| **Events Scraped** | 22 electoral events |
| **Records Extracted** | 164,606 vote results |
| **Geographic Levels** | Island, senatorial district, representative district, municipality, precinct |

### Data Freshness

| Event | Last Updated |
|-------|--------------|
| Elecciones Generales 2024 | 2024-11-15 |
| Primarias Locales 2024 | 2024-06-10 |
| Eleccion Especial Gurabo 2025 | 2025-01-XX |

### Collection Method

Data is collected via automated web scraping:
- **Requests library**: HTTP fetching
- **BeautifulSoup4**: HTML parsing
- **Custom XML parser**: For CEE's three-tier result architecture
- **Rate limiting**: 1-3 seconds between requests
- **Archived**: Raw HTML stored for reproducibility

---

## 2. Census Data / Datos Censales

### Source / Fuente

**US Census Bureau - American Community Survey (ACS)**

| Attribute | Details |
|-----------|---------|
| **Organization** | United States Census Bureau |
| **Website** | https://www.census.gov/programs-surveys/acs |
| **API** | https://api.census.gov/data/ |
| **Data Format** | JSON via Census API |
| **License** | Public domain (US Government work) |

### API Endpoints

```
Base URL: https://api.census.gov/data/{year}/acs/acs5

Municipality Level:
GET /data/{year}/acs/acs5?get={variables}&for=county:*&in=state:72

Census Tract Level:
GET /data/{year}/acs/acs5?get={variables}&for=tract:*&in=state:72

Block Group Level:
GET /data/{year}/acs/acs5?get={variables}&for=block%20group:*&in=state:72
```

### Variables Collected

| Table Code | Variable | Description |
|------------|----------|-------------|
| B01003_001E | total_population | Total population |
| B19013_001E | median_household_income | Median household income (USD) |
| B17001_002E | poverty_count | Population below poverty line |
| B23025_005E | unemployed | Unemployed population |
| B23025_002E | labor_force | Total labor force |
| B15003_017E | hs_graduates | High school graduates |
| B15003_022E | bachelors | Bachelor's degree holders |
| B15003_023E | masters | Master's degree holders |
| B15003_024E | professional | Professional degree holders |
| B15003_025E | doctorate | Doctorate holders |

### Years Available

| Year | Survey | Geographic Levels | Election Match |
|------|--------|-------------------|----------------|
| 2012 | ACS 5-Year | Municipalities | 2012 General Election |
| 2016 | ACS 5-Year | Municipalities | 2016 General Election |
| 2020 | ACS 5-Year | Municipalities | 2020 General Election |
| 2022 | ACS 5-Year | Municipalities, Tracts, Block Groups | 2024 General Election |
| 2023 | ACS 5-Year | Municipalities | 2024 General Election |

### Data Freshness

Census data is matched to electoral events by year proximity:

| Electoral Year | Census Data Used |
|----------------|------------------|
| 2024 | ACS 2022 5-Year Estimates |
| 2020 | ACS 2019 5-Year + 2020 Decennial |
| 2016 | ACS 2015 5-Year Estimates |

### Collection Tool

```bash
python analysis/census_fetcher.py --years 2012,2016,2020,2022,2023
```

---

## 3. Geographic Boundaries / Limites Geograficos

### 3.1 MGGG 2016 Precinct Shapefiles

**Metric Geometry and Gerrymandering Group (MGGG)**

| Attribute | Details |
|-----------|---------|
| **Organization** | MGGG Redistricting Lab (Tufts/MIT) |
| **Repository** | https://github.com/mggg-states/PR-shapefiles |
| **Download URL** | https://github.com/mggg-states/PR-shapefiles/raw/main/PR.zip |
| **Data Format** | ESRI Shapefile (.shp, .dbf, .shx, .prj) |
| **License** | MIT License |
| **Reference Year** | 2016 |

#### Fields in Shapefile

| Field | Description |
|-------|-------------|
| PRECINTO | Precinct identifier |
| DIST_SENADO | Senatorial district (1-8) |
| DIST_REP | Representative district (1-40) |
| MUNICIPIO | Municipality name |
| geometry | Polygon/MultiPolygon boundary |

#### Coverage

- **Total Precincts**: 110
- **Municipalities**: 78
- **Representative Districts**: 40
- **Senatorial Districts**: 8

### 3.2 CEE 2022 PDF Maps

**Comision Estatal de Elecciones**

| Attribute | Details |
|-----------|---------|
| **Organization** | CEE Puerto Rico |
| **Source Page** | https://ww2.ceepur.org/Home/MapasDistritosRepresentativos |
| **JSON Endpoint** | https://ww2.ceepur.org/Data/.Mapas%20Distrito%20Representativos.json |
| **Data Format** | PDF (vector graphics) |
| **License** | Public government data |
| **Reference Year** | 2022 |

#### Extraction Method

Precinct boundaries are extracted from PDF vector paths:
1. Download PDFs via `pdf_downloader.py`
2. Extract vector curves via `pdf_extractor.py` (using pdfplumber)
3. Georeference via `pdf_georeferencer.py` (affine transformation)

See [PDF Extraction Methodology](PDF_EXTRACTION.md) for details.

#### Coverage

- **District Maps**: 40 PDFs
- **Precincts Extracted**: 114
- **Accuracy**: ~5 km average error

### 3.3 Municipality Centroids

| Attribute | Details |
|-----------|---------|
| **File** | `data/pdf_maps/pr_municipality_centroids.json` |
| **Source** | Computed from Census TIGER/Line shapefiles |
| **CRS** | WGS84 (EPSG:4326) |
| **Format** | JSON (municipality name -> lat/lon) |

Used as control points for PDF georeferencing.

---

## 4. Crosswalk Tables / Tablas de Referencia Cruzada

### 4.1 2016 Precinct Crosswalk

| Attribute | Details |
|-----------|---------|
| **Source** | Derived from MGGG shapefiles |
| **File** | `data/crosswalks/precinct_municipality_crosswalk.json` |
| **Coverage** | 110 precincts |

### 4.2 2022 Precinct Crosswalk

| Attribute | Details |
|-----------|---------|
| **Source** | Extracted from CEE PDF maps |
| **File** | `data/crosswalks/precinct_crosswalk_2022.json` |
| **Coverage** | 114 precincts |

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| year | integer | Reference year (2022) |
| district | integer | Representative district (1-40) |
| precinct_index | integer | Precinct index within district |
| municipality | string | Municipality name |
| color | string | Fill color from PDF (hex) |
| centroid_lon | float | Centroid longitude (WGS84) |
| centroid_lat | float | Centroid latitude (WGS84) |
| area_sq_deg | float | Approximate area in square degrees |
| source | string | Data source identifier |

### 4.3 Unified Multi-Year Crosswalk

| Attribute | Details |
|-----------|---------|
| **File** | `data/crosswalks/precinct_crosswalk_unified.parquet` |
| **Format** | Apache Parquet |
| **Years** | 2016, 2022 |
| **Purpose** | Comparative analysis across redistricting cycles |

---

## License Summary / Resumen de Licencias

| Data Source | License | Commercial Use |
|-------------|---------|----------------|
| CEE Electoral Data | Public government data | Yes |
| US Census ACS | Public domain | Yes |
| MGGG Shapefiles | MIT License | Yes (with attribution) |
| CEE PDF Maps | Public government data | Yes |

---

## Data Quality Disclaimers / Avisos de Calidad

### Electoral Data
- Data is scraped from CEE websites; original sources should be cited
- Historical events (pre-2016) may have incomplete precinct-level data
- Write-in candidates are generally not included

### Census Data
- ACS estimates have margins of error (stored in metadata files)
- Small-area estimates (block groups) have higher uncertainty
- 5-year estimates are period estimates, not point-in-time

### Geographic Data
- 2016 MGGG shapefiles are high quality (digitized from official sources)
- 2022 PDF extraction has ~5km average error (approximate only)
- Precinct boundaries may have changed between redistricting cycles

---

## Citation / Cita

If using this data in research or publications, please cite:

```
Puerto Rico Elections Platform
https://github.com/opendatapr/puerto-rico-elections-platform

Data Sources:
- Comision Estatal de Elecciones de Puerto Rico (https://ww2.ceepur.org/)
- US Census Bureau American Community Survey
- MGGG Redistricting Lab PR-shapefiles (https://github.com/mggg-states/PR-shapefiles)
```

---

## Related Documentation

- [Data Dictionary](DATA_DICTIONARY.md) - Field descriptions
- [Methodology](METHODOLOGY.md) - Data processing procedures
- [PDF Extraction](PDF_EXTRACTION.md) - PDF boundary extraction details
