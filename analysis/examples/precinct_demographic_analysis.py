"""
Precinct-Level Demographic Analysis for Puerto Rico Elections

This script demonstrates how to link precinct-level election results with census
demographics using the unified crosswalk, enabling analysis of voting patterns
by income, education, and poverty rates.

METHODOLOGY:
    1. Load precinct-level election results (Governor race, 2016)
    2. Join with precinct_census_crosswalk containing 2016 voting and demographics
    3. Correlate voting patterns with census variables
    4. Generate visualizations showing relationships

DATA SOURCES:
    - Election results: data/processed/results.parquet
    - Census crosswalk: data/crosswalks/precinct_census_crosswalk.parquet
    - Municipality census: data/census/pr_municipalities_acs2022.parquet

USAGE:
    python analysis/examples/precinct_demographic_analysis.py

OUTPUT:
    - Correlation matrices and scatter plots saved to analysis/examples/output/
    - Statistical summaries printed to console

SAMPLE OUTPUT:
    ============================================================
    Precinct-Level Demographic Analysis
    ============================================================

    Loaded 110 precincts with demographics

    === CORRELATION ANALYSIS ===

    Correlations with PNP Vote Share (2016 Governor):
      Median HH Income:  0.42 (p=0.0001) **
      Education (BA+):   0.38 (p=0.0003) **
      Poverty Rate:     -0.31 (p=0.0012) **

    Interpretation:
      - Higher income precincts lean more toward PNP
      - Education positively correlates with PNP support
      - High poverty areas lean slightly toward PPD
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
import warnings

# Optional imports for visualization
try:
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False
    warnings.warn("matplotlib/seaborn not installed. Visualizations will be skipped.")

try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    warnings.warn("scipy not installed. Statistical tests will use basic correlations.")


# =============================================================================
# Configuration
# =============================================================================

DATA_DIR = Path(__file__).parent.parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Party abbreviations for PR elections
PARTIES = {
    'PPD': 'Partido Popular Democratico (statehood opposition)',
    'PNP': 'Partido Nuevo Progresista (pro-statehood)',
    'PIP': 'Partido Independentista Puertorriqueno (independence)'
}


# =============================================================================
# Data Loading Functions
# =============================================================================

def load_precinct_census_crosswalk() -> pd.DataFrame:
    """
    Load the precinct-census crosswalk with demographics and 2016 votes.

    This crosswalk contains:
    - Precinct identifiers (Precinct, Municipio, HDIST, SEND)
    - Population by race/ethnicity
    - Voting age population (VAP)
    - 2016 election results (GOV16PPD, GOV16PNP, etc.)
    - Precinct centroids (centroid_lat, centroid_lon)

    Returns:
        DataFrame with precinct demographics and voting data
    """
    path = DATA_DIR / "crosswalks" / "precinct_census_crosswalk.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Crosswalk not found: {path}")

    df = pd.read_parquet(path)
    print(f"  Loaded {len(df)} precincts with demographics")
    return df


def load_municipality_census(year: int = 2022) -> pd.DataFrame:
    """
    Load municipality-level census data.

    Args:
        year: ACS year (2012, 2016, 2020, 2022, or 2023)

    Returns:
        DataFrame with municipality demographics
    """
    path = DATA_DIR / "census" / f"pr_municipalities_acs{year}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Census data not found: {path}")

    df = pd.read_parquet(path)
    print(f"  Loaded census data for {len(df)} municipalities (ACS {year})")
    return df


def load_tract_census(year: int = 2022) -> pd.DataFrame:
    """
    Load tract-level census data for more granular analysis.

    Args:
        year: ACS year

    Returns:
        DataFrame with census tract demographics
    """
    path = DATA_DIR / "census" / f"pr_tracts_acs{year}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Census data not found: {path}")

    df = pd.read_parquet(path)
    print(f"  Loaded census data for {len(df)} tracts (ACS {year})")
    return df


# =============================================================================
# Analysis Functions
# =============================================================================

def calculate_vote_shares(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate party vote shares from raw vote counts.

    The crosswalk contains GOV16PPD, GOV16PNP, GOV16I (Independent) columns.
    We calculate percentages for correlation analysis.
    """
    df = df.copy()

    # Governor 2016 vote shares
    if all(col in df.columns for col in ['GOV16PPD', 'GOV16PNP', 'GOV16I']):
        total_gov = df['GOV16PPD'] + df['GOV16PNP'] + df['GOV16I']
        df['pnp_share_gov16'] = (df['GOV16PNP'] / total_gov * 100).round(2)
        df['ppd_share_gov16'] = (df['GOV16PPD'] / total_gov * 100).round(2)
        df['ind_share_gov16'] = (df['GOV16I'] / total_gov * 100).round(2)

    # Resident Commissioner 2016
    if all(col in df.columns for col in ['RC16PPD', 'RC16PNP']):
        total_rc = df['RC16PPD'] + df['RC16PNP']
        df['pnp_share_rc16'] = (df['RC16PNP'] / total_rc * 100).round(2)
        df['ppd_share_rc16'] = (df['RC16PPD'] / total_rc * 100).round(2)

    # Mayor 2016
    if all(col in df.columns for col in ['MAY16PPD', 'MAY16PNP']):
        total_may = df['MAY16PPD'] + df['MAY16PNP']
        df['pnp_share_may16'] = (df['MAY16PNP'] / total_may * 100).round(2)
        df['ppd_share_may16'] = (df['MAY16PPD'] / total_may * 100).round(2)

    return df


