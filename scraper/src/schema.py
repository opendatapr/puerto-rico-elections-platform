"""
Data schema for Puerto Rico electoral data.

Defines dataclasses for electoral events, results, and geographic units
with validation methods.
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional
import re


class EventType(Enum):
    """Types of electoral events in Puerto Rico."""
    GENERAL = "general"
    PRIMARY = "primary"
    SPECIAL = "special"
    PLEBISCITE = "plebiscite"
    REFERENDUM = "referendum"


class OfficeType(Enum):
    """Types of elected offices."""
    GOVERNOR = "governor"
    RESIDENT_COMMISSIONER = "resident_commissioner"
    MAYOR = "mayor"
    SENATOR_AT_LARGE = "senator_at_large"
    SENATOR_DISTRICT = "senator_district"
    REPRESENTATIVE = "representative"
    LEGISLATOR_MUNICIPAL = "legislator_municipal"


class Party(Enum):
    """Political parties in Puerto Rico."""
    PNP = "Partido Nuevo Progresista"
    PPD = "Partido Popular Democratico"
    PIP = "Partido Independentista Puertorriqueno"
    MVC = "Movimiento Victoria Ciudadana"
    PD = "Proyecto Dignidad"
    INDEPENDENT = "Independiente"
    OTHER = "Otro"


@dataclass
class GeographicUnit:
    """
    Represents a geographic unit for electoral purposes.

    Puerto Rico's electoral geography:
    - Island-wide (for Governor, Resident Commissioner, At-Large Senators)
    - Senatorial Districts (8 districts)
    - Representative Districts (40 districts)
    - Municipalities (78 municipalities)
    - Precincts (within municipalities)
    - Electoral Units (within precincts)
    """
    level: str  # "island", "senatorial_district", "representative_district", "municipality", "precinct", "unit"
    code: str  # Official CEE code
    name: str
    parent_code: Optional[str] = None

    def __post_init__(self):
        """Validate geographic unit data."""
        valid_levels = {"island", "senatorial_district", "representative_district",
                       "municipality", "precinct", "unit"}
        if self.level not in valid_levels:
            raise ValueError(f"Invalid level: {self.level}. Must be one of {valid_levels}")

        if not self.code:
            raise ValueError("Geographic unit code cannot be empty")

        if not self.name:
            raise ValueError("Geographic unit name cannot be empty")


@dataclass
class Candidate:
    """Represents a candidate in an electoral contest."""
    name: str
    party: Optional[str] = None
    party_abbreviation: Optional[str] = None
    incumbent: bool = False

    def __post_init__(self):
        """Validate candidate data."""
        if not self.name or not self.name.strip():
            raise ValueError("Candidate name cannot be empty")
        self.name = self.name.strip()


@dataclass
class VoteResult:
    """
    Represents vote counts for a candidate or option in a specific geographic unit.
    """
    candidate_name: str
    party: Optional[str]
    votes: int
    percentage: Optional[float] = None

    def __post_init__(self):
        """Validate vote result data."""
        if self.votes < 0:
            raise ValueError(f"Vote count cannot be negative: {self.votes}")

        if self.percentage is not None and not (0 <= self.percentage <= 100):
            raise ValueError(f"Percentage must be between 0 and 100: {self.percentage}")


@dataclass
class ContestResult:
    """
    Results for a single electoral contest (e.g., Governor race, Mayor race).
    """
    office: str
    office_type: Optional[str] = None
    district: Optional[str] = None
    geographic_unit: Optional[GeographicUnit] = None
    results: list[VoteResult] = field(default_factory=list)
    total_votes: int = 0
    blank_votes: int = 0
    null_votes: int = 0
    registered_voters: Optional[int] = None
    participation_rate: Optional[float] = None

    def __post_init__(self):
        """Validate contest result data."""
        if not self.office:
            raise ValueError("Office name cannot be empty")

        if self.total_votes < 0:
            raise ValueError(f"Total votes cannot be negative: {self.total_votes}")

        if self.blank_votes < 0:
            raise ValueError(f"Blank votes cannot be negative: {self.blank_votes}")

        if self.null_votes < 0:
            raise ValueError(f"Null votes cannot be negative: {self.null_votes}")

    def calculate_totals(self):
        """Calculate total votes from individual results."""
        self.total_votes = sum(r.votes for r in self.results) + self.blank_votes + self.null_votes

        if self.total_votes > 0:
            for result in self.results:
                result.percentage = (result.votes / self.total_votes) * 100


@dataclass
class ElectoralEvent:
    """
    Represents an electoral event (election, primary, plebiscite, etc.).
    """
    event_id: str  # Unique identifier
    name: str
    event_type: str
    event_date: date
    description: Optional[str] = None
    source_url: Optional[str] = None
    results_url: Optional[str] = None
    contests: list[ContestResult] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate electoral event data."""
        if not self.event_id:
            raise ValueError("Event ID cannot be empty")

        if not self.name:
            raise ValueError("Event name cannot be empty")

        valid_types = {e.value for e in EventType}
        if self.event_type not in valid_types:
            raise ValueError(f"Invalid event type: {self.event_type}. Must be one of {valid_types}")

    @classmethod
    def generate_event_id(cls, name: str, event_date: date) -> str:
        """Generate a unique event ID from name and date."""
        # Normalize name: lowercase, replace spaces with hyphens, remove special chars
        normalized = re.sub(r'[^a-z0-9\s-]', '', name.lower())
        normalized = re.sub(r'\s+', '-', normalized.strip())
        return f"{normalized}-{event_date.isoformat()}"


