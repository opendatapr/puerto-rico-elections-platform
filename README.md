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

### Census Data (ACS 2022)
- **Source**: US Census Bureau (American Community Survey 5-Year Estimates)
- **Geographic Levels**:
  - 78 municipalities
  - 981 census tracts
  - 2,548 block groups
- **Variables**: Total population, median household income, educational attainment

## Project Structure

```
puerto-rico-elections-platform/
├── data/
│   ├── raw/              # Original scraped data
│   ├── processed/        # Cleaned, standardized data
│   └── census/           # Census data downloads
├── scraper/              # Web scraping pipeline
│   ├── src/
│   └── tests/
├── packages/
│   ├── r/                # R package (prelecciones)
│   ├── python/           # Python package (prelecciones)
│   └── js/               # JavaScript/TypeScript package
├── analysis/             # Cross-reference analysis tools
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
- [x] Download ACS 2022 data at 3 geographic levels
- [x] Geographic matching (municipalities, tracts, block groups)
- [ ] Cross-reference analysis tools (in progress)

### Phase 4: Documentation & Outreach
- [x] Data dictionary and methodology docs
- [ ] Example analyses and visualizations
- [x] API documentation for packages

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the GPL-3.0 License - see [LICENSE](LICENSE) for details.

## Documentation

- [Data Dictionary](docs/DATA_DICTIONARY.md) - Complete field documentation in English and Spanish
- [Methodology](docs/METHODOLOGY.md) - Data collection, cleaning, and validation processes
- [Installation Guide](docs/INSTALLATION.md) - Setup instructions for all packages

## Example Analyses

The `analysis/examples/` directory contains Python scripts demonstrating common analyses:

- **[voter_turnout_trends.py](analysis/examples/voter_turnout_trends.py)** - Analyze voter turnout from 2000-2024
- **[party_performance.py](analysis/examples/party_performance.py)** - Party results by municipality over time

## Related Projects

- [opendatapr](https://github.com/opendatapr) - Open data initiatives for Puerto Rico

## Acknowledgments

- Comision Estatal de Elecciones de Puerto Rico for making electoral data publicly available
- US Census Bureau for demographic data
