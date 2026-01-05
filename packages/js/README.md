# prelecciones

Access Puerto Rico electoral data from JavaScript/TypeScript.

## Installation

```bash
npm install prelecciones
```

## Quick Start

```typescript
import { listEvents, getResults, setDataPath } from 'prelecciones';

// Optionally set data path
setDataPath('/path/to/data/processed');

// List all available electoral events
const events = listEvents();
console.log(events);

// Get results for a specific election
const results = getResults('2020-general');
console.log(results);

// Get municipality-level results with geometry
const resultsGeo = getResults('2020-general', {
  level: 'municipality',
  includeGeometry: true
});
```

## API Reference

### `listEvents(options?)`

Returns an array of all available electoral events.

**Options:**
- `includeGeometry` (boolean): Include geographic boundary information

**Returns:** `ElectoralEvent[]`

### `getResults(eventId, options?)`

Get election results for a specific event.

**Parameters:**
- `eventId` (string): Unique identifier for the electoral event
- `options.level` (string): Geographic aggregation level ("precinct", "municipality", "district", "island")
- `options.includeGeometry` (boolean): Include geographic boundaries as GeoJSON

**Returns:** `ElectionResult[]` or `ResultsWithGeometry`

### `setDataPath(path)`

Set the path to the processed data directory.

## TypeScript

This package includes full TypeScript type definitions.

```typescript
import type {
  ElectoralEvent,
  ElectionResult,
  AggregationLevel,
  GeoJSONFeatureCollection
} from 'prelecciones';
```

## License

MIT
