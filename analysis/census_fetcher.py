"""
Census Data Fetcher for Puerto Rico Municipalities

Fetches demographic data from the American Community Survey (ACS) 5-Year Estimates
using the Census Bureau API.

USAGE:
    python census_fetcher.py [--year YEAR] [--api-key KEY] [--output DIR]

Requirements:
    - Census API key (get one at https://api.census.gov/data/key_signup.html)
    - Set CENSUS_API_KEY environment variable or pass via --api-key
"""

import argparse
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Puerto Rico FIPS code
PR_STATE_FIPS = "72"

# ACS variables to fetch with their human-readable names
# Based on ACS 5-Year Estimates Subject Tables and Data Profiles
ACS_VARIABLES = {
    # Income
    "B19013_001E": "median_household_income",
    # Poverty
    "B17001_001E": "poverty_total_population",
    "B17001_002E": "poverty_below_poverty_level",
    # Education (Population 25+)
    "B15003_001E": "education_total_population",
    "B15003_017E": "education_high_school_graduate",
    "B15003_022E": "education_bachelors_degree",
    "B15003_023E": "education_masters_degree",
    "B15003_024E": "education_professional_degree",
    "B15003_025E": "education_doctorate_degree",
    # Employment
    "B23025_001E": "employment_total_population",
    "B23025_005E": "employment_unemployed",
    "B23025_003E": "employment_in_labor_force",
    # Total Population
    "B01003_001E": "total_population",
    # Age
    "B01002_001E": "median_age",
}

# Puerto Rico municipalities (78 total)
PR_MUNICIPALITIES = [
    "Adjuntas", "Aguada", "Aguadilla", "Aguas Buenas", "Aibonito",
    "Arecibo", "Arroyo", "Barceloneta", "Barranquitas", "Bayamon",
    "Cabo Rojo", "Caguas", "Camuy", "Canovanas", "Carolina",
    "Catano", "Cayey", "Ceiba", "Ciales", "Cidra",
    "Coamo", "Comerio", "Corozal", "Culebra", "Dorado",
    "Fajardo", "Florida", "Guanica", "Guayama", "Guayanilla",
    "Guaynabo", "Gurabo", "Hatillo", "Hormigueros", "Humacao",
    "Isabela", "Jayuya", "Juana Diaz", "Juncos", "Lajas",
    "Lares", "Las Marias", "Las Piedras", "Loiza", "Luquillo",
    "Manati", "Maricao", "Maunabo", "Mayaguez", "Moca",
    "Morovis", "Naguabo", "Naranjito", "Orocovis", "Patillas",
    "Penuelas", "Ponce", "Quebradillas", "Rincon", "Rio Grande",
    "Sabana Grande", "Salinas", "San German", "San Juan", "San Lorenzo",
    "San Sebastian", "Santa Isabel", "Toa Alta", "Toa Baja", "Trujillo Alto",
    "Utuado", "Vega Alta", "Vega Baja", "Vieques", "Villalba",
    "Yabucoa", "Yauco"
]


