# PDF Precinct Boundary Extraction

This document describes the methodology for extracting precinct boundaries from CEE (Comision Estatal de Elecciones) PDF maps.

---

## Overview

The CEE publishes representative district maps as PDF documents, which contain vector drawings of precinct boundaries. Since these boundaries are not officially available as GIS data, we extract them programmatically from the PDFs and georeference them to WGS84 coordinates.

**Pipeline Summary:**
1. **Download** - Fetch 40 district map PDFs from CEE website
2. **Extract** - Parse vector paths from PDF using pdfplumber
3. **Georeference** - Transform PDF coordinates to WGS84 using municipality centroids

---

## Stage 1: Download (`pdf_downloader.py`)

### Process

The downloader fetches the official district map PDFs from the CEE SharePoint system.

```bash
python analysis/pdf_downloader.py --output-dir data/pdf_maps
```

### Data Source

- **Source URL**: `https://ww2.ceepur.org/Home/MapasDistritosRepresentativos`
- **JSON Endpoint**: `https://ww2.ceepur.org/Data/.Mapas%20Distrito%20Representativos.json`
- **Total PDFs**: 40 (one per representative district)

### Output

```
data/pdf_maps/
  distrito_01.pdf
  distrito_02.pdf
  ...
  distrito_40.pdf
  pdf_inventory.json    # Metadata index
```

The inventory JSON contains:
- Original filenames from CEE
- Download timestamps
- File sizes
- Download success status

---

## Stage 2: Vector Extraction (`pdf_extractor.py`)

### Process

The extractor parses each PDF to extract vector curve paths that represent precinct boundaries.

```bash
python analysis/pdf_extractor.py --input-dir data/pdf_maps
```

### How It Works

1. **Open PDF** using pdfplumber library
2. **Extract curves** - PDF vector paths with fill colors
3. **Filter paths**:
   - Skip non-filled curves (outlines only)
   - Skip paths with fewer than 50 points (noise)
   - Skip white/near-white fills (background)
4. **Group by color** - Each fill color typically represents one precinct
5. **Extract text labels** - Municipality names and precinct codes from PDF text layer

### Technical Details

The CEE maps use colored fills to distinguish precincts:
- Each precinct has a unique fill color (e.g., `#ffeabe`, `#fcbfbd`)
- Colors are consistent within each district map
- Precinct boundaries are encoded as closed vector paths

**Coordinate System**: At this stage, coordinates are in PDF space (points, origin at bottom-left).

### Output

```
data/pdf_maps/extracted/
  distrito_01_paths.geojson
  distrito_02_paths.geojson
  ...
  extraction_summary.json
```

Each GeoJSON contains:
- **Features**: One per precinct (by color)
- **Properties**: District number, color, point count
- **Geometry**: Polygon/MultiPolygon in PDF coordinates
- **Metadata**: Page dimensions, extracted text labels

---

## Stage 3: Georeferencing (`pdf_georeferencer.py`)

### Process

The georeferencer transforms PDF coordinates to WGS84 geographic coordinates using control points.

```bash
python analysis/pdf_georeferencer.py --input-dir data/pdf_maps
```

### Approach

#### Control Point Extraction

1. **Extract text with positions** from PDF (municipality labels)
2. **Match labels to centroids** using a pre-built municipality centroid file
3. **Create control point pairs** (PDF x,y -> geographic lon,lat)

#### Transformation Methods

**Affine Transform** (preferred, requires 3+ control points):
- Uses least squares to compute 6-parameter affine matrix
- Accounts for scale, rotation, and translation
- Applied when 3 or more distinct municipality labels are found

**Bounds Fallback** (for single-municipality districts):
- Uses known bounding boxes for major municipalities
- Maps PDF page extent to geographic extent
- Applied when only 1-2 control points are available

The bounds fallback covers these municipalities:
- San Juan, Bayamon, Ponce, Caguas, Carolina
- Mayaguez, Guaynabo, Toa Baja, Catano, Trujillo Alto

### Output

```
data/pdf_maps/georeferenced/
  distrito_01_wgs84.geojson
  distrito_02_wgs84.geojson
  ...
  georeferencing_summary.json
```

Each georeferenced GeoJSON contains:
- **CRS**: EPSG:4326 (WGS84)
- **Features**: Precinct polygons with geographic coordinates
- **Metadata**: Control points used, transformation matrix, error estimates

---

## Accuracy Limitations

### Error Analysis

Based on the georeferencing summary, transformation errors vary by district:

| Metric | Value |
|--------|-------|
| Average error | ~5 km |
| Best case | <2 km (districts with many control points) |
| Worst case | ~25 km (districts spanning large areas) |

### Factors Affecting Accuracy

1. **Control point density** - More municipality labels = better fit
2. **District extent** - Larger districts have more distortion
3. **Label placement** - Labels may not be at exact centroids
4. **PDF resolution** - Vector coordinate precision limits

### Known Limitations

1. **Single-municipality districts** use bounds fallback (less accurate)
2. **Multi-municipality districts** may have significant error at edges
3. **No ground truth** - Cannot validate against official boundaries
4. **Approximate only** - Suitable for visualization, not precision mapping

### Recommended Use Cases

- **Appropriate**: Visualization, approximate spatial analysis, identifying general precinct locations
- **Not recommended**: Precise boundary determination, legal or regulatory use, high-precision GIS analysis

---

## Data Quality Notes

### What This Data Represents

- **Source year**: 2022 (based on CEE website organization)
- **Coverage**: All 40 representative districts
- **Precincts extracted**: 114 total across all districts

### Comparison with 2016 Data

| Attribute | 2016 (MGGG) | 2022 (PDF Extraction) |
|-----------|-------------|----------------------|
| Source | MGGG shapefiles | CEE PDF maps |
| Format | Shapefile | GeoJSON |
| Accuracy | High (digitized) | Approximate (~5km) |
| Districts | 110 | 114 |
| Use case | Precise analysis | Visualization/estimates |

---

## Running the Full Pipeline

```bash
# 1. Download PDFs
python analysis/pdf_downloader.py

# 2. Extract vector paths
python analysis/pdf_extractor.py

# 3. Georeference to WGS84
python analysis/pdf_georeferencer.py

# 4. Create crosswalk (optional)
python analysis/precinct_crosswalk.py --crosswalk-2022
```

### Dependencies

```
pdfplumber   # PDF parsing
numpy        # Affine transformation
geopandas    # Optional, for crosswalk creation
```

---

## File Reference

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `pdf_downloader.py` | Download CEE PDFs | CEE website | `data/pdf_maps/*.pdf` |
| `pdf_extractor.py` | Extract vector paths | PDF files | `data/pdf_maps/extracted/*.geojson` |
| `pdf_georeferencer.py` | Convert to WGS84 | Extracted GeoJSON | `data/pdf_maps/georeferenced/*.geojson` |

---

## Related Documentation

- [Data Dictionary](DATA_DICTIONARY.md) - Field descriptions for crosswalk data
- [Methodology](METHODOLOGY.md) - Overall data processing methodology
- [Data Provenance](DATA_PROVENANCE.md) - Source documentation for all datasets
