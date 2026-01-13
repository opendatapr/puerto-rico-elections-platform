"""
OpenDataPR Altair Theme
Brand-compliant visualization theme matching MojaveDataOps design system.

Usage:
    from theme import enable_opendatapr_theme
    enable_opendatapr_theme()
"""

import altair as alt

# Brand colors from mojavedataops/brand-and-design-language
COLORS = {
    # Surfaces
    'background': '#0c0b0a',      # Near black, warm
    'surface': '#161412',          # Cards
    'surface_elevated': '#252320',

    # Text
    'text': '#f5f2ed',             # Primary (off-white)
    'text_muted': '#a8a098',       # Secondary
    'text_light': '#6d665d',       # Tertiary/disabled

    # Borders
    'border': '#2a2724',
    'border_light': '#3a3734',

    # Organization accent
    'opendatapr': '#4a9eda',       # Blue (primary for this project)
    'mojave': '#d4a373',           # Gold
    'opendatanv': '#7c9a5e',       # Green

    # Status
    'success': '#6b9080',
    'warning': '#d4a373',
    'error': '#c9695a',

    # Data visualization - diverging (blue to red)
    'data_low': '#2166ac',
    'data_mid': '#f7f7f7',
    'data_high': '#b2182b',
}

# Categorical palette for multi-series charts
CATEGORY_PALETTE = [
    '#4a9eda',  # OpenDataPR blue
    '#d4a373',  # Gold
    '#7c9a5e',  # Green
    '#c9695a',  # Muted red
    '#6b9080',  # Teal
    '#9b8bb3',  # Purple
    '#e8c49a',  # Light tan
]

# Diverging palette for heatmaps/choropleth
DIVERGING_PALETTE = [
    '#2166ac',  # Blue (low)
    '#67a9cf',
    '#d1e5f0',
    '#f7f7f7',  # White (mid)
    '#fddbc7',
    '#ef8a62',
    '#b2182b',  # Red (high)
]

# Sequential palette for single-variable gradients
SEQUENTIAL_PALETTE = [
    '#0c0b0a',
    '#1a3a5c',
    '#2166ac',
    '#4a9eda',
    '#8fc4eb',
]


def opendatapr_theme():
    """
    Altair theme configuration for OpenDataPR.

    Implements the MojaveDataOps design system with:
    - Dark background with warm undertones
    - Off-white text for reduced eye strain
    - Editorial aesthetic inspired by NYT, FiveThirtyEight
    - Fraunces display font, Source Sans 3 body
    """
    return {
        'config': {
            # Canvas
            'background': COLORS['background'],
            'padding': 20,

            # Title styling
            'title': {
                'color': COLORS['text'],
                'font': 'Fraunces',
                'fontSize': 18,
                'fontWeight': 600,
                'anchor': 'start',
                'offset': 10,
            },

            # Axis styling
            'axis': {
                'labelColor': COLORS['text_muted'],
                'labelFont': 'Source Sans 3',
                'labelFontSize': 11,
                'titleColor': COLORS['text'],
                'titleFont': 'Source Sans 3',
                'titleFontSize': 12,
                'titleFontWeight': 500,
                'gridColor': COLORS['border'],
                'gridOpacity': 0.5,
                'domainColor': COLORS['border_light'],
                'tickColor': COLORS['border_light'],
            },

            # Legend styling
            'legend': {
                'labelColor': COLORS['text_muted'],
                'labelFont': 'Source Sans 3',
                'labelFontSize': 11,
                'titleColor': COLORS['text'],
                'titleFont': 'Source Sans 3',
                'titleFontSize': 12,
                'titleFontWeight': 500,
                'padding': 10,
                'cornerRadius': 4,
            },

            # View (chart area)
            'view': {
                'stroke': 'transparent',
                'continuousWidth': 600,
                'continuousHeight': 400,
            },

            # Mark defaults
            'mark': {
                'color': COLORS['opendatapr'],
            },
            'point': {
                'color': COLORS['opendatapr'],
                'filled': True,
                'size': 60,
            },
            'line': {
                'color': COLORS['opendatapr'],
                'strokeWidth': 2,
            },
            'bar': {
                'color': COLORS['opendatapr'],
                'cornerRadiusTopLeft': 2,
                'cornerRadiusTopRight': 2,
            },
            'area': {
                'color': COLORS['opendatapr'],
                'opacity': 0.7,
            },
            'rect': {
                'color': COLORS['opendatapr'],
            },

            # Color schemes
            'range': {
                'category': CATEGORY_PALETTE,
                'diverging': DIVERGING_PALETTE,
                'heatmap': SEQUENTIAL_PALETTE,
                'ramp': SEQUENTIAL_PALETTE,
            },
        }
    }


def enable_opendatapr_theme():
    """Register and enable the OpenDataPR theme globally."""
    alt.themes.register('opendatapr', opendatapr_theme)
    alt.themes.enable('opendatapr')


# Auto-enable when imported
enable_opendatapr_theme()
