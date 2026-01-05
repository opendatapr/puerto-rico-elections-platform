"""
prelecciones - Access Puerto Rico electoral data.

This package provides easy access to Puerto Rico electoral data,
including election results and event information.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Union

import pandas as pd

__version__ = "0.1.0"
__all__ = ["list_events", "get_results", "set_data_path"]

# Default data path relative to repository root
_DATA_PATH: Optional[Path] = None


def _get_data_path() -> Path:
    """Get the path to the processed data directory."""
    global _DATA_PATH
    if _DATA_PATH is not None:
        return _DATA_PATH

    # Try to find data relative to this package
    # First, check if we're in a development environment
    package_dir = Path(__file__).parent
    repo_root = package_dir.parent.parent.parent.parent
    processed_dir = repo_root / "data" / "processed"

    if processed_dir.exists():
        return processed_dir

    # Fallback: look for data in current working directory
    cwd_data = Path.cwd() / "data" / "processed"
    if cwd_data.exists():
        return cwd_data

    raise FileNotFoundError(
        "Could not find data directory. "
        "Use set_data_path() to specify the location of processed data."
    )


def set_data_path(path: Union[str, Path]) -> None:
    """
    Set the path to the processed data directory.

    Parameters
    ----------
    path : str or Path
        Path to the directory containing processed electoral data.

    Examples
    --------
    >>> import prelecciones as pre
    >>> pre.set_data_path("/path/to/data/processed")
    """
    global _DATA_PATH
    _DATA_PATH = Path(path)
    if not _DATA_PATH.exists():
        raise FileNotFoundError(f"Data path does not exist: {_DATA_PATH}")


def list_events(include_geometry: bool = False) -> pd.DataFrame:
    """
    List all available electoral events.

    Returns a DataFrame containing information about all electoral events
    in the dataset, including event IDs, dates, types, and descriptions.

    Parameters
    ----------
    include_geometry : bool, default False
        If True, include geographic boundary information for events
        that have spatial data available.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - event_id: Unique identifier for the event
        - date: Date of the election
        - type: Type of election (e.g., "general", "primary", "special")
        - description: Human-readable description of the event
        - has_geometry: Whether spatial data is available (if include_geometry=True)

    Examples
    --------
    >>> import prelecciones as pre
    >>> events = pre.list_events()
    >>> events.head()

    >>> # Include geometry information
    >>> events_geo = pre.list_events(include_geometry=True)
    """
    data_path = _get_data_path()

    # Look for events index file
    events_file = data_path / "events.json"
    events_parquet = data_path / "events.parquet"

    if events_parquet.exists():
        df = pd.read_parquet(events_parquet)
    elif events_file.exists():
        with open(events_file, "r", encoding="utf-8") as f:
            events_data = json.load(f)
        df = pd.DataFrame(events_data)
    else:
        # Return empty DataFrame with expected schema if no data exists yet
        df = pd.DataFrame(columns=["event_id", "date", "type", "description"])

    if not include_geometry and "geometry" in df.columns:
        df = df.drop(columns=["geometry"])

    return df


def get_results(
    event_id: str,
    *,
    level: str = "precinct",
    include_geometry: bool = False,
) -> pd.DataFrame:
    """
    Get election results for a specific event.

    Retrieves detailed election results including vote counts by candidate,
    party, and geographic unit.

    Parameters
    ----------
    event_id : str
        The unique identifier for the electoral event.
        Use list_events() to see available event IDs.
    level : str, default "precinct"
        Geographic aggregation level for results. Options:
        - "precinct": Most granular level
        - "municipality": Aggregated by municipality
        - "district": Aggregated by legislative district
        - "island": Island-wide totals
    include_geometry : bool, default False
        If True, include GeoDataFrame with geographic boundaries.
        Requires geopandas to be installed.

    Returns
    -------
    pd.DataFrame or geopandas.GeoDataFrame
        DataFrame with election results. Columns vary by event type but
        typically include:
        - geographic identifiers (precinct_id, municipality, etc.)
        - candidate/party names
        - vote counts
        - percentages

    Raises
    ------
    ValueError
        If event_id is not found or level is invalid.

    Examples
    --------
    >>> import prelecciones as pre
    >>>
    >>> # Get precinct-level results
    >>> results = pre.get_results("2020-general")
    >>>
    >>> # Get municipality-level results with geometry
    >>> results_geo = pre.get_results(
    ...     "2020-general",
    ...     level="municipality",
    ...     include_geometry=True
    ... )
    """
    valid_levels = {"precinct", "municipality", "district", "island"}
    if level not in valid_levels:
        raise ValueError(
            f"Invalid level '{level}'. Must be one of: {', '.join(sorted(valid_levels))}"
        )

    data_path = _get_data_path()

    # Look for results file
    results_parquet = data_path / f"{event_id}" / f"results_{level}.parquet"
    results_json = data_path / f"{event_id}" / f"results_{level}.json"

    # Also check flat file structure
    flat_parquet = data_path / f"{event_id}_{level}.parquet"
    flat_json = data_path / f"{event_id}_{level}.json"

    df: Optional[pd.DataFrame] = None

    if results_parquet.exists():
        df = pd.read_parquet(results_parquet)
    elif flat_parquet.exists():
        df = pd.read_parquet(flat_parquet)
    elif results_json.exists():
        with open(results_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    elif flat_json.exists():
        with open(flat_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    else:
        # Check if event exists at all
        event_dir = data_path / event_id
        if not event_dir.exists() and not any(
            f.name.startswith(event_id) for f in data_path.glob("*")
        ):
            raise ValueError(
                f"Event '{event_id}' not found. Use list_events() to see available events."
            )
        # Event exists but level not available
        raise ValueError(
            f"Results at level '{level}' not available for event '{event_id}'."
        )

    if include_geometry and df is not None:
        try:
            import geopandas as gpd

            # Look for geometry file
            geo_file = data_path / f"{event_id}" / f"geometry_{level}.geojson"
            flat_geo = data_path / f"geometry_{level}.geojson"

            if geo_file.exists():
                gdf = gpd.read_file(geo_file)
            elif flat_geo.exists():
                gdf = gpd.read_file(flat_geo)
            else:
                # No geometry available, return regular DataFrame
                return df

            # Merge geometry with results
            # Assuming there's a common key column
            key_col = f"{level}_id" if f"{level}_id" in df.columns else df.columns[0]
            geo_key = key_col if key_col in gdf.columns else gdf.columns[0]

            df = gdf.merge(df, left_on=geo_key, right_on=key_col, how="right")

        except ImportError:
            import warnings
            warnings.warn(
                "geopandas is required for include_geometry=True. "
                "Install with: pip install geopandas"
            )

    return df
