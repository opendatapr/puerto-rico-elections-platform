"""
CEE XML Parser

Parses electoral data from CEE's XML-based results system.
Modern CEE results (2016+) use a three-tier architecture:
1. Landing page (XML with XSL) - contains event navigation
2. SPA shell (JavaScript) - loads data dynamically
3. Data files (XML) - actual election results

This module directly fetches and parses the XML data files.

XML Types:
- homepage: Landing page with subevent links
- tree/NAVIGATION.xml: Menu of all available data files
- default: Island-wide summary results
- default_list: List of results by geographic level (districts, precincts)
- pic_list: Detailed precinct/unit results
- map: Geographic map data with results
"""

import logging
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

from schema import (
    ContestResult, VoteResult, GeographicUnit, ElectoralEvent
)

logger = logging.getLogger(__name__)


@dataclass
class CEEDataFile:
    """Represents a CEE data file reference from NAVIGATION.xml."""
    contest_name_es: str
    contest_name_en: str
    data_level: str  # "resumen", "precintos", "distritos_senatoriales", etc.
    filename: str

    @property
    def contest_name(self) -> str:
        return self.contest_name_es


@dataclass
class CEESubevent:
    """Represents a subevent from the landing page."""
    description: str
    link: str
    base_url: str = ""

    @property
    def full_url(self) -> str:
        return urljoin(self.base_url, self.link.lstrip('/'))

    @property
    def data_url(self) -> str:
        """Get the data folder URL for this subevent."""
        # SPA URLs like /Escrutinio_General_93/index.html -> /Escrutinio_General_93/data/
        base = self.full_url.rsplit('/', 1)[0] if '/' in self.full_url else self.full_url
        return f"{base}/data/"


@dataclass
class ParsedCandidate:
    """Parsed candidate data from XML."""
    name_es: str
    name_en: str
    party_es: str
    party_en: str
    party_abbrev: str
    votes: int
    color: str = ""
    image_url: str = ""

    @property
    def name(self) -> str:
        return self.name_es

    @property
    def party(self) -> str:
        return self.party_es


@dataclass
class ParsedContest:
    """Parsed contest from XML with full data."""
    office_es: str
    office_en: str
    level: str  # "island", "senatorial_district", "municipality", "precinct"
    geographic_name: str = ""
    candidates: list[ParsedCandidate] = field(default_factory=list)
    total_ballots: int = 0
    blank_votes: int = 0
    null_votes: int = 0
    write_ins: int = 0
    registered_voters: int = 0
    participation_rate: float = 0.0
    voting_places_reported: int = 0
    voting_places_total: int = 0
    timestamp: str = ""

    @property
    def office(self) -> str:
        return self.office_es


