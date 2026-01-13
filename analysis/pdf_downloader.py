"""
PDF District Map Downloader

Downloads all 40 representative district map PDFs from CEE Puerto Rico.

USAGE:
    python pdf_downloader.py [--output-dir DIR]

Output:
    - data/pdf_maps/distrito_01.pdf through distrito_40.pdf
    - data/pdf_maps/pdf_inventory.json (metadata index)
"""

import json
import urllib.request
import urllib.parse
import time
from pathlib import Path
import argparse
import sys


# CEE JSON endpoint for district map list
JSON_URL = "https://ww2.ceepur.org/Data/.Mapas%20Distrito%20Representativos.json"
BASE_URL = "https://ww2.ceepur.org"


def fetch_pdf_list():
    """Fetch the JSON list of district map PDFs from CEE."""
    print(f"Fetching PDF list from CEE...")

    with urllib.request.urlopen(JSON_URL) as response:
        data = json.loads(response.read().decode('utf-8'))

    pdfs = []
    for item in data:
        filename = item.get('FileLeafRef', '')
        file_ref = item.get('FileRef', '')
        file_size = item.get('File_x0020_Size', 0)

        if filename.endswith('.pdf'):
            # Extract district number from filename
            # "Distrito Representativo 01.pdf" -> 1
            num_str = filename.replace('Distrito Representativo ', '').replace('.pdf', '').strip()
            try:
                district_num = int(num_str)
            except ValueError:
                district_num = 0

            pdfs.append({
                'district': district_num,
                'original_filename': filename,
                'path': file_ref,
                'url': BASE_URL + urllib.parse.quote(file_ref),
                'size_bytes': int(file_size) if file_size else 0,
            })

    # Sort by district number
    pdfs.sort(key=lambda x: x['district'])
    return pdfs


def download_pdf(url: str, output_path: Path, retries: int = 3) -> bool:
    """Download a single PDF with retries."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; PR-Elections-Platform/1.0)'}
            )
            with urllib.request.urlopen(req, timeout=60) as response:
                content = response.read()

            output_path.write_bytes(content)
            return True

        except Exception as e:
            if attempt < retries - 1:
                print(f"    Retry {attempt + 1}/{retries}: {e}")
                time.sleep(2)
            else:
                print(f"    FAILED: {e}")
                return False

    return False


def main():
    parser = argparse.ArgumentParser(description='Download CEE district map PDFs')
    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=Path(__file__).parent.parent / 'data' / 'pdf_maps',
        help='Output directory for PDFs'
    )
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        help='Skip PDFs that already exist'
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("CEE District Map PDF Downloader")
    print("=" * 60)

    # Fetch PDF list
    pdfs = fetch_pdf_list()
    print(f"Found {len(pdfs)} district map PDFs\n")

    # Download each PDF
    downloaded = 0
    skipped = 0
    failed = 0

    for pdf in pdfs:
        district = pdf['district']
        output_filename = f"distrito_{district:02d}.pdf"
        output_path = output_dir / output_filename

        # Add local filename to metadata
        pdf['local_filename'] = output_filename

        print(f"[{district:02d}/40] {pdf['original_filename']}")

        if args.skip_existing and output_path.exists():
            print(f"    Skipped (exists): {output_path.name}")
            skipped += 1
            pdf['downloaded'] = True
            continue

        success = download_pdf(pdf['url'], output_path)

        if success:
            actual_size = output_path.stat().st_size
            print(f"    Downloaded: {output_path.name} ({actual_size // 1024} KB)")
            downloaded += 1
            pdf['downloaded'] = True
        else:
            failed += 1
            pdf['downloaded'] = False

        # Be nice to the server
        time.sleep(0.5)

    # Save inventory
    inventory_path = output_dir / 'pdf_inventory.json'
    with open(inventory_path, 'w') as f:
        json.dump({
            'source': 'CEE Puerto Rico',
            'url': 'https://ww2.ceepur.org/Home/MapasDistritosRepresentativos',
            'downloaded_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'total_pdfs': len(pdfs),
            'pdfs': pdfs
        }, f, indent=2)

    print("\n" + "=" * 60)
    print(f"Downloaded: {downloaded}")
    print(f"Skipped:    {skipped}")
    print(f"Failed:     {failed}")
    print(f"Inventory:  {inventory_path}")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