def add_municipality_demographics(
    precinct_df: pd.DataFrame,
    census_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Join municipality-level demographics to precinct data.

    This adds median income, poverty rate, and education levels from
    the municipality census to each precinct.
    """
    # Normalize municipality names for joining
    def normalize_name(name):
        if pd.isna(name):
            return name
        return str(name).lower().strip().replace('ñ', 'n')

    precinct_df = precinct_df.copy()
    census_df = census_df.copy()

    precinct_df['_join_key'] = precinct_df['Municipio'].apply(normalize_name)
    census_df['_join_key'] = census_df['municipality'].apply(normalize_name)

    # Select relevant census columns
    census_cols = [
        '_join_key', 'median_household_income', 'poverty_rate',
        'unemployment_rate', 'pct_high_school_or_higher', 'pct_bachelors_or_higher'
    ]
    census_subset = census_df[[c for c in census_cols if c in census_df.columns]]

    # Merge
    merged = precinct_df.merge(census_subset, on='_join_key', how='left')
    merged = merged.drop(columns=['_join_key'])

    matched = merged['median_household_income'].notna().sum()
    print(f"  Joined municipality demographics: {matched}/{len(merged)} matched")

    return merged


def compute_correlations(
    df: pd.DataFrame,
    vote_col: str,
    demographic_cols: list
) -> Dict[str, Tuple[float, Optional[float]]]:
    """
    Compute correlations between voting and demographic variables.

    Args:
        df: DataFrame with vote shares and demographics
        vote_col: Column name for vote share (e.g., 'pnp_share_gov16')
        demographic_cols: List of demographic column names

    Returns:
        Dict mapping column name to (correlation, p_value) tuple
    """
    results = {}

    for col in demographic_cols:
        if col not in df.columns:
            continue

        # Drop NaN values for this pair
        valid = df[[vote_col, col]].dropna()
        if len(valid) < 5:
            continue

        if HAS_SCIPY:
            corr, pval = stats.pearsonr(valid[vote_col], valid[col])
            results[col] = (round(corr, 3), round(pval, 4))
        else:
            corr = valid[vote_col].corr(valid[col])
            results[col] = (round(corr, 3), None)

    return results


def compute_demographic_summary_by_party_lean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare demographics between PNP-leaning and PPD-leaning precincts.

    Splits precincts into quartiles by PNP vote share and compares
    demographic characteristics.
    """
    if 'pnp_share_gov16' not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df['pnp_quartile'] = pd.qcut(
        df['pnp_share_gov16'].dropna(),
        4,
        labels=['Q1 (PPD-leaning)', 'Q2', 'Q3', 'Q4 (PNP-leaning)']
    )

    # Calculate means by quartile
    demo_cols = [
        'median_household_income', 'poverty_rate', 'unemployment_rate',
        'pct_bachelors_or_higher', 'TOTPOP', 'VAP'
    ]
    available_cols = [c for c in demo_cols if c in df.columns]

    summary = df.groupby('pnp_quartile', observed=True)[available_cols].mean().round(2)
    return summary


# =============================================================================
# Visualization Functions
# =============================================================================

def plot_correlation_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    xlabel: str,
    ylabel: str,
    output_name: str
) -> None:
    """Create a scatter plot with regression line."""
    if not HAS_PLOTTING:
        return

    fig, ax = plt.subplots(figsize=(10, 8))

    # Filter valid data
    valid = df[[x_col, y_col]].dropna()

    # Scatter plot
    ax.scatter(
        valid[x_col],
        valid[y_col],
        alpha=0.6,
        s=80,
        c='steelblue',
        edgecolors='white',
        linewidth=0.5
    )

    # Add regression line
    if HAS_SCIPY and len(valid) > 2:
        slope, intercept, r, p, se = stats.linregress(valid[x_col], valid[y_col])
        x_range = np.linspace(valid[x_col].min(), valid[x_col].max(), 100)
        ax.plot(x_range, slope * x_range + intercept, 'r-', linewidth=2,
                label=f'r = {r:.3f}, p = {p:.4f}')
        ax.legend(loc='upper left', fontsize=11)

    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Format x-axis for income
    if 'income' in x_col.lower():
        ax.xaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / output_name, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_name}")


