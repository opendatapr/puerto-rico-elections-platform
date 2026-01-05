"""Puerto Rico Elections Platform - Scraper Module"""

from .schema import (
    ElectoralEvent,
    ContestResult,
    VoteResult,
    GeographicUnit,
    Candidate,
    ScrapedPage,
    EventType,
    OfficeType,
    Party,
    PR_MUNICIPALITIES,
)

from .cee_scraper import CEEScraper

__all__ = [
    "CEEScraper",
    "ElectoralEvent",
    "ContestResult",
    "VoteResult",
    "GeographicUnit",
    "Candidate",
    "ScrapedPage",
    "EventType",
    "OfficeType",
    "Party",
    "PR_MUNICIPALITIES",
]
