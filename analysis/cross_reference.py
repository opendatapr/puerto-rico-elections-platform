"""
Cross-Reference Electoral Results with Census Data

This module provides functions to join Puerto Rico electoral results with
Census demographic data for analysis of voting patterns and demographics.

USAGE:
    from cross_reference import join_census, load_census_data, prepare_electoral_data

    # Load and join data
    census_df = load_census_data()
    results_df = pd.read_csv("electoral_results.csv")
    combined = join_census(results_df, census_df, variables=["median_household_income", "poverty_rate"])
"""

import logging
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd

from geo_matching import (
    get_municipality_geoid,
    normalize_municipality_name,
    validate_municipality_coverage,
    create_municipality_crosswalk,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default census variables to include in joins
DEFAULT_CENSUS_VARIABLES = [
    "total_population",
    "median_household_income",
    "poverty_rate",
    "unemployment_rate",
    "pct_high_school_or_higher",
    "pct_bachelors_or_higher",
    "median_age",
]


def load_census_data(
    data_path: Optional[Union[str, Path]] = None,
    year: int = 2022
) -> pd.DataFrame:
    """
    Load census data from the data/census directory.

    Args:
        data_path: Path to census CSV file. If None, uses default location.
        year: ACS year to load (default: 2022)

    Returns:
        DataFrame with census data indexed by municipality
    """
    if data_path is None:
        # Default to data/census/ relative to repo root
        script_dir = Path(__file__).parent
        data_path = script_dir.parent / "data" / "census" / f"pr_municipalities_acs{year}.csv"

    data_path = Path(data_path)

    if not data_path.exists():
        raise FileNotFoundError(
            f"Census data file not found: {data_path}\n"
            f"Run census_fetcher.py first to download census data."
        )

    df = pd.read_csv(data_path)

    # Normalize municipality names for joining
    df["municipality_normalized"] = df["municipality"].apply(normalize_municipality_name)

    logger.info(f"Loaded census data for {len(df)} municipalities from {data_path}")
    return df


def prepare_electoral_data(
    electoral_df: pd.DataFrame,
    municipality_column: str = "municipality"
) -> pd.DataFrame:
    """
    Prepare electoral data for joining with census data.

    Adds normalized municipality names and GEOIDs.

    Args:
        electoral_df: DataFrame with electoral results
        municipality_column: Name of the column containing municipality names

    Returns:
        DataFrame with added columns for normalized names and GEOIDs
    """
    df = electoral_df.copy()

    # Normalize municipality names
    df["municipality_normalized"] = df[municipality_column].apply(normalize_municipality_name)

    # Add GEOIDs
    df["geoid"] = df[municipality_column].apply(get_municipality_geoid)

    # Check for unmatched municipalities
    unmatched = df[df["geoid"].isna()][municipality_column].unique()
    if len(unmatched) > 0:
        logger.warning(
            f"Could not match {len(unmatched)} municipalities to GEOIDs: {list(unmatched)}"
        )

    return df


def join_census(
    electoral_df: pd.DataFrame,
    census_df: Optional[pd.DataFrame] = None,
    variables: Optional[List[str]] = None,
    municipality_column: str = "municipality",
    how: str = "left"
) -> pd.DataFrame:
    """
    Join electoral results with census demographic data.

    Args:
        electoral_df: DataFrame with electoral results. Must have a municipality column.
        census_df: DataFrame with census data. If None, loads from default location.
        variables: List of census variables to include. If None, includes all defaults.
        municipality_column: Name of the municipality column in electoral_df.
        how: Type of join ('left', 'right', 'inner', 'outer'). Default is 'left'.

    Returns:
        DataFrame with electoral results joined with census demographics.

    Example:
        >>> results = pd.read_csv("electoral_results.csv")
        >>> combined = join_census(results, variables=["median_household_income", "poverty_rate"])
        >>> combined.columns
        Index(['municipality', 'candidate', 'votes', 'median_household_income', 'poverty_rate'])
    """
    # Load census data if not provided
    if census_df is None:
        census_df = load_census_data()

    # Select variables to include
    if variables is None:
        variables = DEFAULT_CENSUS_VARIABLES

    # Filter to available variables
    available_vars = [v for v in variables if v in census_df.columns]
    missing_vars = set(variables) - set(available_vars)
    if missing_vars:
        logger.warning(f"Census variables not found: {missing_vars}")

    # Prepare electoral data
    electoral_prepared = prepare_electoral_data(electoral_df, municipality_column)

    # Prepare census data for join
    census_columns = ["municipality_normalized", "geoid"] + available_vars
    census_for_join = census_df[census_columns].copy()

    # Perform join
    result = electoral_prepared.merge(
        census_for_join,
        on="municipality_normalized",
        how=how,
        suffixes=("", "_census")
    )

    # Handle duplicate geoid columns
    if "geoid_census" in result.columns:
        # Prefer the census geoid if electoral one was missing
        result["geoid"] = result["geoid"].fillna(result["geoid_census"])
        result = result.drop(columns=["geoid_census"])

    logger.info(
        f"Joined {len(electoral_df)} electoral rows with {len(available_vars)} census variables"
    )

    return result


def aggregate_by_municipality(
    electoral_df: pd.DataFrame,
    value_column: str = "votes",
    group_columns: Optional[List[str]] = None,
    municipality_column: str = "municipality"
) -> pd.DataFrame:
    """
    Aggregate electoral results by municipality for census joining.

    Useful when electoral data is at precinct level and needs to be
    aggregated to municipality level for census comparison.

    Args:
        electoral_df: DataFrame with electoral results
        value_column: Column to aggregate (default: "votes")
        group_columns: Additional columns to group by (e.g., ["candidate", "party"])
        municipality_column: Name of municipality column

    Returns:
        DataFrame aggregated to municipality level
    """
    if group_columns is None:
        group_columns = []

    group_by = [municipality_column] + group_columns

    # Check which columns exist
    existing_groups = [c for c in group_by if c in electoral_df.columns]
    if len(existing_groups) != len(group_by):
        missing = set(group_by) - set(existing_groups)
        logger.warning(f"Group columns not found: {missing}")

    result = electoral_df.groupby(existing_groups, as_index=False).agg({
        value_column: "sum"
    })

    return result


def calculate_demographic_correlations(
    combined_df: pd.DataFrame,
    electoral_metric: str,
    census_variables: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Calculate correlations between electoral metrics and census demographics.

    Args:
        combined_df: DataFrame from join_census() with both electoral and census data
        electoral_metric: Column name of the electoral metric to correlate
        census_variables: Census variables to correlate with. If None, uses all defaults.

    Returns:
        DataFrame with correlation coefficients
    """
    if census_variables is None:
        census_variables = DEFAULT_CENSUS_VARIABLES

    # Filter to available variables
    available = [v for v in census_variables if v in combined_df.columns]

    if electoral_metric not in combined_df.columns:
        raise ValueError(f"Electoral metric '{electoral_metric}' not found in data")

    correlations = {}
    for var in available:
        # Skip if too many missing values
        valid_data = combined_df[[electoral_metric, var]].dropna()
        if len(valid_data) < 10:
            logger.warning(f"Insufficient data for correlation with {var}")
            continue

        corr = valid_data[electoral_metric].corr(valid_data[var])
        correlations[var] = corr

    result = pd.DataFrame([
        {"variable": var, "correlation": corr}
        for var, corr in correlations.items()
    ])

    return result.sort_values("correlation", ascending=False).reset_index(drop=True)


def create_analysis_dataset(
    electoral_df: pd.DataFrame,
    census_df: Optional[pd.DataFrame] = None,
    municipality_column: str = "municipality",
    aggregate_column: Optional[str] = None,
    aggregate_groups: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Create a complete analysis dataset combining electoral and census data.

    This is a convenience function that handles common preprocessing steps.

    Args:
        electoral_df: Raw electoral results data
        census_df: Census data (loads default if None)
        municipality_column: Name of municipality column
        aggregate_column: If provided, aggregate this column to municipality level
        aggregate_groups: Additional grouping columns for aggregation

    Returns:
        Analysis-ready DataFrame with electoral and demographic data
    """
    df = electoral_df.copy()

    # Aggregate if needed
    if aggregate_column:
        df = aggregate_by_municipality(
            df,
            value_column=aggregate_column,
            group_columns=aggregate_groups,
            municipality_column=municipality_column
        )

    # Join with census data
    result = join_census(
        df,
        census_df=census_df,
        municipality_column=municipality_column
    )

    # Validate coverage
    validation = validate_municipality_coverage(
        result[municipality_column].unique().tolist()
    )

    logger.info(
        f"Analysis dataset created with {validation['coverage_pct']:.1f}% "
        f"municipality coverage"
    )

    if validation["unmatched_input"]:
        logger.warning(
            f"Unmatched municipalities: {validation['unmatched_input']}"
        )

    return result


def export_crosswalk(output_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """
    Export the municipality crosswalk table.

    Args:
        output_path: Path to save crosswalk CSV. If None, returns DataFrame only.

    Returns:
        Municipality crosswalk DataFrame
    """
    crosswalk = create_municipality_crosswalk()

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        crosswalk.to_csv(output_path, index=False)
        logger.info(f"Exported crosswalk to {output_path}")

    return crosswalk


if __name__ == "__main__":
    # Demo usage
    print("Cross-Reference Module Demo")
    print("=" * 50)

    # Create sample electoral data
    sample_electoral = pd.DataFrame({
        "municipality": ["San Juan", "Bayamón", "Ponce", "Mayagüez", "Carolina"],
        "candidate_a_votes": [150000, 100000, 80000, 45000, 70000],
        "candidate_b_votes": [140000, 95000, 85000, 50000, 65000],
    })

    print("\nSample Electoral Data:")
    print(sample_electoral)

    # Prepare for joining
    prepared = prepare_electoral_data(sample_electoral)
    print("\nPrepared with GEOIDs:")
    print(prepared[["municipality", "municipality_normalized", "geoid"]])

    # Export crosswalk
    crosswalk = export_crosswalk()
    print(f"\nCrosswalk has {len(crosswalk)} municipalities")
    print("\nSample crosswalk rows:")
    print(crosswalk.head())

    print("\n" + "=" * 50)
    print("To use with real data:")
    print("  1. Run census_fetcher.py to download census data")
    print("  2. Load your electoral results")
    print("  3. Use join_census() to combine datasets")
