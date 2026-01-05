"""
Geographic Matching for Puerto Rico Electoral and Census Data

This module provides functions to match Puerto Rico municipalities to census
geographic identifiers (GEOIDs) for cross-referencing electoral results with
demographic data.

USAGE:
    from geo_matching import (
        get_municipality_geoid,
        normalize_municipality_name,
        match_municipalities_to_census,
        create_municipality_crosswalk
    )

Matching Methodology:
    1. Puerto Rico municipalities are equivalent to "counties" in Census terminology
    2. Each municipality has a unique 5-digit GEOID: state FIPS (72) + county FIPS (3 digits)
    3. Municipality names are normalized for matching (lowercase, accent removal, etc.)
    4. Census tracts are nested within municipalities (county subdivision)
"""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple

import pandas as pd

# Puerto Rico FIPS code
PR_STATE_FIPS = "72"

# Official mapping of Puerto Rico municipality names to county FIPS codes
# Based on Census Bureau FIPS codes for Puerto Rico
MUNICIPALITY_FIPS_MAP = {
    "adjuntas": "001",
    "aguada": "003",
    "aguadilla": "005",
    "aguas buenas": "007",
    "aibonito": "009",
    "anasco": "011",
    "arecibo": "013",
    "arroyo": "015",
    "barceloneta": "017",
    "barranquitas": "019",
    "bayamon": "021",
    "cabo rojo": "023",
    "caguas": "025",
    "camuy": "027",
    "canovanas": "029",
    "carolina": "031",
    "catano": "033",
    "cayey": "035",
    "ceiba": "037",
    "ciales": "039",
    "cidra": "041",
    "coamo": "043",
    "comerio": "045",
    "corozal": "047",
    "culebra": "049",
    "dorado": "051",
    "fajardo": "053",
    "florida": "054",
    "guanica": "055",
    "guayama": "057",
    "guayanilla": "059",
    "guaynabo": "061",
    "gurabo": "063",
    "hatillo": "065",
    "hormigueros": "067",
    "humacao": "069",
    "isabela": "071",
    "jayuya": "073",
    "juana diaz": "075",
    "juncos": "077",
    "lajas": "079",
    "lares": "081",
    "las marias": "083",
    "las piedras": "085",
    "loiza": "087",
    "luquillo": "089",
    "manati": "091",
    "maricao": "093",
    "maunabo": "095",
    "mayaguez": "097",
    "moca": "099",
    "morovis": "101",
    "naguabo": "103",
    "naranjito": "105",
    "orocovis": "107",
    "patillas": "109",
    "penuelas": "111",
    "ponce": "113",
    "quebradillas": "115",
    "rincon": "117",
    "rio grande": "119",
    "sabana grande": "121",
    "salinas": "123",
    "san german": "125",
    "san juan": "127",
    "san lorenzo": "129",
    "san sebastian": "131",
    "santa isabel": "133",
    "toa alta": "135",
    "toa baja": "137",
    "trujillo alto": "139",
    "utuado": "141",
    "vega alta": "143",
    "vega baja": "145",
    "vieques": "147",
    "villalba": "149",
    "yabucoa": "151",
    "yauco": "153",
}

# Alternative spellings and common variations
MUNICIPALITY_ALIASES = {
    # Accented versions
    "anasco": ["añasco"],
    "bayamon": ["bayamón"],
    "canovanas": ["canóvanas"],
    "catano": ["cataño"],
    "comerio": ["comerío"],
    "guanica": ["guánica"],
    "juana diaz": ["juana díaz"],
    "loiza": ["loíza"],
    "manati": ["manatí"],
    "mayaguez": ["mayagüez"],
    "penuelas": ["peñuelas"],
    "rincon": ["rincón"],
    "san german": ["san germán"],
    "san sebastian": ["san sebastián"],
    # Common abbreviations
    "san juan": ["sj", "sanjuan"],
    "bayamon": ["bay"],
    "ponce": ["pon"],
    # Other variations
    "cabo rojo": ["caborojo"],
    "rio grande": ["riogrande"],
    "toa alta": ["toaalta"],
    "toa baja": ["toabaja"],
    "vega alta": ["vegaalta"],
    "vega baja": ["vegabaja"],
    "las piedras": ["laspiedras"],
    "las marias": ["lasmarias", "las marías"],
    "san lorenzo": ["sanlorenzo"],
    "santa isabel": ["santaisabel"],
    "aguas buenas": ["aguasbuenas"],
    "trujillo alto": ["trujilloalto"],
    "sabana grande": ["sabanagrande"],
}


