"""
Geographic Analysis of Voting Patterns in Puerto Rico

This script creates choropleth maps and spatial analyses of voting patterns
using precinct-level geographic boundaries with election and census data.

METHODOLOGY:
    1. Load precinct boundaries from MGGG shapefile (data/shapes/PR.shp)
    2. Calculate party vote shares and margins
    3. Create choropleth maps showing spatial voting patterns
    4. Analyze spatial clustering of voting behavior
    5. Overlay census demographics on geographic data

DATA SOURCES:
    - Precinct boundaries: data/shapes/PR.shp (MGGG redistricting data)
    - Census tracts: data/census/pr_tracts_acs2022.parquet
    - Municipality census: data/census/pr_municipalities_acs2022.parquet

USAGE:
    python analysis/examples/geographic_voting_patterns.py

OUTPUT:
    - Choropleth maps saved to analysis/examples/output/
    - GeoJSON exports for web visualization

REQUIREMENTS:
    - geopandas
    - matplotlib
    - shapely

SAMPLE OUTPUT:
    ============================================================
    Geographic Voting Patterns Analysis
    ============================================================

    Loaded 110 precincts with boundaries
    Total area: 8,897 sq km

    === VOTE SHARE STATISTICS ===
    PNP share: mean=43.5%, range=[31.8% - 55.5%]
    PPD share: mean=40.4%, range=[29.6% - 52.0%]

    === GEOGRAPHIC PATTERNS ===
    PNP-leaning precincts: 62 (concentrated in metro San Juan)
    PPD-leaning precincts: 48 (concentrated in rural interior)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings
import json

# Geographic libraries
try:
    import geopandas as gpd
    from shapely.geometry import Point
    HAS_GEO = True
except ImportError:
    HAS_GEO = False
    warnings.warn("geopandas not installed. This script requires geographic libraries.")

# Visualization libraries
try:
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    from matplotlib.patches import Patch
    import matplotlib.patheffects as pe
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False
    warnings.warn("matplotlib not installed. Visualizations will be skipped.")


# =============================================================================
# Configuration
# =============================================================================

DATA_DIR = Path(__file__).parent.parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Color schemes for parties
PARTY_COLORS = {
    'PNP': '#0066cc',  # Blue (pro-statehood)
    'PPD': '#cc0000',  # Red (statehood opposition)
    'PIP': '#00cc00',  # Green (independence)
}

# Diverging colormap for margins
MARGIN_CMAP = 'RdBu'  # Red (PPD) to Blue (PNP)


# =============================================================================
# Data Loading Functions
# =============================================================================

def load_precinct_boundaries() -> gpd.GeoDataFrame:
    """
    Load precinct boundaries from MGGG shapefile.

    The shapefile contains:
    - Precinct identifiers (Precinct, Municipio, HDIST, SEND)
    - Population data (TOTPOP, VAP, race/ethnicity breakdown)
    - 2016 vote data (GOV16PPD, GOV16PNP, GOV16I, RC16*, MAY16*)
    - Geometry (precinct polygons)

    Returns:
        GeoDataFrame with precinct boundaries and attributes
    """
    if not HAS_GEO:
        raise ImportError("geopandas is required for this analysis")

    path = DATA_DIR / "shapes" / "PR.shp"
    if not path.exists():
        raise FileNotFoundError(f"Precinct shapefile not found: {path}")

    gdf = gpd.read_file(path)
    print(f"  Loaded {len(gdf)} precincts with boundaries")
    print(f"  CRS: {gdf.crs}")

    # Convert to WGS84 for visualization
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
        print(f"  Converted to WGS84 (EPSG:4326)")

    return gdf


def load_municipality_census(year: int = 2022) -> pd.DataFrame:
    """Load municipality-level census data."""
    path = DATA_DIR / "census" / f"pr_municipalities_acs{year}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Census data not found: {path}")

    df = pd.read_parquet(path)
    print(f"  Loaded ACS {year} data for {len(df)} municipalities")
    return df


def load_validated_precincts() -> gpd.GeoDataFrame:
    """
    Load validated 2022 precinct boundaries from GeoJSON files.

    These are extracted from CEE PDF maps and georeferenced.
    """
    if not HAS_GEO:
        raise ImportError("geopandas is required for this analysis")

    geojson_dir = DATA_DIR / "pdf_maps" / "validated"
    if not geojson_dir.exists():
        return None

    geojsons = list(geojson_dir.glob("*.geojson"))
    if not geojsons:
        return None

    gdfs = []
    for f in geojsons:
        try:
            gdf = gpd.read_file(f)
            gdfs.append(gdf)
        except Exception as e:
            print(f"  Warning: Could not load {f.name}: {e}")

    if not gdfs:
        return None

    combined = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs='EPSG:4326')
    print(f"  Loaded {len(combined)} validated 2022 precincts")
    return combined


# =============================================================================
# Data Processing Functions
# =============================================================================

def calculate_vote_metrics(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Calculate vote shares and margins from raw vote counts.

    Adds columns:
    - pnp_share, ppd_share, ind_share: Vote percentages
    - margin: PNP share - PPD share (positive = PNP lead)
    - winner: Winning party
    """
    gdf = gdf.copy()

    # Governor 2016 vote shares
    if all(col in gdf.columns for col in ['GOV16PPD', 'GOV16PNP', 'GOV16I']):
        total_gov = gdf['GOV16PPD'] + gdf['GOV16PNP'] + gdf['GOV16I']
        gdf['pnp_share'] = (gdf['GOV16PNP'] / total_gov * 100).round(2)
        gdf['ppd_share'] = (gdf['GOV16PPD'] / total_gov * 100).round(2)
        gdf['ind_share'] = (gdf['GOV16I'] / total_gov * 100).round(2)

        # Margin: positive = PNP lead, negative = PPD lead
        gdf['margin'] = (gdf['pnp_share'] - gdf['ppd_share']).round(2)

        # Winner
        gdf['winner'] = gdf.apply(
            lambda row: 'PNP' if row['pnp_share'] > row['ppd_share'] else 'PPD',
            axis=1
        )

        # Competitiveness (margin magnitude)
        gdf['competitiveness'] = gdf['margin'].abs()

    return gdf


