# Research Proposal: Electoral Dynamics in Puerto Rico

**Using the Puerto Rico Elections Platform for Political Science, Demography, and Geographic Research**

---

## Executive Summary

The Puerto Rico Elections Platform provides a comprehensive, open-access dataset enabling rigorous empirical research on electoral behavior, demographic change, and geographic political patterns in Puerto Rico. This proposal outlines four interconnected research agendas suitable for academic publication, policy analysis, and civic engagement.

**Target Audiences:**
- Political scientists studying voting behavior and party systems
- Demographers examining migration and population dynamics
- Geographers analyzing spatial patterns in political preferences
- Policy researchers focused on Puerto Rico's status and governance
- Data journalists covering Caribbean electoral politics

---

## I. Research Context

### Puerto Rico's Unique Position

Puerto Rico occupies a distinctive position in American political geography:

- **Territory status**: Unincorporated U.S. territory since 1898
- **Population dynamics**: 15% decline (3.7M → 3.2M) from 2010-2020
- **Economic challenges**: Highest poverty rate among U.S. jurisdictions (43%)
- **Political system**: Multi-party system with unique status politics
- **Hurricane impact**: Maria (2017) triggered mass out-migration

### Research Gap

Despite Puerto Rico's significance, quantitative electoral research faces barriers:
- Electoral data historically scattered across CEE websites
- No standardized API or data portal
- Census-electoral linkage requires manual crosswalks
- Precinct-level analysis requires shapefile integration

**This platform addresses these gaps** by providing cleaned, linked, and documented electoral-demographic data.

---

## II. Dataset Overview

### Electoral Data

| Coverage | Details |
|----------|---------|
| Time span | 2000-2025 (103 electoral events) |
| Election types | General, primary, special, referendum |
| Geographic levels | Island, district, municipality, precinct |
| Parties | PNP, PPD, PIP, MVC, PD, independents |
| Offices | Governor, legislature, mayor, resident commissioner |

### Census Data

| Level | Units | Years |
|-------|-------|-------|
| Municipalities | 78 | 2012, 2016, 2020, 2022, 2023 |
| Census tracts | 981 | 2022 |
| Block groups | 2,548 | 2022 |

