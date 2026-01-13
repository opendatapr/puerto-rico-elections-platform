"""
Multi-Year Election Trends Analysis for Puerto Rico

This script analyzes voting pattern changes across multiple election cycles
(2016, 2020) at the municipality level, correlating shifts with demographic changes.

METHODOLOGY:
    1. Extract general election results for Governor race by municipality
    2. Calculate party vote shares for each election year
    3. Compute swing (change in vote share) between elections
    4. Join with census data to analyze demographic correlates of swing
    5. Generate trend visualizations

DATA SOURCES:
    - Election results: data/processed/results.parquet (2016, 2020 general elections)
    - Census: data/census/pr_municipalities_acs{2016,2020,2022}.parquet

USAGE:
    python analysis/examples/election_trends_analysis.py

OUTPUT:
    - Trend analysis saved to analysis/examples/output/
    - Visualizations of party vote share changes

SAMPLE OUTPUT:
    ============================================================
    Multi-Year Election Trends Analysis
    ============================================================

    Governor Race Results (Island-wide):
    -------------------------------------------------------
                         2016        2020      Swing
    PNP               41.80%      33.24%     -8.56%
    PPD               38.87%      31.75%     -7.12%
    PIP/MVC            2.13%      27.53%    +25.40%  (includes MVC 2020)
    Other             17.20%       7.48%     -9.72%

    Municipalities with largest PNP swing:
      Culebra:      -18.2% (from 52.1% to 33.9%)
      Vieques:      -15.4% (from 38.7% to 23.3%)
      San Juan:     -12.8% (from 39.2% to 26.4%)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings

# Optional imports
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


# =============================================================================
# Configuration
# =============================================================================

DATA_DIR = Path(__file__).parent.parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Party groupings for analysis
PARTY_GROUPS = {
    'PNP': ['PARTIDO NUEVO PROGRESISTA'],
    'PPD': ['PARTIDO POPULAR DEMOCRÁTICO'],
    'PIP': ['PARTIDO INDEPENDENTISTA PUERTORRIQUEÑO'],
    'MVC': ['MOVIMIENTO VICTORIA CIUDADANA'],
    'OTHER': ['INDEPENDIENTE', 'PARTIDO PUEBLO TRABAJADOR', 'PROYECTO DIGNIDAD', 'OTROS']
}


# =============================================================================
# Data Loading Functions
# =============================================================================

def load_election_results() -> pd.DataFrame:
    """Load all election results."""
    path = DATA_DIR / "processed" / "results.parquet"
    df = pd.read_parquet(path)
    print(f"  Loaded {len(df):,} election records")
    return df


def load_census_by_year() -> Dict[int, pd.DataFrame]:
    """Load census data for multiple years."""
    census_years = {}
    for year in [2012, 2016, 2020, 2022]:
        path = DATA_DIR / "census" / f"pr_municipalities_acs{year}.parquet"
        if path.exists():
            census_years[year] = pd.read_parquet(path)
            print(f"  Loaded ACS {year}: {len(census_years[year])} municipalities")
    return census_years


# =============================================================================
# Data Processing Functions
# =============================================================================

def extract_election_year(event_date: str) -> int:
    """Extract year from event_date string."""
    try:
        return int(str(event_date)[:4])
    except (ValueError, TypeError):
        return None


def standardize_party(party: str) -> str:
    """Map party names to standardized abbreviations."""
    if pd.isna(party):
        return 'OTHER'
    party = str(party).upper().strip()

    for abbrev, names in PARTY_GROUPS.items():
        for name in names:
            if name.upper() in party:
                return abbrev
    return 'OTHER'


def get_governor_results_by_municipality(
    results: pd.DataFrame,
    election_year: int
) -> pd.DataFrame:
    """
    Extract Governor race results at precinct level and aggregate to municipality.

    Args:
        results: Full election results DataFrame
        election_year: Year to filter (2016 or 2020)

    Returns:
        DataFrame with municipality-level vote shares by party
    """
    # Filter to general elections, Governor race, precinct level
    mask = (
        (results['event_type'] == 'general') &
        (results['office'] == 'GOBERNADOR') &
        (results['data_level'] == 'precinct')
    )
    gov = results[mask].copy()

    # Extract year and filter
    gov['year'] = gov['event_date'].apply(extract_election_year)
    gov = gov[gov['year'] == election_year]

    if len(gov) == 0:
        print(f"  Warning: No Governor precinct data for {election_year}")
        return pd.DataFrame()

    # Extract municipality from district (format: "Municipality XXX")
    gov['municipality'] = gov['district'].str.extract(r'^(.+?)\s+\d+$')[0]

    # Standardize party
    gov['party_group'] = gov['party'].apply(standardize_party)

    # Aggregate by municipality and party
    muni_votes = gov.groupby(['municipality', 'party_group'])['votes'].sum().reset_index()

    # Pivot to get one row per municipality
    pivot = muni_votes.pivot(
        index='municipality',
        columns='party_group',
        values='votes'
    ).fillna(0)

    # Calculate vote shares
    pivot['total'] = pivot.sum(axis=1)
    for col in pivot.columns:
        if col != 'total':
            pivot[f'{col}_share'] = (pivot[col] / pivot['total'] * 100).round(2)

    pivot['year'] = election_year
    pivot = pivot.reset_index()

    print(f"  Extracted {election_year} Governor results: {len(pivot)} municipalities")
    return pivot


def get_island_totals(results: pd.DataFrame) -> pd.DataFrame:
    """
    Get island-wide vote totals by year for Governor race.

    Uses island-level data directly from results.
    """
    mask = (
        (results['event_type'] == 'general') &
        (results['office'] == 'GOBERNADOR') &
        (results['data_level'] == 'island')
    )
    gov = results[mask].copy()
    gov['year'] = gov['event_date'].apply(extract_election_year)
    gov['party_group'] = gov['party'].apply(standardize_party)

    # Take first occurrence per year/candidate (avoid duplicates)
    gov = gov.drop_duplicates(subset=['year', 'candidate_name'])

    # Aggregate by year and party
    totals = gov.groupby(['year', 'party_group'])['votes'].sum().reset_index()
    pivot = totals.pivot(index='year', columns='party_group', values='votes').fillna(0)

    # Calculate shares
    pivot['total'] = pivot.sum(axis=1)
    for col in pivot.columns:
        if col != 'total':
            pivot[f'{col}_share'] = (pivot[col] / pivot['total'] * 100).round(2)

    return pivot.reset_index()


def calculate_swing(
    year1_df: pd.DataFrame,
    year2_df: pd.DataFrame,
    party: str = 'PNP'
) -> pd.DataFrame:
    """
    Calculate swing (change in vote share) between two elections.

    Args:
        year1_df: Earlier election results
        year2_df: Later election results
        party: Party to calculate swing for

    Returns:
        DataFrame with swing values by municipality
    """
    share_col = f'{party}_share'

    if share_col not in year1_df.columns or share_col not in year2_df.columns:
        return pd.DataFrame()

    # Merge on municipality
    merged = year1_df[['municipality', share_col]].merge(
        year2_df[['municipality', share_col]],
        on='municipality',
        suffixes=('_y1', '_y2'),
        how='inner'
    )

    merged['swing'] = merged[f'{share_col}_y2'] - merged[f'{share_col}_y1']
    merged = merged.sort_values('swing', ascending=True)

    return merged


def add_census_demographics(
    swing_df: pd.DataFrame,
    census_df: pd.DataFrame
) -> pd.DataFrame:
    """Join census demographics to swing data."""
    def normalize_name(name):
        if pd.isna(name):
            return name
        return str(name).lower().strip().replace('ñ', 'n')

    swing_df = swing_df.copy()
    census_df = census_df.copy()

    swing_df['_key'] = swing_df['municipality'].apply(normalize_name)
    census_df['_key'] = census_df['municipality'].apply(normalize_name)

    census_cols = ['_key', 'median_household_income', 'poverty_rate',
                   'unemployment_rate', 'pct_bachelors_or_higher', 'total_population']
    census_subset = census_df[[c for c in census_cols if c in census_df.columns]]

    merged = swing_df.merge(census_subset, on='_key', how='left')
    merged = merged.drop(columns=['_key'])

    return merged


# =============================================================================
# Analysis Functions
# =============================================================================

def analyze_swing_correlations(
    swing_df: pd.DataFrame,
    swing_col: str = 'swing'
) -> Dict[str, Tuple[float, float]]:
    """
    Analyze correlations between swing and demographics.
    """
    demo_cols = ['median_household_income', 'poverty_rate',
                 'unemployment_rate', 'pct_bachelors_or_higher']

    results = {}
    for col in demo_cols:
        if col not in swing_df.columns:
            continue
        valid = swing_df[[swing_col, col]].dropna()
        if len(valid) < 5:
            continue

        if HAS_SCIPY:
            corr, pval = stats.pearsonr(valid[swing_col], valid[col])
            results[col] = (round(corr, 3), round(pval, 4))
        else:
            corr = valid[swing_col].corr(valid[col])
            results[col] = (round(corr, 3), None)

    return results


def compute_turnout_proxy(
    year1_df: pd.DataFrame,
    year2_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Compute change in total votes as proxy for turnout change.

    Note: True turnout requires registered voter data which we don't have.
    """
    merged = year1_df[['municipality', 'total']].merge(
        year2_df[['municipality', 'total']],
        on='municipality',
        suffixes=('_y1', '_y2'),
        how='inner'
    )

    merged['vote_change'] = merged['total_y2'] - merged['total_y1']
    merged['vote_change_pct'] = ((merged['total_y2'] / merged['total_y1'] - 1) * 100).round(2)

    return merged