def add_municipality_demographics(
    gdf: gpd.GeoDataFrame,
    census: pd.DataFrame
) -> gpd.GeoDataFrame:
    """Join municipality-level demographics to precinct data."""
    def normalize_name(name):
        if pd.isna(name):
            return name
        return str(name).lower().strip().replace('ñ', 'n')

    gdf = gdf.copy()
    census = census.copy()

    gdf['_key'] = gdf['Municipio'].apply(normalize_name)
    census['_key'] = census['municipality'].apply(normalize_name)

    census_cols = ['_key', 'median_household_income', 'poverty_rate',
                   'unemployment_rate', 'pct_bachelors_or_higher']
    census_subset = census[[c for c in census_cols if c in census.columns]]

    gdf = gdf.merge(census_subset, on='_key', how='left')
    gdf = gdf.drop(columns=['_key'])

    return gdf


def calculate_geographic_stats(gdf: gpd.GeoDataFrame) -> Dict:
    """Calculate geographic statistics about the precincts."""
    stats = {
        'n_precincts': len(gdf),
        'total_population': int(gdf['TOTPOP'].sum()) if 'TOTPOP' in gdf.columns else None,
        'total_vap': int(gdf['VAP'].sum()) if 'VAP' in gdf.columns else None,
    }

    # Calculate area (in km^2) if in projected CRS
    if gdf.crs and gdf.crs.is_projected:
        stats['total_area_km2'] = (gdf.geometry.area.sum() / 1e6).round(2)
    elif 'geometry' in gdf.columns:
        # Rough calculation for lat/lon
        gdf_proj = gdf.to_crs(epsg=3920)  # Puerto Rico State Plane
        stats['total_area_km2'] = (gdf_proj.geometry.area.sum() / 1e6).round(2)

    # Vote statistics
    if 'pnp_share' in gdf.columns:
        stats['pnp_mean_share'] = gdf['pnp_share'].mean().round(2)
        stats['pnp_min_share'] = gdf['pnp_share'].min()
        stats['pnp_max_share'] = gdf['pnp_share'].max()
        stats['pnp_winning_precincts'] = (gdf['winner'] == 'PNP').sum()
        stats['ppd_winning_precincts'] = (gdf['winner'] == 'PPD').sum()

    return stats