class CensusFetcher:
    """Fetches census data from the American Community Survey API."""

    BASE_URL = "https://api.census.gov/data"

    def __init__(self, api_key: Optional[str] = None, year: int = 2022):
        """
        Initialize the Census Fetcher.

        Args:
            api_key: Census API key. If not provided, reads from CENSUS_API_KEY env var.
            year: ACS 5-year estimate year (default: 2022 for 2018-2022 estimates)
        """
        self.api_key = api_key or os.getenv("CENSUS_API_KEY")
        if not self.api_key:
            logger.warning(
                "No Census API key provided. Some requests may be rate-limited. "
                "Get a key at https://api.census.gov/data/key_signup.html"
            )
        self.year = year

    def _build_url(self, dataset: str = "acs/acs5") -> str:
        """Build the API URL for the given dataset."""
        return f"{self.BASE_URL}/{self.year}/{dataset}"

    def _make_request(self, url: str, params: dict) -> list:
        """Make a request to the Census API."""
        if self.api_key:
            params["key"] = self.api_key

        logger.info(f"Requesting data from: {url}")
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()

        return response.json()

    def fetch_municipality_data(self) -> pd.DataFrame:
        """
        Fetch ACS data for all Puerto Rico municipalities.

        Returns:
            DataFrame with census variables for each municipality.
        """
        variables = list(ACS_VARIABLES.keys())
        variables_str = ",".join(["NAME"] + variables)

        url = self._build_url()
        params = {
            "get": variables_str,
            "for": "county:*",
            "in": f"state:{PR_STATE_FIPS}"
        }

        data = self._make_request(url, params)

        # First row is headers
        headers = data[0]
        rows = data[1:]

        df = pd.DataFrame(rows, columns=headers)

        # Rename columns to human-readable names
        rename_map = {var: name for var, name in ACS_VARIABLES.items()}
        df = df.rename(columns=rename_map)

        # Clean municipality names (remove ", Puerto Rico" suffix)
        df["municipality"] = df["NAME"].str.replace(" Municipio, Puerto Rico", "", regex=False)

        # Convert numeric columns
        numeric_cols = list(ACS_VARIABLES.values())
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Add FIPS codes
        df["state_fips"] = df["state"]
        df["county_fips"] = df["county"]
        df["geoid"] = df["state_fips"] + df["county_fips"]

        # Calculate derived metrics
        df = self._calculate_derived_metrics(df)

        # Select and reorder columns
        final_columns = [
            "municipality", "geoid", "state_fips", "county_fips",
            "total_population", "median_age", "median_household_income",
            "poverty_rate", "unemployment_rate",
            "pct_high_school_or_higher", "pct_bachelors_or_higher"
        ]

        # Only include columns that exist
        final_columns = [col for col in final_columns if col in df.columns]

        return df[final_columns].sort_values("municipality").reset_index(drop=True)

    def _calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate derived metrics from raw census variables."""

        # Poverty rate
        if "poverty_total_population" in df.columns and "poverty_below_poverty_level" in df.columns:
            df["poverty_rate"] = (
                df["poverty_below_poverty_level"] / df["poverty_total_population"] * 100
            ).round(2)

        # Unemployment rate
        if "employment_in_labor_force" in df.columns and "employment_unemployed" in df.columns:
            df["unemployment_rate"] = (
                df["employment_unemployed"] / df["employment_in_labor_force"] * 100
            ).round(2)

        # Education: High school or higher
        if "education_total_population" in df.columns:
            hs_cols = [
                "education_high_school_graduate",
                "education_bachelors_degree",
                "education_masters_degree",
                "education_professional_degree",
                "education_doctorate_degree"
            ]
            existing_cols = [c for c in hs_cols if c in df.columns]
            if existing_cols:
                df["pct_high_school_or_higher"] = (
                    df[existing_cols].sum(axis=1) / df["education_total_population"] * 100
                ).round(2)

        # Education: Bachelor's or higher
        if "education_total_population" in df.columns:
            bachelors_cols = [
                "education_bachelors_degree",
                "education_masters_degree",
                "education_professional_degree",
                "education_doctorate_degree"
            ]
            existing_cols = [c for c in bachelors_cols if c in df.columns]
            if existing_cols:
                df["pct_bachelors_or_higher"] = (
                    df[existing_cols].sum(axis=1) / df["education_total_population"] * 100
                ).round(2)

        return df

    def fetch_tract_data(self, county_fips: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch ACS data at the census tract level for Puerto Rico.

        Args:
            county_fips: Optional specific county (municipality) FIPS code.
                        If not provided, fetches all tracts in PR.

        Returns:
            DataFrame with census variables for each tract.
        """
        variables = list(ACS_VARIABLES.keys())
        variables_str = ",".join(["NAME"] + variables)

        url = self._build_url()

        if county_fips:
            params = {
                "get": variables_str,
                "for": "tract:*",
                "in": f"state:{PR_STATE_FIPS} county:{county_fips}"
            }
        else:
            params = {
                "get": variables_str,
                "for": "tract:*",
                "in": f"state:{PR_STATE_FIPS}"
            }

        data = self._make_request(url, params)

        headers = data[0]
        rows = data[1:]

        df = pd.DataFrame(rows, columns=headers)

        # Rename columns
        rename_map = {var: name for var, name in ACS_VARIABLES.items()}
        df = df.rename(columns=rename_map)

        # Convert numeric columns
        numeric_cols = list(ACS_VARIABLES.values())
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Build tract GEOID
        df["state_fips"] = df["state"]
        df["county_fips"] = df["county"]
        df["tract_code"] = df["tract"]
        df["geoid"] = df["state_fips"] + df["county_fips"] + df["tract_code"]

        df = self._calculate_derived_metrics(df)

        return df


