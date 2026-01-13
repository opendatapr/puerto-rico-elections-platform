"""
PDF Georeferencer for CEE District Maps

Converts PDF coordinate paths to WGS84 geographic coordinates using
municipality centroids as control points.

USAGE:
    python pdf_georeferencer.py [--input-dir DIR] [--output-dir DIR]

Approach:
    1. Extract text with positions from PDFs (precinct labels)
    2. Match labels to known municipality centroids
    3. Compute affine transformation (PDF → WGS84)
    4. Apply transformation to all precinct boundaries
"""

import json
import re
import math
from pathlib import Path
from typing import Optional
import argparse
import sys

try:
    import pdfplumber
    import numpy as np
except ImportError as e:
    print(f"Error: {e}. Install with: pip install pdfplumber numpy")
    sys.exit(1)


def load_municipality_centroids(path: Path) -> dict:
    """Load municipality name → (lat, lon) mapping."""
    with open(path) as f:
        data = json.load(f)
    # Normalize names for matching
    normalized = {}
    for name, coords in data.items():
        key = normalize_name(name)
        normalized[key] = coords
    return normalized


def normalize_name(name: str) -> str:
    """Normalize municipality name for matching."""
    name = name.lower().strip()
    # Handle accented characters
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'ü': 'u'
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    return name


def extract_text_with_positions(pdf_path: Path) -> list:
    """
    Extract text labels with their PDF coordinates.

    Returns list of {text, x, y, municipality, precinct_code}
    """
    labels = []

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]

        # Extract words with bounding boxes
        words = page.extract_words()

        # Group words into potential precinct labels
        # Pattern: "Municipality NNN" where NNN is 3-digit code
        for word in words:
            text = word.get('text', '')
            x = word.get('x0', 0)
            y = word.get('top', 0)

            labels.append({
                'text': text,
                'x': x,
                'y': y,
                'width': word.get('x1', x) - x,
                'height': word.get('bottom', y) - y
            })

    return labels


def find_control_points(labels: list, centroids: dict, page_height: float) -> list:
    """
    Match text labels to municipality centroids to create control points.

    Handles multi-word municipality names by checking consecutive word combinations.
    Allows multiple occurrences of same municipality at different positions.

    Returns list of {pdf_x, pdf_y, geo_lon, geo_lat, municipality}
    """
    control_points = []
    used_indices = set()

    # Try to match 1, 2, and 3 word combinations
    n = len(labels)

    for word_count in [3, 2, 1]:  # Try longer matches first
        for i in range(n - word_count + 1):
            if any(j in used_indices for j in range(i, i + word_count)):
                continue

            # Combine consecutive words
            combined_text = ' '.join(labels[j]['text'] for j in range(i, i + word_count))
            normalized = normalize_name(combined_text)

            # Check if this matches a municipality
            if normalized in centroids:
                coords = centroids[normalized]

                # Calculate center position of the combined text
                first_label = labels[i]
                last_label = labels[i + word_count - 1]
                center_x = (first_label['x'] + last_label['x'] + last_label['width']) / 2
                center_y = (first_label['y'] + last_label['y']) / 2

                # PDF coordinates: origin at top-left, y increases downward
                pdf_y_flipped = page_height - center_y

                control_points.append({
                    'municipality': combined_text,
                    'pdf_x': center_x,
                    'pdf_y': pdf_y_flipped,
                    'geo_lon': coords['lon'],
                    'geo_lat': coords['lat']
                })

                for j in range(i, i + word_count):
                    used_indices.add(j)

    return control_points


