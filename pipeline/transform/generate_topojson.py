"""
Generate TopoJSON files from shapefiles for web visualization.
Uses geopandas for conversion when GDAL CLI tools are not available.
"""

import json
import subprocess
import sys
from pathlib import Path

try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False


def shapefile_to_geojson_geopandas(shapefile_path: Path, output_path: Path) -> bool:
    """Convert shapefile to GeoJSON using geopandas."""
    if not HAS_GEOPANDAS:
        print("geopandas not available")
        return False

    try:
        gdf = gpd.read_file(shapefile_path)
        # Reproject to WGS84 if needed
        if gdf.crs and gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)
        gdf.to_file(output_path, driver='GeoJSON')
        return True
    except Exception as e:
        print(f"Error converting with geopandas: {e}")
        return False


def shapefile_to_geojson_ogr(shapefile_path: Path, output_path: Path) -> bool:
    """Convert shapefile to GeoJSON using ogr2ogr."""
    try:
        subprocess.run(
            [
                'ogr2ogr',
                '-f', 'GeoJSON',
                '-t_srs', 'EPSG:4326',
                str(output_path),
                str(shapefile_path)
            ],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting shapefile: {e.stderr.decode()}")
        return False
    except FileNotFoundError:
        return False


def geojson_to_topojson_cli(geojson_path: Path, output_path: Path, object_name: str = 'data') -> bool:
    """Convert GeoJSON to TopoJSON using geo2topo CLI."""
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
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def geojson_to_topojson_python(geojson_path: Path, output_path: Path, object_name: str = 'municipalities') -> bool:
    """Convert GeoJSON to TopoJSON format in pure Python (simplified)."""
    try:
        with open(geojson_path) as f:
            geojson = json.load(f)

        # Simple TopoJSON structure (not quantized, but functional)
        # This creates a valid TopoJSON that can be read by topojson-client
        topojson = {
            "type": "Topology",
            "objects": {
                object_name: {
                    "type": "GeometryCollection",
                    "geometries": []
                }
            },
            "arcs": []
        }

        # Build arcs and geometries
        arc_index = 0
        for feature in geojson.get('features', []):
            geom = feature.get('geometry', {})
            props = feature.get('properties', {})

            if geom['type'] == 'Polygon':
                new_arcs = []
                for ring in geom['coordinates']:
                    topojson['arcs'].append(ring)
                    new_arcs.append([arc_index])
                    arc_index += 1
                topojson['objects'][object_name]['geometries'].append({
                    'type': 'Polygon',
                    'arcs': new_arcs,
                    'properties': props
                })
            elif geom['type'] == 'MultiPolygon':
                new_arcs = []
                for polygon in geom['coordinates']:
                    polygon_arcs = []
                    for ring in polygon:
                        topojson['arcs'].append(ring)
                        polygon_arcs.append([arc_index])
                        arc_index += 1
                    new_arcs.append(polygon_arcs)
                topojson['objects'][object_name]['geometries'].append({
                    'type': 'MultiPolygon',
                    'arcs': new_arcs,
                    'properties': props
                })

        with open(output_path, 'w') as f:
            json.dump(topojson, f)

        return True
    except Exception as e:
        print(f"Error converting to TopoJSON: {e}")
        return False


def create_municipalities_topojson(data_dir: Path, output_dir: Path) -> bool:
    """Create municipalities TopoJSON from PR shapefile."""
    shapefile = data_dir / 'shapes' / 'PR.shp'

    if not shapefile.exists():
        print(f"Shapefile not found: {shapefile}")
        return False

    output_dir.mkdir(parents=True, exist_ok=True)
    geojson_path = output_dir / 'municipalities.geojson'
    topojson_path = output_dir / 'municipalities.topojson'

    # Step 1: Convert shapefile to GeoJSON
    print(f"Converting {shapefile} to GeoJSON...")
    if HAS_GEOPANDAS:
        if not shapefile_to_geojson_geopandas(shapefile, geojson_path):
            print("Geopandas conversion failed, trying ogr2ogr...")
            if not shapefile_to_geojson_ogr(shapefile, geojson_path):
                print("Failed to convert shapefile to GeoJSON")
                return False
    else:
        if not shapefile_to_geojson_ogr(shapefile, geojson_path):
            print("ogr2ogr not available and geopandas not installed")
            return False

    # Step 2: Convert GeoJSON to TopoJSON
    print("Converting GeoJSON to TopoJSON...")
    if not geojson_to_topojson_cli(geojson_path, topojson_path, 'municipalities'):
        print("CLI tool not available, using Python conversion...")
        if not geojson_to_topojson_python(geojson_path, topojson_path, 'municipalities'):
            print("Failed to convert to TopoJSON")
            return False

    print(f"Created: {topojson_path}")

    # Clean up intermediate GeoJSON (optional, keep for debugging)
    # geojson_path.unlink()

    return True


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    data_dir = repo_root / 'data'
    output_dir = repo_root / 'webapp' / 'static' / 'data' / 'geo'

    print("Generating TopoJSON files...")

    if not create_municipalities_topojson(data_dir, output_dir):
        print("Failed to create municipalities TopoJSON")
        sys.exit(1)

    print("Done!")


if __name__ == '__main__':
    main()
