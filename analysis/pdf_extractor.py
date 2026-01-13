"""
PDF Vector Path Extractor for CEE District Maps

Extracts precinct boundary paths from CEE PDF maps as GeoJSON (PDF coordinate system).

USAGE:
    python pdf_extractor.py [--input-dir DIR] [--output-dir DIR] [--district NUM]

Output:
    - data/pdf_maps/extracted/distrito_XX_paths.geojson (one per district)
    - data/pdf_maps/extracted/extraction_summary.json
"""

import json
import re
from pathlib import Path
from typing import Any
import argparse
import sys

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber required. Install with: pip install pdfplumber")
    sys.exit(1)


def rgb_to_hex(rgb: tuple) -> str:
    """Convert RGB tuple (0-1 range) to hex color string."""
    if rgb is None:
        return "#000000"
    r, g, b = [int(c * 255) for c in rgb[:3]]
    return f"#{r:02x}{g:02x}{b:02x}"


def extract_paths_from_pdf(pdf_path: Path) -> dict:
    """
    Extract vector paths from a single PDF.

    Returns dict with:
        - district: district number
        - page_size: (width, height)
        - precincts: list of precinct boundaries with colors
        - text_labels: extracted text labels
    """
    district_num = int(pdf_path.stem.split('_')[1])

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]

        result = {
            'district': district_num,
            'source_file': pdf_path.name,
            'page_size': {
                'width': page.width,
                'height': page.height
            },
            'precincts': [],
            'text_labels': []
        }

        # Extract text for precinct names
        text = page.extract_text() or ""

        # Parse precinct codes from text (format: "Municipality NNN")
        # Common patterns: "San Juan 001", "Cataño 009", etc.
        precinct_pattern = r'([A-Za-záéíóúñÁÉÍÓÚÑ\s]+)\s+(\d{3})'
        matches = re.findall(precinct_pattern, text)
        for muni, code in matches:
            muni = muni.strip()
            if muni and len(muni) > 2 and not muni.startswith('NÚM'):
                result['text_labels'].append({
                    'municipality': muni,
                    'precinct_code': code
                })

        # Extract curves (vector paths)
        curves = page.curves if hasattr(page, 'curves') else []

        # Group curves by color (each color = one precinct typically)
        color_curves = {}

        for i, curve in enumerate(curves):
            pts = curve.get('pts', [])
            fill = curve.get('fill', False)
            color = curve.get('non_stroking_color', None)

            # Skip non-filled curves and very small paths
            if not fill or len(pts) < 50:
                continue

            # Skip white/near-white (background)
            if color and all(c > 0.98 for c in color[:3]):
                continue

            color_hex = rgb_to_hex(color)

            if color_hex not in color_curves:
                color_curves[color_hex] = {
                    'color': color_hex,
                    'rgb': list(color) if color else None,
                    'paths': []
                }

            # Convert path to coordinate list
            coords = [[pt[0], pt[1]] for pt in pts]

            # Get bounding box
            xs = [pt[0] for pt in pts]
            ys = [pt[1] for pt in pts]
            bbox = {
                'x_min': min(xs),
                'y_min': min(ys),
                'x_max': max(xs),
                'y_max': max(ys)
            }

            color_curves[color_hex]['paths'].append({
                'curve_index': i,
                'point_count': len(pts),
                'bbox': bbox,
                'coordinates': coords
            })

        # Convert to precinct list
        for color_hex, data in color_curves.items():
            # Merge all paths of same color into one precinct
            all_coords = []
            total_points = 0
            merged_bbox = {
                'x_min': float('inf'),
                'y_min': float('inf'),
                'x_max': float('-inf'),
                'y_max': float('-inf')
            }

            for path in data['paths']:
                all_coords.append(path['coordinates'])
                total_points += path['point_count']
                merged_bbox['x_min'] = min(merged_bbox['x_min'], path['bbox']['x_min'])
                merged_bbox['y_min'] = min(merged_bbox['y_min'], path['bbox']['y_min'])
                merged_bbox['x_max'] = max(merged_bbox['x_max'], path['bbox']['x_max'])
                merged_bbox['y_max'] = max(merged_bbox['y_max'], path['bbox']['y_max'])

            result['precincts'].append({
                'color': color_hex,
                'rgb': data['rgb'],
                'path_count': len(data['paths']),
                'total_points': total_points,
                'bbox': merged_bbox,
                'rings': all_coords  # Each path is a ring (may be outer or hole)
            })

        return result