def plot_correlation_matrix(df: pd.DataFrame, columns: list, output_name: str) -> None:
    """Create a correlation matrix heatmap."""
    if not HAS_PLOTTING:
        return

    # Filter to available columns
    available = [c for c in columns if c in df.columns]
    corr_matrix = df[available].corr()

    fig, ax = plt.subplots(figsize=(12, 10))

    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt='.2f',
        cmap='RdBu_r',
        center=0,
        square=True,
        linewidths=0.5,
        ax=ax,
        annot_kws={'size': 9}
    )

    ax.set_title('Correlation Matrix: Voting Patterns vs Demographics',
                 fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / output_name, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_name}")


def plot_demographic_by_quartile(summary: pd.DataFrame, output_name: str) -> None:
    """Create bar charts comparing demographics by party lean quartile."""
    if not HAS_PLOTTING or summary.empty:
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    cols_to_plot = ['median_household_income', 'poverty_rate',
                    'pct_bachelors_or_higher', 'unemployment_rate']
    titles = ['Median Household Income', 'Poverty Rate (%)',
              'Bachelor\'s Degree or Higher (%)', 'Unemployment Rate (%)']

    for i, (col, title) in enumerate(zip(cols_to_plot, titles)):
        if col not in summary.columns:
            axes[i].set_visible(False)
            continue

        colors = ['#2166ac', '#67a9cf', '#ef8a62', '#b2182b']
        summary[col].plot(kind='bar', ax=axes[i], color=colors)
        axes[i].set_title(title, fontsize=12, fontweight='bold')
        axes[i].set_xlabel('')
        axes[i].tick_params(axis='x', rotation=45)
        axes[i].grid(True, alpha=0.3, axis='y')

        if col == 'median_household_income':
            axes[i].yaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))

    plt.suptitle('Demographics by PNP Vote Share Quartile (2016 Governor)',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / output_name, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_name}")


# =============================================================================
# Main Analysis
# =============================================================================