# Known municipality bounding boxes for single-municipality districts (approximate)
MUNICIPALITY_BOUNDS = {
    'san juan': {'min_lon': -66.15, 'max_lon': -65.98, 'min_lat': 18.35, 'max_lat': 18.48},
    'bayamon': {'min_lon': -66.20, 'max_lon': -66.10, 'min_lat': 18.35, 'max_lat': 18.43},
    'ponce': {'min_lon': -66.70, 'max_lon': -66.55, 'min_lat': 17.95, 'max_lat': 18.10},
    'caguas': {'min_lon': -66.10, 'max_lon': -65.95, 'min_lat': 18.18, 'max_lat': 18.30},
    'carolina': {'min_lon': -66.00, 'max_lon': -65.90, 'min_lat': 18.35, 'max_lat': 18.45},
    'mayaguez': {'min_lon': -67.20, 'max_lon': -67.05, 'min_lat': 18.15, 'max_lat': 18.25},
    'guaynabo': {'min_lon': -66.15, 'max_lon': -66.05, 'min_lat': 18.32, 'max_lat': 18.42},
    'toa baja': {'min_lon': -66.30, 'max_lon': -66.18, 'min_lat': 18.40, 'max_lat': 18.48},
    'catano': {'min_lon': -66.15, 'max_lon': -66.08, 'min_lat': 18.42, 'max_lat': 18.47},
    'trujillo alto': {'min_lon': -66.05, 'max_lon': -65.95, 'min_lat': 18.32, 'max_lat': 18.40},
}


def compute_bounds_transform(control_points: list, page_width: float, page_height: float) -> Optional[np.ndarray]:
    """
    For single-municipality districts, compute transform using known bounds.

    Uses the municipality name from control points to look up known bounds,
    then creates a simple scale/translate transformation.
    """
    if not control_points:
        return None

    # Get the municipality name
    muni_name = normalize_name(control_points[0]['municipality'])

    if muni_name not in MUNICIPALITY_BOUNDS:
        return None

    bounds = MUNICIPALITY_BOUNDS[muni_name]

    # Map PDF coordinates to geographic bounds
    # Assume the map content fills most of the page (with margins)
    margin = 100  # Approximate margin in PDF units
    pdf_x_min, pdf_x_max = margin, page_width - margin
    pdf_y_min, pdf_y_max = margin, page_height - margin

    # Compute scale and offset
    scale_x = (bounds['max_lon'] - bounds['min_lon']) / (pdf_x_max - pdf_x_min)
    scale_y = (bounds['max_lat'] - bounds['min_lat']) / (pdf_y_max - pdf_y_min)

    offset_x = bounds['min_lon'] - scale_x * pdf_x_min
    offset_y = bounds['min_lat'] - scale_y * pdf_y_min

    # Create affine matrix
    transform = np.array([
        [scale_x, 0, offset_x],
        [0, scale_y, offset_y]
    ])

    return transform


def compute_affine_transform(control_points: list) -> Optional[np.ndarray]:
    """
    Compute affine transformation matrix from control points.

    Uses least squares to find best fit transformation:
    [geo_lon]   [a b c] [pdf_x]
    [geo_lat] = [d e f] [pdf_y]
                        [  1  ]

    Returns 2x3 transformation matrix or None if insufficient points.
    """
    if len(control_points) < 3:
        return None

    # Build matrices for least squares
    n = len(control_points)
    A = np.zeros((2 * n, 6))
    b = np.zeros(2 * n)

    for i, cp in enumerate(control_points):
        pdf_x, pdf_y = cp['pdf_x'], cp['pdf_y']
        geo_lon, geo_lat = cp['geo_lon'], cp['geo_lat']

        # For longitude (x)
        A[2*i, 0] = pdf_x
        A[2*i, 1] = pdf_y
        A[2*i, 2] = 1
        b[2*i] = geo_lon

        # For latitude (y)
        A[2*i+1, 3] = pdf_x
        A[2*i+1, 4] = pdf_y
        A[2*i+1, 5] = 1
        b[2*i+1] = geo_lat

    # Solve least squares
    try:
        params, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
        transform = np.array([
            [params[0], params[1], params[2]],
            [params[3], params[4], params[5]]
        ])
        return transform
    except np.linalg.LinAlgError:
        return None


