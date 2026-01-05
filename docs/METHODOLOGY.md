# Methodology / Metodologia

This document describes the data collection, processing, and validation methodology used in the Puerto Rico Elections Platform.

Este documento describe la metodologia de recoleccion, procesamiento y validacion de datos utilizada en la Plataforma de Elecciones de Puerto Rico.

---

## Table of Contents / Tabla de Contenidos

1. [Data Sources / Fuentes de Datos](#1-data-sources--fuentes-de-datos)
2. [Web Scraping Process / Proceso de Extraccion Web](#2-web-scraping-process--proceso-de-extraccion-web)
3. [Data Cleaning / Limpieza de Datos](#3-data-cleaning--limpieza-de-datos)
4. [Validation / Validacion](#4-validation--validacion)
5. [Geographic Matching / Emparejamiento Geografico](#5-geographic-matching--emparejamiento-geografico)
6. [Census Integration / Integracion Censal](#6-census-integration--integracion-censal)
7. [Data Updates / Actualizaciones de Datos](#7-data-updates--actualizaciones-de-datos)
8. [Reproducibility / Reproducibilidad](#8-reproducibility--reproducibilidad)

---

## 1. Data Sources / Fuentes de Datos

### Primary Source: Comision Estatal de Elecciones (CEE)

All electoral data is sourced directly from the Puerto Rico State Elections Commission.

Todos los datos electorales provienen directamente de la Comision Estatal de Elecciones de Puerto Rico.

| Source Type | URL Pattern | Coverage |
|-------------|-------------|----------|
| Main Portal | `https://ww2.ceepur.org/` | Event listings |
| Modern Events (2016+) | `https://elecciones{year}.ceepur.org/` | Full results |
| Legacy Events (2008-2012) | `http://168.62.166.179/reydi{year}/` | Archived results |
| Special Elections | `https://{municipality}{year}.ceepur.org/` | Municipal specials |

### Secondary Source: US Census Bureau

Census data is obtained from the American Community Survey (ACS) for demographic cross-referencing.

Los datos censales se obtienen de la Encuesta de la Comunidad Americana (ACS) para referencia cruzada demografica.

| Dataset | Variables | Update Frequency |
|---------|-----------|------------------|
| ACS 5-Year Estimates | Income, Education, Employment | Annual |
| Decennial Census | Population, Age, Ethnicity | Every 10 years |
| TIGER/Line Shapefiles | Geographic boundaries | Annual |

---

## 2. Web Scraping Process / Proceso de Extraccion Web

### Technology Stack

```
Python 3.10+
├── requests        # HTTP requests
├── BeautifulSoup4  # HTML parsing
├── Scrapy          # Large-scale scraping
├── pandas          # Data manipulation
└── sqlite3         # Local storage
```

### Scraping Workflow

```
1. Event Discovery
   └── Parse main CEE portal for event links
       └── Extract event metadata (date, type, URL)

2. Results Extraction
   └── For each event:
       ├── Identify results pages
       ├── Parse vote tables
       ├── Extract candidate information
       └── Capture geographic breakdowns

3. Data Storage
   └── Save to SQLite database
       ├── Raw HTML archived
       ├── Parsed data in structured tables
       └── Extraction metadata logged
```

### Politeness and Rate Limiting

To ensure respectful use of CEE servers, the scraper implements:

Para asegurar uso respetuoso de los servidores de la CEE, el scraper implementa:

- **Request delays**: 1-3 seconds between requests
- **User-Agent identification**: Identifies as research project
- **robots.txt compliance**: Respects disallow directives
- **Off-peak scheduling**: Runs during low-traffic hours
- **Error backoff**: Exponential backoff on failures

### Error Handling

| Error Type | Response |
|------------|----------|
| HTTP 429 (Rate Limited) | Wait 60 seconds, retry with backoff |
| HTTP 5xx (Server Error) | Retry up to 3 times with 30s delay |
| Timeout | Retry up to 3 times with 15s delay |
| Parse Error | Log error, skip record, continue |
| Missing Data | Mark as null, flag for review |

---

## 3. Data Cleaning / Limpieza de Datos

### Standardization Steps

1. **Character Encoding**
   - Convert all text to UTF-8
   - Handle Spanish characters (n, accents)
   - Remove invisible characters

2. **Name Normalization**
   - Standardize candidate names (title case)
   - Normalize party names to codes
   - Handle name variations across events

3. **Numeric Cleaning**
   - Remove thousand separators
   - Convert percentages to decimals
   - Handle missing values (null vs zero)

4. **Date Standardization**
   - Convert all dates to ISO 8601 (YYYY-MM-DD)
   - Extract year for grouping
   - Validate date ranges

### Data Transformations

```python
# Example: Vote count cleaning
def clean_vote_count(raw_value):
    """
    Transform raw vote strings to integers.

    Examples:
        "1,234" -> 1234
        "1.234" -> 1234 (European format)
        "-"     -> None
        ""      -> None
    """
    if pd.isna(raw_value) or raw_value in ["-", "", "N/A"]:
        return None

    # Remove separators
    cleaned = str(raw_value).replace(",", "").replace(".", "")
    return int(cleaned)
```

### Handling Inconsistencies

| Issue | Resolution |
|-------|------------|
| Different municipality spellings | Standardized to official FIPS names |
| Party name changes over time | Mapped to consistent party codes |
| Precinct renumbering | Cross-referenced with municipality |
| Missing totals | Calculated from component values |

---

## 4. Validation / Validacion

### Automated Validation Checks

The data pipeline runs validation checks at multiple stages:

El pipeline de datos ejecuta verificaciones de validacion en multiples etapas:

#### Row-Level Validations

```python
validations = {
    "vote_count_positive": lambda x: x["votes"] >= 0,
    "percentage_range": lambda x: 0 <= x["percentage"] <= 100,
    "valid_party_code": lambda x: x["party_code"] in KNOWN_PARTIES,
    "valid_municipality": lambda x: x["geographic_code"] in MUNICIPALITIES,
}
```

#### Aggregate Validations

| Check | Description | Threshold |
|-------|-------------|-----------|
| Vote totals match | Sum of candidate votes = total votes | Exact match |
| Percentage sum | Percentages sum to ~100% | +/- 0.5% |
| Turnout reasonable | Turnout between 0-100% | Strict |
| Winner identified | Exactly one winner per contest | Exact |

#### Cross-Reference Validations

- Compare totals with official CEE announcements
- Verify against historical patterns (flag anomalies)
- Check geographic hierarchy consistency

### Manual Review Process

Records flagged by automated validation undergo manual review:

1. Compare against original CEE webpage (archived)
2. Cross-reference with news reports if available
3. Document discrepancies in `validation_notes` field
4. Escalate unresolved issues to project maintainers

---

## 5. Geographic Matching / Emparejamiento Geografico

### Challenge / Desafio

Electoral precincts in Puerto Rico do not align with US Census geographic units. This makes demographic analysis challenging.

Los precintos electorales en Puerto Rico no se alinean con las unidades geograficas del Censo de EE.UU. Esto hace que el analisis demografico sea desafiante.

### Approach / Enfoque

#### Municipality Level (High Confidence)

Municipalities align directly between electoral and census data.

```
Electoral: Municipality 127 (Trujillo Alto)
Census: County FIPS 72127 (Trujillo Alto Municipio)
Confidence: 100%
```

#### Precinct to Census Tract (Medium Confidence)

We use areal interpolation to estimate demographic characteristics:

Usamos interpolacion areal para estimar caracteristicas demograficas:

1. **Obtain precinct boundaries** (when available)
   - Request from CEE
   - Digitize from official maps
   - Estimate from voting unit addresses

2. **Calculate overlap with census tracts**
   ```
   For each precinct P:
       For each census tract T that overlaps P:
           weight[P,T] = area(P ∩ T) / area(T)
   ```

3. **Interpolate demographic values**
   ```
   demographic[P] = Σ (weight[P,T] × demographic[T])
   ```

#### Confidence Levels

| Geographic Level | Confidence | Notes |
|------------------|------------|-------|
| Island | 100% | Direct aggregation |
| Senatorial District | 95% | Near-exact alignment |
| Municipality | 100% | Direct match via FIPS |
| Precinct | 60-80% | Estimated via interpolation |
| Voting Unit | 40-60% | High uncertainty |

### Documentation of Uncertainty

All cross-referenced data includes uncertainty estimates:

```json
{
  "precinct_code": "127-03",
  "median_income": 42500,
  "median_income_margin_of_error": 3200,
  "interpolation_confidence": 0.72,
  "census_tracts_used": ["72127001100", "72127001200", "72127001300"],
  "interpolation_weights": [0.45, 0.35, 0.20]
}
```

---

## 6. Census Integration / Integracion Censal

### Available Variables

| Category | Variables | ACS Table |
|----------|-----------|-----------|
| Income | Median household income, Income brackets | B19013, B19001 |
| Education | Educational attainment (HS, Bachelor's, Graduate) | B15003 |
| Employment | Labor force participation, Unemployment rate | B23025 |
| Age | Median age, Age distribution | B01002, B01001 |
| Housing | Owner vs renter, Home values | B25003, B25077 |
| Language | Spanish speakers, English proficiency | B16001 |

### API Usage

Census data is retrieved via the Census Bureau API:

```python
from census import Census

c = Census("YOUR_API_KEY")

# Get median income for Puerto Rico municipalities
data = c.acs5.state_county(
    fields=["B19013_001E"],  # Median household income
    state_fips="72",
    county_fips="*",
    year=2022
)
```

### Temporal Alignment

Census data is matched to electoral events by year:

| Electoral Event Year | Census Data Used |
|---------------------|------------------|
| 2024 | ACS 2022 5-Year |
| 2020 | ACS 2019 5-Year + 2020 Decennial |
| 2016 | ACS 2015 5-Year |
| 2012 | ACS 2011 5-Year |
| 2008 | ACS 2007 5-Year |
| 2000-2004 | 2000 Decennial |

---

## 7. Data Updates / Actualizaciones de Datos

### Update Schedule

| Trigger | Action |
|---------|--------|
| New electoral event | Full scrape of new event |
| CEE site update | Re-scrape affected events |
| Census release | Update demographic data |
| Error report | Targeted correction |

### Version Control

All data releases are versioned following semantic versioning:

```
v1.2.3
│ │ └── Patch: Bug fixes, minor corrections
│ └──── Minor: New events, additional variables
└────── Major: Schema changes, methodology updates
```

### Change Log

Each release includes a CHANGELOG documenting:
- New events added
- Corrections made
- Schema changes
- Methodology updates

---

## 8. Reproducibility / Reproducibilidad

### Data Provenance

Every data record includes provenance metadata:

```json
{
  "result_id": "2024-gen-gov-001",
  "source_url": "https://elecciones2024.ceepur.org/Escrutinio/113/001",
  "scraped_at": "2024-11-10T14:32:00Z",
  "scraper_version": "1.2.0",
  "raw_html_hash": "sha256:abc123...",
  "processing_version": "1.1.0"
}
```

### Archived Raw Data

Original HTML pages are archived for verification:

```
data/
└── raw/
    └── 2024/
        └── elecciones-generales/
            ├── index.html
            ├── gobernador/
            │   ├── isla.html
            │   ├── municipio-001.html
            │   └── ...
            └── metadata.json
```

### Reproducible Pipeline

The full pipeline can be re-run from scratch:

```bash
# Re-scrape all data
python -m scraper.run --full

# Re-process with current cleaning rules
python -m processor.run --reprocess

# Validate against archived raw data
python -m validator.run --verify
```

---

## References / Referencias

1. Comision Estatal de Elecciones de Puerto Rico. https://ww2.ceepur.org/
2. US Census Bureau. American Community Survey. https://www.census.gov/programs-surveys/acs
3. US Census Bureau. TIGER/Line Shapefiles. https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
4. Python Software Foundation. Beautiful Soup Documentation. https://www.crummy.com/software/BeautifulSoup/
5. Scrapy Documentation. https://docs.scrapy.org/

---

## Contact / Contacto

For questions about methodology or to report data issues:

Para preguntas sobre metodologia o reportar problemas con los datos:

- GitHub Issues: https://github.com/opendatapr/puerto-rico-elections-platform/issues
- Email: [project maintainers]
