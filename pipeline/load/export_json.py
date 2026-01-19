"""
Export election and census data as JSON for the webapp.
"""

import json
from pathlib import Path
from typing import Any

import pandas as pd


def export_elections(data_dir: Path, output_dir: Path) -> None:
    """Export election results as JSON files by year."""
    results_file = data_dir / 'processed' / 'results.parquet'

    if not results_file.exists():
        print(f"Results file not found: {results_file}")
        # Try JSON fallback
        results_json = data_dir / 'processed' / 'results.json'
        if results_json.exists():
            print(f"Using JSON fallback: {results_json}")
            with open(results_json) as f:
                results = json.load(f)
            df = pd.DataFrame(results)
        else:
            print("No election data found")
            return
    else:
        df = pd.read_parquet(results_file)

    # Extract year from event_date
    if 'event_date' in df.columns:
        df['year'] = pd.to_datetime(df['event_date']).dt.year
    elif 'event_id' in df.columns:
        # Extract year from event_id (e.g., "EG2020" -> 2020)
        df['year'] = df['event_id'].str.extract(r'(\d{4})').astype(int)
    else:
        print("Cannot determine election year")
        return

    # Export by year
    elections_dir = output_dir / 'elections'
    elections_dir.mkdir(parents=True, exist_ok=True)

    for year in df['year'].unique():
        year_df = df[df['year'] == year]
        year_file = elections_dir / f'{year}.json'

        # Convert to records format
        records = year_df.to_dict(orient='records')

        with open(year_file, 'w') as f:
            json.dump(records, f, default=str)

        print(f"Exported {len(records)} records for {year}")


def export_census(data_dir: Path, output_dir: Path) -> None:
    """Export census data as JSON."""
    census_dir = data_dir / 'census'

    if not census_dir.exists():
        print(f"Census directory not found: {census_dir}")
        return

    output_census_dir = output_dir / 'census'
    output_census_dir.mkdir(parents=True, exist_ok=True)

    # Combine all municipality census data
    all_census = []

    for parquet_file in census_dir.glob('pr_municipalities_acs*.parquet'):
        # Extract year from filename
        year = parquet_file.stem.split('acs')[-1]

        df = pd.read_parquet(parquet_file)
        df['census_year'] = int(year)
        all_census.append(df)

    if all_census:
        combined = pd.concat(all_census, ignore_index=True)
        output_file = output_census_dir / 'municipalities.json'

        records = combined.to_dict(orient='records')
        with open(output_file, 'w') as f:
            json.dump(records, f, default=str)

        print(f"Exported {len(records)} census records to {output_file}")
    else:
        # Try CSV files
        for csv_file in census_dir.glob('pr_municipalities_acs*.csv'):
            year = csv_file.stem.split('acs')[-1]
            df = pd.read_csv(csv_file)
            df['census_year'] = int(year)
            all_census.append(df)

        if all_census:
            combined = pd.concat(all_census, ignore_index=True)
            output_file = output_census_dir / 'municipalities.json'

            records = combined.to_dict(orient='records')
            with open(output_file, 'w') as f:
                json.dump(records, f, default=str)

            print(f"Exported {len(records)} census records from CSV")


def export_crosswalks(data_dir: Path, output_dir: Path) -> None:
    """Export crosswalk files."""
    crosswalks_dir = data_dir / 'crosswalks'

    if not crosswalks_dir.exists():
        print(f"Crosswalks directory not found: {crosswalks_dir}")
        return

    output_crosswalks_dir = output_dir / 'crosswalks'
    output_crosswalks_dir.mkdir(parents=True, exist_ok=True)

    for json_file in crosswalks_dir.glob('*.json'):
        output_file = output_crosswalks_dir / json_file.name
        # Just copy JSON files
        output_file.write_text(json_file.read_text())
        print(f"Copied {json_file.name}")


def create_summary_data(data_dir: Path, output_dir: Path) -> None:
    """Create summary statistics for quick loading."""
    summary = {
        'municipalities': 78,
        'years': [],
        'event_types': [],
        'last_updated': pd.Timestamp.now().isoformat()
    }

    # Get available years
    results_file = data_dir / 'processed' / 'results.parquet'
    if results_file.exists():
        df = pd.read_parquet(results_file)
        if 'event_date' in df.columns:
            df['year'] = pd.to_datetime(df['event_date']).dt.year
            summary['years'] = sorted(df['year'].unique().tolist())
        if 'event_type' in df.columns:
            summary['event_types'] = df['event_type'].unique().tolist()

    output_file = output_dir / 'summary.json'
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"Created summary: {output_file}")


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    data_dir = repo_root / 'data'
    output_dir = repo_root / 'webapp' / 'static' / 'data'

    output_dir.mkdir(parents=True, exist_ok=True)

    print("Exporting data for webapp...")

    export_elections(data_dir, output_dir)
    export_census(data_dir, output_dir)
    export_crosswalks(data_dir, output_dir)
    create_summary_data(data_dir, output_dir)

    print("Done!")


if __name__ == '__main__':
    main()