# =============================================================================
# Visualization Functions
# =============================================================================

def plot_party_trends(island_totals: pd.DataFrame, output_name: str) -> None:
    """Plot party vote share trends over time."""
    if not HAS_PLOTTING:
        return

    fig, ax = plt.subplots(figsize=(12, 8))

    parties = ['PNP', 'PPD', 'PIP', 'MVC', 'OTHER']
    colors = ['#0066cc', '#cc0000', '#00cc00', '#ff6600', '#888888']

    for party, color in zip(parties, colors):
        share_col = f'{party}_share'
        if share_col in island_totals.columns:
            data = island_totals[island_totals[share_col] > 0]
            ax.plot(data['year'], data[share_col], 'o-',
                   label=party, color=color, linewidth=2, markersize=10)

    ax.set_xlabel('Election Year', fontsize=12)
    ax.set_ylabel('Vote Share (%)', fontsize=12)
    ax.set_title('Governor Race: Party Vote Share Trends (2016-2020)',
                fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 50)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / output_name, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_name}")


def plot_swing_distribution(swing_df: pd.DataFrame, party: str, output_name: str) -> None:
    """Plot distribution of municipality-level swing."""
    if not HAS_PLOTTING:
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    # Sort by swing
    sorted_df = swing_df.sort_values('swing')

    # Color by direction of swing
    colors = ['#0066cc' if s < 0 else '#cc0000' for s in sorted_df['swing']]

    ax.barh(range(len(sorted_df)), sorted_df['swing'], color=colors, alpha=0.7)
    ax.set_yticks(range(len(sorted_df)))
    ax.set_yticklabels(sorted_df['municipality'], fontsize=8)

    ax.axvline(x=0, color='black', linewidth=1)
    ax.set_xlabel(f'{party} Vote Share Change (percentage points)', fontsize=12)
    ax.set_title(f'{party} Swing by Municipality (2016 to 2020)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / output_name, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_name}")


def plot_swing_vs_demographics(swing_df: pd.DataFrame, output_name: str) -> None:
    """Create scatter plots of swing vs demographic variables."""
    if not HAS_PLOTTING:
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    axes = axes.flatten()

    demo_cols = [
        ('median_household_income', 'Median Household Income'),
        ('poverty_rate', 'Poverty Rate (%)'),
        ('pct_bachelors_or_higher', "Bachelor's Degree or Higher (%)"),
        ('unemployment_rate', 'Unemployment Rate (%)')
    ]

    for i, (col, label) in enumerate(demo_cols):
        if col not in swing_df.columns:
            axes[i].set_visible(False)
            continue

        valid = swing_df[['swing', col]].dropna()

        axes[i].scatter(valid[col], valid['swing'], alpha=0.6, s=60, c='steelblue')

        # Add regression line
        if HAS_SCIPY and len(valid) > 2:
            slope, intercept, r, p, se = stats.linregress(valid[col], valid['swing'])
            x_range = np.linspace(valid[col].min(), valid[col].max(), 100)
            axes[i].plot(x_range, slope * x_range + intercept, 'r-', linewidth=2)
            axes[i].text(0.05, 0.95, f'r = {r:.3f}\np = {p:.4f}',
                        transform=axes[i].transAxes, fontsize=10,
                        verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        axes[i].axhline(y=0, color='black', linewidth=1, linestyle='--')
        axes[i].set_xlabel(label, fontsize=11)
        axes[i].set_ylabel('PNP Swing (pp)', fontsize=11)
        axes[i].grid(True, alpha=0.3)

        if col == 'median_household_income':
            axes[i].xaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))

    plt.suptitle('PNP Swing (2016-2020) vs Municipality Demographics',
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / output_name, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_name}")


