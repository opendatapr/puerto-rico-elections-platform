"""
Generate precincts TopoJSON file for web visualization.
Merges all district GeoJSON files and creates a single TopoJSON output.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    import geopandas as gpd
    import pandas as pd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False

try:
    import topojson as tp
    HAS_TOPOJSON = True
except ImportError:
    HAS_TOPOJSON = False


def merge_district_geojsons(georeferenced_dir: Path) -> Optional[gpd.GeoDataFrame]:
    """
    Merge all district GeoJSON files into a single GeoDataFrame.

    Args:
        georeferenced_dir: Directory containing distrito_*_wgs84.geojson files

    Returns:
        Merged GeoDataFrame with all precincts
    """
    if not HAS_GEOPANDAS:
        print("Error: geopandas is required but not installed")
        return None

    geojson_files = sorted(georeferenced_dir.glob("distrito_*_wgs84.geojson"))

    if not geojson_files:
        print(f"No GeoJSON files found in {georeferenced_dir}")
        return None

    print(f"Found {len(geojson_files)} district GeoJSON files")

    gdfs = []
    for geojson_file in geojson_files:
        try:
            gdf = gpd.read_file(geojson_file)
            # Ensure CRS is WGS84
            if gdf.crs is None:
                gdf.set_crs(epsg=4326, inplace=True)
            elif gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs(epsg=4326)

            # Extract district number from filename
            district_num = int(geojson_file.stem.split('_')[1])

            # Ensure district property exists
            if 'district' not in gdf.columns:
                gdf['district'] = district_num

            gdfs.append(gdf)
            print(f"  Loaded {geojson_file.name}: {len(gdf)} precincts")
        except Exception as e:
            print(f"  Error loading {geojson_file.name}: {e}")
            continue

    if not gdfs:
        print("No GeoDataFrames could be loaded")
        return None

    # Merge all GeoDataFrames
    merged = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs="EPSG:4326")
    print(f"\nTotal precincts merged: {len(merged)}")

    return merged


def simplify_geometry(gdf: gpd.GeoDataFrame, tolerance: float = 0.0001) -> gpd.GeoDataFrame:
    """
    Simplify geometry to reduce file size while preserving shape.

    Args:
        gdf: GeoDataFrame with geometries
        tolerance: Simplification tolerance in degrees (0.0001 ~ 11 meters at equator)

    Returns:
        GeoDataFrame with simplified geometries
    """
    original_points = sum(
        sum(len(ring) for ring in (geom.exterior.coords if hasattr(geom, 'exterior') else []))
        for geom in gdf.geometry if geom is not None
    )

    gdf['geometry'] = gdf.geometry.simplify(tolerance, preserve_topology=True)

    simplified_points = sum(
        sum(len(ring) for ring in (geom.exterior.coords if hasattr(geom, 'exterior') else []))
        for geom in gdf.geometry if geom is not None
    )

    if original_points > 0:
        reduction = (1 - simplified_points / original_points) * 100
        print(f"Geometry simplified: {original_points} -> {simplified_points} points ({reduction:.1f}% reduction)")

    return gdf


def generate_topojson_python(gdf: gpd.GeoDataFrame, output_path: Path, object_name: str = 'precincts') -> bool:
    """
    Convert GeoDataFrame to TopoJSON using the topojson library.

    Args:
        gdf: GeoDataFrame to convert
        output_path: Output file path
        object_name: Name of the object in TopoJSON

    Returns:
        True if successful
    """
    if not HAS_TOPOJSON:
        print("topojson library not available, using fallback method")
        return generate_topojson_fallback(gdf, output_path, object_name)

    try:
        # Convert to TopoJSON with quantization for smaller file size
        topo = tp.Topology(gdf, object_name=object_name, prequantize=1e6)

        # Write to file
        with open(output_path, 'w') as f:
            f.write(topo.to_json())

        return True
    except Exception as e:
        print(f"Error with topojson library: {e}")
        return generate_topojson_fallback(gdf, output_path, object_name)


def generate_topojson_fallback(gdf: gpd.GeoDataFrame, output_path: Path, object_name: str = 'precincts') -> bool:
    """
    Fallback TopoJSON generation via GeoJSON intermediate.
    Uses geo2topo CLI if available, otherwise pure Python conversion.
    """
    # First save as GeoJSON
    geojson_path = output_path.with_suffix('.geojson')

    try:
        gdf.to_file(geojson_path, driver='GeoJSON')
        print(f"Saved intermediate GeoJSON: {geojson_path}")
    except Exception as e:
        print(f"Error saving GeoJSON: {e}")
        return False

    # Try geo2topo CLI
    try:
        subprocess.run(
            [
                'geo2topo',
                f'{object_name}={geojson_path}',
                '-o', str(output_path)
            ],
            check=True,
            capture_output=True
        )
        print(f"Created TopoJSON using geo2topo CLI")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"geo2topo not available, using Python fallback: {e}")

    # Pure Python TopoJSON conversion (simplified, not quantized)
    try:
        with open(geojson_path) as f:
            geojson = json.load(f)

        topojson_data = {
            "type": "Topology",
            "objects": {
                object_name: {
                    "type": "GeometryCollection",
                    "geometries": []
                }
            },
            "arcs": []
        }

        arc_index = 0
        for feature in geojson.get('features', []):
            geom = feature.get('geometry', {})
            props = feature.get('properties', {})

            if geom['type'] == 'Polygon':
                new_arcs = []
                for ring in geom['coordinates']:
                    topojson_data['arcs'].append(ring)
                    new_arcs.append([arc_index])
                    arc_index += 1
                topojson_data['objects'][object_name]['geometries'].append({
                    'type': 'Polygon',
                    'arcs': new_arcs,
                    'properties': props
                })
            elif geom['type'] == 'MultiPolygon':
                new_arcs = []
                for polygon in geom['coordinates']:
                    polygon_arcs = []
                    for ring in polygon:
                        topojson_data['arcs'].append(ring)
                        polygon_arcs.append([arc_index])
                        arc_index += 1
                    new_arcs.append(polygon_arcs)
                topojson_data['objects'][object_name]['geometries'].append({
                    'type': 'MultiPolygon',
                    'arcs': new_arcs,
                    'properties': props
                })

        with open(output_path, 'w') as f:
            json.dump(topojson_data, f)

        print(f"Created TopoJSON using Python fallback")
        return True
    except Exception as e:
        print(f"Error in Python TopoJSON conversion: {e}")
        return False


def create_precinct_crosswalk(crosswalk_source: Path, output_path: Path) -> bool:
    """
    Create a simplified precinct crosswalk JSON for the webapp.
    Maps district -> municipality -> precincts with relevant metadata.

    Args:
        crosswalk_source: Path to source crosswalk file (parquet or json)
        output_path: Output JSON path

    Returns:
        True if successful
    """
    try:
        if crosswalk_source.suffix == '.parquet':
            df = pd.read_parquet(crosswalk_source)
        elif crosswalk_source.suffix == '.json':
            df = pd.read_json(crosswalk_source)
        else:
            print(f"Unsupported crosswalk format: {crosswalk_source.suffix}")
            return False

        print(f"Loaded crosswalk with {len(df)} records")

        # Build hierarchical structure: district -> municipality -> precincts
        crosswalk = {
            "districts": {},
            "municipalities": {},
            "precincts": []
        }

        # Get unique districts
        if 'district' in df.columns:
            for district in sorted(df['district'].dropna().unique()):
                district_int = int(district)
                district_df = df[df['district'] == district]

                crosswalk["districts"][str(district_int)] = {
                    "district": district_int,
                    "municipalities": list(district_df['municipality'].dropna().unique()),
                    "precinct_count": len(district_df)
                }

        # Get unique municipalities with their districts
        if 'municipality' in df.columns:
            for muni in df['municipality'].dropna().unique():
                muni_df = df[df['municipality'] == muni]
                districts = list(muni_df['district'].dropna().unique())

                crosswalk["municipalities"][muni] = {
                    "municipality": muni,
                    "districts": [int(d) for d in districts],
                    "precinct_count": len(muni_df)
                }

        # Simplified precinct list with essential info
        for _, row in df.iterrows():
            precinct = {
                "precinct_id": row.get('precinct_id', ''),
                "district": int(row['district']) if pd.notna(row.get('district')) else None,
                "municipality": row.get('municipality', ''),
            }

            # Add optional fields if present
            if pd.notna(row.get('precinct_code')):
                precinct["code"] = int(row['precinct_code'])
            if pd.notna(row.get('senate_district')):
                precinct["senate_district"] = int(row['senate_district'])
            if pd.notna(row.get('house_district')):
                precinct["house_district"] = int(row['house_district'])
            if pd.notna(row.get('centroid_lat')) and pd.notna(row.get('centroid_lon')):
                precinct["centroid"] = [float(row['centroid_lon']), float(row['centroid_lat'])]

            crosswalk["precincts"].append(precinct)

        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(crosswalk, f, indent=2, ensure_ascii=False)

        print(f"Created precinct crosswalk: {output_path}")
        print(f"  Districts: {len(crosswalk['districts'])}")
        print(f"  Municipalities: {len(crosswalk['municipalities'])}")
        print(f"  Precincts: {len(crosswalk['precincts'])}")

        return True
    except Exception as e:
        print(f"Error creating precinct crosswalk: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_precincts_topojson(data_dir: Path, output_dir: Path, simplify_tolerance: float = 0.0001) -> bool:
    """
    Create precincts TopoJSON from merged district GeoJSON files.

    Args:
        data_dir: Data directory containing pdf_maps/georeferenced/
        output_dir: Output directory for TopoJSON file
        simplify_tolerance: Geometry simplification tolerance

    Returns:
        True if successful
    """
    georeferenced_dir = data_dir / 'pdf_maps' / 'georeferenced'

    if not georeferenced_dir.exists():
        print(f"Georeferenced directory not found: {georeferenced_dir}")
        return False

    output_dir.mkdir(parents=True, exist_ok=True)
    topojson_path = output_dir / 'precincts.topojson'

    # Step 1: Merge all district GeoJSONs
    print("\n=== Merging district GeoJSON files ===")
    merged_gdf = merge_district_geojsons(georeferenced_dir)

    if merged_gdf is None:
        return False

    # Step 2: Simplify geometry
    print("\n=== Simplifying geometry ===")
    simplified_gdf = simplify_geometry(merged_gdf, tolerance=simplify_tolerance)

    # Step 3: Clean up properties for web
    print("\n=== Preparing properties for web ===")
    # Keep only essential properties
    essential_cols = ['district', 'precinct_index', 'color', 'geometry']
    available_cols = [col for col in essential_cols if col in simplified_gdf.columns]
    simplified_gdf = simplified_gdf[available_cols]

    # Create unique precinct_id
    simplified_gdf['id'] = simplified_gdf.apply(
        lambda row: f"d{int(row['district']):02d}_p{int(row['precinct_index']):02d}"
        if pd.notna(row.get('precinct_index')) else f"d{int(row['district']):02d}_p00",
        axis=1
    )

    print(f"Properties: {list(simplified_gdf.columns)}")

    # Step 4: Generate TopoJSON
    print("\n=== Generating TopoJSON ===")
    if not generate_topojson_python(simplified_gdf, topojson_path, object_name='precincts'):
        return False

    # Check file size
    file_size_mb = topojson_path.stat().st_size / (1024 * 1024)
    print(f"\nCreated: {topojson_path}")
    print(f"File size: {file_size_mb:.2f} MB")

    return True


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    data_dir = repo_root / 'data'
    output_dir = repo_root / 'webapp' / 'static' / 'data' / 'geo'
    crosswalk_output_dir = repo_root / 'webapp' / 'static' / 'data' / 'crosswalks'

    print("=" * 60)
    print("Generating Precincts TopoJSON and Crosswalk")
    print("=" * 60)

    # Generate TopoJSON
    if not create_precincts_topojson(data_dir, output_dir, simplify_tolerance=0.0001):
        print("\nFailed to create precincts TopoJSON")
        sys.exit(1)

    # Generate crosswalk
    print("\n=== Creating precinct crosswalk ===")
    crosswalk_source = data_dir / 'crosswalks' / 'precinct_crosswalk_unified.json'
    crosswalk_output = crosswalk_output_dir / 'precincts.json'

    if crosswalk_source.exists():
        if not create_precinct_crosswalk(crosswalk_source, crosswalk_output):
            print("Warning: Failed to create precinct crosswalk")
    else:
        print(f"Warning: Crosswalk source not found: {crosswalk_source}")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == '__main__':
    main()
