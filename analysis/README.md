# Analysis Module - Census Data Integration

This module provides tools for integrating U.S. Census Bureau demographic data with Puerto Rico electoral results, enabling analysis of voting patterns across different demographic characteristics.

## Overview

The analysis module consists of three main components:

1. **census_fetcher.py** - Downloads demographic data from the American Community Survey (ACS) API
2. **geo_matching.py** - Provides geographic matching between municipalities and census identifiers
3. **cross_reference.py** - Joins electoral results with census demographics

## Installation

```bash
cd analysis
pip install -r requirements.txt
```

## Census API Key

To fetch census data, you'll need a free API key from the Census Bureau:

1. Request a key at: https://api.census.gov/data/key_signup.html
2. Set the environment variable:
   ```bash
   export CENSUS_API_KEY="your_api_key_here"
   ```

## Usage

### 1. Download Census Data

```bash
# Fetch ACS 2022 5-year estimates for Puerto Rico municipalities
python census_fetcher.py --year 2022

# Also fetch tract-level data (more granular)
python census_fetcher.py --year 2022 --include-tracts

# Specify output directory
python census_fetcher.py --output /path/to/output
```

Data is saved to `data/census/` in both CSV and JSON formats.

### 2. Match Municipalities to Census Identifiers

```python
from geo_matching import get_municipality_geoid, normalize_municipality_name

# Get GEOID for a municipality
geoid = get_municipality_geoid("San Juan")  # Returns "72127"
geoid = get_municipality_geoid("Mayaguez")   # Returns "72097"

# Handles variations in spelling
geoid = get_municipality_geoid("bayamon")    # Returns "72021"

# Create full crosswalk table
from geo_matching import create_municipality_crosswalk
crosswalk = create_municipality_crosswalk()
```

### 3. Join Electoral Results with Census Data

```python
import pandas as pd
from cross_reference import join_census, load_census_data

# Load your electoral results
results = pd.read_csv("electoral_results.csv")

# Join with census demographics
combined = join_census(
    results,
    variables=["median_household_income", "poverty_rate", "unemployment_rate"],
    municipality_column="municipality"
)

# Analyze correlations
from cross_reference import calculate_demographic_correlations
correlations = calculate_demographic_correlations(
    combined,
    electoral_metric="vote_share",
    census_variables=["median_household_income", "poverty_rate"]
)
```

## Census Variables

The following demographic variables are available:

| Variable | Description |
|----------|-------------|
| `total_population` | Total population |
| `median_age` | Median age |
| `median_household_income` | Median household income (dollars) |
| `poverty_rate` | Percentage below poverty level |
| `unemployment_rate` | Unemployment rate |
| `pct_high_school_or_higher` | Percentage with high school diploma or higher |
| `pct_bachelors_or_higher` | Percentage with bachelor's degree or higher |

## Geographic Matching Methodology

Puerto Rico's 78 municipalities are equivalent to "counties" in Census Bureau terminology. Each municipality has:

- **State FIPS**: 72 (Puerto Rico)
- **County FIPS**: 3-digit code unique to each municipality
- **GEOID**: 5-digit combination (state + county FIPS)

The matching process:
1. Normalizes municipality names (lowercase, remove accents, standardize spacing)
2. Looks up the county FIPS code from the official Census Bureau mapping
3. Constructs the full GEOID for joining with census data

### Handling Name Variations

The module handles common variations:
- Accented characters: "Mayaguez" matches "Mayaguez"
- Case variations: "SAN JUAN" matches "San Juan"
- Common abbreviations and misspellings

## Data Sources

- **Census Data**: American Community Survey 5-Year Estimates
  - Source: U.S. Census Bureau
  - URL: https://www.census.gov/programs-surveys/acs
  - Geographic Level: Puerto Rico municipalities (county equivalent)

## File Structure

```
analysis/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── census_fetcher.py      # Census API data fetcher
├── geo_matching.py        # Geographic matching utilities
└── cross_reference.py     # Electoral-census data joining

data/census/               # Downloaded census data (gitignored)
├── pr_municipalities_acs2022.csv
├── pr_municipalities_acs2022.json
└── pr_municipalities_acs2022_metadata.json
```

## Example Analysis

```python
import pandas as pd
from cross_reference import create_analysis_dataset

# Load electoral results (example structure)
electoral = pd.DataFrame({
    "municipality": ["San Juan", "Bayamon", "Ponce"],
    "candidate_a": [100000, 80000, 50000],
    "candidate_b": [95000, 75000, 55000],
})

# Create analysis dataset
analysis = create_analysis_dataset(
    electoral,
    municipality_column="municipality"
)

# Now analyze relationships between voting and demographics
print(analysis[["municipality", "candidate_a", "median_household_income", "poverty_rate"]])
```

## Notes

- Census data updates annually; the most recent ACS 5-year estimates have a 1-2 year lag
- Some census tracts may have suppressed data due to small populations
- Electoral precinct boundaries may not align perfectly with census tract boundaries
- Municipality-level analysis provides the most reliable cross-referencing
