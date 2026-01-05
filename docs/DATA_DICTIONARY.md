# Data Dictionary / Diccionario de Datos

This document describes all data fields in the Puerto Rico Elections Platform.

Este documento describe todos los campos de datos en la Plataforma de Elecciones de Puerto Rico.

---

## Table of Contents / Tabla de Contenidos

- [Electoral Events / Eventos Electorales](#electoral-events--eventos-electorales)
- [Results / Resultados](#results--resultados)
- [Geographic Units / Unidades Geograficas](#geographic-units--unidades-geograficas)
- [Party Codes / Codigos de Partidos](#party-codes--codigos-de-partidos)
- [Contest Types / Tipos de Contiendas](#contest-types--tipos-de-contiendas)

---

## Electoral Events / Eventos Electorales

Electoral events represent distinct voting occasions in Puerto Rico, including general elections, primaries, plebiscites, and special elections.

Los eventos electorales representan ocasiones de votacion distintas en Puerto Rico, incluyendo elecciones generales, primarias, plebiscitos y elecciones especiales.

| Field / Campo | Type / Tipo | Description (EN) | Descripcion (ES) | Example / Ejemplo |
|---------------|-------------|------------------|------------------|-------------------|
| `event_id` | string | Unique identifier for the electoral event | Identificador unico para el evento electoral | `"elecciones-generales-2024"` |
| `event_type` | string | Type of electoral event | Tipo de evento electoral | `"general"`, `"primary"`, `"plebiscite"`, `"special"` |
| `event_date` | date | Date when the event occurred | Fecha en que ocurrio el evento | `"2024-11-05"` |
| `description_en` | string | Description in English | Descripcion en ingles | `"2024 General Elections"` |
| `description_es` | string | Description in Spanish | Descripcion en espanol | `"Elecciones Generales 2024"` |
| `source_url` | string | URL of the original data source | URL de la fuente de datos original | `"https://elecciones2024.ceepur.org"` |
| `total_registered_voters` | integer | Total registered voters for the event | Total de electores inscritos para el evento | `2348000` |
| `total_votes_cast` | integer | Total votes cast in the event | Total de votos emitidos en el evento | `1456000` |
| `turnout_percentage` | float | Voter turnout as a percentage | Participacion electoral como porcentaje | `62.01` |

### Event Types / Tipos de Eventos

| Code / Codigo | English | Espanol |
|---------------|---------|---------|
| `general` | General Elections | Elecciones Generales |
| `primary` | Primary Elections | Primarias |
| `plebiscite` | Plebiscite/Referendum | Plebiscito/Referendum |
| `special` | Special Elections | Elecciones Especiales |

---

## Results / Resultados

Results contain vote counts for candidates and options at various geographic levels.

Los resultados contienen conteos de votos para candidatos y opciones en varios niveles geograficos.

| Field / Campo | Type / Tipo | Description (EN) | Descripcion (ES) | Example / Ejemplo |
|---------------|-------------|------------------|------------------|-------------------|
| `result_id` | string | Unique identifier for the result record | Identificador unico para el registro de resultado | `"2024-gen-gov-san-juan-001"` |
| `event_id` | string | Reference to the electoral event | Referencia al evento electoral | `"elecciones-generales-2024"` |
| `geographic_unit` | string | Level of geographic aggregation | Nivel de agregacion geografica | `"precinct"`, `"municipality"`, `"island"` |
| `geographic_code` | string | Code identifying the geographic area | Codigo que identifica el area geografica | `"127-01"` |
| `contest_type` | string | Type of contest/race | Tipo de contienda/carrera | `"governor"`, `"senator"`, `"representative"` |
| `contest_name` | string | Full name of the contest | Nombre completo de la contienda | `"Gobernador de Puerto Rico"` |
| `candidate_name` | string | Name of the candidate or option | Nombre del candidato u opcion | `"Juan del Pueblo"` |
| `party_code` | string | Party abbreviation code | Codigo de abreviatura del partido | `"PNP"`, `"PPD"`, `"MVC"` |
| `party_name` | string | Full party name | Nombre completo del partido | `"Partido Nuevo Progresista"` |
| `votes` | integer | Number of votes received | Numero de votos recibidos | `45678` |
| `percentage` | float | Percentage of total votes | Porcentaje del total de votos | `48.23` |
| `is_winner` | boolean | Whether this candidate/option won | Si este candidato/opcion gano | `true` |
| `is_incumbent` | boolean | Whether candidate is incumbent | Si el candidato es incumbente | `false` |

### Geographic Unit Levels / Niveles de Unidad Geografica

| Code / Codigo | English | Espanol | Description |
|---------------|---------|---------|-------------|
| `island` | Island-wide | Isla | Puerto Rico as a whole / Puerto Rico en su totalidad |
| `senatorial_district` | Senatorial District | Distrito Senatorial | 8 senatorial districts / 8 distritos senatoriales |
| `representative_district` | Representative District | Distrito Representativo | 40 representative districts / 40 distritos representativos |
| `municipality` | Municipality | Municipio | 78 municipalities / 78 municipios |
| `precinct` | Precinct | Precinto | Electoral precincts / Precintos electorales |
| `unit` | Electoral Unit | Unidad | Smallest voting unit / Unidad de votacion mas pequena |

---

## Geographic Units / Unidades Geograficas

Geographic units define the administrative and electoral boundaries of Puerto Rico.

Las unidades geograficas definen los limites administrativos y electorales de Puerto Rico.

| Field / Campo | Type / Tipo | Description (EN) | Descripcion (ES) | Example / Ejemplo |
|---------------|-------------|------------------|------------------|-------------------|
| `unit_code` | string | Unique code for the geographic unit | Codigo unico para la unidad geografica | `"127"` (Trujillo Alto) |
| `unit_type` | string | Type of geographic unit | Tipo de unidad geografica | `"municipality"` |
| `name_en` | string | Name in English | Nombre en ingles | `"San Juan"` |
| `name_es` | string | Name in Spanish | Nombre en espanol | `"San Juan"` |
| `parent_code` | string | Code of the parent unit | Codigo de la unidad padre | `"SD-01"` (Senatorial District 1) |
| `population` | integer | Population count | Conteo de poblacion | `318441` |
| `area_km2` | float | Area in square kilometers | Area en kilometros cuadrados | `76.93` |
| `geometry` | GeoJSON | Geographic boundary as GeoJSON | Limite geografico como GeoJSON | `{"type": "Polygon", ...}` |
| `census_tract_ids` | array | Associated census tract IDs | IDs de tractos censales asociados | `["72127001100", "72127001200"]` |

### Municipality Codes / Codigos de Municipios

Puerto Rico has 78 municipalities. Each municipality has a 3-digit FIPS code.

Puerto Rico tiene 78 municipios. Cada municipio tiene un codigo FIPS de 3 digitos.

| Code | Municipality | Code | Municipality | Code | Municipality |
|------|--------------|------|--------------|------|--------------|
| 001 | Adjuntas | 027 | Canovanas | 053 | Fajardo |
| 003 | Aguada | 029 | Carolina | 054 | Florida |
| 005 | Aguadilla | 031 | Catano | 055 | Guanica |
| 007 | Aguas Buenas | 033 | Cayey | 057 | Guayama |
| 009 | Aibonito | 035 | Ceiba | 059 | Guayanilla |
| 011 | Anasco | 037 | Ciales | 061 | Guaynabo |
| 013 | Arecibo | 039 | Cidra | 063 | Gurabo |
| 015 | Arroyo | 041 | Coamo | 065 | Hatillo |
| 017 | Barceloneta | 043 | Comerio | 067 | Hormigueros |
| 019 | Barranquitas | 045 | Corozal | 069 | Humacao |
| 021 | Bayamon | 047 | Culebra | 071 | Isabela |
| 023 | Cabo Rojo | 049 | Dorado | 073 | Jayuya |
| 025 | Caguas | 051 | Fajardo | 075 | Juana Diaz |

*(Full list of 78 municipalities available in the geographic_units dataset)*

---

## Party Codes / Codigos de Partidos

Political parties that have participated in Puerto Rico elections.

Partidos politicos que han participado en elecciones de Puerto Rico.

| Code / Codigo | Full Name (EN) | Nombre Completo (ES) | Status / Estado |
|---------------|----------------|----------------------|-----------------|
| `PNP` | New Progressive Party | Partido Nuevo Progresista | Active / Activo |
| `PPD` | Popular Democratic Party | Partido Popular Democratico | Active / Activo |
| `PIP` | Puerto Rican Independence Party | Partido Independentista Puertorriqueno | Active / Activo |
| `MVC` | Citizen's Victory Movement | Movimiento Victoria Ciudadana | Active / Activo |
| `PD` | Dignity Project | Proyecto Dignidad | Active / Activo |
| `IND` | Independent | Independiente | N/A |
| `PPR` | Puerto Ricans for Puerto Rico | Puertorriquenos por Puerto Rico | Inactive / Inactivo |
| `PPT` | Working People's Party | Partido del Pueblo Trabajador | Inactive / Inactivo |

### Historical Party Notes / Notas Historicas de Partidos

- **MVC** (Movimiento Victoria Ciudadana): Founded in 2019, first participated in 2020 elections
- **PD** (Proyecto Dignidad): Founded in 2019, first participated in 2020 elections
- **PPR**: Active from 2008-2012
- **PPT**: Active in early 2000s elections

---

## Contest Types / Tipos de Contiendas

Types of electoral contests available in the data.

Tipos de contiendas electorales disponibles en los datos.

| Code / Codigo | English | Espanol | Level / Nivel |
|---------------|---------|---------|---------------|
| `governor` | Governor | Gobernador | Island / Isla |
| `resident_commissioner` | Resident Commissioner | Comisionado Residente | Island / Isla |
| `senator_at_large` | Senator at Large | Senador por Acumulacion | Island / Isla |
| `senator_district` | District Senator | Senador por Distrito | District / Distrito |
| `representative_at_large` | Representative at Large | Representante por Acumulacion | Island / Isla |
| `representative_district` | District Representative | Representante por Distrito | District / Distrito |
| `mayor` | Mayor | Alcalde | Municipality / Municipio |
| `municipal_legislator` | Municipal Legislator | Legislador Municipal | Municipality / Municipio |
| `plebiscite_option` | Plebiscite Option | Opcion de Plebiscito | Island / Isla |

---

## Data Quality Notes / Notas sobre Calidad de Datos

### Coverage / Cobertura
- **Temporal**: 2000-present (2000-presente)
- **Geographic**: All 78 municipalities (Los 78 municipios)
- **Completeness**: Varies by event; older events may have less granular data

### Known Limitations / Limitaciones Conocidas

1. **Precinct boundaries**: Electoral precinct boundaries are not officially published in digital format. Cross-referencing with census tracts uses approximations.

   *Los limites de precintos electorales no se publican oficialmente en formato digital. La referencia cruzada con tractos censales usa aproximaciones.*

2. **Historical data**: Events before 2004 may have limited precinct-level data availability.

   *Los eventos antes de 2004 pueden tener disponibilidad limitada de datos a nivel de precinto.*

3. **Write-in votes**: Write-in candidates are generally not included in the data.

   *Los candidatos por nominacion directa generalmente no se incluyen en los datos.*

---

## Data Updates / Actualizaciones de Datos

The data is updated after each electoral event. Check the `source_url` field to verify data recency.

Los datos se actualizan despues de cada evento electoral. Verifique el campo `source_url` para verificar la actualidad de los datos.

| Last Updated / Ultima Actualizacion | Event / Evento |
|-------------------------------------|----------------|
| 2024-11-15 | 2024 General Elections |
| 2024-06-10 | 2024 Primary Elections |
| 2025-01-XX | 2025 Special Election (Gurabo) |

---

## Related Resources / Recursos Relacionados

- [Methodology Documentation](METHODOLOGY.md) / [Documentacion de Metodologia](METHODOLOGY.md)
- [Installation Guide](INSTALLATION.md) / [Guia de Instalacion](INSTALLATION.md)
- [CEE Official Site](https://ww2.ceepur.org/) / [Sitio Oficial de la CEE](https://ww2.ceepur.org/)
- [US Census Bureau Puerto Rico](https://www.census.gov/programs-surveys/acs/geography-acs/areas-published.html)