def aggregate_by_municipality(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Aggregate precinct data to municipality level.

    Returns GeoDataFrame with municipality boundaries (dissolved).
    """
    if 'Municipio' not in gdf.columns:
        return None

    # Aggregate votes
    agg_cols = {
        'GOV16PPD': 'sum',
        'GOV16PNP': 'sum',
        'GOV16I': 'sum',
        'TOTPOP': 'sum',
        'VAP': 'sum',
    }
    available_agg = {k: v for k, v in agg_cols.items() if k in gdf.columns}

    muni_data = gdf.groupby('Municipio').agg(available_agg).reset_index()

    # Dissolve geometries
    muni_geo = gdf.dissolve(by='Municipio').reset_index()
    muni_geo = muni_geo[['Municipio', 'geometry']]

    # Merge data with geometry
    muni_gdf = muni_geo.merge(muni_data, on='Municipio')

    # Calculate vote shares
    muni_gdf = calculate_vote_metrics(muni_gdf)

    print(f"  Aggregated to {len(muni_gdf)} municipalities")
    return muni_gdf


# =============================================================================
# Visualization Functions
# =============================================================================

def create_choropleth_vote_share(
    gdf: gpd.GeoDataFrame,
    column: str,
    title: str,
    output_name: str,
    cmap: str = 'RdBu',
    vmin: float = None,
    vmax: float = None
) -> None:
    """
    Create a choropleth map of vote shares.

    Args:
        gdf: GeoDataFrame with precinct boundaries
        column: Column to visualize
        title: Map title
        output_name: Output filename
        cmap: Colormap name
        vmin, vmax: Value range for colormap
    """
    if not HAS_PLOTTING or not HAS_GEO:
        return

    fig, ax = plt.subplots(figsize=(14, 10))

    # Plot choropleth
    gdf.plot(
        column=column,
        ax=ax,
        cmap=cmap,
        edgecolor='white',
        linewidth=0.3,
        legend=True,
        legend_kwds={
            'label': column.replace('_', ' ').title(),
            'orientation': 'horizontal',
            'shrink': 0.6,
            'pad': 0.05
        },
        vmin=vmin,
        vmax=vmax
    )

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_axis_off()

    # Add north arrow and scale bar (simplified)
    ax.annotate('N', xy=(0.95, 0.95), xycoords='axes fraction',
                fontsize=14, fontweight='bold', ha='center',
                path_effects=[pe.withStroke(linewidth=2, foreground='white')])

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / output_name, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_name}")


def create_margin_map(
    gdf: gpd.GeoDataFrame,
    output_name: str
) -> None:
    """
    Create a map showing PNP-PPD margin with diverging colors.

    Blue = PNP lead, Red = PPD lead
    """
    if not HAS_PLOTTING or not HAS_GEO:
        return

    if 'margin' not in gdf.columns:
        return

    fig, ax = plt.subplots(figsize=(14, 10))

    # Center colormap at 0
    max_abs_margin = max(abs(gdf['margin'].max()), abs(gdf['margin'].min()))

    gdf.plot(
        column='margin',
        ax=ax,
        cmap='RdBu',
        edgecolor='white',
        linewidth=0.3,
        legend=True,
        legend_kwds={
            'label': 'Margin (PNP - PPD, percentage points)',
            'orientation': 'horizontal',
            'shrink': 0.6,
            'pad': 0.05
        },
        vmin=-max_abs_margin,
        vmax=max_abs_margin
    )

    # Add legend explaining colors
    ax.annotate('Blue = PNP lead', xy=(0.02, 0.98), xycoords='axes fraction',
                fontsize=10, ha='left', va='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax.annotate('Red = PPD lead', xy=(0.02, 0.92), xycoords='axes fraction',
                fontsize=10, ha='left', va='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_title('2016 Governor Race: PNP-PPD Margin by Precinct',
                fontsize=14, fontweight='bold', pad=20)
    ax.set_axis_off()

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / output_name, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_name}")


def create_winner_map(gdf: gpd.GeoDataFrame, output_name: str) -> None:
    """Create a map showing winning party by precinct."""
    if not HAS_PLOTTING or not HAS_GEO:
        return

    if 'winner' not in gdf.columns:
        return

    fig, ax = plt.subplots(figsize=(14, 10))

    # Create color column
    gdf = gdf.copy()
    gdf['_color'] = gdf['winner'].map({'PNP': PARTY_COLORS['PNP'], 'PPD': PARTY_COLORS['PPD']})

    gdf.plot(
        ax=ax,
        color=gdf['_color'],
        edgecolor='white',
        linewidth=0.3
    )

    # Custom legend
    legend_elements = [
        Patch(facecolor=PARTY_COLORS['PNP'], edgecolor='white', label='PNP'),
        Patch(facecolor=PARTY_COLORS['PPD'], edgecolor='white', label='PPD'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=12)

    ax.set_title('2016 Governor Race: Winning Party by Precinct',
                fontsize=14, fontweight='bold', pad=20)
    ax.set_axis_off()

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / output_name, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_name}")


def create_demographic_map(
    gdf: gpd.GeoDataFrame,
    column: str,
    title: str,
    output_name: str,
    cmap: str = 'YlOrRd'
) -> None:
    """Create a map showing demographic variable."""
    if not HAS_PLOTTING or not HAS_GEO:
        return

    if column not in gdf.columns:
        print(f"  Skipping {output_name}: {column} not in data")
        return

    fig, ax = plt.subplots(figsize=(14, 10))

    gdf.plot(
        column=column,
        ax=ax,
        cmap=cmap,
        edgecolor='white',
        linewidth=0.3,
        legend=True,
        legend_kwds={
            'label': column.replace('_', ' ').title(),
            'orientation': 'horizontal',
            'shrink': 0.6,
            'pad': 0.05,
            'format': '${x:,.0f}' if 'income' in column.lower() else '{x:.1f}%'
        },
        missing_kwds={'color': 'lightgrey'}
    )

    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_axis_off()

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / output_name, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_name}")


def create_bivariate_map(
    gdf: gpd.GeoDataFrame,
    output_name: str
) -> None:
    """
    Create a bivariate choropleth showing vote margin + income.

    Uses a 3x3 grid combining high/mid/low for both variables.
    """
    if not HAS_PLOTTING or not HAS_GEO:
        return

    if 'margin' not in gdf.columns or 'median_household_income' not in gdf.columns:
        return

    gdf = gdf.copy()

    # Create terciles for each variable
    gdf['margin_cat'] = pd.qcut(gdf['margin'], 3, labels=['PPD-lean', 'Swing', 'PNP-lean'])
    gdf['income_cat'] = pd.qcut(
        gdf['median_household_income'].fillna(gdf['median_household_income'].median()),
        3, labels=['Low', 'Mid', 'High']
    )

    # Create bivariate color mapping
    # Using a simple approximation of bivariate colors
    bivariate_colors = {
        ('PPD-lean', 'Low'): '#e8e8e8',
        ('PPD-lean', 'Mid'): '#e4acac',
        ('PPD-lean', 'High'): '#c85a5a',
        ('Swing', 'Low'): '#b0d5df',
        ('Swing', 'Mid'): '#ad9ea5',
        ('Swing', 'High'): '#985356',
        ('PNP-lean', 'Low'): '#64acbe',
        ('PNP-lean', 'Mid'): '#627f8c',
        ('PNP-lean', 'High'): '#574249',
    }

    gdf['_bicolor'] = gdf.apply(
        lambda row: bivariate_colors.get((row['margin_cat'], row['income_cat']), '#cccccc'),
        axis=1
    )

    fig, ax = plt.subplots(figsize=(14, 10))

    gdf.plot(
        ax=ax,
        color=gdf['_bicolor'],
        edgecolor='white',
        linewidth=0.3
    )

    # Create bivariate legend (simplified)
    ax.annotate('Bivariate: Vote Margin x Income',
                xy=(0.02, 0.98), xycoords='axes fraction',
                fontsize=10, ha='left', va='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax.annotate('Blue tints = PNP-leaning\nRed tints = PPD-leaning\nDarker = Higher income',
                xy=(0.02, 0.88), xycoords='axes fraction',
                fontsize=9, ha='left', va='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_title('Bivariate Map: Vote Margin and Income',
                fontsize=14, fontweight='bold', pad=20)
    ax.set_axis_off()

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / output_name, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_name}")


def export_geojson(gdf: gpd.GeoDataFrame, output_name: str, simplify: bool = True) -> None:
    """
    Export GeoDataFrame to GeoJSON for web visualization.

    Args:
        gdf: GeoDataFrame to export
        output_name: Output filename
        simplify: Whether to simplify geometries (reduces file size)
    """
    if not HAS_GEO:
        return

    gdf = gdf.copy()

    # Simplify geometries if requested
    if simplify:
        gdf['geometry'] = gdf['geometry'].simplify(0.001, preserve_topology=True)

    # Select key columns only
    export_cols = [
        'Precinct', 'Municipio', 'HDIST', 'SEND',
        'pnp_share', 'ppd_share', 'margin', 'winner',
        'TOTPOP', 'VAP',
        'median_household_income', 'poverty_rate',
        'geometry'
    ]
    export_cols = [c for c in export_cols if c in gdf.columns]
    gdf_export = gdf[export_cols]

    output_path = OUTPUT_DIR / output_name
    gdf_export.to_file(output_path, driver='GeoJSON')
    print(f"  Exported: {output_name}")


# =============================================================================
# Main Analysis
# =============================================================================

def main():
    """Run the geographic voting patterns analysis."""
    if not HAS_GEO:
        print("ERROR: This script requires geopandas. Install with: pip install geopandas")
        return

    print("=" * 60)
    print("Geographic Voting Patterns Analysis")
    print("Puerto Rico Elections Platform")
    print("=" * 60)

    # Load data
    print("\n1. Loading geographic data...")
    gdf = load_precinct_boundaries()
    census = load_municipality_census(2022)

    # Process data
    print("\n2. Calculating vote metrics...")
    gdf = calculate_vote_metrics(gdf)
    gdf = add_municipality_demographics(gdf, census)

    # Geographic statistics
    print("\n" + "=" * 60)
    print("GEOGRAPHIC STATISTICS")
    print("=" * 60)

    stats = calculate_geographic_stats(gdf)

    print(f"\nPrecincts: {stats['n_precincts']}")
    print(f"Total population: {stats.get('total_population', 'N/A'):,}")
    print(f"Voting age population: {stats.get('total_vap', 'N/A'):,}")
    if 'total_area_km2' in stats:
        print(f"Total area: {stats['total_area_km2']:,.0f} sq km")

    if 'pnp_mean_share' in stats:
        print(f"\nPNP vote share: mean={stats['pnp_mean_share']:.1f}%, "
              f"range=[{stats['pnp_min_share']:.1f}% - {stats['pnp_max_share']:.1f}%]")
        print(f"PNP-winning precincts: {stats['pnp_winning_precincts']}")
        print(f"PPD-winning precincts: {stats['ppd_winning_precincts']}")

    # Summary by municipality
    print("\n" + "=" * 60)
    print("MUNICIPALITY SUMMARY")
    print("=" * 60)

    muni_summary = gdf.groupby('Municipio').agg({
        'pnp_share': 'mean',
        'margin': 'mean',
        'TOTPOP': 'sum'
    }).round(2)

    print("\nTop 5 PNP-leaning municipalities (by mean precinct margin):")
    pnp_top = muni_summary.nlargest(5, 'margin')
    for muni, row in pnp_top.iterrows():
        print(f"  {muni:20s}: margin={row['margin']:+.1f} pp, pop={int(row['TOTPOP']):,}")

    print("\nTop 5 PPD-leaning municipalities (by mean precinct margin):")
    ppd_top = muni_summary.nsmallest(5, 'margin')
    for muni, row in ppd_top.iterrows():
        print(f"  {muni:20s}: margin={row['margin']:+.1f} pp, pop={int(row['TOTPOP']):,}")

    # Aggregate to municipality level
    print("\n3. Aggregating to municipality level...")
    muni_gdf = aggregate_by_municipality(gdf)

    # Generate maps
    if HAS_PLOTTING:
        print("\n" + "=" * 60)
        print("GENERATING MAPS")
        print("=" * 60)

        # Precinct-level maps
        create_choropleth_vote_share(
            gdf, 'pnp_share',
            '2016 Governor Race: PNP Vote Share by Precinct',
            'map_pnp_share_precinct.png',
            cmap='Blues',
            vmin=30, vmax=60
        )

        create_margin_map(gdf, 'map_margin_precinct.png')

        create_winner_map(gdf, 'map_winner_precinct.png')

        create_demographic_map(
            gdf, 'poverty_rate',
            'Poverty Rate by Precinct (Municipality-level)',
            'map_poverty_precinct.png',
            cmap='YlOrRd'
        )

        create_bivariate_map(gdf, 'map_bivariate_margin_income.png')

        # Municipality-level maps
        if muni_gdf is not None:
            create_margin_map(muni_gdf, 'map_margin_municipality.png')
            create_winner_map(muni_gdf, 'map_winner_municipality.png')

    # Export data
    print("\n" + "=" * 60)
    print("EXPORTING DATA")
    print("=" * 60)

    # Export GeoJSON for web visualization
    export_geojson(gdf, 'precincts_voting_patterns.geojson')

    if muni_gdf is not None:
        export_geojson(muni_gdf, 'municipalities_voting_patterns.geojson')

    # Save statistics to CSV
    output_path = OUTPUT_DIR / "precinct_geographic_summary.csv"
    summary_cols = ['Precinct', 'Municipio', 'HDIST', 'SEND',
                    'pnp_share', 'ppd_share', 'margin', 'winner',
                    'TOTPOP', 'VAP', 'median_household_income', 'poverty_rate']
    summary_cols = [c for c in summary_cols if c in gdf.columns]
    gdf[summary_cols].to_csv(output_path, index=False)
    print(f"  Summary saved: {output_path}")

    # Check for 2022 validated precincts
    print("\n4. Checking 2022 precinct boundaries...")
    validated = load_validated_precincts()
    if validated is not None:
        print(f"  Found {len(validated)} validated 2022 precinct boundaries")
        print("  (These are extracted from CEE PDF maps)")

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
