#!/usr/bin/env python
"""
Data pipeline orchestration for PR Elections Scrollytelling webapp.

Usage:
    python pipeline/run_pipeline.py [--output DIR] [--skip-geo] [--skip-data]
"""

import argparse
import sys
from pathlib import Path

# Add pipeline modules to path
sys.path.insert(0, str(Path(__file__).parent))

from transform.generate_topojson import main as generate_geo
from transform.aggregate_chapters import main as aggregate_chapters
from load.export_json import main as export_data


def main():
    parser = argparse.ArgumentParser(description='Run data pipeline for webapp')
    parser.add_argument(
        '--output',
        type=Path,
        default=Path(__file__).parent.parent / 'webapp' / 'static' / 'data',
        help='Output directory for processed data'
    )
    parser.add_argument(
        '--skip-geo',
        action='store_true',
        help='Skip TopoJSON generation (requires GDAL and topojson-cli)'
    )
    parser.add_argument(
        '--skip-data',
        action='store_true',
        help='Skip election/census data export'
    )
    parser.add_argument(
        '--skip-aggregate',
        action='store_true',
        help='Skip chapter aggregation'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("PR Elections Data Pipeline")
    print("=" * 60)

    if not args.skip_geo:
        print("\n[1/3] Generating TopoJSON files...")
        print("-" * 40)
        try:
            generate_geo()
        except Exception as e:
            print(f"Warning: TopoJSON generation failed: {e}")
            print("You may need to install GDAL and topojson-cli")
    else:
        print("\n[1/3] Skipping TopoJSON generation")

    if not args.skip_data:
        print("\n[2/3] Exporting data files...")
        print("-" * 40)
        try:
            export_data()
        except Exception as e:
            print(f"Error exporting data: {e}")
            sys.exit(1)
    else:
        print("\n[2/3] Skipping data export")

    if not args.skip_aggregate:
        print("\n[3/3] Aggregating chapter data...")
        print("-" * 40)
        try:
            aggregate_chapters()
        except Exception as e:
            print(f"Error aggregating chapters: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("\n[3/3] Skipping chapter aggregation")

    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print(f"Output: {args.output}")
    print("=" * 60)


if __name__ == '__main__':
    main()
