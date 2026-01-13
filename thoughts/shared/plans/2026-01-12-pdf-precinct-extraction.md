# Plan: Extracting Precinct Boundaries from CEE PDF Maps

**Created:** 2026-01-12
**Updated:** 2026-01-13
**Status:** PHASES 1-3 COMPLETE
**Priority:** High (enables multi-year precinct analysis)

## Executive Summary

CEE (Comision Estatal de Elecciones) publishes precinct boundary maps as PDFs. Analysis confirms these are **vector PDFs** containing extractable path data (not raster images). This plan outlines how to extract geographic boundaries from these PDFs to enable precinct-level analysis for election years beyond 2016.

## Problem Statement

Currently, we only have precinct/district shapefiles from MGGG for 2016. CEE publishes official boundary maps for multiple redistricting cycles, but only as PDFs. To correlate census data with election results at the precinct level across multiple years, we need to extract these boundaries.

## Feasibility Analysis

### PDF Content Analysis (Distrito 01 - San Juan)

```
Source: https://ww2.ceepur.org/es-pr/Paginas/Mapas-Distritos-Representativos.aspx
File: Distrito Representativo Núm. 1 (579 KB)

Analysis Results:
- Format: PDF 1.6, 1 page
- Page size: 1224x792 points (17" x 11")
- Vector elements: 21 curves, 2 rectangles
- Largest curve: 4,998 points (boundary paths)
- Coordinate range: x(152-1179), y(91-598)
- Path commands: 'm' (moveto), 'l' (lineto)
- Colors: Fill colors distinguish precincts
```

### Key Finding

The PDF contains **vector paths**, not raster images. Each curve is a series of (x, y) coordinates that trace boundaries. Example path segment:
```python
[('m', (152.99, 193.67)),  # Start at point
 ('l', (152.63, 193.67)),  # Line to next point
 ('l', (152.63, 193.31)),  # Continue tracing
 ...]
```

This data can be extracted programmatically using `pdfplumber`.

## Implementation Plan

### Phase 1: PDF Inventory and Download

**Goal:** Catalog and download all available boundary PDFs from CEE

**Tasks:**
1. Scrape list of all district map PDFs from CEE website
2. Download all PDFs to `data/pdf_maps/`
3. Create metadata index (district number, year, file size, URL)

**CEE Source Pages:**
- Mapas Distritos Representativos: https://ww2.ceepur.org/es-pr/Paginas/Mapas-Distritos-Representativos.aspx
- Desglose de Sectores: https://ww2.ceepur.org/es-pr/Paginas/Desglose-de-Sectores-por-Precinto.aspx (text only, no boundaries)

**Output:**
- `data/pdf_maps/distrito_*.pdf` (40 district maps)
- `data/pdf_maps/pdf_inventory.json`

### Phase 2: Vector Path Extraction

**Goal:** Extract all boundary paths from PDFs as raw coordinates

**Tasks:**
1. Create `analysis/pdf_extractor.py` using pdfplumber
2. For each PDF:
   - Extract all curves with their coordinates
   - Identify boundary curves vs decorative elements (by size, color)
   - Store as intermediate format (GeoJSON with PDF coordinates)
3. Handle multi-path districts (precincts within districts)

**Technique:**
```python
import pdfplumber

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    for curve in page.curves:
        if curve['pts'] and len(curve['pts']) > 100:  # Significant paths
            path_coords = curve['pts']
            fill_color = curve['non_stroking_color']
            # Store for georeferencing
```

**Output:**
- `data/pdf_maps/extracted/distrito_*.geojson` (PDF coordinate system)

### Phase 3: Georeferencing

**Goal:** Transform PDF coordinates to geographic coordinates (WGS84)

**Challenge:** PDFs use arbitrary coordinate system. Must find control points.

**Approaches (in order of preference):**

#### Option A: Affine Transform with Control Points
1. Identify 4+ labeled locations on each map (municipality names, landmarks)
2. Look up their known coordinates from census TIGER data
3. Compute affine transformation matrix
4. Apply to all extracted paths