@dataclass
class ScrapedPage:
    """Represents a scraped web page with metadata."""
    url: str
    scraped_at: str  # ISO format datetime
    status_code: int
    content_hash: str  # MD5 hash of content for change detection
    raw_html: Optional[str] = None
    extracted_data: Optional[dict] = None
    error: Optional[str] = None

    def __post_init__(self):
        """Validate scraped page data."""
        if not self.url:
            raise ValueError("URL cannot be empty")

        if self.status_code < 100 or self.status_code >= 600:
            raise ValueError(f"Invalid HTTP status code: {self.status_code}")


def validate_municipality_code(code: str) -> bool:
    """
    Validate a Puerto Rico municipality code.

    Puerto Rico has 78 municipalities, codes are typically 3-digit strings.
    """
    if not code:
        return False

    # Municipality codes are typically numeric strings
    if not code.isdigit():
        return False

    code_int = int(code)
    return 1 <= code_int <= 78


def validate_precinct_code(code: str) -> bool:
    """
    Validate a precinct code.

    Format: municipality_code + precinct_number (e.g., "001-001")
    """
    if not code:
        return False

    # Allow various formats
    pattern = r'^\d{1,3}[-_]?\d{1,4}$'
    return bool(re.match(pattern, code))


# Puerto Rico municipalities for reference
PR_MUNICIPALITIES = [
    "Adjuntas", "Aguada", "Aguadilla", "Aguas Buenas", "Aibonito",
    "Anasco", "Arecibo", "Arroyo", "Barceloneta", "Barranquitas",
    "Bayamon", "Cabo Rojo", "Caguas", "Camuy", "Canovanas",
    "Carolina", "Catano", "Cayey", "Ceiba", "Ciales",
    "Cidra", "Coamo", "Comerio", "Corozal", "Culebra",
    "Dorado", "Fajardo", "Florida", "Guanica", "Guayama",
    "Guayanilla", "Guaynabo", "Gurabo", "Hatillo", "Hormigueros",
    "Humacao", "Isabela", "Jayuya", "Juana Diaz", "Juncos",
    "Lajas", "Lares", "Las Marias", "Las Piedras", "Loiza",
    "Luquillo", "Manati", "Maricao", "Maunabo", "Mayaguez",
    "Moca", "Morovis", "Naguabo", "Naranjito", "Orocovis",
    "Patillas", "Penuelas", "Ponce", "Quebradillas", "Rincon",
    "Rio Grande", "Sabana Grande", "Salinas", "San German", "San Juan",
    "San Lorenzo", "San Sebastian", "Santa Isabel", "Toa Alta", "Toa Baja",
    "Trujillo Alto", "Utuado", "Vega Alta", "Vega Baja", "Vieques",
    "Villalba", "Yabucoa", "Yauco"
]