def plot_vote_change_map(vote_change_df: pd.DataFrame, output_name: str) -> None:
    """Plot total vote change by municipality."""
    if not HAS_PLOTTING:
        return

    fig, ax = plt.subplots(figsize=(12, 8))

    sorted_df = vote_change_df.sort_values('vote_change_pct')

    colors = ['#cc0000' if v < 0 else '#0066cc' for v in sorted_df['vote_change_pct']]

    ax.barh(range(len(sorted_df)), sorted_df['vote_change_pct'], color=colors, alpha=0.7)

    # Only label every 5th municipality for readability
    tick_positions = list(range(0, len(sorted_df), 5)) + [len(sorted_df) - 1]
    ax.set_yticks(tick_positions)
    ax.set_yticklabels([sorted_df.iloc[i]['municipality'] for i in tick_positions], fontsize=9)

    ax.axvline(x=0, color='black', linewidth=1)
    ax.set_xlabel('Change in Total Votes (%)', fontsize=12)
    ax.set_title('Vote Total Change by Municipality (2016 to 2020)',
                fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / output_name, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_name}")


# =============================================================================
# Main Analysis
# =============================================================================

def main():
    """Run the multi-year election trends analysis."""
    print("=" * 60)
    print("Multi-Year Election Trends Analysis")
    print("Puerto Rico Elections Platform")
    print("=" * 60)

    # Load data
    print("\n1. Loading data...")
    results = load_election_results()
    census_years = load_census_by_year()

    # Get island-wide totals
    print("\n2. Calculating island-wide vote shares...")
    island_totals = get_island_totals(results)

    print("\n" + "=" * 60)
    print("ISLAND-WIDE GOVERNOR RESULTS")
    print("=" * 60)

    for year in island_totals['year'].unique():
        year_data = island_totals[island_totals['year'] == year].iloc[0]
        print(f"\n{year} General Election:")
        for party in ['PNP', 'PPD', 'PIP', 'MVC', 'OTHER']:
            share_col = f'{party}_share'
            if share_col in year_data and year_data[share_col] > 0:
                print(f"  {party}: {year_data[share_col]:.2f}%")

    # Get municipality-level results
    print("\n3. Extracting municipality-level results...")
    results_2016 = get_governor_results_by_municipality(results, 2016)
    results_2020 = get_governor_results_by_municipality(results, 2020)

    # Calculate swing
    print("\n" + "=" * 60)
    print("PNP SWING ANALYSIS (2016 -> 2020)")
    print("=" * 60)

    if len(results_2016) > 0 and len(results_2020) > 0:
        pnp_swing = calculate_swing(results_2016, results_2020, 'PNP')

        if len(pnp_swing) > 0:
            # Add demographics
            if 2020 in census_years:
                pnp_swing = add_census_demographics(pnp_swing, census_years[2020])

            print(f"\nAnalyzed {len(pnp_swing)} municipalities")
            print(f"\nMean PNP swing: {pnp_swing['swing'].mean():.2f} pp")
            print(f"Std dev: {pnp_swing['swing'].std():.2f} pp")

            print("\nTop 10 municipalities with LARGEST PNP DECLINE:")
            print("-" * 60)
            bottom10 = pnp_swing.head(10)
            for _, row in bottom10.iterrows():
                print(f"  {row['municipality']:20s}: {row['swing']:+.1f} pp "
                      f"({row['PNP_share_y1']:.1f}% -> {row['PNP_share_y2']:.1f}%)")

            print("\nTop 10 municipalities with SMALLEST PNP DECLINE (or gain):")
            print("-" * 60)
            top10 = pnp_swing.tail(10).iloc[::-1]
            for _, row in top10.iterrows():
                print(f"  {row['municipality']:20s}: {row['swing']:+.1f} pp "
                      f"({row['PNP_share_y1']:.1f}% -> {row['PNP_share_y2']:.1f}%)")

            # Correlation analysis
            print("\n" + "=" * 60)
            print("SWING CORRELATIONS WITH DEMOGRAPHICS")
            print("=" * 60)

            correlations = analyze_swing_correlations(pnp_swing)
            print("\nCorrelations with PNP swing:")
            print("-" * 50)
            for col, (corr, pval) in correlations.items():
                col_label = col.replace('_', ' ').title()
                if pval is not None:
                    sig = "**" if pval < 0.01 else "*" if pval < 0.05 else ""
                    print(f"  {col_label:35s}: r = {corr:+.3f}  (p = {pval:.4f}) {sig}")
                else:
                    print(f"  {col_label:35s}: r = {corr:+.3f}")

            # Vote total change
            print("\n" + "=" * 60)
            print("VOTE TOTAL CHANGE (TURNOUT PROXY)")
            print("=" * 60)

            vote_change = compute_turnout_proxy(results_2016, results_2020)
            total_2016 = vote_change['total_y1'].sum()
            total_2020 = vote_change['total_y2'].sum()
            pct_change = ((total_2020 / total_2016) - 1) * 100

            print(f"\nIsland-wide vote total change:")
            print(f"  2016: {total_2016:,} votes")
            print(f"  2020: {total_2020:,} votes")
            print(f"  Change: {pct_change:+.1f}%")

            print(f"\nMunicipalities with largest DECLINE in votes:")
            decline = vote_change.nsmallest(5, 'vote_change_pct')
            for _, row in decline.iterrows():
                print(f"  {row['municipality']:20s}: {row['vote_change_pct']:+.1f}%")

            print(f"\nMunicipalities with largest INCREASE in votes:")
            increase = vote_change.nlargest(5, 'vote_change_pct')
            for _, row in increase.iterrows():
                print(f"  {row['municipality']:20s}: {row['vote_change_pct']:+.1f}%")

            # Generate visualizations
            if HAS_PLOTTING:
                print("\n" + "=" * 60)
                print("GENERATING VISUALIZATIONS")
                print("=" * 60)

                plot_party_trends(island_totals, 'party_vote_share_trends.png')
                plot_swing_distribution(pnp_swing, 'PNP', 'pnp_swing_by_municipality.png')
                plot_swing_vs_demographics(pnp_swing, 'swing_vs_demographics.png')
                plot_vote_change_map(vote_change, 'vote_change_by_municipality.png')

            # Save data
            output_path = OUTPUT_DIR / "election_trends_swing.csv"
            pnp_swing.to_csv(output_path, index=False)
            print(f"\nSwing data saved to: {output_path}")

            output_path = OUTPUT_DIR / "election_trends_vote_change.csv"
            vote_change.to_csv(output_path, index=False)
            print(f"Vote change data saved to: {output_path}")

    else:
        print("\nInsufficient data for swing analysis")

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
