# prelecciones

Access Puerto Rico electoral data from Python.

## Installation

```bash
pip install prelecciones
```

## Quick Start

```python
import prelecciones as pre

# List all available electoral events
events = pre.list_events()
print(events)

# Get results for a specific election
results = pre.get_results("2020-general")
print(results.head())

# Get municipality-level results with geometry
results_geo = pre.get_results(
    "2020-general",
    level="municipality",
    include_geometry=True
)
```

## API Reference

### `list_events(include_geometry=False)`

Returns a DataFrame with all available electoral events.

**Parameters:**
- `include_geometry` (bool): Include geographic boundary information

**Returns:** `pandas.DataFrame`

### `get_results(event_id, level="precinct", include_geometry=False)`

Get election results for a specific event.

**Parameters:**
- `event_id` (str): Unique identifier for the electoral event
- `level` (str): Geographic aggregation level ("precinct", "municipality", "district", "island")
- `include_geometry` (bool): Include geographic boundaries (requires geopandas)

**Returns:** `pandas.DataFrame` or `geopandas.GeoDataFrame`

### `set_data_path(path)`

Set the path to the processed data directory.

## License

MIT
