"""
Precinct-to-Census Geographic Crosswalk for Puerto Rico

Downloads MGGG precinct shapefiles and creates crosswalk tables to link
electoral precincts to census geographic units.

USAGE:
    python precinct_crosswalk.py --download   # Download MGGG shapefiles
    python precinct_crosswalk.py --crosswalk  # Create crosswalk tables
    python precinct_crosswalk.py --all        # Do both

Requirements:
    - geopandas
    - requests

Data Sources:
    - MGGG PR-shapefiles: https://github.com/mggg-states/PR-shapefiles
    - Precincts digitized from CEE PDF maps with 2010 Census data prorated
"""

import argparse
import json
import logging
import os
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MGGG shapefiles URL
MGGG_PR_URL = "https://github.com/mggg-states/PR-shapefiles/raw/main/PR.zip"

# Default paths
DEFAULT_SHAPES_DIR = Path(__file__).parent.parent / "data" / "shapes"
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "data" / "crosswalks"


def download_mggg_shapefiles(output_dir: Path) -> Path:
    """
    Download MGGG Puerto Rico precinct shapefiles.

    Args:
        output_dir: Directory to save shapefiles

    Returns:
        Path to extracted shapefile directory
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    zip_path = output_dir / "PR.zip"

    # Check if already downloaded (shapefiles directly in output_dir)
    if any(output_dir.glob("PR.shp")):
        logger.info(f"Shapefiles already exist at {output_dir}")
        return output_dir

    logger.info(f"Downloading MGGG PR shapefiles from {MGGG_PR_URL}")

    response = requests.get(MGGG_PR_URL, stream=True, timeout=120)
    response.raise_for_status()

    # Save and extract
    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    logger.info(f"Downloaded {zip_path.stat().st_size / 1024 / 1024:.1f} MB")

    # Extract
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(output_dir)

    logger.info(f"Extracted to {output_dir}")

    return output_dir


def load_precinct_shapefile(shapes_dir: Path) -> "geopandas.GeoDataFrame":
    """
    Load the MGGG precinct shapefile.

    Args:
        shapes_dir: Directory containing extracted shapefiles

    Returns:
        GeoDataFrame with precinct boundaries
    """
    try:
        import geopandas as gpd
    except ImportError:
        raise ImportError(
            "geopandas is required for shapefile operations. "
            "Install with: pip install geopandas"
        )

    # Find the shapefile - check multiple possible locations
    shp_files = list(shapes_dir.glob("*.shp"))
    if not shp_files:
        # Check subdirectory
        shp_files = list(shapes_dir.glob("*/*.shp"))
    if not shp_files:
        # Check parent directory (in case extract_dir is wrong)
        shp_files = list(shapes_dir.parent.glob("*.shp"))

    if not shp_files:
        raise FileNotFoundError(f"No shapefiles found in {shapes_dir} or parent")

    shp_path = shp_files[0]
    logger.info(f"Loading shapefile: {shp_path}")

    gdf = gpd.read_file(shp_path)
    logger.info(f"Loaded {len(gdf)} precincts with columns: {list(gdf.columns)}")

    return gdf


def create_precinct_municipality_crosswalk(gdf: "geopandas.GeoDataFrame") -> pd.DataFrame:
    """
    Create crosswalk mapping precincts to municipalities.

    The MGGG shapefile includes municipality information.

    Args:
        gdf: GeoDataFrame with precinct data

    Returns:
        DataFrame with precinct-municipality mapping
    """
    result = pd.DataFrame()

    # MGGG PR shapefile column mapping (known structure)
    col_map = {
        # Geographic identifiers
        "precinct_id": ["Precinct", "PREC", "PRECINCT", "precinct", "Code"],
        "precinct_code": ["Code"],
        "municipality": ["Municipio", "MUN", "MUNICIPALITY"],
        "municipality_fips": ["MUNIFP", "COUNTYFP", "COUNTY"],
        "state_fips": ["STATEFP", "STATE"],
        # Legislative districts
        "senate_district": ["SEND"],
        "senate_district_name": ["SEND-name"],
        "house_district": ["HDIST", "SREP", "REP"],
    }

    for target_col, source_cols in col_map.items():
        for src in source_cols:
            if src in gdf.columns:
                result[target_col] = gdf[src]
                break

    # Build full GEOID if we have state and municipality FIPS
    if "state_fips" in result.columns and "municipality_fips" in result.columns:
        result["municipality_geoid"] = result["state_fips"].astype(str) + result["municipality_fips"].astype(str).str.zfill(3)

    # Add geometry centroid for reference
    if hasattr(gdf, "geometry") and gdf.geometry is not None:
        centroids = gdf.geometry.centroid
        result["centroid_lat"] = centroids.y
        result["centroid_lon"] = centroids.x

    # Add population data
    if "TOTPOP" in gdf.columns:
        result["population_2010"] = gdf["TOTPOP"]
    if "VAP" in gdf.columns:
        result["voting_age_pop_2010"] = gdf["VAP"]

    logger.info(f"Created crosswalk with {len(result)} precincts and columns: {list(result.columns)}")

    return result


def create_detailed_crosswalk(gdf: "geopandas.GeoDataFrame") -> pd.DataFrame:
    """
    Create detailed crosswalk with all available demographic data.

    Args:
        gdf: GeoDataFrame with precinct data

    Returns:
        DataFrame with full crosswalk including demographics
    """
    # Include all columns except geometry
    non_geom_cols = [c for c in gdf.columns if c != "geometry"]
    result = gdf[non_geom_cols].copy()

    # Add centroids
    if hasattr(gdf, "geometry"):
        centroids = gdf.geometry.centroid
        result["centroid_lat"] = centroids.y
        result["centroid_lon"] = centroids.x

    return result


def save_crosswalk(df: pd.DataFrame, output_dir: Path, name: str) -> None:
    """Save crosswalk in multiple formats."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # CSV
    csv_path = output_dir / f"{name}.csv"
    df.to_csv(csv_path, index=False)
    logger.info(f"Saved CSV: {csv_path}")

    # Parquet
    parquet_path = output_dir / f"{name}.parquet"
    df.to_parquet(parquet_path, index=False)
    logger.info(f"Saved Parquet: {parquet_path}")

    # JSON (without geometry)
    json_path = output_dir / f"{name}.json"
    df.to_json(json_path, orient="records", indent=2)
    logger.info(f"Saved JSON: {json_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Create precinct-to-census crosswalk for Puerto Rico"
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download MGGG shapefiles"
    )
    parser.add_argument(
        "--crosswalk",
        action="store_true",
        help="Create crosswalk tables from existing shapefiles"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download and create crosswalk"
    )
    parser.add_argument(
        "--shapes-dir",
        type=str,
        default=None,
        help=f"Directory for shapefiles (default: {DEFAULT_SHAPES_DIR})"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help=f"Output directory for crosswalks (default: {DEFAULT_OUTPUT_DIR})"
    )

    args = parser.parse_args()

    shapes_dir = Path(args.shapes_dir) if args.shapes_dir else DEFAULT_SHAPES_DIR
    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR

    if args.all:
        args.download = True
        args.crosswalk = True

    if not (args.download or args.crosswalk):
        parser.print_help()
        return

    # Download shapefiles
    if args.download:
        extract_dir = download_mggg_shapefiles(shapes_dir)
    else:
        extract_dir = shapes_dir

    # Create crosswalk
    if args.crosswalk:
        logger.info("Creating crosswalk tables...")

        gdf = load_precinct_shapefile(extract_dir)

        # Basic precinct-municipality crosswalk
        basic_crosswalk = create_precinct_municipality_crosswalk(gdf)
        save_crosswalk(basic_crosswalk, output_dir, "precinct_municipality_crosswalk")

        # Detailed crosswalk with all data
        detailed_crosswalk = create_detailed_crosswalk(gdf)
        save_crosswalk(detailed_crosswalk, output_dir, "precinct_census_crosswalk")

        # Summary
        print("\n" + "="*60)
        print("Precinct Crosswalk Summary")
        print("="*60)
        print(f"Total precincts: {len(gdf)}")
        print(f"Columns available: {list(gdf.columns)}")
        if "MUN" in gdf.columns:
            print(f"Municipalities covered: {gdf['MUN'].nunique()}")
        print(f"\nCrosswalks saved to: {output_dir}")
        print("="*60)


if __name__ == "__main__":
    main()
