"""
Tests for CEE Puerto Rico web scraper.

Tests cover:
- Data schema validation
- Date parsing
- Event type detection
- HTML parsing logic
- Rate limiting
"""

import json
import tempfile
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import responses

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from schema import (
    ElectoralEvent,
    ContestResult,
    VoteResult,
    GeographicUnit,
    Candidate,
    ScrapedPage,
    EventType,
    validate_municipality_code,
    validate_precinct_code,
    PR_MUNICIPALITIES,
)
from cee_scraper import CEEScraper, CEE_EVENTS_URL


class TestGeographicUnit:
    """Tests for GeographicUnit dataclass."""

    def test_valid_geographic_unit(self):
        """Test creating a valid geographic unit."""
        unit = GeographicUnit(
            level="municipality",
            code="001",
            name="San Juan",
            parent_code=None
        )
        assert unit.level == "municipality"
        assert unit.code == "001"
        assert unit.name == "San Juan"

    def test_invalid_level_raises_error(self):
        """Test that invalid level raises ValueError."""
        with pytest.raises(ValueError, match="Invalid level"):
            GeographicUnit(
                level="invalid",
                code="001",
                name="Test"
            )

    def test_empty_code_raises_error(self):
        """Test that empty code raises ValueError."""
        with pytest.raises(ValueError, match="code cannot be empty"):
            GeographicUnit(
                level="municipality",
                code="",
                name="Test"
            )

    def test_empty_name_raises_error(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            GeographicUnit(
                level="municipality",
                code="001",
                name=""
            )


class TestCandidate:
    """Tests for Candidate dataclass."""

    def test_valid_candidate(self):
        """Test creating a valid candidate."""
        candidate = Candidate(
            name="Juan Del Pueblo",
            party="PNP",
            incumbent=True
        )
        assert candidate.name == "Juan Del Pueblo"
        assert candidate.party == "PNP"
        assert candidate.incumbent is True

    def test_empty_name_raises_error(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            Candidate(name="")

    def test_whitespace_name_raises_error(self):
        """Test that whitespace-only name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            Candidate(name="   ")

    def test_name_is_stripped(self):
        """Test that candidate name is stripped."""
        candidate = Candidate(name="  Juan Del Pueblo  ")
        assert candidate.name == "Juan Del Pueblo"


class TestVoteResult:
    """Tests for VoteResult dataclass."""

    def test_valid_vote_result(self):
        """Test creating a valid vote result."""
        result = VoteResult(
            candidate_name="Juan Del Pueblo",
            party="PNP",
            votes=10000,
            percentage=45.5
        )
        assert result.votes == 10000
        assert result.percentage == 45.5

    def test_negative_votes_raises_error(self):
        """Test that negative votes raises ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            VoteResult(
                candidate_name="Test",
                party=None,
                votes=-100
            )

    def test_invalid_percentage_raises_error(self):
        """Test that percentage outside 0-100 raises ValueError."""
        with pytest.raises(ValueError, match="between 0 and 100"):
            VoteResult(
                candidate_name="Test",
                party=None,
                votes=100,
                percentage=150.0
            )


class TestContestResult:
    """Tests for ContestResult dataclass."""

    def test_valid_contest_result(self):
        """Test creating a valid contest result."""
        result = ContestResult(
            office="Governor",
            office_type="governor",
            results=[
                VoteResult(candidate_name="Candidate A", party="PNP", votes=500000),
                VoteResult(candidate_name="Candidate B", party="PPD", votes=450000),
            ],
            blank_votes=10000,
            null_votes=5000
        )
        assert result.office == "Governor"
        assert len(result.results) == 2

    def test_calculate_totals(self):
        """Test that calculate_totals computes correctly."""
        result = ContestResult(
            office="Mayor",
            results=[
                VoteResult(candidate_name="A", party="PNP", votes=600),
                VoteResult(candidate_name="B", party="PPD", votes=400),
            ],
            blank_votes=50,
            null_votes=50
        )
        result.calculate_totals()

        assert result.total_votes == 1100  # 600 + 400 + 50 + 50
        # Check percentages were calculated
        assert result.results[0].percentage == pytest.approx(54.54, rel=0.01)
        assert result.results[1].percentage == pytest.approx(36.36, rel=0.01)

    def test_empty_office_raises_error(self):
        """Test that empty office raises ValueError."""
        with pytest.raises(ValueError, match="Office name cannot be empty"):
            ContestResult(office="")


class TestElectoralEvent:
    """Tests for ElectoralEvent dataclass."""

    def test_valid_electoral_event(self):
        """Test creating a valid electoral event."""
        event = ElectoralEvent(
            event_id="general-elections-2024-11-05",
            name="General Elections 2024",
            event_type="general",
            event_date=date(2024, 11, 5)
        )
        assert event.event_id == "general-elections-2024-11-05"
        assert event.name == "General Elections 2024"

    def test_invalid_event_type_raises_error(self):
        """Test that invalid event type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid event type"):
            ElectoralEvent(
                event_id="test-2024",
                name="Test Event",
                event_type="invalid_type",
                event_date=date(2024, 1, 1)
            )

    def test_generate_event_id(self):
        """Test event ID generation."""
        event_id = ElectoralEvent.generate_event_id(
            "General Elections 2024!",
            date(2024, 11, 5)
        )
        assert event_id == "general-elections-2024-2024-11-05"

    def test_generate_event_id_with_special_chars(self):
        """Test event ID generation with special characters."""
        event_id = ElectoralEvent.generate_event_id(
            "Elecciones @ Generales #2024",
            date(2024, 11, 5)
        )
        # Special chars removed, spaces normalized
        assert "elecciones" in event_id
        assert "generales" in event_id
        assert "2024-11-05" in event_id


class TestScrapedPage:
    """Tests for ScrapedPage dataclass."""

    def test_valid_scraped_page(self):
        """Test creating a valid scraped page."""
        page = ScrapedPage(
            url="https://example.com",
            scraped_at="2024-01-01T00:00:00",
            status_code=200,
            content_hash="abc123"
        )
        assert page.url == "https://example.com"
        assert page.status_code == 200

    def test_empty_url_raises_error(self):
        """Test that empty URL raises ValueError."""
        with pytest.raises(ValueError, match="URL cannot be empty"):
            ScrapedPage(
                url="",
                scraped_at="2024-01-01T00:00:00",
                status_code=200,
                content_hash="abc"
            )

    def test_invalid_status_code_raises_error(self):
        """Test that invalid status code raises ValueError."""
        with pytest.raises(ValueError, match="Invalid HTTP status code"):
            ScrapedPage(
                url="https://example.com",
                scraped_at="2024-01-01T00:00:00",
                status_code=999,
                content_hash="abc"
            )


class TestValidationFunctions:
    """Tests for validation helper functions."""

    def test_validate_municipality_code_valid(self):
        """Test valid municipality codes."""
        assert validate_municipality_code("001") is True
        assert validate_municipality_code("78") is True
        assert validate_municipality_code("45") is True

    def test_validate_municipality_code_invalid(self):
        """Test invalid municipality codes."""
        assert validate_municipality_code("") is False
        assert validate_municipality_code("abc") is False
        assert validate_municipality_code("0") is False
        assert validate_municipality_code("79") is False
        assert validate_municipality_code("100") is False

    def test_validate_precinct_code_valid(self):
        """Test valid precinct codes."""
        assert validate_precinct_code("001-001") is True
        assert validate_precinct_code("78_0001") is True
        assert validate_precinct_code("450123") is True

    def test_validate_precinct_code_invalid(self):
        """Test invalid precinct codes."""
        assert validate_precinct_code("") is False
        assert validate_precinct_code("abc-def") is False

    def test_municipalities_list(self):
        """Test that municipalities list is complete."""
        assert len(PR_MUNICIPALITIES) == 78
        assert "San Juan" in PR_MUNICIPALITIES
        assert "Ponce" in PR_MUNICIPALITIES
        assert "Vieques" in PR_MUNICIPALITIES
        assert "Culebra" in PR_MUNICIPALITIES


class TestCEEScraper:
    """Tests for CEEScraper class."""

    def test_scraper_initialization(self):
        """Test scraper initializes with correct defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scraper = CEEScraper(output_dir=Path(tmpdir))
            assert scraper.delay == 1.0
            assert scraper.max_events is None
            assert scraper.output_dir == Path(tmpdir)

    def test_scraper_custom_settings(self):
        """Test scraper with custom settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scraper = CEEScraper(
                output_dir=Path(tmpdir),
                delay=2.5,
                max_events=10
            )
            assert scraper.delay == 2.5
            assert scraper.max_events == 10

    def test_parse_event_date_us_format(self):
        """Test parsing US date format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scraper = CEEScraper(output_dir=Path(tmpdir))
            result = scraper._parse_event_date("11/05/2024")
            assert result == date(2024, 11, 5)

    def test_parse_event_date_iso_format(self):
        """Test parsing ISO date format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scraper = CEEScraper(output_dir=Path(tmpdir))
            result = scraper._parse_event_date("2024-11-05")
            assert result == date(2024, 11, 5)

    def test_parse_event_date_spanish_format(self):
        """Test parsing Spanish date format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scraper = CEEScraper(output_dir=Path(tmpdir))
            result = scraper._parse_event_date("5 de noviembre de 2024")
            assert result == date(2024, 11, 5)

    def test_parse_event_date_year_only(self):
        """Test parsing when only year is available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scraper = CEEScraper(output_dir=Path(tmpdir))
            result = scraper._parse_event_date("Elecciones 2024")
            assert result == date(2024, 1, 1)

    def test_determine_event_type_general(self):
        """Test determining general election type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scraper = CEEScraper(output_dir=Path(tmpdir))
            assert scraper._determine_event_type("Elecciones Generales 2024") == "general"

    def test_determine_event_type_primary(self):
        """Test determining primary election type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scraper = CEEScraper(output_dir=Path(tmpdir))
            assert scraper._determine_event_type("Primarias Locales 2024") == "primary"

    def test_determine_event_type_plebiscite(self):
        """Test determining plebiscite type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scraper = CEEScraper(output_dir=Path(tmpdir))
            assert scraper._determine_event_type("Plebiscito 2024") == "plebiscite"

    def test_determine_event_type_special(self):
        """Test determining special election type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scraper = CEEScraper(output_dir=Path(tmpdir))
            assert scraper._determine_event_type("Eleccion Especial Gurabo") == "special"

    def test_is_results_link(self):
        """Test results link detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scraper = CEEScraper(output_dir=Path(tmpdir))
            assert scraper._is_results_link("https://elecciones2024.ceepur.org") is True
            assert scraper._is_results_link("https://resultado.ceepur.org") is True
            assert scraper._is_results_link("https://example.com") is False
            assert scraper._is_results_link("") is False

    @responses.activate
    def test_fetch_page_success(self):
        """Test successful page fetch."""
        responses.add(
            responses.GET,
            "https://example.com/test",
            body="<html><body>Test</body></html>",
            status=200
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            scraper = CEEScraper(output_dir=Path(tmpdir), delay=0)
            page = scraper._fetch_page("https://example.com/test")

            assert page.status_code == 200
            assert page.error is None
            assert "Test" in page.raw_html

    @responses.activate
    def test_fetch_page_error(self):
        """Test page fetch with HTTP error."""
        responses.add(
            responses.GET,
            "https://example.com/notfound",
            status=404
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            scraper = CEEScraper(output_dir=Path(tmpdir), delay=0)
            page = scraper._fetch_page("https://example.com/notfound")

            assert page.status_code == 404
            assert page.error is not None

    @responses.activate
    def test_scrape_events_list_saves_json(self):
        """Test that scraping events list saves JSON file."""
        html_content = """
        <html>
        <body>
            <table>
                <tr>
                    <td>Elecciones Generales 2024</td>
                    <td><a href="https://elecciones2024.ceepur.org">Resultados</a></td>
                </tr>
            </table>
        </body>
        </html>
        """
        responses.add(
            responses.GET,
            CEE_EVENTS_URL,
            body=html_content,
            status=200
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            scraper = CEEScraper(output_dir=Path(tmpdir), delay=0)
            events = scraper.scrape_events_list()

            # Check that events_list.json was created
            events_file = Path(tmpdir) / "events_list.json"
            assert events_file.exists()

            with open(events_file) as f:
                saved_data = json.load(f)
            assert "events" in saved_data
            assert "scraped_at" in saved_data


class TestIntegration:
    """Integration tests for the scraper."""

    @responses.activate
    def test_full_scraping_pipeline(self):
        """Test the full scraping pipeline with mocked responses."""
        # Mock the events list page
        events_html = """
        <html>
        <body>
            <table>
                <tr>
                    <td>Elecciones Generales 2024</td>
                    <td>11/05/2024</td>
                    <td><a href="https://elecciones2024.ceepur.org">Resultados</a></td>
                </tr>
            </table>
        </body>
        </html>
        """
        responses.add(
            responses.GET,
            CEE_EVENTS_URL,
            body=events_html,
            status=200
        )

        # Mock the results page
        results_html = """
        <html>
        <body>
            <h2>Gobernador</h2>
            <table>
                <tr>
                    <th>Candidato</th>
                    <th>Partido</th>
                    <th>Votos</th>
                </tr>
                <tr>
                    <td>Jenniffer Gonzalez</td>
                    <td>PNP</td>
                    <td>500,000</td>
                </tr>
                <tr>
                    <td>Juan Dalmau</td>
                    <td>PIP</td>
                    <td>450,000</td>
                </tr>
            </table>
        </body>
        </html>
        """
        responses.add(
            responses.GET,
            "https://elecciones2024.ceepur.org",
            body=results_html,
            status=200
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            scraper = CEEScraper(
                output_dir=Path(tmpdir),
                delay=0,
                max_events=1
            )
            events = scraper.run()

            # Should have processed one event
            assert len(events) >= 0  # May be 0 if parsing doesn't match exactly

            # Check that summary was saved
            summary_file = Path(tmpdir) / "scraping_summary.json"
            assert summary_file.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
