# Project Plan: Puerto Rico Elections Platform

## Executive Summary

Build an open data platform that makes Puerto Rico electoral data accessible to researchers, journalists, civic technologists, and the general public through:
1. A robust web scraping pipeline
2. Multi-language data packages (R, Python, JS)
3. Census data integration for demographic analysis

## Technical Architecture

### Data Pipeline

```
CEE Website → Scraper → Raw Data → Processor → Standardized Data → Packages
                                                      ↓
                                              Census Integration
```

### Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Scraper | Python (Scrapy/BeautifulSoup) | Mature ecosystem, handles complex sites |
| Data Storage | Parquet + SQLite | Portable, version-controllable, no server needed |
| R Package | R + devtools | Native R experience |
| Python Package | Python + pandas | Data science standard |
| JS Package | TypeScript | Type safety, works in Node and browser |
| CI/CD | GitHub Actions | Free for public repos, native integration |
| Documentation | Quarto | Multi-language support, beautiful output |

## Phase 1: Data Infrastructure (Weeks 1-4)

### 1.1 Web Scraper Development

**Target Sites Analysis:**

| Pattern | Example URL | Notes |
|---------|-------------|-------|
| Modern events | `elecciones2024.ceepur.org` | Standard subdomain pattern |
| Older events | `168.62.166.179/reydi2008/` | Legacy archived sites |
| Special elections | `gurabo2025.ceepur.org` | Municipality-specific |

**Scraper Features:**
- [ ] Event discovery from main page
- [ ] Results page parsing (vote counts by precinct/municipality)
- [ ] Candidate information extraction
- [ ] Historical data from archived sites
- [ ] Rate limiting and politeness
- [ ] Error handling and retry logic
- [ ] Incremental updates

### 1.2 Data Schema Design

**Core Tables:**

```
electoral_events
├── event_id (PK)
├── event_type (general|primary|plebiscite|special)
├── event_date
├── description_es
├── description_en
└── source_url

results
├── result_id (PK)
├── event_id (FK)
├── geographic_unit (precinct|municipality|island)
├── geographic_code
├── contest_type (governor|senator|representative|mayor|etc)
├── candidate_name
├── party_code
├── votes
└── percentage

geographic_units
├── unit_code (PK)
├── unit_type
├── name_es
├── parent_code
├── geometry (GeoJSON)
└── census_tract_ids (for cross-reference)
```

### 1.3 Data Pipeline

- [ ] Scheduled scraping (GitHub Actions cron)
- [ ] Data validation checks
- [ ] Automated data releases
- [ ] Change detection for updates

## Phase 2: Package Development (Weeks 5-8)

### 2.1 R Package (`prelecciones`)

**API Design:**
```r
# Get available events
prelecciones::list_events()

# Get results for an event
prelecciones::get_results("elecciones-2024")

# Get results with geographic data
prelecciones::get_results("elecciones-2024", include_geometry = TRUE)

# Filter by contest type
prelecciones::get_results("elecciones-2024", contest = "gobernador")
```

**Features:**
- [ ] Tidyverse-compatible tibbles
- [ ] sf integration for spatial data
- [ ] Caching for repeated queries
- [ ] Vignettes with example analyses

### 2.2 Python Package (`prelecciones`)

**API Design:**
```python
import prelecciones as pr

# Get available events
pr.list_events()

# Get results as DataFrame
pr.get_results("elecciones-2024")

# With geographic data (GeoDataFrame)
pr.get_results("elecciones-2024", include_geometry=True)
```

**Features:**
- [ ] pandas/geopandas integration
- [ ] Type hints throughout
- [ ] Jupyter notebook examples
- [ ] PyPI distribution

### 2.3 JavaScript Package (`prelecciones`)

**API Design:**
```typescript
import { listEvents, getResults } from 'prelecciones';

// Get available events
const events = await listEvents();

// Get results
const results = await getResults('elecciones-2024');

// With GeoJSON
const resultsGeo = await getResults('elecciones-2024', {
  includeGeometry: true
});
```

**Features:**
- [ ] TypeScript with full type definitions
- [ ] Works in Node.js and browser
- [ ] GeoJSON support
- [ ] npm distribution

## Phase 3: Census Integration (Weeks 9-12)

### 3.1 Census Data Sources

| Dataset | Variables | Geographic Level |
|---------|-----------|------------------|
| ACS 5-Year | Income, Education, Employment | Census Tract |
| Decennial Census | Population, Age, Race/Ethnicity | Block Group |
| Census TIGER | Geographic boundaries | All levels |

### 3.2 Geographic Matching

Challenge: Electoral precincts don't align with census tracts.

**Approach:**
1. Obtain precinct boundaries (request from CEE or digitize)
2. Use areal interpolation for census tract → precinct
3. Document uncertainty in cross-referenced data

### 3.3 Cross-Reference API

```r
# R example
prelecciones::get_results("elecciones-2024") |>
  prelecciones::join_census(variables = c("median_income", "education_bachelors"))
```

```python
# Python example
pr.get_results("elecciones-2024").join_census(
    variables=["median_income", "education_bachelors"]
)
```

## Phase 4: Documentation & Outreach (Ongoing)

### 4.1 Documentation

- [ ] Data dictionary (bilingual ES/EN)
- [ ] Methodology documentation
- [ ] API reference for each package
- [ ] Installation guides

### 4.2 Example Analyses

- [ ] Voter turnout trends (2000-2024)
- [ ] Party performance by municipality
- [ ] Demographic correlations with voting patterns
- [ ] Geographic visualizations

### 4.3 Community Building

- [ ] Example Jupyter/R notebooks
- [ ] Blog posts announcing releases
- [ ] Conference presentations (useR!, PyCon, etc.)

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| CEE website structure changes | Modular scraper design, monitoring alerts |
| Historical data inaccessible | Wayback Machine, early archival |
| Precinct boundaries unavailable | Start with municipality-level, pursue FOIA |
| Census variables limited for PR | Document limitations, use available ACS data |

## Success Metrics

1. **Data Coverage**: 100% of available CEE events scraped and standardized
2. **Package Adoption**: Downloads/installs tracked via CRAN/PyPI/npm
3. **Community**: GitHub stars, issues, PRs from external contributors
4. **Usage**: Citations in academic papers, news articles using the data

## Open Questions

- [ ] Can we obtain official precinct boundary shapefiles from CEE?
- [ ] What is the earliest year with digitized results?
- [ ] Are there API endpoints hidden on CEE sites we can use?
- [ ] Interest in adding other electoral data (campaign finance, etc.)?
