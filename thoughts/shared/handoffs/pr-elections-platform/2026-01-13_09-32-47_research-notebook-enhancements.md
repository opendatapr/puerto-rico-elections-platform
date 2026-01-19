---
date: 2026-01-13T09:32:47-04:00
session_name: pr-elections-platform
researcher: Claude
git_commit: f0abf2bd5e3341e3c16f504ebb291ecee8f91f0f
branch: main
repository: puerto-rico-elections-platform
topic: "Research Notebook Enhancement with Brand Design"
tags: [quarto, visualization, brand-design, altair, research]
status: in_progress
last_updated: 2026-01-13
last_updated_by: Claude
type: implementation_strategy
root_span_id:
turn_span_id:
---

# Handoff: Enhance Research Notebooks with Brand Design & External Sources

## Task(s)

1. **Research exploration and notebook creation** - COMPLETED
   - Created 4 Quarto analysis notebooks covering turnout, migration, spatial, referendum
   - Fixed data structure issues (precinct-level aggregation)
   - Rendered all notebooks successfully to HTML

2. **Research notebook enhancements** - PLANNED (user request)
   - Add more narrative text accompanying analyses
   - Support arguments with external academic/news sources
   - Replace matplotlib with brand-compliant visualizations
   - Apply MojaveDataOps/OpenDataPR design system

## Critical References

1. `/tmp/brand-design/tokens/variables.css` - Full design token system (cloned from mojavedataops/brand-and-design-language)
2. `docs/research/RESEARCH_PROPOSAL.md` - Academic context and research questions
3. `analysis/research/*.qmd` - The 4 Quarto notebooks to enhance

## Recent changes

- `analysis/research/01-turnout-patterns.qmd:53-77` - Fixed to extract municipality from precinct names
- `analysis/research/02-migration-impact.qmd:183-221` - Added municipality extraction helper, fixed correlation analysis
- `analysis/research/03-spatial-voting.qmd:257-288` - Updated swing geography for precinct data
- `analysis/research/_quarto.yml` - Removed bibliography reference (not created)
- `analysis/research/.gitignore` - Added to exclude _output/, _freeze/, temp files

## Learnings

### Data Structure Discovery
- Election results are at **precinct level**, not municipality level
- Precinct district format: `"San Juan 001"` → extract municipality by splitting on last space
- Must aggregate to municipality level for census matching
- The `data_level` column has values: `island`, `senatorial_district`, `precinct` (no `municipality`)

### Brand Design System (MojaveDataOps)
Located at `mojavedataops/brand-and-design-language` (private repo, cloned to `/tmp/brand-design/`):

**Color Palette for OpenDataPR:**
```
Primary accent: #4a9eda (OpenDataPR blue)
Background: #0c0b0a (near black, warm)
Surface: #161412 (cards)
Text: #f5f2ed (off-white)
Text muted: #a8a098
Data viz diverging: #2166ac (blue) → #f7f7f7 (white) → #b2182b (red)
Success: #6b9080 (muted green)
Error: #c9695a (muted red)
```

**Typography:**
- Display: Fraunces (serif) - for headings
- Body: Source Sans 3 (sans-serif)
- Code: JetBrains Mono

**Philosophy:** Editorial aesthetic inspired by NYT, FiveThirtyEight, ProPublica

## Post-Mortem (Required for Artifact Index)

### What Worked
- Parallel subagent exploration of 4 research topics generated comprehensive analysis plans
- Quarto notebooks with code-fold provide clean reproducible research
- Fixing precinct extraction with `rsplit(' ', 1)` handled municipality names with spaces correctly
- Using paired dropna for correlation analysis prevented shape mismatch errors

### What Failed
- Tried: Quarto render with PDF format → Failed because: No TeX installation
  - Fixed by: Removing `pdf:` format from notebook YAML frontmatter
- Tried: Direct municipality filter on `data_level` → Failed because: No municipality-level data exists
  - Fixed by: Aggregating precinct data with municipality extraction
- Tried: bibliography: references.bib → Failed because: File doesn't exist
  - Fixed by: Removing bibliography line from _quarto.yml

### Key Decisions
- **Decision:** Use Altair for visualizations instead of matplotlib
  - Alternatives: Plotly (too interactive/heavy), seaborn (similar to matplotlib), bokeh
  - Reason: Altair produces clean, declarative charts matching editorial aesthetic; supports custom themes easily