**Variables**: Population, median age, household income, poverty rate, unemployment rate, educational attainment (high school, bachelor's, graduate degrees)

### Geographic Crosswalks

- **Precinct-census linkage**: 110 precincts with demographic overlays
- **Shapefile integration**: MGGG redistricting project boundaries
- **Centroid coordinates**: WGS84 for spatial analysis

---

## III. Proposed Research Agendas

### Agenda 1: Voter Turnout and Socioeconomic Status

**Research Question**: What demographic factors predict voter turnout in Puerto Rico?

**Hypotheses**:
- H1: Higher income municipalities exhibit higher turnout rates
- H2: Educational attainment positively correlates with participation
- H3: Poverty rate negatively correlates with turnout

**Methodology**:
1. Merge 2020 general election results with ACS 2020 demographics at municipality level
2. Calculate turnout as votes per 1,000 population (or per registered voter if available)
3. Estimate OLS regression: `Turnout ~ Income + Education + Poverty + Age + Population`
4. Replicate at precinct level using crosswalk
5. Test robustness across 2016 and 2024 elections

**Data Requirements**: ✅ All available in platform

**Expected Output**: Correlation matrices, regression tables, municipality-level maps

**Timeline**: 2-3 weeks for full analysis

---

### Agenda 2: Migration and Electoral Change

**Research Question**: How has population loss affected Puerto Rico's electoral landscape?

**Hypotheses**:
- H1: High out-migration municipalities show larger vote share shifts
- H2: Post-Maria (2017) out-migration correlated with turnout decline
- H3: Remaining populations are older, lower-income, shifting electoral preferences

**Methodology**:
1. Calculate population change by municipality (2012→2022)
2. Calculate electoral swing (PNP/PPD vote share change 2016→2020)
3. Test correlation: Population decline ↔ party swing
4. Pre/post-Maria comparison using 2016 vs 2020 ACS
5. Demographic decomposition: Which characteristics changed most in high-loss areas?

**Data Requirements**: ✅ Census years aligned with election cycles

**Expected Output**: Population change maps, swing analysis, demographic shift tables

**Timeline**: 3-4 weeks

---

### Agenda 3: Spatial Voting Patterns

**Research Question**: Are voting patterns spatially clustered, and what demographic factors explain regional coalitions?

**Hypotheses**:
- H1: PNP and PPD support exhibit positive spatial autocorrelation (clustering)
- H2: Income and education predict precinct-level party support
- H3: Intra-municipal variation is significant in large urban areas

**Methodology**:
1. Calculate Moran's I for PNP/PPD vote shares across precincts
2. Local Indicators of Spatial Association (LISA) to identify hot/cold spots
3. Spatial regression with demographic covariates
4. Within-municipality variance analysis for large cities (San Juan, Bayamón, Ponce)

**Data Requirements**:
- ✅ Precinct boundaries (2016 MGGG shapefiles)
- ✅ Precinct-level voting data
- ⚠️ Precinct-level demographics (available via crosswalk, ~60-80% confidence)

**Expected Output**: Choropleth maps, LISA cluster maps, spatial regression results

**Timeline**: 4-5 weeks (requires GIS tools)

---

### Agenda 4: Status Referendum Analysis

**Research Question**: What demographic and political factors predict support for Puerto Rico statehood?

**Hypotheses**:
- H1: PNP voters strongly favor statehood; PPD voters oppose
- H2: Higher-income, higher-education areas show different status preferences
- H3: Status preference has evolved across referendums (2012, 2020)

**Methodology**:
1. Analyze 2020 referendum results (Sí/No) at precinct level
2. Correlate with 2020 governor race party vote shares
3. Merge with census demographics for SES analysis
4. *If 2012 data added*: Track shifts in status preference by municipality

**Data Requirements**:
- ✅ 2020 referendum data (476 records)
- ⚠️ 2012 referendum data (requires scraper extension)
- ✅ Party voting data for correlation

**Expected Output**: Party-referendum cross-tabulation, demographic correlations, trend analysis (if 2012 added)

**Timeline**: 2-3 weeks (2020 only); +2 weeks if 2012 added

---

## IV. Publication Strategy

### Target Journals

| Journal | Agenda Fit | Impact Factor |
|---------|------------|---------------|
| *Political Research Quarterly* | Agendas 1, 4 | 2.4 |
| *Latin American Politics and Society* | Agendas 1-4 | 1.8 |
| *Demography* | Agenda 2 | 4.2 |
| *Political Geography* | Agenda 3 | 3.8 |
| *Caribbean Studies* | Agendas 1-4 | 0.5 |
| *Centro Journal* (CUNY) | Agendas 1-4 | 0.3 |

### Working Paper Series

Prior to journal submission, analyses can be released as:
- GitHub releases with reproducible code
- Preprints on OSF or SSRN
- Policy briefs for Puerto Rico-focused organizations

### Conference Presentations

- American Political Science Association (APSA)
- Latin American Studies Association (LASA)
- Population Association of America (PAA)
- Puerto Rico Political Science Association

---

## V. Collaboration Opportunities

### Academic Partners

| Institution | Relevant Programs |
|-------------|-------------------|
| University of Puerto Rico | Political Science, Demography |
| CUNY Centro de Estudios Puertorriqueños | Puerto Rico Studies |
| Harvard Kennedy School | Latino Politics |
| MIT Election Data + Science Lab | Election administration |
| UCLA Latino Politics & Policy Initiative | Comparative analysis |

### Civic Organizations

- Center for a New Economy (CNE) - Puerto Rico
- Puerto Rico Institute of Statistics
- Espacios Abiertos (civic tech)
- Proyecto 85 (electoral engagement)

### Data Partnerships

- U.S. Census Bureau (ACS data validation)
- Comisión Estatal de Elecciones (official data access)
- MGGG Redistricting Lab (boundary data)

---

## VI. Resource Requirements

### Technical Infrastructure

| Resource | Status | Notes |
|----------|--------|-------|
| Python/R analysis environment | ✅ Ready | Parquet format optimized |
| GIS tools (QGIS, GeoPandas) | ✅ Ready | Shapefiles available |
| Statistical packages | ✅ Ready | scipy, statsmodels |
| Visualization tools | ✅ Ready | matplotlib, seaborn |
| Quarto for publication | ✅ Installed | Notebooks created |

### Data Extensions Needed

| Extension | Priority | Effort |
|-----------|----------|--------|
| 2012 referendum data | High | 1-2 weeks |
| Pre-2016 election results | Medium | 2-3 weeks |
| Voter registration data | Low | Unknown (CEE access) |
| Puerto Rican diaspora data | Low | External sources |

### Personnel

| Role | Hours/Week | Duration |
|------|------------|----------|
| Lead researcher | 10-15 | 3-6 months |
| GIS specialist | 5 | 1-2 months |
| Puerto Rico policy expert | Consultation | As needed |
| Spanish translator | 5 | Publication phase |

---

## VII. Expected Outcomes

### Academic Contributions

1. **Peer-reviewed publications**: 2-4 journal articles from the four agendas
2. **Working papers**: Pre-publication analyses for immediate impact
3. **Methodology contributions**: Documented approaches for census-electoral linkage in U.S. territories

### Policy Impact

1. **Electoral administration**: Insights for CEE on turnout patterns
2. **Status debate**: Empirical evidence on preference determinants
3. **Civic engagement**: Data-driven targeting for voter mobilization

### Platform Development

1. **Extended coverage**: Historical data (2000-2015) for long-term analysis
2. **API development**: Programmatic access for researchers
3. **Visualization tools**: Interactive maps and dashboards

---

## VIII. Timeline

```
Month 1-2:
- Complete Agenda 1 (Turnout analysis)
- Begin Agenda 3 (Spatial analysis setup)

Month 2-3:
- Complete Agenda 4 (2020 referendum)
- Scrape 2012 referendum data
- Draft first working paper

Month 3-4:
- Complete Agenda 2 (Migration impact)
- Spatial analysis completion
- Submit first paper to journal

Month 4-6:
- Revision and resubmission
- Complete remaining analyses
- Present at conference
```

---

## IX. Conclusion

The Puerto Rico Elections Platform enables rigorous, reproducible research on electoral dynamics in one of America's most politically complex jurisdictions. The proposed research agendas address fundamental questions in political science, demography, and geography while providing actionable insights for policymakers and civic organizations.

**Key Strengths**:
- Comprehensive data coverage (2000-2025)
- Census integration at three geographic levels
- Open-source, reproducible methodology
- Bilingual documentation (English/Spanish)

**Immediate Next Steps**:
1. Run Quarto notebooks to generate initial outputs
2. Identify lead researcher for each agenda
3. Secure institutional partnership
4. Begin Agenda 1 (Turnout) as proof of concept

---

*Proposal prepared using Puerto Rico Elections Platform*
*Repository: https://github.com/opendatapr/puerto-rico-elections-platform*
*License: GPL-3.0*
