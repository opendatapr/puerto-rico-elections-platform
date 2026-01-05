# Installation Guide

This guide covers how to install and set up the `prelecciones` data packages for Python, R, and JavaScript.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Python Package](#python-package)
- [R Package](#r-package)
- [JavaScript Package](#javascript-package)
- [Development Setup](#development-setup)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### General Requirements

- Internet connection for downloading data
- Git (for development setup)

### Language-Specific Requirements

| Language | Minimum Version | Recommended |
|----------|----------------|-------------|
| Python | 3.9+ | 3.11+ |
| R | 4.0+ | 4.3+ |
| Node.js | 18+ | 20 LTS |

---

## Python Package

### Installation via pip

The easiest way to install the Python package is via pip:

```bash
# Basic installation
pip install prelecciones

# With geographic support (recommended)
pip install prelecciones[geo]

# Full installation with all optional dependencies
pip install prelecciones[all]
```

### Installation from GitHub

For the latest development version:

```bash
pip install git+https://github.com/opendatapr/puerto-rico-elections-platform.git#subdirectory=packages/python
```

### Dependencies

The Python package has the following dependencies:

**Required:**
- `pandas >= 2.0`
- `requests >= 2.28`

**Optional (geo extras):**
- `geopandas >= 0.13`
- `shapely >= 2.0`

**Optional (all extras):**
- `matplotlib >= 3.7`
- `seaborn >= 0.12`
- `jupyter >= 1.0`

### Verifying Installation

```python
import prelecciones as pr

# Check version
print(pr.__version__)

# List available events
events = pr.list_events()
print(events)
```

### Quick Start Example

```python
import prelecciones as pr

# Get all general election events
events = pr.list_events(event_type="general")

# Get results for the 2024 general election
results_2024 = pr.get_results("elecciones-generales-2024")

# Get results with geographic boundaries
results_geo = pr.get_results(
    "elecciones-generales-2024",
    include_geometry=True
)

# Filter by contest type
governor_results = pr.get_results(
    "elecciones-generales-2024",
    contest="governor"
)
```

---

## R Package

### Installation via remotes

The R package can be installed directly from GitHub:

```r
# Install remotes if needed
install.packages("remotes")

# Install prelecciones
remotes::install_github(
    "opendatapr/puerto-rico-elections-platform",
    subdir = "packages/r"
)
```

### Installation via devtools

Alternatively, using devtools:

```r
# Install devtools if needed
install.packages("devtools")

# Install prelecciones
devtools::install_github(
    "opendatapr/puerto-rico-elections-platform",
    subdir = "packages/r"
)
```

### Dependencies

The R package has the following dependencies:

**Required:**
- `httr` (>= 1.4)
- `jsonlite` (>= 1.8)
- `tibble` (>= 3.0)
- `dplyr` (>= 1.1)

**Suggested (for geographic data):**
- `sf` (>= 1.0)

**Suggested (for visualization):**
- `ggplot2` (>= 3.4)

### Verifying Installation

```r
library(prelecciones)

# Check version
packageVersion("prelecciones")

# List available events
events <- list_events()
print(events)
```

### Quick Start Example

```r
library(prelecciones)
library(dplyr)

# Get all general election events
events <- list_events(event_type = "general")

# Get results for the 2024 general election
results_2024 <- get_results("elecciones-generales-2024")

# Get results with geographic boundaries (returns sf object)
results_geo <- get_results(
    "elecciones-generales-2024",
    include_geometry = TRUE
)

# Filter and analyze
results_2024 |>
    filter(contest_type == "governor") |>
    group_by(party_code) |>
    summarise(total_votes = sum(votes))
```

---

## JavaScript Package

### Installation via npm

```bash
# Using npm
npm install prelecciones

# Using yarn
yarn add prelecciones

# Using pnpm
pnpm add prelecciones
```

### Installation from GitHub

For the latest development version:

```bash
npm install github:opendatapr/puerto-rico-elections-platform#main:packages/js
```

### Browser Usage via CDN

For quick browser usage without a build step:

```html
<script src="https://unpkg.com/prelecciones"></script>
<script>
    const { listEvents, getResults } = prelecciones;
    // Use the library...
</script>
```

### Dependencies

The JavaScript package has minimal dependencies:

**Runtime:**
- None (zero dependencies for the core package)

**Development:**
- TypeScript
- Jest (testing)
- ESLint + Prettier (code quality)

### Verifying Installation

```javascript
const { listEvents, getResults } = require('prelecciones');
// or using ES modules:
// import { listEvents, getResults } from 'prelecciones';

// List available events
const events = await listEvents();
console.log(events);
```

### Quick Start Example

```javascript
import { listEvents, getResults } from 'prelecciones';

// Get all general election events
const events = await listEvents({ eventType: 'general' });

// Get results for the 2024 general election
const results2024 = await getResults('elecciones-generales-2024');

// Get results with GeoJSON boundaries
const resultsGeo = await getResults('elecciones-generales-2024', {
    includeGeometry: true
});

// Filter by contest type
const governorResults = await getResults('elecciones-generales-2024', {
    contest: 'governor'
});

// Use in a web application
console.log(`Total results: ${results2024.length}`);
```

### TypeScript Support

The package includes full TypeScript definitions:

```typescript
import { listEvents, getResults, ElectoralEvent, Result } from 'prelecciones';

const events: ElectoralEvent[] = await listEvents();
const results: Result[] = await getResults('elecciones-generales-2024');
```

---

## Development Setup

For contributing to the project or running from source:

### Clone the Repository

```bash
git clone https://github.com/opendatapr/puerto-rico-elections-platform.git
cd puerto-rico-elections-platform
```

### Python Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
cd packages/python
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
```

### R Development

```r
# Install development dependencies
install.packages(c("devtools", "testthat", "roxygen2"))

# Load package in development mode
devtools::load_all("packages/r")

# Run tests
devtools::test()

# Check package
devtools::check()
```

### JavaScript Development

```bash
cd packages/js

# Install dependencies
npm install

# Build
npm run build

# Run tests
npm test

# Lint
npm run lint
```

---

## Troubleshooting

### Common Issues

#### Python: ModuleNotFoundError

**Problem:** `ModuleNotFoundError: No module named 'prelecciones'`

**Solution:**
1. Verify installation: `pip list | grep prelecciones`
2. Check you're in the correct virtual environment
3. Try reinstalling: `pip install --force-reinstall prelecciones`

#### R: Package Not Found

**Problem:** `Error in library(prelecciones): there is no package called 'prelecciones'`

**Solution:**
1. Check installation succeeded without errors
2. Try installing dependencies first:
   ```r
   install.packages(c("httr", "jsonlite", "tibble", "dplyr"))
   remotes::install_github("opendatapr/puerto-rico-elections-platform", subdir = "packages/r")
   ```

#### JavaScript: Network Errors

**Problem:** Network errors when fetching data

**Solution:**
1. Check internet connection
2. Verify firewall isn't blocking requests
3. Try with a proxy if needed:
   ```javascript
   import { configure } from 'prelecciones';
   configure({ proxy: 'http://your-proxy:8080' });
   ```

#### Geographic Data Issues

**Problem:** Geographic operations failing

**Python Solution:**
```bash
# Install with geo extras
pip install prelecciones[geo]

# Or install geopandas separately
pip install geopandas
```

**R Solution:**
```r
# Install sf package
install.packages("sf")

# On Ubuntu/Debian, you may need system libraries:
# sudo apt-get install libgdal-dev libgeos-dev libproj-dev
```

### Getting Help

If you encounter issues not covered here:

1. **Search existing issues:** https://github.com/opendatapr/puerto-rico-elections-platform/issues
2. **Open a new issue** with:
   - Your operating system and version
   - Language and package version
   - Complete error message
   - Minimal code to reproduce the issue

---

## Version Compatibility

| Package Version | Python | R | Node.js | Data Schema |
|-----------------|--------|---|---------|-------------|
| 1.0.x | 3.9+ | 4.0+ | 18+ | v1 |
| 0.9.x (beta) | 3.8+ | 4.0+ | 16+ | v1 |

---

## Next Steps

After installation, check out:

- [Data Dictionary](DATA_DICTIONARY.md) - Understand the data structure
- [Methodology](METHODOLOGY.md) - Learn about data collection
- [Example Analyses](../analysis/examples/) - See the packages in action