def to_geojson(extraction: dict) -> dict:
    """
    Convert extracted data to GeoJSON format.

    Note: Coordinates are in PDF space, not geographic.
    Requires georeferencing to convert to real lat/lon.
    """
    features = []

    for i, precinct in enumerate(extraction['precincts']):
        # Create a MultiPolygon feature for each precinct
        # Each ring is treated as a separate polygon for now
        # (proper topology analysis would identify holes)

        polygons = []
        for ring in precinct['rings']:
            # Close the ring if not closed
            if ring[0] != ring[-1]:
                ring = ring + [ring[0]]
            polygons.append([ring])

        feature = {
            'type': 'Feature',
            'properties': {
                'district': extraction['district'],
                'precinct_index': i,
                'color': precinct['color'],
                'path_count': precinct['path_count'],
                'total_points': precinct['total_points'],
                'coordinate_system': 'pdf',
                'page_width': extraction['page_size']['width'],
                'page_height': extraction['page_size']['height']
            },
            'geometry': {
                'type': 'MultiPolygon' if len(polygons) > 1 else 'Polygon',
                'coordinates': polygons if len(polygons) > 1 else polygons[0]
            }
        }

        features.append(feature)

    return {
        'type': 'FeatureCollection',
        'name': f'distrito_{extraction["district"]:02d}_pdf_paths',
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'PDF_COORDINATE_SYSTEM'
            }
        },
        'metadata': {
            'source': extraction['source_file'],
            'page_size': extraction['page_size'],
            'text_labels': extraction['text_labels'],
            'note': 'Coordinates are in PDF space. Requires georeferencing to convert to geographic coordinates.'
        },
        'features': features
    }


def main():
    parser = argparse.ArgumentParser(description='Extract vector paths from CEE district map PDFs')
    parser.add_argument(
        '--input-dir', '-i',
        type=Path,
        default=Path(__file__).parent.parent / 'data' / 'pdf_maps',
        help='Directory containing PDFs'
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=None,
        help='Output directory for GeoJSON files (default: input-dir/extracted)'
    )
    parser.add_argument(
        '--district', '-d',
        type=int,
        default=None,
        help='Extract only specific district (1-40)'
    )
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir or (input_dir / 'extracted')
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("CEE District Map Vector Extractor")
    print("=" * 60)

    # Find PDFs to process
    if args.district:
        pdfs = [input_dir / f"distrito_{args.district:02d}.pdf"]
    else:
        pdfs = sorted(input_dir.glob("distrito_*.pdf"))

    print(f"Found {len(pdfs)} PDFs to process\n")

    summary = {
        'total_districts': len(pdfs),
        'districts': []
    }

    for pdf_path in pdfs:
        if not pdf_path.exists():
            print(f"[SKIP] {pdf_path.name} not found")
            continue

        print(f"Processing {pdf_path.name}...")

        try:
            extraction = extract_paths_from_pdf(pdf_path)
            geojson = to_geojson(extraction)

            # Save GeoJSON
            output_path = output_dir / f"distrito_{extraction['district']:02d}_paths.geojson"
            with open(output_path, 'w') as f:
                json.dump(geojson, f, indent=2)

            precinct_count = len(extraction['precincts'])
            total_points = sum(p['total_points'] for p in extraction['precincts'])
            label_count = len(extraction['text_labels'])

            print(f"  Precincts: {precinct_count}, Points: {total_points:,}, Labels: {label_count}")
            print(f"  Saved: {output_path.name}")

            summary['districts'].append({
                'district': extraction['district'],
                'precinct_count': precinct_count,
                'total_points': total_points,
                'label_count': label_count,
                'labels': extraction['text_labels'][:5],  # First 5 labels
                'output_file': output_path.name
            })

        except Exception as e:
            print(f"  ERROR: {e}")
            summary['districts'].append({
                'district': int(pdf_path.stem.split('_')[1]),
                'error': str(e)
            })

    # Save summary
    summary_path = output_dir / 'extraction_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 60)
    print(f"Processed: {len(summary['districts'])} districts")
    print(f"Summary:   {summary_path}")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    sys.exit(main())