def normalize_municipality_name(name: str) -> str:
    """
    Normalize a municipality name for matching.

    Normalization steps:
    1. Convert to lowercase
    2. Remove accents (NFD normalization)
    3. Remove non-alphanumeric characters (except spaces)
    4. Normalize whitespace

    Args:
        name: Raw municipality name

    Returns:
        Normalized name for matching
    """
    if not name:
        return ""

    # Convert to lowercase
    normalized = name.lower().strip()

    # Remove accents using NFD normalization
    normalized = unicodedata.normalize('NFD', normalized)
    normalized = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')

    # Remove special characters but keep spaces
    normalized = re.sub(r'[^a-z0-9\s]', '', normalized)

    # Normalize whitespace (multiple spaces to single)
    normalized = ' '.join(normalized.split())

    return normalized


def get_municipality_geoid(municipality_name: str) -> Optional[str]:
    """
    Get the Census GEOID for a Puerto Rico municipality.

    The GEOID is a 5-digit code: state FIPS (72) + county FIPS (3 digits).

    Args:
        municipality_name: Name of the municipality

    Returns:
        5-digit GEOID string, or None if municipality not found

    Example:
        >>> get_municipality_geoid("San Juan")
        "72127"
        >>> get_municipality_geoid("Mayagüez")
        "72097"
    """
    normalized = normalize_municipality_name(municipality_name)

    # Direct lookup
    if normalized in MUNICIPALITY_FIPS_MAP:
        return PR_STATE_FIPS + MUNICIPALITY_FIPS_MAP[normalized]

    # Check aliases
    for canonical, aliases in MUNICIPALITY_ALIASES.items():
        normalized_aliases = [normalize_municipality_name(a) for a in aliases]
        if normalized in normalized_aliases:
            return PR_STATE_FIPS + MUNICIPALITY_FIPS_MAP[canonical]

    return None


def get_county_fips(municipality_name: str) -> Optional[str]:
    """
    Get the 3-digit county FIPS code for a municipality.

    Args:
        municipality_name: Name of the municipality

    Returns:
        3-digit county FIPS string, or None if not found
    """
    normalized = normalize_municipality_name(municipality_name)

    if normalized in MUNICIPALITY_FIPS_MAP:
        return MUNICIPALITY_FIPS_MAP[normalized]

    # Check aliases
    for canonical, aliases in MUNICIPALITY_ALIASES.items():
        normalized_aliases = [normalize_municipality_name(a) for a in aliases]
        if normalized in normalized_aliases:
            return MUNICIPALITY_FIPS_MAP[canonical]

    return None


def match_municipalities_to_census(
    municipality_names: List[str]
) -> Dict[str, Optional[str]]:
    """
    Match a list of municipality names to Census GEOIDs.

    Args:
        municipality_names: List of municipality names to match

    Returns:
        Dictionary mapping input names to GEOIDs (None if no match)
    """
    results = {}
    for name in municipality_names:
        results[name] = get_municipality_geoid(name)
    return results


def create_municipality_crosswalk() -> pd.DataFrame:
    """
    Create a complete crosswalk table for Puerto Rico municipalities.

    Returns:
        DataFrame with columns:
        - municipality: Official municipality name
        - normalized_name: Normalized name for matching
        - county_fips: 3-digit county FIPS code
        - geoid: 5-digit state+county GEOID
        - aliases: List of known alternative spellings
    """
    rows = []
    for normalized, fips in MUNICIPALITY_FIPS_MAP.items():
        # Convert normalized back to title case for display
        display_name = normalized.title()

        # Handle multi-word names
        display_name = display_name.replace(" De ", " de ")
        display_name = display_name.replace(" Del ", " del ")

        geoid = PR_STATE_FIPS + fips
        aliases = MUNICIPALITY_ALIASES.get(normalized, [])

        rows.append({
            "municipality": display_name,
            "normalized_name": normalized,
            "county_fips": fips,
            "geoid": geoid,
            "aliases": aliases
        })

    df = pd.DataFrame(rows)
    return df.sort_values("municipality").reset_index(drop=True)


