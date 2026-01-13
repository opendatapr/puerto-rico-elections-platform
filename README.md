# Puerto Rico Elections Platform

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![R](https://img.shields.io/badge/R-4.0+-blue.svg)](https://www.r-project.org/)
[![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)

Open data platform providing access to Puerto Rico electoral data from the [Comision Estatal de Elecciones (CEE)](https://ww2.ceepur.org/).

## Objectives

1. **Data Collection**: Systematically download and archive all electoral events data from CEE (2000-present)
2. **Data Packages**: Provide easy access via R, Python, and JavaScript packages
3. **Census Integration**: Cross-reference electoral data with US Census spatial data (income, education, household composition, etc.)

## Current Data

### Electoral Data
- **Source**: [CEE Puerto Rico - Eventos Electorales](https://ww2.ceepur.org/Home/EventosElectorales)
- **Coverage**: 22 electoral events (2000-2025) with vote data extracted
- **Records**: 164,606 vote results across all geographic levels
- **Event Types**:
  - General Elections (Elecciones Generales)
  - Primary Elections (Primarias)
  - Plebiscites (Plebiscitos)
  - Special Elections (Elecciones Especiales)
- **Geographic Levels**: Island, senatorial district, representative district, municipality, precinct

### Census Data (ACS 2012-2023)
- **Source**: US Census Bureau (American Community Survey 5-Year Estimates)
- **Years Available**: 2012, 2016, 2020, 2022, 2023 (matching election cycles)
- **Geographic Levels**:
  - 78 municipalities (all years)
  - 981 census tracts (2022)
  - 2,548 block groups (2022)
- **Variables**: Total population, median household income, poverty rate, unemployment rate, educational attainment

### Geographic Crosswalks
- **2016 Source**: [MGGG PR-shapefiles](https://github.com/mggg-states/PR-shapefiles) - 110 districts
- **2022 Source**: CEE PDF maps (extracted via `pdf_extractor.py`) - 114 precincts across 40 districts
- **Unified Crosswalk**: `precinct_crosswalk_unified.parquet` combines both years for comparative analysis
- **Data**: District boundaries, municipality mapping, centroids (WGS84)

## Project Structure

```
puerto-rico-elections-platform/
├── data/
│   ├── raw/              # Original scraped data
│   ├── processed/        # Cleaned election data (Parquet/JSON)
│   ├── census/           # ACS data by year (Parquet)
│   ├── crosswalks/       # Geographic crosswalk tables
│   └── shapes/           # MGGG precinct shapefiles
├── scraper/              # Web scraping pipeline
│   └── src/
├── packages/
│   ├── r/                # R package (prelecciones)
│   ├── python/           # Python package (prelecciones)
│   └── js/               # JavaScript/TypeScript package
├── analysis/
│   ├── census_fetcher.py     # Multi-year census data fetcher
│   ├── precinct_crosswalk.py # Geographic crosswalk builder (2016 + 2022)
│   ├── pdf_downloader.py     # Download CEE district map PDFs
│   ├── pdf_extractor.py      # Extract vector paths from PDFs
│   ├── pdf_georeferencer.py  # Georeference to WGS84
│   ├── geo_matching.py       # Municipality-census GEOID mapping
│   └── examples/             # Example analysis scripts
└── docs/                 # Documentation and data dictionaries
```

## Packages

| Package | Language | Status | Installation |
|---------|----------|--------|--------------|
| `prelecciones` | R | ✅ Ready | `remotes::install_github("opendatapr/puerto-rico-elections-platform", subdir="packages/r")` |
| `prelecciones` | Python | ✅ Ready | `pip install git+https://github.com/opendatapr/puerto-rico-elections-platform#subdirectory=packages/python` |
| `prelecciones` | JavaScript | ✅ Ready | `npm install github:opendatapr/puerto-rico-elections-platform#packages/js` |

### Quick Start

**Python:**
```python
import prelecciones as pre

# List available events
events = pre.list_events()

# Get election results
results = pre.get_results("elecciones-generales-2020", level="municipality")
```

**R:**
```r
library(prelecciones)

# List available events
events <- list_events()

# Get election results
results <- get_results("elecciones-generales-2020", level = "municipality")
```

**JavaScript:**
```typescript
import { listEvents, getResults, setDataPath } from 'prelecciones';

setDataPath('./data/processed');
const events = listEvents();
const results = getResults('elecciones-generales-2020', { level: 'municipality' });
```

## Roadmap

### Phase 1: Data Infrastructure ✅
- [x] Build web scraper for CEE electoral results (XML parser for CEE's three-tier architecture)
- [x] Design standardized data schema
- [x] Extract electoral data (22 events, 164K+ results)
- [x] Store as efficient Parquet format

### Phase 2: Core Packages ✅
- [x] R package with tidyverse-friendly API
- [x] Python package with pandas integration
- [x] JavaScript package for web applications

### Phase 3: Census Integration ✅
- [x] Download ACS data for multiple years (2012-2023)
- [x] Geographic matching (municipalities, tracts, block groups)
- [x] Cross-reference analysis tools
- [x] Precinct-to-municipality crosswalk (via MGGG shapefiles)

### Phase 4: Documentation & Outreach ✅
- [x] Data dictionary and methodology docs
- [x] Example analyses (election + census correlation)
- [x] API documentation for packages

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the GPL-3.0 License - see [LICENSE](LICENSE) for details.

## Documentation

- [Data Dictionary](docs/DATA_DICTIONARY.md) - Complete field documentation in English and Spanish
- [Methodology](docs/METHODOLOGY.md) - Data collection, cleaning, and validation processes
- [Installation Guide](docs/INSTALLATION.md) - Setup instructions for all packages
- [PDF Extraction](docs/PDF_EXTRACTION.md) - How precinct boundaries are extracted from CEE PDFs
- [Data Provenance](docs/DATA_PROVENANCE.md) - Sources, licenses, and freshness for all data

## Example Analyses

The `analysis/examples/` directory contains Python scripts demonstrating common analyses:

- **[election_census_analysis.py](analysis/examples/election_census_analysis.py)** - Basic election + census correlation
- **[precinct_demographic_analysis.py](analysis/examples/precinct_demographic_analysis.py)** - Precinct-level voting patterns vs demographics (income, poverty, education)
- **[election_trends_analysis.py](analysis/examples/election_trends_analysis.py)** - Multi-year comparison of party vote shares (2016 vs 2020)
- **[geographic_voting_patterns.py](analysis/examples/geographic_voting_patterns.py)** - Choropleth maps of voting patterns using precinct boundaries

### Combining Election + Census Data

```python
import pandas as pd

# Load data
elections = pd.read_parquet('data/processed/results.parquet')
census_2020 = pd.read_parquet('data/census/pr_municipalities_acs2020.parquet')

# Filter to municipality level
muni_results = elections[elections['data_level'] == 'municipality']

# Join on municipality name
merged = muni_results.merge(
    census_2020,
    left_on='district',  # municipality name in election data
    right_on='municipality',
    how='left'
)

# Analyze: votes vs income correlation
print(merged[['votes', 'median_household_income']].corr())
```

### Fetching Additional Census Years

```bash
# Fetch census data for specific years
python analysis/census_fetcher.py --years 2012,2016,2020

# Fetch all election-matching years
python analysis/census_fetcher.py --election-years --granularity municipality
```

## Related Projects

- [opendatapr](https://github.com/opendatapr) - Open data initiatives for Puerto Rico

## Acknowledgments

- Comision Estatal de Elecciones de Puerto Rico for making electoral data publicly available
- US Census Bureau for demographic data