def apply_transform(coords: list, transform: np.ndarray, page_height: float) -> list:
    """
    Apply affine transformation to PDF coordinates.

    Input coords: [[x, y], ...] in PDF space
    Output: [[lon, lat], ...] in WGS84
    """
    result = []
    for x, y in coords:
        # Flip y coordinate
        y_flipped = page_height - y

        # Apply transformation
        lon = transform[0, 0] * x + transform[0, 1] * y_flipped + transform[0, 2]
        lat = transform[1, 0] * x + transform[1, 1] * y_flipped + transform[1, 2]

        result.append([lon, lat])

    return result


def transform_geojson(input_geojson: dict, transform: np.ndarray, page_height: float) -> dict:
    """Transform all coordinates in a GeoJSON from PDF to WGS84."""

    def transform_coords(coords):
        """Recursively transform coordinate arrays."""
        if not coords:
            return coords
        if isinstance(coords[0], (int, float)):
            # Single coordinate pair
            return apply_transform([coords], transform, page_height)[0]
        else:
            # Nested array
            return [transform_coords(c) for c in coords]

    output = {
        'type': 'FeatureCollection',
        'name': input_geojson.get('name', '').replace('_pdf_paths', '_wgs84'),
        'crs': {
            'type': 'name',
            'properties': {'name': 'EPSG:4326'}
        },
        'features': []
    }

    for feature in input_geojson.get('features', []):
        new_feature = {
            'type': 'Feature',
            'properties': dict(feature.get('properties', {})),
            'geometry': {
                'type': feature['geometry']['type'],
                'coordinates': transform_coords(feature['geometry']['coordinates'])
            }
        }
        # Update coordinate system in properties
        new_feature['properties']['coordinate_system'] = 'wgs84'
        new_feature['properties'].pop('page_width', None)
        new_feature['properties'].pop('page_height', None)

        output['features'].append(new_feature)

    return output


def estimate_transform_error(control_points: list, transform: np.ndarray, page_height: float) -> dict:
    """Estimate transformation error using control points."""
    errors = []

    for cp in control_points:
        # Transform PDF coords to geo
        transformed = apply_transform(
            [[cp['pdf_x'], page_height - cp['pdf_y']]],
            transform,
            page_height
        )[0]

        # Compare to actual geo coords
        lon_err = transformed[0] - cp['geo_lon']
        lat_err = transformed[1] - cp['geo_lat']

        # Distance error in degrees (rough approximation)
        dist_err = math.sqrt(lon_err**2 + lat_err**2)

        # Convert to approximate meters (at PR latitude, 1 degree ≈ 111km lat, 105km lon)
        dist_m = dist_err * 108000  # Average

        errors.append({
            'municipality': cp['municipality'],
            'lon_error': lon_err,
            'lat_error': lat_err,
            'distance_m': dist_m
        })

    avg_error = sum(e['distance_m'] for e in errors) / len(errors) if errors else 0
    max_error = max(e['distance_m'] for e in errors) if errors else 0

    return {
        'control_points': len(errors),
        'avg_error_m': round(avg_error, 1),
        'max_error_m': round(max_error, 1),
        'details': errors
    }


