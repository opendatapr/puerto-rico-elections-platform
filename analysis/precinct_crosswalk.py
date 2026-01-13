"""
Precinct-to-Census Geographic Crosswalk for Puerto Rico

Downloads MGGG precinct shapefiles and creates crosswalk tables to link
electoral precincts to census geographic units.

USAGE:
    python precinct_crosswalk.py --download   # Download MGGG shapefiles
    python precinct_crosswalk.py --crosswalk  # Create crosswalk tables (2016)
    python precinct_crosswalk.py --crosswalk-2022  # Create 2022 crosswalk from PDFs
    python precinct_crosswalk.py --all        # Do everything

Requirements:
    - geopandas
    - requests
    - shapely

Data Sources:
    - 2016: MGGG PR-shapefiles (https://github.com/mggg-states/PR-shapefiles)
    - 2022: CEE PDF maps extracted via pdf_extractor.py and pdf_georeferencer.py
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
DEFAULT_PDF_VALIDATED_DIR = Path(__file__).parent.parent / "data" / "pdf_maps" / "validated"
DEFAULT_CENTROIDS_PATH = Path(__file__).parent.parent / "data" / "pdf_maps" / "pr_municipality_centroids.json"


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


def load_2022_validated_geojson(validated_dir: Path) -> "geopandas.GeoDataFrame":
    """
    Load validated 2022 district boundaries from GeoJSON files.

    Args:
        validated_dir: Directory containing validated GeoJSON files

    Returns:
        GeoDataFrame with all 2022 district/precinct boundaries
    """
    try:
        import geopandas as gpd
        from shapely.geometry import shape
    except ImportError:
        raise ImportError(
            "geopandas and shapely required. Install with: pip install geopandas shapely"
        )

    all_features = []

    for geojson_path in sorted(validated_dir.glob("*_validated.geojson")):
        district = int(geojson_path.stem.split('_')[1])

        with open(geojson_path) as f:
            data = json.load(f)

        for i, feature in enumerate(data['features']):
            props = feature.get('properties', {})
            props['district'] = district
            props['precinct_index'] = i
            props['source_file'] = geojson_path.name

            all_features.append({
                'geometry': shape(feature['geometry']),
                **props
            })

    gdf = gpd.GeoDataFrame(all_features, crs="EPSG:4326")
    logger.info(f"Loaded {len(gdf)} precincts from 2022 validated GeoJSON files")

    return gdf


def match_precinct_to_municipality(
    gdf: "geopandas.GeoDataFrame",
    centroids_path: Path
) -> "geopandas.GeoDataFrame":
    """
    Match 2022 precincts to municipalities using spatial containment.

    Args:
        gdf: GeoDataFrame with precinct boundaries
        centroids_path: Path to municipality centroids JSON

    Returns:
        GeoDataFrame with municipality assignments
    """
    from shapely.geometry import Point

    # Load municipality centroids
    with open(centroids_path) as f:
        centroids = json.load(f)

    # For each precinct, find which municipality centroid it contains or is closest to
    municipalities = []

    for idx, row in gdf.iterrows():
        geom = row.geometry
        centroid = geom.centroid

        best_match = None
        min_dist = float('inf')

        for muni_name, coords in centroids.items():
            muni_point = Point(coords['lon'], coords['lat'])

            # Check if precinct contains the municipality centroid
            if geom.contains(muni_point):
                best_match = muni_name
                break

            # Otherwise find closest
            dist = centroid.distance(muni_point)
            if dist < min_dist:
                min_dist = dist
                best_match = muni_name

        municipalities.append(best_match)

    gdf = gdf.copy()
    gdf['municipality'] = municipalities

    return gdf


def create_2022_crosswalk(
    validated_dir: Path,
    centroids_path: Path
) -> pd.DataFrame:
    """
    Create crosswalk for 2022 district boundaries extracted from CEE PDFs.

    Args:
        validated_dir: Directory with validated GeoJSON files
        centroids_path: Path to municipality centroids

    Returns:
        DataFrame with 2022 precinct crosswalk
    """
    # Load validated boundaries
    gdf = load_2022_validated_geojson(validated_dir)

    # Match to municipalities
    gdf = match_precinct_to_municipality(gdf, centroids_path)

    # Calculate centroids
    centroids = gdf.geometry.centroid

    # Build crosswalk dataframe
    result = pd.DataFrame({
        'year': 2022,
        'district': gdf['district'],
        'precinct_index': gdf['precinct_index'],
        'municipality': gdf['municipality'],
        'color': gdf.get('color', None),
        'centroid_lon': centroids.x,
        'centroid_lat': centroids.y,
        'area_sq_deg': gdf.geometry.area,
        'source': '2022_cee_pdf'
    })

    logger.info(f"Created 2022 crosswalk with {len(result)} precincts")

    return result


def create_unified_crosswalk(output_dir: Path) -> pd.DataFrame:
    """
    Create unified crosswalk combining 2016 and 2022 data for comparative analysis.

    Args:
        output_dir: Directory containing existing crosswalk files

    Returns:
        DataFrame with unified crosswalk
    """
    dfs = []

    # Load 2016 MGGG crosswalk if exists
    mggg_path = output_dir / "precinct_municipality_crosswalk.parquet"
    if mggg_path.exists():
        df_2016 = pd.read_parquet(mggg_path)
        df_2016['year'] = 2016
        df_2016['source'] = '2016_mggg'
        # Standardize column names
        if 'precinct_id' in df_2016.columns:
            df_2016['district'] = df_2016['house_district']
        dfs.append(df_2016)
        logger.info(f"Loaded 2016 MGGG crosswalk: {len(df_2016)} records")

    # Load 2022 crosswalk if exists
    cee_path = output_dir / "precinct_crosswalk_2022.parquet"
    if cee_path.exists():
        df_2022 = pd.read_parquet(cee_path)
        dfs.append(df_2022)
        logger.info(f"Loaded 2022 CEE crosswalk: {len(df_2022)} records")

    if not dfs:
        logger.warning("No crosswalk files found to unify")
        return pd.DataFrame()

    # Combine
    unified = pd.concat(dfs, ignore_index=True)

    # Standardize columns
    standard_cols = ['year', 'district', 'municipality', 'centroid_lon', 'centroid_lat', 'source']
    available_cols = [c for c in standard_cols if c in unified.columns]

    logger.info(f"Created unified crosswalk with {len(unified)} records across {unified['year'].nunique()} years")

    return unified


def main():
    parser = argparse.ArgumentParser(
        description="Create precinct-to-census crosswalk for Puerto Rico"
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download MGGG shapefiles (2016)"
    )
    parser.add_argument(
        "--crosswalk",
        action="store_true",
        help="Create 2016 crosswalk from MGGG shapefiles"
    )
    parser.add_argument(
        "--crosswalk-2022",
        action="store_true",
        help="Create 2022 crosswalk from validated PDF extractions"
    )
    parser.add_argument(
        "--unified",
        action="store_true",
        help="Create unified crosswalk combining all years"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Do everything: download, crosswalk 2016, crosswalk 2022, unified"
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
    parser.add_argument(
        "--validated-dir",
        type=str,
        default=None,
        help=f"Directory with validated 2022 GeoJSON (default: {DEFAULT_PDF_VALIDATED_DIR})"
    )

    args = parser.parse_args()

    shapes_dir = Path(args.shapes_dir) if args.shapes_dir else DEFAULT_SHAPES_DIR
    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    validated_dir = Path(args.validated_dir) if args.validated_dir else DEFAULT_PDF_VALIDATED_DIR

    if args.all:
        args.download = True
        args.crosswalk = True
        args.crosswalk_2022 = True
        args.unified = True

    if not (args.download or args.crosswalk or args.crosswalk_2022 or args.unified):
        parser.print_help()
        return

    # Download shapefiles
    if args.download:
        extract_dir = download_mggg_shapefiles(shapes_dir)
    else:
        extract_dir = shapes_dir

    # Create 2016 crosswalk
    if args.crosswalk:
        logger.info("Creating 2016 MGGG crosswalk tables...")

        gdf = load_precinct_shapefile(extract_dir)

        # Basic precinct-municipality crosswalk
        basic_crosswalk = create_precinct_municipality_crosswalk(gdf)
        save_crosswalk(basic_crosswalk, output_dir, "precinct_municipality_crosswalk")

        # Detailed crosswalk with all data
        detailed_crosswalk = create_detailed_crosswalk(gdf)
        save_crosswalk(detailed_crosswalk, output_dir, "precinct_census_crosswalk")

        print("\n" + "="*60)
        print("2016 MGGG Crosswalk Summary")
        print("="*60)
        print(f"Total precincts: {len(gdf)}")
        if "Municipio" in gdf.columns:
            print(f"Municipalities covered: {gdf['Municipio'].nunique()}")
        print(f"Crosswalks saved to: {output_dir}")

    # Create 2022 crosswalk
    if args.crosswalk_2022:
        logger.info("Creating 2022 CEE PDF crosswalk tables...")

        if not validated_dir.exists():
            logger.error(f"Validated directory not found: {validated_dir}")
            logger.info("Run pdf_georeferencer.py first, then validate boundaries")
            return

        crosswalk_2022 = create_2022_crosswalk(validated_dir, DEFAULT_CENTROIDS_PATH)
        save_crosswalk(crosswalk_2022, output_dir, "precinct_crosswalk_2022")

        print("\n" + "="*60)
        print("2022 CEE PDF Crosswalk Summary")
        print("="*60)
        print(f"Total precincts: {len(crosswalk_2022)}")
        print(f"Districts: {crosswalk_2022['district'].nunique()}")
        print(f"Municipalities: {crosswalk_2022['municipality'].nunique()}")
        print(f"Crosswalk saved to: {output_dir}")

    # Create unified crosswalk
    if args.unified:
        logger.info("Creating unified multi-year crosswalk...")

        unified = create_unified_crosswalk(output_dir)
        if not unified.empty:
            save_crosswalk(unified, output_dir, "precinct_crosswalk_unified")

            print("\n" + "="*60)
            print("Unified Crosswalk Summary")
            print("="*60)
            print(f"Total records: {len(unified)}")
            print(f"Years: {sorted(unified['year'].unique())}")
            print(f"Crosswalk saved to: {output_dir}")

    print("\n" + "="*60)


if __name__ == "__main__":
    main()