class CEEXMLParser:
    """
    Parser for CEE XML data files.

    Handles the various XML formats used by CEE for election results.
    """

    # Data level mappings from filename patterns
    LEVEL_PATTERNS = {
        '_Resumen': 'island',
        '_Distritos_Senatoriales': 'senatorial_district',
        '_Distritos_Representativos': 'representative_district',
        '_Municipios': 'municipality',
        '_Precintos': 'precinct',
        '_Mapa_': 'map',
    }

    def __init__(self):
        self.encoding = 'ISO-8859-1'  # CEE uses ISO-8859-1

    def is_xml_content(self, content: str) -> bool:
        """Check if content is XML."""
        content_stripped = content.strip()
        return content_stripped.startswith('<?xml') or content_stripped.startswith('<')

    def detect_xml_type(self, content: str) -> Optional[str]:
        """Detect the type of CEE XML document."""
        if not self.is_xml_content(content):
            return None

        try:
            root = ET.fromstring(content)
            return root.tag
        except ET.ParseError:
            return None

    def parse_landing_page(self, content: str, base_url: str) -> list[CEESubevent]:
        """
        Parse the XML landing page to extract subevent links.

        Args:
            content: XML content of landing page
            base_url: Base URL for resolving relative links

        Returns:
            List of CEESubevent objects
        """
        subevents = []

        try:
            root = ET.fromstring(content)

            # Handle <homepage> format
            for event in root.findall('.//event'):
                for subevent in event.findall('subevent'):
                    desc_elem = subevent.find('description')
                    link_elem = subevent.find('link')

                    if desc_elem is not None and link_elem is not None:
                        subevents.append(CEESubevent(
                            description=desc_elem.text or '',
                            link=link_elem.text or '',
                            base_url=base_url
                        ))

        except ET.ParseError as e:
            logger.error(f"Error parsing landing page XML: {e}")

        return subevents

    def parse_navigation(self, content: str) -> list[CEEDataFile]:
        """
        Parse NAVIGATION.xml to get list of available data files.

        Args:
            content: XML content of NAVIGATION.xml

        Returns:
            List of CEEDataFile objects
        """
        data_files = []

        try:
            root = ET.fromstring(content)

            for branch in root.findall('.//branch'):
                # Get contest name
                branch_text = branch.find('branchText')
                contest_es = ''
                contest_en = ''

                if branch_text is not None:
                    es_elem = branch_text.find('es')
                    en_elem = branch_text.find('en')
                    contest_es = es_elem.text if es_elem is not None else ''
                    contest_en = en_elem.text if en_elem is not None else ''

                # Get all leaf nodes (data files)
                for leaf in branch.findall('leaf'):
                    leaf_text = leaf.find('leafText')
                    link = leaf.find('link')

                    if link is not None and link.text:
                        level_es = ''
                        if leaf_text is not None:
                            es_elem = leaf_text.find('es')
                            level_es = es_elem.text if es_elem is not None else ''

                        # Determine data level from filename
                        data_level = self._detect_data_level(link.text)

                        data_files.append(CEEDataFile(
                            contest_name_es=contest_es,
                            contest_name_en=contest_en,
                            data_level=data_level,
                            filename=link.text
                        ))

        except ET.ParseError as e:
            logger.error(f"Error parsing NAVIGATION.xml: {e}")

        return data_files

    def _detect_data_level(self, filename: str) -> str:
        """Detect the data level from filename."""
        for pattern, level in self.LEVEL_PATTERNS.items():
            if pattern in filename:
                return level
        return 'unknown'

    def parse_summary(self, content: str) -> Optional[ParsedContest]:
        """
        Parse a summary (Resumen) XML file - island-wide results.

        Format: <default type="default">
        """
        try:
            root = ET.fromstring(content)

            if root.tag != 'default':
                return None

            # Get title (contest name)
            title = root.find('title')
            office_es = ''
            office_en = ''
            if title is not None:
                es = title.find('es')
                en = title.find('en')
                office_es = es.text if es is not None else ''
                office_en = en.text if en is not None else ''

            # Get timestamp
            date_elem = root.find('date')
            timestamp = date_elem.text if date_elem is not None else ''

            # Parse candidates/options
            candidates = []
            for option in root.findall('option'):
                candidate = self._parse_option(option)
                if candidate:
                    candidates.append(candidate)

            # Parse additional vote data from tables
            blank_votes = 0
            null_votes = 0
            write_ins = 0
            total_ballots = 0

            table1 = root.find('table1')
            if table1 is not None:
                for row in table1.findall('row'):
                    desc = row.find('desc/es')
                    qty = row.find('qty')
                    if desc is not None and qty is not None:
                        desc_text = desc.text.upper() if desc.text else ''
                        qty_val = int(qty.text) if qty.text and qty.text.isdigit() else 0

                        if 'EN BLANCO' in desc_text or 'BLANK' in desc_text:
                            blank_votes = qty_val
                        elif 'NULA' in desc_text or 'NULL' in desc_text:
                            null_votes = qty_val
                        elif 'NOMINACIÓN DIRECTA' in desc_text or 'WRITE IN' in desc_text:
                            write_ins = qty_val
                        elif 'TOTAL DE PAPELETAS' in desc_text:
                            total_ballots = qty_val

            # Parse participation data from table2
            registered_voters = 0
            participation_rate = 0.0

            table2 = root.find('table2')
            if table2 is not None:
                for row in table2.findall('row'):
                    desc = row.find('desc/es')
                    qty = row.find('qty')
                    if desc is not None and qty is not None:
                        desc_text = desc.text.upper() if desc.text else ''
                        qty_val = int(qty.text) if qty.text and qty.text.isdigit() else 0

                        if 'INSCRITOS' in desc_text:
                            registered_voters = qty_val

                # Get participation rate
                for rowp in table2.findall('rowp'):
                    qty = rowp.find('qty')
                    if qty is not None and qty.text:
                        try:
                            participation_rate = float(qty.text)
                        except ValueError:
                            pass

            # Parse reporting status
            report = root.find('report')
            voting_places_reported = 0
            voting_places_total = 0
            if report is not None:
                qty = report.find('qty')
                total = report.find('total')
                if qty is not None and qty.text:
                    voting_places_reported = int(qty.text)
                if total is not None and total.text:
                    voting_places_total = int(total.text)

            return ParsedContest(
                office_es=office_es,
                office_en=office_en,
                level='island',
                geographic_name='Puerto Rico',
                candidates=candidates,
                total_ballots=total_ballots,
                blank_votes=blank_votes,
                null_votes=null_votes,
                write_ins=write_ins,
                registered_voters=registered_voters,
                participation_rate=participation_rate,
                voting_places_reported=voting_places_reported,
                voting_places_total=voting_places_total,
                timestamp=timestamp
            )

        except ET.ParseError as e:
            logger.error(f"Error parsing summary XML: {e}")
            return None

    def parse_list(self, content: str) -> list[ParsedContest]:
        """
        Parse a list XML file (districts, municipalities, precincts).

        Format: <default_list type="default">
        Contains multiple <group> elements, each with results for a geographic unit.
        """
        contests = []

        try:
            root = ET.fromstring(content)

            if root.tag != 'default_list':
                return contests

            # Get title (contest name)
            title = root.find('title')
            office_es = ''
            office_en = ''
            if title is not None:
                es = title.find('es')
                en = title.find('en')
                office_es = es.text if es is not None else ''
                office_en = en.text if en is not None else ''

            # Determine level from subtitle
            subtitle = root.find('subtitle')
            level = 'unknown'
            if subtitle is not None:
                es = subtitle.find('es')
                if es is not None and es.text:
                    subtitle_text = es.text.upper()
                    if 'PRECINTO' in subtitle_text or 'ELECTORAL DISTRICT' in subtitle_text:
                        level = 'precinct'
                    elif 'DISTRITO SENATORIAL' in subtitle_text:
                        level = 'senatorial_district'
                    elif 'DISTRITO REPRESENTATIVO' in subtitle_text:
                        level = 'representative_district'
                    elif 'MUNICIPIO' in subtitle_text:
                        level = 'municipality'

            # Get timestamp
            date_elem = root.find('date')
            timestamp = date_elem.text if date_elem is not None else ''

            # Parse each group (geographic unit)
            for group in root.findall('group'):
                name_elem = group.find('name')
                geo_name = ''
                detail_link = ''

                if name_elem is not None:
                    desc = name_elem.find('description/es')
                    link = name_elem.find('link/es')
                    geo_name = desc.text if desc is not None else ''
                    detail_link = link.text if link is not None else ''

                # Parse candidates in this group
                candidates = []
                for option in group.findall('option'):
                    candidate = self._parse_option_simple(option)
                    if candidate:
                        candidates.append(candidate)

                if candidates:
                    contests.append(ParsedContest(
                        office_es=office_es,
                        office_en=office_en,
                        level=level,
                        geographic_name=geo_name,
                        candidates=candidates,
                        timestamp=timestamp
                    ))

        except ET.ParseError as e:
            logger.error(f"Error parsing list XML: {e}")

        return contests

    def parse_precinct_detail(self, content: str) -> list[ParsedContest]:
        """
        Parse a detailed precinct/unit XML file.

        Format: <pic_list type="default">
        Contains detailed results for a single precinct including all contests.
        """
        contests = []

        try:
            root = ET.fromstring(content)

            if root.tag != 'pic_list':
                return contests

            # Get precinct name from subtitle or demarcation
            precinct_name = ''
            subtitle = root.find('subtitle/es')
            if subtitle is not None:
                precinct_name = subtitle.text or ''
            else:
                demarcation = root.find('demarcation/es')
                if demarcation is not None:
                    precinct_name = demarcation.text or ''

            # Get timestamp
            date_elem = root.find('date')
            timestamp = date_elem.text if date_elem is not None else ''

            # Parse each contest group
            for group in root.findall('group'):
                name_elem = group.find('name/es')
                office_es = name_elem.text if name_elem is not None else ''

                name_en_elem = group.find('name/en')
                office_en = name_en_elem.text if name_en_elem is not None else ''

                # Parse candidates
                candidates = []
                for option in group.findall('option'):
                    candidate = self._parse_option(option)
                    if candidate:
                        candidates.append(candidate)

                # Parse additional vote data from table1
                blank_votes = 0
                null_votes = 0
                write_ins = 0
                total_ballots = 0

                table1 = group.find('table1')
                if table1 is not None:
                    for row in table1.findall('row'):
                        desc = row.find('desc/es')
                        qty = row.find('qty')
                        if desc is not None and qty is not None:
                            desc_text = (desc.text or '').upper()
                            qty_val = int(qty.text) if qty.text and qty.text.isdigit() else 0

                            if 'EN BLANCO' in desc_text:
                                blank_votes = qty_val
                            elif 'NULA' in desc_text:
                                null_votes = qty_val
                            elif 'NOMINACIÓN DIRECTA' in desc_text:
                                write_ins = qty_val
                            elif 'TOTAL DE PAPELETAS' in desc_text:
                                total_ballots = qty_val

                if candidates:
                    contests.append(ParsedContest(
                        office_es=office_es,
                        office_en=office_en,
                        level='precinct',
                        geographic_name=precinct_name,
                        candidates=candidates,
                        total_ballots=total_ballots,
                        blank_votes=blank_votes,
                        null_votes=null_votes,
                        write_ins=write_ins,
                        timestamp=timestamp
                    ))

            # Also parse participation data from table3
            registered_voters = 0
            participation_rate = 0.0

            table3 = root.find('table3')
            if table3 is not None:
                for row in table3.findall('row'):
                    desc = row.find('desc/es')
                    qty = row.find('qty')
                    if desc is not None and qty is not None and 'INSCRITOS' in (desc.text or '').upper():
                        registered_voters = int(qty.text) if qty.text and qty.text.isdigit() else 0

                for rowp in table3.findall('rowp'):
                    qty = rowp.find('qty')
                    if qty is not None and qty.text:
                        try:
                            participation_rate = float(qty.text)
                        except ValueError:
                            pass

            # Update first contest with participation data (applies to precinct)
            if contests:
                contests[0].registered_voters = registered_voters
                contests[0].participation_rate = participation_rate

        except ET.ParseError as e:
            logger.error(f"Error parsing precinct detail XML: {e}")

        return contests

    def _parse_option(self, option: ET.Element) -> Optional[ParsedCandidate]:
        """Parse a candidate/option element with full details."""
        name_es = ''
        name_en = ''
        party_es = ''
        party_en = ''
        party_abbrev = ''
        votes = 0
        color = ''
        image = ''

        # Name
        name_elem = option.find('name')
        if name_elem is not None:
            es = name_elem.find('es')
            en = name_elem.find('en')
            name_es = es.text if es is not None else ''
            name_en = en.text if en is not None else ''

        # Party (pe = political entity)
        pe_elem = option.find('pe')
        if pe_elem is not None:
            es = pe_elem.find('es')
            en = pe_elem.find('en')
            party_es = es.text if es is not None else ''
            party_en = en.text if en is not None else ''

        # Party abbreviation
        peini_elem = option.find('peini')
        if peini_elem is not None:
            es = peini_elem.find('es')
            party_abbrev = es.text if es is not None else ''

        # Votes
        votes_elem = option.find('votes')
        if votes_elem is not None and votes_elem.text:
            try:
                votes = int(votes_elem.text.replace(',', ''))
            except ValueError:
                votes = 0

        # Color
        color_elem = option.find('pecolor')
        if color_elem is not None:
            color = color_elem.text or ''

        # Image
        img_elem = option.find('img')
        if img_elem is not None:
            image = img_elem.text or ''

        if not name_es and not name_en:
            return None

        return ParsedCandidate(
            name_es=name_es,
            name_en=name_en,
            party_es=party_es,
            party_en=party_en,
            party_abbrev=party_abbrev,
            votes=votes,
            color=color,
            image_url=image
        )

    def _parse_option_simple(self, option: ET.Element) -> Optional[ParsedCandidate]:
        """Parse a simplified option element (from list views)."""
        name_es = ''
        name_en = ''
        party_es = ''
        party_en = ''
        party_abbrev = ''
        votes = 0
        color = ''

        # Name
        name_elem = option.find('name')
        if name_elem is not None:
            es = name_elem.find('es')
            en = name_elem.find('en')
            name_es = es.text if es is not None else ''
            name_en = en.text if en is not None else ''

        # Party
        pe_elem = option.find('pe')
        if pe_elem is not None:
            es = pe_elem.find('es')
            en = pe_elem.find('en')
            party_es = es.text if es is not None else ''
            party_en = en.text if en is not None else ''

        # Party abbreviation
        peini_elem = option.find('peini')
        if peini_elem is not None:
            es = peini_elem.find('es')
            party_abbrev = es.text if es is not None else ''

        # Votes
        votes_elem = option.find('votes')
        if votes_elem is not None and votes_elem.text:
            try:
                votes = int(votes_elem.text.replace(',', ''))
            except ValueError:
                votes = 0

        # Color
        color_elem = option.find('pecolor')
        if color_elem is not None:
            color = color_elem.text or ''

        if not name_es and not name_en:
            return None

        return ParsedCandidate(
            name_es=name_es,
            name_en=name_en,
            party_es=party_es,
            party_en=party_en,
            party_abbrev=party_abbrev,
            votes=votes,
            color=color
        )

    def to_contest_result(self, parsed: ParsedContest) -> ContestResult:
        """Convert ParsedContest to schema ContestResult."""
        results = []
        for candidate in parsed.candidates:
            total = sum(c.votes for c in parsed.candidates)
            percentage = (candidate.votes / total * 100) if total > 0 else 0.0

            results.append(VoteResult(
                candidate_name=candidate.name,
                party=candidate.party,
                votes=candidate.votes,
                percentage=percentage
            ))

        # Determine office type
        office_type = None
        office_lower = parsed.office.lower()
        if 'gobernador' in office_lower or 'governor' in office_lower:
            office_type = 'governor'
        elif 'comisionado' in office_lower or 'commissioner' in office_lower:
            office_type = 'resident_commissioner'
        elif 'alcalde' in office_lower or 'mayor' in office_lower:
            office_type = 'mayor'
        elif 'senador' in office_lower and 'acumulación' in office_lower:
            office_type = 'senator_at_large'
        elif 'senador' in office_lower:
            office_type = 'senator_district'
        elif 'representante' in office_lower:
            office_type = 'representative'
        elif 'legislador' in office_lower:
            office_type = 'legislator_municipal'

        # Create geographic unit if applicable
        geo_unit = None
        if parsed.level != 'island' and parsed.geographic_name:
            geo_unit = GeographicUnit(
                level=parsed.level,
                code=parsed.geographic_name,  # Use name as code for now
                name=parsed.geographic_name
            )

        return ContestResult(
            office=parsed.office,
            office_type=office_type,
            district=parsed.geographic_name if parsed.level != 'island' else None,
            geographic_unit=geo_unit,
            results=results,
            total_votes=parsed.total_ballots,
            blank_votes=parsed.blank_votes,
            null_votes=parsed.null_votes,
            registered_voters=parsed.registered_voters if parsed.registered_voters > 0 else None,
            participation_rate=parsed.participation_rate if parsed.participation_rate > 0 else None
        )