def process_district(
    district_num: int,
    pdf_dir: Path,
    extracted_dir: Path,
    output_dir: Path,
    centroids: dict
) -> dict:
    """Process a single district: extract control points and georeference."""

    pdf_path = pdf_dir / f"distrito_{district_num:02d}.pdf"
    geojson_path = extracted_dir / f"distrito_{district_num:02d}_paths.geojson"

    result = {
        'district': district_num,
        'status': 'unknown'
    }

    if not pdf_path.exists():
        result['status'] = 'error'
        result['error'] = 'PDF not found'
        return result

    if not geojson_path.exists():
        result['status'] = 'error'
        result['error'] = 'Extracted GeoJSON not found'
        return result

    # Load extracted paths
    with open(geojson_path) as f:
        geojson = json.load(f)

    page_height = geojson['metadata']['page_size']['height']

    # Extract text with positions from PDF
    labels = extract_text_with_positions(pdf_path)

    # Find control points
    control_points = find_control_points(labels, centroids, page_height)

    result['control_points_found'] = len(control_points)
    result['municipalities_matched'] = [cp['municipality'] for cp in control_points]

    page_width = geojson['metadata']['page_size']['width']
    transform = None
    used_bounds_fallback = False

    if len(control_points) >= 3:
        # Use affine transformation with control points
        transform = compute_affine_transform(control_points)
    elif len(control_points) >= 1:
        # Try bounds-based fallback for single-municipality districts
        transform = compute_bounds_transform(control_points, page_width, page_height)
        if transform is not None:
            used_bounds_fallback = True

    if transform is None:
        result['status'] = 'insufficient_control_points'
        result['error'] = f'Only {len(control_points)} control points found and no bounds fallback available'
        return result

    # Estimate error (only meaningful for affine transform)
    if used_bounds_fallback:
        error_stats = {'avg_error_m': -1, 'max_error_m': -1, 'control_points': len(control_points)}
        result['method'] = 'bounds_fallback'
    else:
        error_stats = estimate_transform_error(control_points, transform, page_height)
        result['method'] = 'affine'
    result['transform_error'] = {
        'avg_m': error_stats['avg_error_m'],
        'max_m': error_stats['max_error_m']
    }

    # Transform GeoJSON
    georeferenced = transform_geojson(geojson, transform, page_height)

    # Add metadata
    georeferenced['metadata'] = {
        'source': geojson['metadata']['source'],
        'coordinate_system': 'WGS84 (EPSG:4326)',
        'control_points': len(control_points),
        'transform_error_m': error_stats['avg_error_m'],
        'municipalities': result['municipalities_matched'],
        'transform_matrix': transform.tolist()
    }

    # Save
    output_path = output_dir / f"distrito_{district_num:02d}_wgs84.geojson"
    with open(output_path, 'w') as f:
        json.dump(georeferenced, f, indent=2)

    result['status'] = 'success'
    result['output_file'] = output_path.name
    result['features'] = len(georeferenced['features'])

    return result


def main():
    parser = argparse.ArgumentParser(description='Georeference CEE district map PDFs')
    parser.add_argument(
        '--input-dir', '-i',
        type=Path,
        default=Path(__file__).parent.parent / 'data' / 'pdf_maps',
        help='Directory containing PDFs and extracted GeoJSON'
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=None,
        help='Output directory for georeferenced files (default: input-dir/georeferenced)'
    )
    parser.add_argument(
        '--district', '-d',
        type=int,
        default=None,
        help='Process only specific district (1-40)'
    )
    args = parser.parse_args()

    input_dir = args.input_dir
    extracted_dir = input_dir / 'extracted'
    output_dir = args.output_dir or (input_dir / 'georeferenced')
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("CEE District Map Georeferencer")
    print("=" * 60)

    # Load municipality centroids
    centroids_path = input_dir / 'pr_municipality_centroids.json'
    if not centroids_path.exists():
        print(f"Error: Municipality centroids not found at {centroids_path}")
        return 1

    centroids = load_municipality_centroids(centroids_path)
    print(f"Loaded {len(centroids)} municipality centroids\n")

    # Process districts
    if args.district:
        districts = [args.district]
    else:
        districts = list(range(1, 41))

    results = []
    success_count = 0

    for district in districts:
        print(f"Processing Distrito {district:02d}...", end=" ")

        result = process_district(
            district,
            input_dir,
            extracted_dir,
            output_dir,
            centroids
        )

        if result['status'] == 'success':
            print(f"OK ({result['control_points_found']} ctrl pts, {result['transform_error']['avg_m']:.0f}m avg error)")
            success_count += 1
        else:
            print(f"FAILED: {result.get('error', result['status'])}")

        results.append(result)

    # Save summary
    summary = {
        'total_districts': len(districts),
        'successful': success_count,
        'failed': len(districts) - success_count,
        'results': results
    }

    summary_path = output_dir / 'georeferencing_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 60)
    print(f"Successful: {success_count}/{len(districts)}")
    print(f"Summary:    {summary_path}")
    print("=" * 60)

    return 0 if success_count > 0 else 1


if __name__ == '__main__':
    sys.exit(main())