def find_closest_municipality(name: str, threshold: float = 0.8) -> Optional[Tuple[str, float]]:
    """
    Find the closest matching municipality using fuzzy matching.

    Uses simple Levenshtein-like similarity for approximate matching.

    Args:
        name: Input municipality name
        threshold: Minimum similarity score (0-1) to return a match

    Returns:
        Tuple of (canonical_name, similarity_score) or None if no match above threshold
    """
    from difflib import SequenceMatcher

    normalized_input = normalize_municipality_name(name)
    best_match = None
    best_score = 0.0

    for canonical in MUNICIPALITY_FIPS_MAP.keys():
        score = SequenceMatcher(None, normalized_input, canonical).ratio()
        if score > best_score:
            best_score = score
            best_match = canonical

        # Also check aliases
        aliases = MUNICIPALITY_ALIASES.get(canonical, [])
        for alias in aliases:
            normalized_alias = normalize_municipality_name(alias)
            score = SequenceMatcher(None, normalized_input, normalized_alias).ratio()
            if score > best_score:
                best_score = score
                best_match = canonical

    if best_match and best_score >= threshold:
        return (best_match.title(), best_score)

    return None


def validate_municipality_coverage(names: List[str]) -> Dict[str, any]:
    """
    Validate that a list of municipality names covers all PR municipalities.

    Useful for checking electoral data completeness.

    Args:
        names: List of municipality names from electoral data

    Returns:
        Dictionary with:
        - matched: List of successfully matched municipalities
        - unmatched_input: Input names that couldn't be matched
        - missing_municipalities: Official municipalities not in input
        - coverage_pct: Percentage of PR municipalities covered
    """
    normalized_inputs = {normalize_municipality_name(n): n for n in names}
    all_municipalities = set(MUNICIPALITY_FIPS_MAP.keys())

    matched = []
    unmatched_input = []

    for original, normalized in normalized_inputs.items():
        geoid = get_municipality_geoid(original)
        if geoid:
            matched.append({
                "input_name": original,
                "canonical_name": normalized,
                "geoid": geoid
            })
        else:
            unmatched_input.append(original)

    matched_normalized = {m["canonical_name"] for m in matched}
    missing = all_municipalities - matched_normalized

    return {
        "matched": matched,
        "unmatched_input": unmatched_input,
        "missing_municipalities": list(missing),
        "coverage_pct": len(matched) / len(all_municipalities) * 100
    }


def get_all_municipality_geoids() -> Dict[str, str]:
    """
    Get a dictionary of all Puerto Rico municipalities and their GEOIDs.

    Returns:
        Dictionary mapping municipality names (title case) to 5-digit GEOIDs
    """
    return {
        name.title(): PR_STATE_FIPS + fips
        for name, fips in MUNICIPALITY_FIPS_MAP.items()
    }


# Module-level convenience exports
ALL_MUNICIPALITIES = list(MUNICIPALITY_FIPS_MAP.keys())
TOTAL_MUNICIPALITIES = len(MUNICIPALITY_FIPS_MAP)  # Should be 78


if __name__ == "__main__":
    # Demo usage
    print("Puerto Rico Municipality Geographic Matching")
    print("=" * 50)

    # Create crosswalk
    crosswalk = create_municipality_crosswalk()
    print(f"\nTotal municipalities: {len(crosswalk)}")

    # Test some lookups
    test_names = [
        "San Juan",
        "Mayagüez",
        "PONCE",
        "bayamon",
        "Juana Díaz",
        "Unknown Place"
    ]

    print("\nTest lookups:")
    for name in test_names:
        geoid = get_municipality_geoid(name)
        print(f"  {name:20} -> {geoid or 'NOT FOUND'}")

    # Show first few rows of crosswalk
    print("\nCrosswalk sample:")
    print(crosswalk[["municipality", "geoid", "county_fips"]].head(10).to_string())
