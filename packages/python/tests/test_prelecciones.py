"""Tests for the prelecciones package."""

import json
import tempfile
from pathlib import Path

import pandas as pd
import pytest

import prelecciones as pre


@pytest.fixture
def sample_data_dir(tmp_path: Path) -> Path:
    """Create a temporary data directory with sample data."""
    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True)

    # Create sample events
    events = [
        {
            "event_id": "2020-general",
            "date": "2020-11-03",
            "type": "general",
            "description": "2020 General Election",
        },
        {
            "event_id": "2020-primary",
            "date": "2020-08-09",
            "type": "primary",
            "description": "2020 Primary Election",
        },
    ]
    events_file = processed_dir / "events.json"
    with open(events_file, "w", encoding="utf-8") as f:
        json.dump(events, f)

    # Create sample results directory
    event_dir = processed_dir / "2020-general"
    event_dir.mkdir()

    results = [
        {
            "precinct_id": "001-001",
            "municipality": "San Juan",
            "candidate": "Candidate A",
            "party": "PNP",
            "votes": 1500,
        },
        {
            "precinct_id": "001-001",
            "municipality": "San Juan",
            "candidate": "Candidate B",
            "party": "PPD",
            "votes": 1200,
        },
        {
            "precinct_id": "001-002",
            "municipality": "San Juan",
            "candidate": "Candidate A",
            "party": "PNP",
            "votes": 800,
        },
        {
            "precinct_id": "001-002",
            "municipality": "San Juan",
            "candidate": "Candidate B",
            "party": "PPD",
            "votes": 950,
        },
    ]
    results_file = event_dir / "results_precinct.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f)

    return processed_dir


class TestListEvents:
    """Tests for list_events function."""

    def test_list_events_returns_dataframe(self, sample_data_dir: Path) -> None:
        """Test that list_events returns a DataFrame."""
        pre.set_data_path(sample_data_dir)
        events = pre.list_events()

        assert isinstance(events, pd.DataFrame)
        assert len(events) == 2

    def test_list_events_has_expected_columns(self, sample_data_dir: Path) -> None:
        """Test that list_events returns expected columns."""
        pre.set_data_path(sample_data_dir)
        events = pre.list_events()

        expected_columns = {"event_id", "date", "type", "description"}
        assert expected_columns.issubset(set(events.columns))

    def test_list_events_content(self, sample_data_dir: Path) -> None:
        """Test that list_events returns correct content."""
        pre.set_data_path(sample_data_dir)
        events = pre.list_events()

        assert "2020-general" in events["event_id"].values
        assert "2020-primary" in events["event_id"].values


class TestGetResults:
    """Tests for get_results function."""

    def test_get_results_returns_dataframe(self, sample_data_dir: Path) -> None:
        """Test that get_results returns a DataFrame."""
        pre.set_data_path(sample_data_dir)
        results = pre.get_results("2020-general")

        assert isinstance(results, pd.DataFrame)
        assert len(results) == 4

    def test_get_results_has_expected_data(self, sample_data_dir: Path) -> None:
        """Test that get_results returns expected data."""
        pre.set_data_path(sample_data_dir)
        results = pre.get_results("2020-general")

        assert "precinct_id" in results.columns
        assert "votes" in results.columns
        assert results["votes"].sum() == 4450

    def test_get_results_invalid_event(self, sample_data_dir: Path) -> None:
        """Test that get_results raises error for invalid event."""
        pre.set_data_path(sample_data_dir)

        with pytest.raises(ValueError, match="not found"):
            pre.get_results("invalid-event")

    def test_get_results_invalid_level(self, sample_data_dir: Path) -> None:
        """Test that get_results raises error for invalid level."""
        pre.set_data_path(sample_data_dir)

        with pytest.raises(ValueError, match="Invalid level"):
            pre.get_results("2020-general", level="invalid")


class TestSetDataPath:
    """Tests for set_data_path function."""

    def test_set_data_path_valid(self, sample_data_dir: Path) -> None:
        """Test setting a valid data path."""
        pre.set_data_path(sample_data_dir)
        # Should not raise
        events = pre.list_events()
        assert len(events) >= 0

    def test_set_data_path_invalid(self) -> None:
        """Test setting an invalid data path raises error."""
        with pytest.raises(FileNotFoundError):
            pre.set_data_path("/nonexistent/path")


class TestVersion:
    """Tests for package version."""

    def test_version_exists(self) -> None:
        """Test that version is defined."""
        assert hasattr(pre, "__version__")
        assert isinstance(pre.__version__, str)
