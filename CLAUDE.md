# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Open data platform providing access to Puerto Rico electoral data from the Comision Estatal de Elecciones (CEE). The project has four main components:

1. **Web Scraper** (`scraper/`) - Python scraper for CEE electoral data (2000-present)
2. **Data Packages** (`packages/`) - R, Python, and JavaScript packages named `prelecciones`
3. **Census Integration** (`analysis/`) - ACS data fetching and geographic crosswalks
4. **Scrollytelling Webapp** (`webapp/`) - Svelte 5 data journalism app with 12 chapters

## Development Commands

### Python Environment
```bash
# Activate virtual environment
source .venv/bin/activate

# Run scraper
python scraper/src/cee_scraper.py --output-dir data/raw

# Run census fetcher
python analysis/census_fetcher.py --years 2012,2016,2020

# Run tests (Python package)
cd packages/python && pytest
```

### JavaScript/TypeScript
```bash
# JS package (prelecciones library)
cd packages/js
npm install
npm run build      # Build with tsup
npm test           # Run vitest tests

# Webapp (scrollytelling)
cd webapp
npm install
npm run dev        # Development server
npm run build      # Production build
npm run preview    # Preview production build
```

### R Package
```r
# In R console
devtools::load_all("packages/r")
devtools::test()
devtools::check()
```

### Data Pipeline
```bash
# Full pipeline (geo + data + aggregations)
.venv/bin/python pipeline/run_pipeline.py

# Skip steps
.venv/bin/python pipeline/run_pipeline.py --skip-geo --skip-data  # Aggregation only

# Render research notebooks
.venv/bin/quarto render analysis/research/
```

## Architecture

### Data Flow
```
CEE Website → Scraper → data/raw/ → Processor → data/processed/ → Packages
                                                      ↓
                                              Census Integration
                                                      ↓
                                              Pipeline → webapp/static/data/
```

### Key Directories
- `data/raw/` - Original scraped JSON from CEE
- `data/processed/` - Cleaned Parquet files (results.parquet, events.parquet)
- `data/census/` - ACS data by year
- `data/crosswalks/` - Geographic crosswalk tables (precinct-to-municipality)
- `data/shapes/` - MGGG precinct shapefiles
- `webapp/static/data/chapters/` - Pre-aggregated chapter-specific JSON (~8KB each)

### Scraper Architecture

The CEE website uses a three-tier XML architecture (2016+):
1. Landing page (XML with XSL)
2. SPA shell (JavaScript)
3. Data files (XML) - `/data/NAVIGATION.xml`

The scraper (`scraper/src/cee_scraper.py`) directly fetches XML data files, bypassing the JavaScript SPA. It handles both modern XML-based sites and legacy HTML formats.

### Webapp Structure

SvelteKit app with Scrollama for scroll-driven narratives:
- `webapp/src/lib/components/scrollytelling/` - ScrollySection, Step, Sticky, Progress
- `webapp/src/lib/components/maps/ChoroplethMap.svelte` - D3-based interactive map
- `webapp/src/routes/chapters/` - 12 chapter routes organized by theme:
  - Part I (Transformation): exodus, turnout, shrinking
  - Part II (Status): plebiscites, referendum-2020, geography
  - Part III (Governor): fortaleza, battlegrounds, precincts
  - Parts IV-V (Legislature + Synthesis): senate, house, future

### Package API

All three packages (`prelecciones`) expose the same API:
```python
# Python
import prelecciones as pre
events = pre.list_events()
results = pre.get_results("elecciones-generales-2020", level="municipality")
```

Levels: `island`, `district`, `municipality`, `precinct`

## Data Schema

### Core Tables (in data/processed/)
- `results.parquet` - Vote results with columns: event_id, data_level, district, candidate, party, votes
- `events.parquet` - Electoral events with: event_id, event_type, event_date, description

### Geographic Levels
- Island (1)
- Senatorial districts (8)
- Representative districts (40)
- Municipalities (78)
- Precincts (~1,100)

### Census Data
- Municipalities: `pr_municipalities_acs{year}.parquet`
- Tracts: `pr_tracts_acs{year}.parquet`
- Block groups: `pr_blockgroups_acs{year}.parquet`

## Known Issues

- CEE pages have varied HTML structures - scraper needs site-specific parsers for legacy events
- Precinct boundaries not directly available from CEE - extracted from PDF maps via `analysis/pdf_extractor.py`
- Some legacy CEE URLs (168.62.166.179) may be inaccessible
- Raw election JSONs have duplicate records per candidate (multiple data sources) - aggregation deduplicates
