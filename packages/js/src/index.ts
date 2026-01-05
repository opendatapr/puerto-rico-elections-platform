/**
 * prelecciones - Access Puerto Rico electoral data
 *
 * This package provides easy access to Puerto Rico electoral data,
 * including election results and event information.
 */

import { readFileSync, existsSync, readdirSync } from "fs";
import { join, dirname } from "path";

export const VERSION = "0.1.0";

/**
 * Geographic aggregation levels for election results
 */
export type AggregationLevel = "precinct" | "municipality" | "district" | "island";

/**
 * Electoral event information
 */
export interface ElectoralEvent {
  eventId: string;
  date: string;
  type: "general" | "primary" | "special" | string;
  description: string;
  hasGeometry?: boolean;
}

/**
 * Election result record
 */
export interface ElectionResult {
  [key: string]: string | number | boolean | null | undefined;
}

/**
 * GeoJSON Feature for spatial data
 */
export interface GeoJSONFeature {
  type: "Feature";
  properties: Record<string, unknown>;
  geometry: {
    type: string;
    coordinates: unknown;
  };
}

/**
 * GeoJSON FeatureCollection
 */
export interface GeoJSONFeatureCollection {
  type: "FeatureCollection";
  features: GeoJSONFeature[];
}

/**
 * Options for listEvents function
 */
export interface ListEventsOptions {
  /** Include geographic boundary information */
  includeGeometry?: boolean;
}

/**
 * Options for getResults function
 */
export interface GetResultsOptions {
  /** Geographic aggregation level */
  level?: AggregationLevel;
  /** Include geographic boundaries as GeoJSON */
  includeGeometry?: boolean;
}

/**
 * Results with optional geometry
 */
export interface ResultsWithGeometry {
  results: ElectionResult[];
  geometry?: GeoJSONFeatureCollection;
}

// Module-level data path
let dataPath: string | null = null;

/**
 * Set the path to the processed data directory
 *
 * @param path - Path to the directory containing processed electoral data
 * @throws Error if the path does not exist
 *
 * @example
 * ```typescript
 * import { setDataPath } from 'prelecciones';
 * setDataPath('/path/to/data/processed');
 * ```
 */
export function setDataPath(path: string): void {
  if (!existsSync(path)) {
    throw new Error(`Data path does not exist: ${path}`);
  }
  dataPath = path;
}

/**
 * Get the path to the processed data directory
 * @internal
 */
function getDataPath(): string {
  if (dataPath !== null) {
    return dataPath;
  }

  // Try to find data relative to this module
  // Check various potential locations
  const currentDir = dirname(new URL(import.meta.url).pathname);

  // Development: packages/js/src -> repo root
  const possiblePaths = [
    join(currentDir, "..", "..", "..", "data", "processed"),
    join(currentDir, "..", "..", "..", "..", "data", "processed"),
    join(process.cwd(), "data", "processed"),
  ];

  for (const p of possiblePaths) {
    if (existsSync(p)) {
      return p;
    }
  }

  throw new Error(
    "Could not find data directory. " +
      "Use setDataPath() to specify the location of processed data."
  );
}

/**
 * List all available electoral events
 *
 * Returns an array containing information about all electoral events
 * in the dataset, including event IDs, dates, types, and descriptions.
 *
 * @param options - Configuration options
 * @param options.includeGeometry - If true, include geographic boundary information
 * @returns Array of electoral event objects
 *
 * @example
 * ```typescript
 * import { listEvents } from 'prelecciones';
 *
 * // List all events
 * const events = listEvents();
 * console.log(events);
 *
 * // Include geometry information
 * const eventsGeo = listEvents({ includeGeometry: true });
 * ```
 */
export function listEvents(options: ListEventsOptions = {}): ElectoralEvent[] {
  const { includeGeometry = false } = options;
  const dataDir = getDataPath();

  const eventsFile = join(dataDir, "events.json");

  if (existsSync(eventsFile)) {
    const content = readFileSync(eventsFile, "utf-8");
    const events = JSON.parse(content) as ElectoralEvent[];

    if (!includeGeometry) {
      return events.map(({ hasGeometry, ...event }) => event as ElectoralEvent);
    }

    return events;
  }

  // Return empty array if no data exists yet
  return [];
}

/**
 * Get election results for a specific event
 *
 * Retrieves detailed election results including vote counts by candidate,
 * party, and geographic unit.
 *
 * @param eventId - The unique identifier for the electoral event
 * @param options - Configuration options
 * @param options.level - Geographic aggregation level (default: "precinct")
 * @param options.includeGeometry - Include geographic boundaries as GeoJSON
 * @returns Election results, optionally with geometry
 *
 * @throws Error if eventId is not found or level is invalid
 *
 * @example
 * ```typescript
 * import { getResults } from 'prelecciones';
 *
 * // Get precinct-level results
 * const results = getResults('2020-general');
 *
 * // Get municipality-level results with geometry
 * const resultsGeo = getResults('2020-general', {
 *   level: 'municipality',
 *   includeGeometry: true
 * });
 * ```
 */
export function getResults(
  eventId: string,
  options: GetResultsOptions = {}
): ElectionResult[] | ResultsWithGeometry {
  const { level = "precinct", includeGeometry = false } = options;

  const validLevels: AggregationLevel[] = [
    "precinct",
    "municipality",
    "district",
    "island",
  ];
  if (!validLevels.includes(level)) {
    throw new Error(
      `Invalid level '${level}'. Must be one of: ${validLevels.sort().join(", ")}`
    );
  }

  const dataDir = getDataPath();

  // Look for results file
  const resultsJson = join(dataDir, eventId, `results_${level}.json`);
  const flatJson = join(dataDir, `${eventId}_${level}.json`);

  let results: ElectionResult[] | null = null;

  if (existsSync(resultsJson)) {
    const content = readFileSync(resultsJson, "utf-8");
    results = JSON.parse(content) as ElectionResult[];
  } else if (existsSync(flatJson)) {
    const content = readFileSync(flatJson, "utf-8");
    results = JSON.parse(content) as ElectionResult[];
  } else {
    // Check if event exists at all
    const eventDir = join(dataDir, eventId);
    let matchingFiles: string[] = [];

    try {
      matchingFiles = readdirSync(dataDir).filter((f) =>
        f.startsWith(eventId)
      );
    } catch {
      // Directory might not exist
    }

    if (!existsSync(eventDir) && matchingFiles.length === 0) {
      throw new Error(
        `Event '${eventId}' not found. Use listEvents() to see available events.`
      );
    }

    throw new Error(
      `Results at level '${level}' not available for event '${eventId}'.`
    );
  }

  if (includeGeometry) {
    // Look for geometry file
    const geoFile = join(dataDir, eventId, `geometry_${level}.geojson`);
    const flatGeo = join(dataDir, `geometry_${level}.geojson`);

    let geometry: GeoJSONFeatureCollection | undefined;

    if (existsSync(geoFile)) {
      const content = readFileSync(geoFile, "utf-8");
      geometry = JSON.parse(content) as GeoJSONFeatureCollection;
    } else if (existsSync(flatGeo)) {
      const content = readFileSync(flatGeo, "utf-8");
      geometry = JSON.parse(content) as GeoJSONFeatureCollection;
    }

    return {
      results,
      geometry,
    };
  }

  return results;
}

// Default exports
export default {
  VERSION,
  setDataPath,
  listEvents,
  getResults,
};
