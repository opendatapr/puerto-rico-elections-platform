---
layout: default
title: Puerto Rico Elections Platform
---

# Puerto Rico Elections Platform

Open data platform providing access to Puerto Rico electoral data from the [Comision Estatal de Elecciones (CEE)](https://ww2.ceepur.org/).

Part of the [opendatapr](https://github.com/opendatapr) open data initiative for Puerto Rico.

---

## Data Coverage

| Metric | Value |
|--------|-------|
| **Electoral Events** | 22 events (2000-2025) |
| **Vote Results** | 164,606 records |
| **Census Years** | 2012, 2016, 2020, 2022, 2023 |
| **Municipalities** | 78 |
| **Census Tracts** | 981 |
| **Block Groups** | 2,548 |

**Event Types:** General Elections, Primary Elections, Plebiscites, Special Elections

**Geographic Levels:** Island-wide, Senatorial Districts, Representative Districts, Municipalities, Precincts

---

## Key Features

- **Electoral Data**: Complete vote results from CEE for all election types since 2000
- **Census Integration**: American Community Survey data matched to election cycles
- **Geographic Crosswalks**: Precinct-to-municipality mappings for spatial analysis
- **Multi-Language Packages**: Native support for Python, R, and JavaScript

---

## Quick Start

### Python

```bash
pip install git+https://github.com/opendatapr/puerto-rico-elections-platform#subdirectory=packages/python
```

```python
import prelecciones as pre

# List available electoral events
events = pre.list_events()

# Get 2020 general election results by municipality
results = pre.get_results("elecciones-generales-2020", level="municipality")
```

### R

```r
remotes::install_github("opendatapr/puerto-rico-elections-platform", subdir="packages/r")
```

```r
library(prelecciones)

# List available electoral events
events <- list_events()

# Get 2020 general election results by municipality
results <- get_results("elecciones-generales-2020", level = "municipality")
```

### JavaScript

```bash
npm install github:opendatapr/puerto-rico-elections-platform#packages/js
```

```typescript
import { listEvents, getResults, setDataPath } from 'prelecciones';

setDataPath('./data/processed');
const events = listEvents();
const results = getResults('elecciones-generales-2020', { level: 'municipality' });
```

---

## Data Sources

- **Electoral Data**: [CEE Puerto Rico - Eventos Electorales](https://ww2.ceepur.org/Home/EventosElectorales)
- **Census Data**: US Census Bureau (American Community Survey 5-Year Estimates)
- **Geographic Data**: [MGGG PR-shapefiles](https://github.com/mggg-states/PR-shapefiles) and CEE PDF maps

---

## Example: Combining Election and Census Data

```python
import pandas as pd

# Load election results and census data
elections = pd.read_parquet('data/processed/results.parquet')
census_2020 = pd.read_parquet('data/census/pr_municipalities_acs2020.parquet')

# Filter to municipality level
muni_results = elections[elections['data_level'] == 'municipality']

# Join on municipality name
merged = muni_results.merge(
    census_2020,
    left_on='district',
    right_on='municipality',
    how='left'
)

# Analyze correlation between votes and income
print(merged[['votes', 'median_household_income']].corr())
```

---

## Documentation

- [Installation Guide](INSTALLATION.md) - Setup instructions for all packages
- [Data Dictionary](DATA_DICTIONARY.md) - Complete field documentation (English/Spanish)
- [Methodology](METHODOLOGY.md) - Data collection, cleaning, and validation processes
- [Data Provenance](DATA_PROVENANCE.md) - Source documentation for all datasets
- [PDF Extraction](PDF_EXTRACTION.md) - CEE PDF map boundary extraction methodology

---

## Project Structure

```
puerto-rico-elections-platform/
├── data/
│   ├── raw/              # Original scraped data
│   ├── processed/        # Cleaned election data (Parquet/JSON)
│   ├── census/           # ACS data by year (Parquet)
│   └── crosswalks/       # Geographic crosswalk tables
├── packages/
│   ├── r/                # R package (prelecciones)
│   ├── python/           # Python package (prelecciones)
│   └── js/               # JavaScript/TypeScript package
├── analysis/             # Census fetcher and example analyses
└── docs/                 # Documentation
```

---

## Contributing

We welcome contributions! See our [Contributing Guide](https://github.com/opendatapr/puerto-rico-elections-platform/blob/main/CONTRIBUTING.md) for guidelines.

---

## License

This project is licensed under the [GPL-3.0 License](https://github.com/opendatapr/puerto-rico-elections-platform/blob/main/LICENSE).

---

## Links

- [GitHub Repository](https://github.com/opendatapr/puerto-rico-elections-platform)
- [opendatapr Organization](https://github.com/opendatapr)
- [CEE Puerto Rico](https://ww2.ceepur.org/)
