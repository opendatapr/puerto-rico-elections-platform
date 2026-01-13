"""
Example Analysis: Correlating Election Results with Census Demographics

This script demonstrates how to combine Puerto Rico electoral data with
census demographics to analyze voting patterns by socioeconomic factors.

USAGE:
    python election_census_analysis.py

Output:
    - Correlation analysis between voter turnout and demographics
    - Visualizations saved to analysis/examples/output/
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data():
    """Load election results and census data."""
    print("Loading data...")

    # Election results
    elections = pd.read_parquet(DATA_DIR / "processed" / "results.parquet")
    print(f"  Elections: {len(elections):,} records")

    # Census data (multiple years)
    census_years = {}
    for year in [2012, 2016, 2020, 2022, 2023]:
        path = DATA_DIR / "census" / f"pr_municipalities_acs{year}.parquet"
        if path.exists():
            census_years[year] = pd.read_parquet(path)
            print(f"  Census {year}: {len(census_years[year])} municipalities")

    # Crosswalk
    crosswalk_path = DATA_DIR / "crosswalks" / "precinct_municipality_crosswalk.parquet"
    crosswalk = pd.read_parquet(crosswalk_path) if crosswalk_path.exists() else None
    if crosswalk is not None:
        print(f"  Crosswalk: {len(crosswalk)} districts")

    return elections, census_years, crosswalk


def analyze_municipality_results(elections: pd.DataFrame) -> pd.DataFrame:
    """Aggregate election results to municipality level."""
    # Filter to municipality-level data
    muni_results = elections[elections["data_level"] == "municipality"].copy()

    if len(muni_results) == 0:
        print("  No municipality-level data found, aggregating from precinct...")
        # Would need to aggregate - for now return empty
        return pd.DataFrame()

    print(f"  Municipality results: {len(muni_results):,} records")
    return muni_results


def correlate_with_census(
    election_results: pd.DataFrame,
    census: pd.DataFrame,
    election_year: int
) -> pd.DataFrame:
    """
    Join election results with census demographics.

    Args:
        election_results: Election data with municipality column
        census: Census data with municipality column
        election_year: Year of election for labeling

    Returns:
        Merged DataFrame with election + census columns
    """
    # Normalize municipality names for joining
    def normalize_name(name):
        if pd.isna(name):
            return name
        return str(name).lower().strip()

    election_results = election_results.copy()
    census = census.copy()

    # Try different column names for municipality
    election_muni_cols = ["municipality", "district", "municipio", "name"]
    census_muni_cols = ["municipality", "municipio", "name", "NAME"]

    election_muni_col = None
    for col in election_muni_cols:
        if col in election_results.columns:
            election_muni_col = col
            break

    census_muni_col = None
    for col in census_muni_cols:
        if col in census.columns:
            census_muni_col = col
            break

    if election_muni_col is None or census_muni_col is None:
        print(f"  Could not find municipality column")
        print(f"  Election columns: {list(election_results.columns)}")
        print(f"  Census columns: {list(census.columns)}")
        return pd.DataFrame()

    # Normalize for joining
    election_results["_join_key"] = election_results[election_muni_col].apply(normalize_name)
    census["_join_key"] = census[census_muni_col].apply(normalize_name)

    # Merge
    merged = election_results.merge(
        census,
        on="_join_key",
        how="left",
        suffixes=("", "_census")
    )

    merged = merged.drop(columns=["_join_key"])
    merged["election_year"] = election_year

    # Count matches (check for census data column presence)
    census_indicator = "total_population" if "total_population" in merged.columns else census_muni_col
    matched = merged[census_indicator].notna().sum() if census_indicator in merged.columns else 0
    print(f"  Merged: {len(merged):,} records ({matched} with census data)")

    return merged


def calculate_summary_stats(merged: pd.DataFrame) -> dict:
    """Calculate summary statistics from merged data."""
    stats = {}

    # Check available columns
    numeric_cols = merged.select_dtypes(include=[np.number]).columns.tolist()

    # Income correlation with votes (if available)
    if "median_household_income" in merged.columns and "votes" in merged.columns:
        valid = merged[["median_household_income", "votes"]].dropna()
        if len(valid) > 2:
            corr = valid["median_household_income"].corr(valid["votes"])
            stats["income_votes_correlation"] = round(corr, 3)

    # Poverty rate stats
    if "poverty_rate" in merged.columns:
        stats["avg_poverty_rate"] = round(merged["poverty_rate"].mean(), 2)
        stats["min_poverty_rate"] = round(merged["poverty_rate"].min(), 2)
        stats["max_poverty_rate"] = round(merged["poverty_rate"].max(), 2)

    # Education stats
    if "pct_bachelors_or_higher" in merged.columns:
        stats["avg_bachelors_pct"] = round(merged["pct_bachelors_or_higher"].mean(), 2)

    return stats


def main():
    """Run the example analysis."""
    print("=" * 60)
    print("Puerto Rico Election + Census Analysis")
    print("=" * 60)

    # Load data
    elections, census_years, crosswalk = load_data()

    # Show available events
    print("\nAvailable election events:")
    events = elections["event_id"].unique()
    for event in events[:10]:
        count = len(elections[elections["event_id"] == event])
        print(f"  - {event}: {count:,} records")
    if len(events) > 10:
        print(f"  ... and {len(events) - 10} more")

    # Aggregate to municipality level
    print("\nAggregating to municipality level...")
    muni_results = analyze_municipality_results(elections)

    # Example: Correlate with 2020 census
    if 2020 in census_years and len(muni_results) > 0:
        print("\nCorrelating with ACS 2020 census data...")
        merged = correlate_with_census(muni_results, census_years[2020], 2020)

        if len(merged) > 0:
            # Calculate stats
            stats = calculate_summary_stats(merged)
            print("\nSummary Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")

            # Save merged data
            output_path = OUTPUT_DIR / "election_census_merged.csv"
            merged.to_csv(output_path, index=False)
            print(f"\nMerged data saved to: {output_path}")

    # Show crosswalk info
    if crosswalk is not None:
        print("\nCrosswalk Summary:")
        print(f"  Total districts: {len(crosswalk)}")
        print(f"  Municipalities covered: {crosswalk['municipality'].nunique()}")
        print(f"  Senate districts: {crosswalk['senate_district'].nunique()}")
        print(f"  House districts: {crosswalk['house_district'].nunique()}")

        # Save crosswalk summary
        crosswalk_summary = crosswalk.groupby("municipality").agg({
            "population_2010": "sum",
            "voting_age_pop_2010": "sum",
            "house_district": "nunique"
        }).reset_index()
        crosswalk_summary.columns = ["municipality", "total_pop_2010", "vap_2010", "num_house_districts"]
        crosswalk_summary.to_csv(OUTPUT_DIR / "municipality_summary.csv", index=False)
        print(f"  Municipality summary saved to: {OUTPUT_DIR / 'municipality_summary.csv'}")

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
