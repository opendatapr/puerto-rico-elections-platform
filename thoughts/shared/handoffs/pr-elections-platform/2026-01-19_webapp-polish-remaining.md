# Handoff: Webapp Polish - Remaining Tasks

**Created:** 2026-01-19
**Context:** Session reached 79% context after fixing map colors and accent matching

## Completed This Session

1. **CLAUDE.md** - Project guidance file created
2. **Linting configs** - pyproject.toml (ruff), ESLint for packages/js
3. **Chapter data wiring** - All 12 chapters now use consistent fetch-from-JSON pattern
4. **Precinct polygons** - Generated precincts.topojson (114 precincts, 0.8MB)
5. **Mobile responsiveness** - Breakpoints at 640px/1024px, touch-friendly
6. **Precinct map support** - ChoroplethMap supports `level="precinct"`
7. **Map color schemes** - Fixed diverging→sequential for loss/turnout data
8. **Municipality accent matching** - Accent-insensitive matching for 17 affected municipalities

## Remaining Tasks

### 1. Spanish Language Version (HIGH PRIORITY)
**Scope:** Full translation of all 12 chapters

**Approach options:**
- **Option A (i18n):** Add svelte-i18n, create locale files, wrap all text in `$t()` calls
- **Option B (Duplicate routes):** Create `/es/chapters/` routes with Spanish content
- **Option C (Toggle):** Single routes with language toggle, content stored in JSON

**Key files:**
- `webapp/src/routes/chapters/*/+page.svelte` - Chapter content
- `webapp/src/routes/+page.svelte` - Home page
- `webapp/src/routes/+layout.svelte` - Navigation

**Considerations:**
- Puerto Rico's primary language is Spanish
- Academic/journalistic credibility requires proper translation
- ~50KB of text content across 12 chapters

### 2. Direct Source Links in Text Boxes (MEDIUM PRIORITY)
**Problem:** Text boxes mention sources but don't link directly

**Current state:**
- Sources section at bottom of each chapter has citations
- In-text references don't link to actual data

**Fix:**
- Add inline links: `According to [CEE data](https://elecciones2020.ceepur.org/)...`
- Link census stats to Census Bureau pages
- Link academic citations to DOIs/papers

**Key sources to link:**
- CEE election results: https://ww2.ceepur.org/Home/EventosElectorales
- US Census ACS: https://data.census.gov/
- Academic papers: DOIs for migration studies, electoral analysis

### 3. Text Box Structure Variety (MEDIUM PRIORITY)
**Problem:** All step text boxes follow identical structure

**Current pattern:**
```
[Big number stat]
[Paragraph of explanation]
```

**Suggested variety:**
- **Quote pull-outs:** For impactful statements
- **Comparison boxes:** Side-by-side before/after
- **Key finding callouts:** Highlighted conclusions
- **Question prompts:** Rhetorical questions to engage readers
- **Timeline snippets:** For historical context

**Implementation:**
- Create new Step variants in `webapp/src/lib/components/scrollytelling/`
- Update chapter pages to use varied structures

### 4. Plot Engagement and Design (MEDIUM PRIORITY)
**Problem:** Plots are functional but basic

**Current D3 implementations:**
- Bar charts (horizontal, vertical)
- Line charts (time series)
- Scatter plots
- Choropleth maps

**Improvements:**
- **Animations:** Smooth transitions between steps
- **Interactivity:** Hover states, tooltips with context
- **Annotations:** Call out key data points
- **Better typography:** Axis labels, legends
- **Color consistency:** Match brand palette

**Key files:**
- `webapp/src/lib/components/charts/` - Chart components (if exists)
- Individual chapter SVG implementations

## Technical Notes

### Accent Matching Fix (for reference)
Added to `ChoroplethMap.svelte`:
```typescript
function normalizeString(s: string): string {
    return s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
}
```

### Color Scales Added (for reference)
In `colors.ts`:
- `createLossScale([min, max])` - Light→dark red for loss data
- `createSequentialBlueScale([min, max])` - Light→dark blue for percentages
- `createPovertyScale([min, max])` - Light→dark orange-red for poverty

## Commands

```bash
# Dev server
cd webapp && npm run dev

# Build
cd webapp && npm run build

# Preview production
cd webapp && npm run preview
```

## Commits This Session

```
0269feb Fix map colors and municipality accent matching
27b863f Add mobile responsiveness and precinct-level map support
26e7744 Update continuity ledger
35d87e4 Wire remaining chapters and add precinct polygons
a1e5192 Add repo tooling: CLAUDE.md, linting configs, pipeline, and handoffs
```