**Requirements:**
- PR municipality centroids (already have in census data)
- Text extraction to find labeled places on map

#### Option B: Corner Matching
1. Determine map extent from title/legend (e.g., "San Juan 001")
2. Use known municipality or district bounding box
3. Scale/translate PDF coords to fit known extent

#### Option C: Manual Ground Control Points
1. Open each PDF in QGIS
2. Manually identify 4 control points per map
3. Export transformation parameters
4. Apply programmatically to remaining maps

**Output:**
- `data/pdf_maps/georeferenced/distrito_*.geojson` (WGS84)
- `data/pdf_maps/transforms.json` (transformation parameters per district)

### Phase 4: Validation and Cleanup

**Goal:** Verify extracted boundaries match known geography

**Tasks:**
1. Overlay extracted boundaries on MGGG 2016 shapefiles (visual check)
2. Compare extracted precinct centroids to expected locations
3. Fix topology errors (gaps, overlaps, self-intersections)
4. Simplify geometries if needed (Douglas-Peucker)

**Tools:**
- geopandas for geometry operations
- shapely for topology validation
- QGIS for visual inspection

**Output:**
- `data/shapes/precincts_2022.shp` (or `.gpkg`)
- Validation report

### Phase 5: Integration

**Goal:** Add extracted boundaries to data platform

**Tasks:**
1. Create crosswalk to census geographies
2. Update `precinct_crosswalk.py` to use new shapefiles
3. Add to R/Python/JS packages
4. Update documentation

**Output:**
- `data/crosswalks/precinct_municipality_crosswalk_2022.parquet`
- Package updates

## Technical Dependencies

```
# Python packages needed
pdfplumber>=0.10.0    # PDF parsing (already installed)
geopandas>=0.14.0     # Geometry handling (already installed)
shapely>=2.0.0        # Topology operations (already installed)
pyproj>=3.6.0         # Coordinate transforms
rasterio>=1.3.0       # Optional: for control point extraction
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| PDFs are raster, not vector | Low (disproven) | High | Confirmed vector via analysis |
| Georeferencing accuracy poor | Medium | Medium | Use multiple control points, validate against known data |
| Different PDF structures per year | Medium | Low | Create flexible parser with fallbacks |
| CEE changes website | Low | Low | Download all PDFs upfront |
| Topology errors in extraction | High | Low | Use shapely validation and repair |

## Success Criteria

1. Extract boundaries from all 40 district PDFs
2. Georeferencing error < 100 meters (sufficient for precinct-level analysis)
3. All precincts have valid polygon geometry
4. Crosswalk links precincts to municipalities and census tracts

## Timeline Estimate

- Phase 1 (Download): 1 session
- Phase 2 (Extraction): 1-2 sessions
- Phase 3 (Georeferencing): 2-3 sessions (most complex)
- Phase 4 (Validation): 1 session
- Phase 5 (Integration): 1 session

Total: ~6-8 sessions

## Alternative Approaches

### If PDF extraction fails:

1. **Contact CEE directly** - Request official shapefiles via FOIA-equivalent
2. **Digitize manually** - Load PDFs in QGIS, trace boundaries by hand
3. **Use 2016 only** - Accept limitation of single-year precinct data
4. **Crowdsource** - Create tool for volunteers to trace boundaries

## Appendix: CEE PDF Inventory

Based on website analysis:

### Mapas Distritos Representativos
- 40 district maps (Distrito 01-40)
- Based on 2022 redistricting
- Each ~500KB-1MB
- Vector format confirmed

### Desglose de Sectores por Precinto
- 114 precinct breakdown PDFs
- Contains sector/neighborhood names
- **Does NOT contain boundary coordinates**
- Useful for: sector-to-precinct mapping

## References

- CEE Website: https://ww2.ceepur.org/
- MGGG PR Shapefiles: https://github.com/mggg-states/PR-shapefiles
- pdfplumber docs: https://github.com/jsvine/pdfplumber
- Georeferencing tutorial: https://docs.qgis.org/latest/en/docs/training_manual/forestry/map_georeferencing.html