def save_data(df: pd.DataFrame, output_dir: Path, filename: str, year: int) -> None:
    """Save DataFrame to CSV and JSON formats."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Add metadata
    metadata = {
        "source": "U.S. Census Bureau American Community Survey 5-Year Estimates",
        "year": year,
        "geography": "Puerto Rico Municipalities",
        "fetched_at": datetime.now().isoformat(),
        "variables": ACS_VARIABLES
    }

    # Save CSV
    csv_path = output_dir / f"{filename}.csv"
    df.to_csv(csv_path, index=False)
    logger.info(f"Saved CSV to {csv_path}")

    # Save JSON with metadata
    json_path = output_dir / f"{filename}.json"
    output = {
        "metadata": metadata,
        "data": df.to_dict(orient="records")
    }
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2)
    logger.info(f"Saved JSON to {json_path}")

    # Save metadata separately
    meta_path = output_dir / f"{filename}_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved metadata to {meta_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Puerto Rico census data from the ACS API"
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2022,
        help="ACS 5-year estimate year (default: 2022)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Census API key (or set CENSUS_API_KEY env var)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory (default: data/census/)"
    )
    parser.add_argument(
        "--include-tracts",
        action="store_true",
        help="Also fetch tract-level data"
    )

    args = parser.parse_args()

    # Determine output directory
    if args.output:
        output_dir = Path(args.output)
    else:
        # Default to data/census/ relative to repo root
        script_dir = Path(__file__).parent
        output_dir = script_dir.parent / "data" / "census"

    logger.info(f"Fetching ACS {args.year} data for Puerto Rico")

    fetcher = CensusFetcher(api_key=args.api_key, year=args.year)

    # Fetch municipality-level data
    logger.info("Fetching municipality-level data...")
    municipality_df = fetcher.fetch_municipality_data()
    save_data(
        municipality_df,
        output_dir,
        f"pr_municipalities_acs{args.year}",
        args.year
    )

    logger.info(f"Successfully fetched data for {len(municipality_df)} municipalities")

    # Optionally fetch tract-level data
    if args.include_tracts:
        logger.info("Fetching tract-level data...")
        tract_df = fetcher.fetch_tract_data()
        save_data(
            tract_df,
            output_dir,
            f"pr_tracts_acs{args.year}",
            args.year
        )
        logger.info(f"Successfully fetched data for {len(tract_df)} census tracts")

    # Print summary
    print("\n" + "="*60)
    print("Census Data Summary")
    print("="*60)
    print(f"Year: {args.year} (ACS 5-Year Estimates)")
    print(f"Municipalities: {len(municipality_df)}")
    print(f"\nVariables included:")
    for var_name in municipality_df.columns:
        print(f"  - {var_name}")
    print(f"\nData saved to: {output_dir}")
    print("="*60)


if __name__ == "__main__":
    main()
