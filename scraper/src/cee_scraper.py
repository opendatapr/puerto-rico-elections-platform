"""
CEE Puerto Rico Web Scraper

Scrapes electoral data from the Puerto Rico State Electoral Commission (CEE).
Handles both modern subdomains and legacy URL formats.

Usage:
    python cee_scraper.py [--output-dir PATH] [--delay SECONDS] [--max-events N]

Example:
    python cee_scraper.py --output-dir data/raw --delay 1.5
"""

import argparse
import hashlib
import json
import logging
import re
import time
from dataclasses import asdict
from datetime import datetime, date
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from schema import (
    ElectoralEvent, ContestResult, VoteResult, GeographicUnit,
    ScrapedPage, EventType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
CEE_BASE_URL = "https://ww2.ceepur.org"
CEE_EVENTS_URL = f"{CEE_BASE_URL}/Home/EventosElectorales"
DEFAULT_DELAY = 1.0  # seconds between requests
DEFAULT_OUTPUT_DIR = Path("data/raw")
REQUEST_TIMEOUT = 30  # seconds

# User agent to identify our scraper
USER_AGENT = (
    "Puerto Rico Elections Platform Scraper/1.0 "
    "(https://github.com/opendatapr/puerto-rico-elections-platform)"
)


class CEEScraper:
    """
    Scraper for Puerto Rico State Electoral Commission (CEE) website.

    Handles rate limiting, error recovery, and data extraction from
    both modern and legacy CEE website formats.
    """

    def __init__(
        self,
        output_dir: Path = DEFAULT_OUTPUT_DIR,
        delay: float = DEFAULT_DELAY,
        max_events: Optional[int] = None
    ):
        """
        Initialize the scraper.

        Args:
            output_dir: Directory to save scraped data
            delay: Delay between requests in seconds
            max_events: Maximum number of events to scrape (None for all)
        """
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.max_events = max_events
        self.session = self._create_session()
        self._last_request_time = 0.0

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _create_session(self) -> requests.Session:
        """Create a requests session with appropriate headers."""
        session = requests.Session()
        session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-PR,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })
        return session

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.delay:
            sleep_time = self.delay - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self._last_request_time = time.time()

    def _fetch_page(self, url: str) -> ScrapedPage:
        """
        Fetch a web page with error handling.

        Args:
            url: URL to fetch

        Returns:
            ScrapedPage object with content and metadata
        """
        self._rate_limit()

        scraped_at = datetime.utcnow().isoformat()
        logger.info(f"Fetching: {url}")

        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            content = response.text
            content_hash = hashlib.md5(content.encode()).hexdigest()

            return ScrapedPage(
                url=url,
                scraped_at=scraped_at,
                status_code=response.status_code,
                content_hash=content_hash,
                raw_html=content,
                error=None if response.ok else f"HTTP {response.status_code}"
            )

        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return ScrapedPage(
                url=url,
                scraped_at=scraped_at,
                status_code=0,
                content_hash="",
                error=str(e)
            )

    def _parse_event_date(self, date_text: str) -> Optional[date]:
        """
        Parse date from various formats used by CEE.

        Args:
            date_text: Date string to parse

        Returns:
            date object or None if parsing fails
        """
        # Common date patterns
        patterns = [
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%m/%d/%Y'),  # 11/05/2024
            (r'(\d{4})-(\d{2})-(\d{2})', '%Y-%m-%d'),      # 2024-11-05
            (r'(\d{1,2}) de (\w+) de (\d{4})', None),      # Spanish format
        ]

        # Spanish month names
        spanish_months = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }

        date_text = date_text.strip()

        # Try standard patterns
        for pattern, date_format in patterns:
            match = re.search(pattern, date_text, re.IGNORECASE)
            if match:
                if date_format:
                    try:
                        return datetime.strptime(match.group(0), date_format).date()
                    except ValueError:
                        continue
                else:
                    # Spanish format
                    day, month_name, year = match.groups()
                    month = spanish_months.get(month_name.lower())
                    if month:
                        try:
                            return date(int(year), month, int(day))
                        except ValueError:
                            continue

        # Try to extract year at minimum
        year_match = re.search(r'20\d{2}', date_text)
        if year_match:
            year = int(year_match.group(0))
            # Default to January 1 if we can only get year
            return date(year, 1, 1)

        return None

    def _determine_event_type(self, name: str) -> str:
        """
        Determine the event type from the event name.

        Args:
            name: Event name

        Returns:
            EventType value string
        """
        name_lower = name.lower()

        if 'plebiscito' in name_lower or 'plebiscite' in name_lower:
            return EventType.PLEBISCITE.value
        elif 'primaria' in name_lower or 'primary' in name_lower:
            return EventType.PRIMARY.value
        elif 'especial' in name_lower or 'special' in name_lower:
            return EventType.SPECIAL.value
        elif 'referendum' in name_lower or 'referéndum' in name_lower:
            return EventType.REFERENDUM.value
        else:
            return EventType.GENERAL.value

    def scrape_events_list(self) -> list[dict]:
        """
        Scrape the list of electoral events from CEE.

        Returns:
            List of event dictionaries with name, date, and URLs
        """
        page = self._fetch_page(CEE_EVENTS_URL)

        if page.error:
            logger.error(f"Failed to fetch events list: {page.error}")
            return []

        soup = BeautifulSoup(page.raw_html, 'html.parser')
        events = []

        # Find event entries - CEE uses various structures
        # Look for common patterns: tables, divs with event info, list items

        # Pattern 1: Table rows with event info
        for row in soup.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                event_info = self._extract_event_from_row(cells)
                if event_info:
                    events.append(event_info)

        # Pattern 2: Div blocks with event info
        for div in soup.find_all('div', class_=re.compile(r'event|electoral|resultado', re.I)):
            event_info = self._extract_event_from_div(div)
            if event_info:
                events.append(event_info)

        # Pattern 3: List items with links
        for li in soup.find_all('li'):
            link = li.find('a', href=True)
            if link and self._is_results_link(link.get('href', '')):
                event_info = self._extract_event_from_link(li, link)
                if event_info:
                    events.append(event_info)

        # Pattern 4: Links containing result-related keywords
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if self._is_results_link(href) and link.get_text(strip=True):
                # Avoid duplicates
                if not any(e.get('results_url') == href for e in events):
                    event_info = self._extract_event_from_standalone_link(link)
                    if event_info:
                        events.append(event_info)

        # Deduplicate events
        seen = set()
        unique_events = []
        for event in events:
            key = (event.get('name', ''), event.get('results_url', ''))
            if key not in seen and event.get('name'):
                seen.add(key)
                unique_events.append(event)

        logger.info(f"Found {len(unique_events)} electoral events")

        # Save raw events list
        self._save_json(
            {"events": unique_events, "scraped_at": page.scraped_at},
            "events_list.json"
        )

        return unique_events

    def _is_results_link(self, href: str) -> bool:
        """Check if a link points to results."""
        if not href:
            return False

        href_lower = href.lower()
        keywords = ['resultado', 'result', 'elecciones', 'election', 'ceepur.org']

        return any(kw in href_lower for kw in keywords)

    def _extract_event_from_row(self, cells: list) -> Optional[dict]:
        """Extract event info from a table row."""
        text_content = ' '.join(cell.get_text(strip=True) for cell in cells)

        # Look for a year indicator
        if not re.search(r'20\d{2}|19\d{2}', text_content):
            return None

        # Find any links
        links = []
        for cell in cells:
            for link in cell.find_all('a', href=True):
                links.append(link)

        results_url = None
        for link in links:
            href = link.get('href', '')
            if self._is_results_link(href):
                results_url = urljoin(CEE_BASE_URL, href)
                break

        # Extract name (first non-empty cell text)
        name = None
        for cell in cells:
            cell_text = cell.get_text(strip=True)
            if cell_text and len(cell_text) > 5:
                name = cell_text
                break

        if not name:
            return None

        return {
            'name': name,
            'date_text': text_content,
            'event_date': self._parse_event_date(text_content),
            'results_url': results_url,
            'source_url': CEE_EVENTS_URL
        }

    def _extract_event_from_div(self, div) -> Optional[dict]:
        """Extract event info from a div element."""
        text = div.get_text(strip=True)
        if not text or len(text) < 10:
            return None

        link = div.find('a', href=True)
        results_url = None
        if link:
            href = link.get('href', '')
            if href:
                results_url = urljoin(CEE_BASE_URL, href)

        return {
            'name': text[:200],  # Truncate long names
            'date_text': text,
            'event_date': self._parse_event_date(text),
            'results_url': results_url,
            'source_url': CEE_EVENTS_URL
        }

    def _extract_event_from_link(self, li, link) -> Optional[dict]:
        """Extract event info from a list item with link."""
        text = li.get_text(strip=True)
        href = link.get('href', '')

        if not text or not href:
            return None

        return {
            'name': text[:200],
            'date_text': text,
            'event_date': self._parse_event_date(text),
            'results_url': urljoin(CEE_BASE_URL, href),
            'source_url': CEE_EVENTS_URL
        }

    def _extract_event_from_standalone_link(self, link) -> Optional[dict]:
        """Extract event info from a standalone link."""
        text = link.get_text(strip=True)
        href = link.get('href', '')

        if not text or len(text) < 5:
            return None

        # Try to get surrounding context
        parent = link.parent
        context = parent.get_text(strip=True) if parent else text

        return {
            'name': text,
            'date_text': context,
            'event_date': self._parse_event_date(context),
            'results_url': urljoin(CEE_BASE_URL, href),
            'source_url': CEE_EVENTS_URL
        }

    def scrape_event_results(self, event: dict) -> Optional[ElectoralEvent]:
        """
        Scrape detailed results for a single electoral event.

        Args:
            event: Event dictionary from scrape_events_list()

        Returns:
            ElectoralEvent object or None if scraping fails
        """
        results_url = event.get('results_url')
        if not results_url:
            logger.warning(f"No results URL for event: {event.get('name')}")
            return None

        page = self._fetch_page(results_url)

        if page.error:
            logger.warning(f"Failed to fetch results for {event.get('name')}: {page.error}")
            return None

        soup = BeautifulSoup(page.raw_html, 'html.parser')

        # Determine event type and create ElectoralEvent
        event_date = event.get('event_date') or date(2024, 1, 1)
        event_type = self._determine_event_type(event.get('name', ''))

        electoral_event = ElectoralEvent(
            event_id=ElectoralEvent.generate_event_id(event.get('name', 'unknown'), event_date),
            name=event.get('name', 'Unknown Event'),
            event_type=event_type,
            event_date=event_date,
            source_url=event.get('source_url'),
            results_url=results_url,
            metadata={
                'scraped_at': page.scraped_at,
                'content_hash': page.content_hash
            }
        )

        # Extract contests and results
        contests = self._extract_contests(soup, results_url)
        electoral_event.contests = contests

        # Save event data
        event_filename = f"event_{electoral_event.event_id}.json"
        self._save_electoral_event(electoral_event, event_filename)

        return electoral_event

    def _extract_contests(self, soup: BeautifulSoup, base_url: str) -> list[ContestResult]:
        """
        Extract contest results from a results page.

        Args:
            soup: BeautifulSoup object of the page
            base_url: Base URL for resolving relative links

        Returns:
            List of ContestResult objects
        """
        contests = []

        # Look for tables with vote data
        for table in soup.find_all('table'):
            contest = self._extract_contest_from_table(table)
            if contest and contest.results:
                contests.append(contest)

        # Look for structured data in divs
        for div in soup.find_all('div', class_=re.compile(r'result|vote|contest', re.I)):
            contest = self._extract_contest_from_div(div)
            if contest and contest.results:
                contests.append(contest)

        logger.info(f"Extracted {len(contests)} contests from {base_url}")
        return contests

    def _extract_contest_from_table(self, table) -> Optional[ContestResult]:
        """Extract a contest result from a table element."""
        rows = table.find_all('tr')
        if len(rows) < 2:
            return None

        # Try to find header row
        header_row = rows[0]
        headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]

        # Check if this looks like a results table
        vote_keywords = ['votos', 'votes', 'candidato', 'candidate', 'partido', 'party', '%']
        if not any(kw in ' '.join(headers) for kw in vote_keywords):
            return None

        # Find column indices
        candidate_col = None
        party_col = None
        votes_col = None
        percent_col = None

        for i, header in enumerate(headers):
            if 'candidato' in header or 'candidate' in header or 'nombre' in header:
                candidate_col = i
            elif 'partido' in header or 'party' in header:
                party_col = i
            elif 'voto' in header or 'vote' in header:
                votes_col = i
            elif '%' in header or 'porciento' in header or 'percent' in header:
                percent_col = i

        # If no specific columns found, try to infer
        if candidate_col is None and len(headers) >= 2:
            candidate_col = 0
            votes_col = len(headers) - 1

        results = []
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue

            try:
                candidate_name = cells[candidate_col].get_text(strip=True) if candidate_col is not None else None
                if not candidate_name:
                    continue

                # Skip header-like rows
                if candidate_name.lower() in ['candidato', 'candidate', 'total', 'totales']:
                    continue

                party = None
                if party_col is not None and party_col < len(cells):
                    party = cells[party_col].get_text(strip=True)

                votes = 0
                if votes_col is not None and votes_col < len(cells):
                    votes_text = cells[votes_col].get_text(strip=True)
                    votes_text = re.sub(r'[,\s]', '', votes_text)
                    if votes_text.isdigit():
                        votes = int(votes_text)

                percentage = None
                if percent_col is not None and percent_col < len(cells):
                    percent_text = cells[percent_col].get_text(strip=True)
                    percent_match = re.search(r'[\d.]+', percent_text)
                    if percent_match:
                        percentage = float(percent_match.group())

                results.append(VoteResult(
                    candidate_name=candidate_name,
                    party=party,
                    votes=votes,
                    percentage=percentage
                ))

            except (IndexError, ValueError) as e:
                logger.debug(f"Error parsing row: {e}")
                continue

        if not results:
            return None

        # Try to get contest name from table caption or preceding header
        office = "Unknown Contest"
        caption = table.find('caption')
        if caption:
            office = caption.get_text(strip=True)
        else:
            # Look for preceding header
            prev = table.find_previous(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if prev:
                office = prev.get_text(strip=True)

        contest = ContestResult(
            office=office,
            results=results
        )
        contest.calculate_totals()

        return contest

    def _extract_contest_from_div(self, div) -> Optional[ContestResult]:
        """Extract a contest result from a div element."""
        # Look for structured content
        text = div.get_text(strip=True)
        if len(text) < 20:
            return None

        # This is a fallback - most structured data should be in tables
        # Try to extract any vote-like patterns
        vote_pattern = r'([A-Za-z\s]+)[\s:]+(\d{1,3}(?:,\d{3})*)\s*(?:votos?|votes?)?'
        matches = re.findall(vote_pattern, text)

        if not matches:
            return None

        results = []
        for candidate, votes in matches:
            candidate = candidate.strip()
            votes = int(votes.replace(',', ''))
            if candidate and votes > 0:
                results.append(VoteResult(
                    candidate_name=candidate,
                    party=None,
                    votes=votes
                ))

        if not results:
            return None

        contest = ContestResult(
            office="Extracted Contest",
            results=results
        )
        contest.calculate_totals()

        return contest

    def _save_json(self, data: dict, filename: str):
        """Save data to a JSON file."""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Saved: {filepath}")

    def _save_electoral_event(self, event: ElectoralEvent, filename: str):
        """Save an electoral event to JSON."""
        # Convert dataclass to dict, handling nested dataclasses
        def serialize(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return asdict(obj)
            elif isinstance(obj, date):
                return obj.isoformat()
            elif isinstance(obj, list):
                return [serialize(item) for item in obj]
            return obj

        data = serialize(event)
        self._save_json(data, filename)

    def run(self) -> list[ElectoralEvent]:
        """
        Run the full scraping pipeline.

        Returns:
            List of scraped ElectoralEvent objects
        """
        logger.info("Starting CEE scraper...")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Request delay: {self.delay}s")

        # Step 1: Get list of events
        events = self.scrape_events_list()

        if not events:
            logger.warning("No events found to scrape")
            return []

        # Apply max_events limit
        if self.max_events:
            events = events[:self.max_events]
            logger.info(f"Limited to {self.max_events} events")

        # Step 2: Scrape each event's results
        electoral_events = []
        for i, event in enumerate(events, 1):
            logger.info(f"Processing event {i}/{len(events)}: {event.get('name', 'Unknown')}")

            try:
                electoral_event = self.scrape_event_results(event)
                if electoral_event:
                    electoral_events.append(electoral_event)
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                continue

        logger.info(f"Scraping complete. Processed {len(electoral_events)} events.")

        # Save summary
        summary = {
            'total_events_found': len(events),
            'events_processed': len(electoral_events),
            'scraped_at': datetime.utcnow().isoformat(),
            'events': [
                {
                    'event_id': e.event_id,
                    'name': e.name,
                    'event_type': e.event_type,
                    'event_date': e.event_date.isoformat() if e.event_date else None,
                    'contests_count': len(e.contests)
                }
                for e in electoral_events
            ]
        }
        self._save_json(summary, 'scraping_summary.json')

        return electoral_events


def main():
    """Main entry point for the scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape electoral data from CEE Puerto Rico",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Scrape all events with default settings
    python cee_scraper.py

    # Scrape with custom output directory
    python cee_scraper.py --output-dir /path/to/output

    # Scrape only first 5 events with 2 second delay
    python cee_scraper.py --max-events 5 --delay 2.0

    # Verbose output
    python cee_scraper.py -v
        """
    )

    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for scraped data (default: {DEFAULT_OUTPUT_DIR})"
    )

    parser.add_argument(
        '--delay', '-d',
        type=float,
        default=DEFAULT_DELAY,
        help=f"Delay between requests in seconds (default: {DEFAULT_DELAY})"
    )

    parser.add_argument(
        '--max-events', '-n',
        type=int,
        default=None,
        help="Maximum number of events to scrape (default: all)"
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Enable verbose/debug logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    scraper = CEEScraper(
        output_dir=args.output_dir,
        delay=args.delay,
        max_events=args.max_events
    )

    events = scraper.run()

    print(f"\nScraping complete!")
    print(f"Total events processed: {len(events)}")
    print(f"Data saved to: {args.output_dir}")

    return 0 if events else 1


if __name__ == '__main__':
    exit(main())