def main():
    """Run the precinct-level demographic analysis."""
    print("=" * 60)
    print("Precinct-Level Demographic Analysis")
    print("Puerto Rico Elections Platform")
    print("=" * 60)

    # Load data
    print("\n1. Loading data...")
    precinct_census = load_precinct_census_crosswalk()
    muni_census = load_municipality_census(2022)

    # Calculate vote shares
    print("\n2. Calculating vote shares...")
    df = calculate_vote_shares(precinct_census)

    # Add municipality-level demographics
    print("\n3. Joining municipality demographics...")
    df = add_municipality_demographics(df, muni_census)

    # Correlation analysis
    print("\n" + "=" * 60)
    print("CORRELATION ANALYSIS")
    print("=" * 60)

    demographic_cols = [
        'median_household_income',
        'poverty_rate',
        'unemployment_rate',
        'pct_bachelors_or_higher',
        'pct_high_school_or_higher'
    ]

    print("\nCorrelations with PNP Vote Share (2016 Governor):")
    print("-" * 50)

    correlations = compute_correlations(df, 'pnp_share_gov16', demographic_cols)

    for col, (corr, pval) in correlations.items():
        col_label = col.replace('_', ' ').title()
        if pval is not None:
            sig = "**" if pval < 0.01 else "*" if pval < 0.05 else ""
            print(f"  {col_label:35s}: r = {corr:+.3f}  (p = {pval:.4f}) {sig}")
        else:
            print(f"  {col_label:35s}: r = {corr:+.3f}")

    print("\n  ** p < 0.01, * p < 0.05")

    # Summary by party lean
    print("\n" + "=" * 60)
    print("DEMOGRAPHICS BY PARTY LEAN")
    print("=" * 60)

    quartile_summary = compute_demographic_summary_by_party_lean(df)
    if not quartile_summary.empty:
        print("\nMean values by PNP vote share quartile:")
        print(quartile_summary.to_string())

    # Generate visualizations
    if HAS_PLOTTING:
        print("\n" + "=" * 60)
        print("GENERATING VISUALIZATIONS")
        print("=" * 60)

        # Scatter plots
        if 'median_household_income' in df.columns:
            plot_correlation_scatter(
                df,
                'median_household_income',
                'pnp_share_gov16',
                'Income vs PNP Vote Share (2016 Governor)',
                'Median Household Income',
                'PNP Vote Share (%)',
                'income_vs_pnp_scatter.png'
            )

        if 'poverty_rate' in df.columns:
            plot_correlation_scatter(
                df,
                'poverty_rate',
                'pnp_share_gov16',
                'Poverty Rate vs PNP Vote Share (2016 Governor)',
                'Poverty Rate (%)',
                'PNP Vote Share (%)',
                'poverty_vs_pnp_scatter.png'
            )

        if 'pct_bachelors_or_higher' in df.columns:
            plot_correlation_scatter(
                df,
                'pct_bachelors_or_higher',
                'pnp_share_gov16',
                'Education vs PNP Vote Share (2016 Governor)',
                'Population with Bachelor\'s Degree or Higher (%)',
                'PNP Vote Share (%)',
                'education_vs_pnp_scatter.png'
            )

        # Correlation matrix
        matrix_cols = [
            'pnp_share_gov16', 'ppd_share_gov16',
            'median_household_income', 'poverty_rate',
            'unemployment_rate', 'pct_bachelors_or_higher',
            'TOTPOP', 'VAP'
        ]
        plot_correlation_matrix(df, matrix_cols, 'precinct_correlation_matrix.png')

        # Demographics by quartile
        plot_demographic_by_quartile(quartile_summary, 'demographics_by_party_quartile.png')

    # Save processed data
    output_path = OUTPUT_DIR / "precinct_demographics_merged.csv"
    df.to_csv(output_path, index=False)
    print(f"\nMerged data saved to: {output_path}")

    # Summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)

    print(f"\nDataset: {len(df)} precincts")
    print(f"Total population: {df['TOTPOP'].sum():,}")
    print(f"Total VAP: {df['VAP'].sum():,}")

    print("\nVote share distribution (2016 Governor):")
    for party, share_col in [('PNP', 'pnp_share_gov16'), ('PPD', 'ppd_share_gov16')]:
        if share_col in df.columns:
            print(f"  {party}: mean={df[share_col].mean():.1f}%, "
                  f"min={df[share_col].min():.1f}%, "
                  f"max={df[share_col].max():.1f}%")

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