- **Decision:** Dark theme for visualizations matching brand
  - Alternatives: Light theme (standard academic), auto-detect
  - Reason: Brand design specifies dark theme with warm undertones

## Artifacts

**Created this session:**
- `analysis/research/01-turnout-patterns.qmd` - Voter turnout analysis
- `analysis/research/02-migration-impact.qmd` - Migration and electoral change
- `analysis/research/03-spatial-voting.qmd` - Geographic voting patterns
- `analysis/research/04-status-referendum.qmd` - Statehood referendum analysis
- `analysis/research/_quarto.yml` - Quarto project config
- `analysis/research/.gitignore` - Ignore rendered output
- `docs/research/RESEARCH_PROPOSAL.md` - Formal research proposal

**Brand design reference (cloned):**
- `/tmp/brand-design/tokens/variables.css` - Design tokens
- `/tmp/brand-design/brand/voice.md` - Brand voice guidelines
- `/tmp/brand-design/components/patterns.md` - UI component patterns

## Action Items & Next Steps

### 1. Switch Visualization Library to Altair
- Install altair: `pip install altair`
- Create custom theme matching brand design tokens
- Replace all matplotlib charts in all 4 notebooks

### 2. Apply Brand Design to Quarto
Update `_quarto.yml` with:
- Custom SCSS theme using brand colors
- Import Fraunces and Source Sans 3 fonts
- Dark theme styling

### 3. Add Narrative Content
For each notebook, add:
- **Context sections** explaining Puerto Rico's political landscape
- **Methodology explanations** in plain language
- **Interpretation paragraphs** after each visualization
- **Limitations and caveats** sections

### 4. Add External Sources
Research and cite:
- Academic papers on Puerto Rico elections (JSTOR, Google Scholar)
- Census Bureau documentation for ACS methodology
- News sources (El Nuevo Día, Centro de Periodismo Investigativo)
- Pew Research on Puerto Rico demographics/migration
- FEMA reports on Hurricane Maria impact

Create `analysis/research/references.bib` with proper citations.

### 5. Altair Theme Implementation
Create `analysis/research/theme.py`:
```python
import altair as alt

# OpenDataPR theme matching brand-and-design-language
def opendatapr_theme():
    return {
        'config': {
            'background': '#0c0b0a',
            'title': {'color': '#f5f2ed', 'font': 'Fraunces'},
            'axis': {
                'labelColor': '#a8a098',
                'titleColor': '#f5f2ed',
                'gridColor': '#2a2724',
                'domainColor': '#3a3734'
            },
            'legend': {'labelColor': '#a8a098', 'titleColor': '#f5f2ed'},
            'view': {'stroke': 'transparent'},
            'range': {
                'category': ['#4a9eda', '#d4a373', '#7c9a5e', '#c9695a', '#6b9080'],
                'diverging': ['#2166ac', '#67a9cf', '#d1e5f0', '#f7f7f7', '#fddbc7', '#ef8a62', '#b2182b']
            }
        }
    }

alt.themes.register('opendatapr', opendatapr_theme)
alt.themes.enable('opendatapr')
```

## Other Notes

### Quarto Rendering
- Render command: `source .venv/bin/activate && .local/quarto/bin/quarto render analysis/research/`
- Output in: `analysis/research/_output/`
- Quarto installed locally at `.local/quarto/` (not system-wide)

### Key External Sources to Find
1. **Migration data**: Pew Research "Puerto Ricans Leave in Record Numbers" post-Maria
2. **Election analysis**: Centro de Estudios Puertorriqueños publications
3. **Turnout studies**: "Voter Turnout in Puerto Rico" academic papers
4. **Status referendum**: Official CEE results, academic analysis of 2012/2017/2020 referendums
5. **Census methodology**: ACS Puerto Rico documentation, sampling notes

### Brand Repo Access
The brand repo is private. Re-clone if needed:
```bash
gh repo clone mojavedataops/brand-and-design-language /tmp/brand-design
```

### Visualization Style Notes from Brand
- "Editorial Aesthetic" - inspired by data journalism
- Generous whitespace
- Subtle animations (less relevant for static charts)
- Muted colors, not pure black/white
- "Authoritative but accessible" voice
