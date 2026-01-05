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

## Data Sources

### Electoral Data
- **Source**: [CEE Puerto Rico - Eventos Electorales](https://ww2.ceepur.org/Home/EventosElectorales)
- **Coverage**: 2000-2025 (~40+ electoral events)
- **Event Types**:
  - General Elections (Elecciones Generales)
  - Primary Elections (Primarias)
  - Plebiscites (Plebiscitos)
  - Special Elections (Elecciones Especiales)

### Census Data
- **Source**: US Census Bureau (American Community Survey)
- **Variables**:
  - Income levels
  - Educational attainment
  - Household size and composition
  - Religious affiliation (where available)
  - Age demographics
  - Employment statistics

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
| `prelecciones` | R | 🚧 Planned | `remotes::install_github("opendatapr/puerto-rico-elections-platform", subdir="packages/r")` |
| `prelecciones` | Python | 🚧 Planned | `pip install prelecciones` |
| `prelecciones` | JavaScript | 🚧 Planned | `npm install prelecciones` |

## Roadmap

### Phase 1: Data Infrastructure
- [ ] Build web scraper for CEE electoral results
- [ ] Design standardized data schema
- [ ] Set up automated data pipeline
- [ ] Create data validation suite

### Phase 2: Core Packages
- [ ] R package with tidyverse-friendly API
- [ ] Python package with pandas integration
- [ ] JavaScript package for web applications

### Phase 3: Census Integration
- [ ] Download relevant Census/ACS data
- [ ] Geographic matching (precincts → census tracts)
- [ ] Cross-reference analysis tools

### Phase 4: Documentation & Outreach
- [ ] Data dictionary and methodology docs
- [ ] Example analyses and visualizations
- [ ] API documentation for packages

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
