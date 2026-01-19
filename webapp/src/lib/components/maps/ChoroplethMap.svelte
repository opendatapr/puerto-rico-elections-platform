<script lang="ts">
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import * as d3 from 'd3';
	import * as topojson from 'topojson-client';
	import type { Topology, GeometryCollection } from 'topojson-specification';

	// Normalize strings for accent-insensitive matching
	// Removes diacritical marks (accents) and converts to lowercase
	function normalizeString(s: string): string {
		return s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
	}

	type MapLevel = 'municipality' | 'precinct';

	interface Props {
		level?: MapLevel;
		data?: Map<string, number>;
		colorScale?: (value: number) => string;
		width?: number;
		height?: number;
		tooltipFormat?: (name: string, value: number | undefined) => string;
		highlightId?: string | null;
		onFeatureClick?: (id: string, name: string) => void;
		onFeatureHover?: (id: string | null, name: string | null) => void;
		// Legacy props for backwards compatibility
		onMunicipalityClick?: (id: string, name: string) => void;
		onMunicipalityHover?: (id: string | null, name: string | null) => void;
	}

	let {
		level = 'municipality',
		data = new Map(),
		colorScale = d3.scaleSequential(d3.interpolateBlues).domain([0, 100]),
		width = 600,
		height = 400,
		tooltipFormat = (name, value) => `${name}: ${value?.toFixed(1) ?? 'N/A'}`,
		highlightId = null,
		onFeatureClick,
		onFeatureHover,
		onMunicipalityClick = () => {},
		onMunicipalityHover = () => {}
	}: Props = $props();

	// Use new handlers if provided, fallback to legacy
	const handleFeatureClick = $derived(onFeatureClick ?? onMunicipalityClick);
	const handleFeatureHover = $derived(onFeatureHover ?? onMunicipalityHover);

	// Create normalized lookup for accent-insensitive matching
	// This handles cases where TopoJSON has "Sábana Grande" but data has "Sabana Grande"
	const normalizedData = $derived(() => {
		const lookup = new Map<string, number>();
		data.forEach((value, key) => {
			lookup.set(normalizeString(key), value);
		});
		return lookup;
	});

	// Helper to get value from data with accent-insensitive matching
	function getDataValue(id: string): number | undefined {
		// First try exact match (faster)
		const exactValue = data.get(id);
		if (exactValue !== undefined) {
			return exactValue;
		}
		// Fall back to normalized match for accent-insensitive lookup
		return normalizedData().get(normalizeString(id));
	}

	let svg: SVGSVGElement;
	let features: any[] = $state([]);
	let hoveredId: string | null = $state(null);
	let tooltipContent: string = $state('');
	let tooltipX: number = $state(0);
	let tooltipY: number = $state(0);
	let showTooltip: boolean = $state(false);

	// Puerto Rico centered projection (reactive to width/height changes)
	let projection = $derived(
		d3.geoMercator()
			.center([-66.5, 18.22])
			.scale(9000)
			.translate([width / 2, height / 2])
	);

	let pathGenerator = $derived(d3.geoPath().projection(projection));

	// Determine the data file and object name based on level
	const geoConfig = $derived({
		file: level === 'precinct' ? 'precincts.topojson' : 'municipalities.topojson',
		objectName: level === 'precinct' ? 'precincts' : 'municipalities'
	});

	async function loadGeoData() {
		try {
			const response = await fetch(`${base}/data/geo/${geoConfig.file}`);
			if (!response.ok) {
				console.warn('TopoJSON not found, using placeholder');
				return;
			}
			const topo: Topology = await response.json();
			const objectName = geoConfig.objectName;
			if (!topo.objects[objectName]) {
				console.error(`Object "${objectName}" not found in TopoJSON`);
				return;
			}
			const geo = topojson.feature(
				topo,
				topo.objects[objectName] as GeometryCollection
			);
			features = (geo as any).features;
		} catch (error) {
			console.error('Failed to load map data:', error);
		}
	}

	// Track previous level to detect changes
	let previousLevel: MapLevel | null = null;

	onMount(() => {
		previousLevel = level;
		loadGeoData();
	});

	// Reload data when level changes (but not on initial mount)
	$effect(() => {
		if (previousLevel !== null && previousLevel !== level) {
			previousLevel = level;
			loadGeoData();
		}
	});

	function getFeatureId(feature: any): string {
		if (level === 'precinct') {
			// Precinct TopoJSON uses 'id' property (format: d01_p00)
			return feature.properties.id || `d${feature.properties.district}_p${feature.properties.precinct_index}`;
		}
		// Municipality TopoJSON uses Municipio/NAME
		return feature.properties.Municipio || feature.properties.MUNICIPIO || feature.properties.NAME || 'Unknown';
	}

	function getFeatureName(feature: any): string {
		if (level === 'precinct') {
			// Format nicely for display: "District 1, Precinct 0" or use id
			const d = feature.properties.district;
			const p = feature.properties.precinct_index;
			return `District ${d}, Precinct ${p}`;
		}
		return feature.properties.Municipio || feature.properties.MUNICIPIO || feature.properties.NAME || 'Unknown';
	}

	function onMouseMove(event: MouseEvent, feature: any) {
		const id = getFeatureId(feature);
		const name = getFeatureName(feature);
		const value = getDataValue(id);
		hoveredId = id;
		tooltipContent = tooltipFormat(name, value);
		tooltipX = event.clientX + 10;
		tooltipY = event.clientY - 10;
		showTooltip = true;
		handleFeatureHover(id, name);
	}

	function onMouseLeave() {
		hoveredId = null;
		showTooltip = false;
		handleFeatureHover(null, null);
	}

	function onClick(feature: any) {
		const id = getFeatureId(feature);
		const name = getFeatureName(feature);
		handleFeatureClick(id, name);
	}

	function getFill(feature: any): string {
		const id = getFeatureId(feature);
		const value = getDataValue(id);
		if (value === undefined) {
			// For precincts, use the built-in color if no data provided
			if (level === 'precinct' && feature.properties.color) {
				return feature.properties.color;
			}
			return 'var(--color-surface-elevated)';
		}
		return colorScale(value);
	}

	function getStroke(feature: any): string {
		const id = getFeatureId(feature);
		if (id === highlightId || id === hoveredId) {
			return 'var(--color-accent)';
		}
		return 'var(--color-border)';
	}

	function getStrokeWidth(feature: any): number {
		const id = getFeatureId(feature);
		if (id === highlightId || id === hoveredId) {
			return 2;
		}
		// Thinner strokes for precincts since there are more of them
		return level === 'precinct' ? 0.3 : 0.5;
	}
</script>

<div class="map-container">
	<svg
		bind:this={svg}
		viewBox="0 0 {width} {height}"
		preserveAspectRatio="xMidYMid meet"
	>
		<g class="features">
			{#each features as feature}
				<path
					d={pathGenerator(feature)}
					fill={getFill(feature)}
					stroke={getStroke(feature)}
					stroke-width={getStrokeWidth(feature)}
					class="feature"
					role="button"
					tabindex="0"
					aria-label={getFeatureName(feature)}
					onmousemove={(e) => onMouseMove(e, feature)}
					onmouseleave={onMouseLeave}
					onclick={() => onClick(feature)}
					onkeydown={(e) => e.key === 'Enter' && onClick(feature)}
				/>
			{/each}
		</g>
	</svg>

	{#if showTooltip}
		<div
			class="tooltip"
			style="left: {tooltipX}px; top: {tooltipY}px;"
		>
			{tooltipContent}
		</div>
	{/if}
</div>

<style>
	.map-container {
		position: relative;
		width: 100%;
		height: 100%;
	}

	svg {
		width: 100%;
		height: 100%;
	}

	.feature {
		cursor: pointer;
		transition:
			fill var(--transition-fast),
			stroke var(--transition-fast),
			stroke-width var(--transition-fast);
	}

	.feature:hover {
		filter: brightness(1.1);
	}

	.feature:focus {
		outline: none;
	}

	.feature:focus-visible {
		stroke: var(--color-accent);
		stroke-width: 2;
	}

	.tooltip {
		position: fixed;
		z-index: 1000;
		pointer-events: none;
		background: var(--color-surface);
		border: 1px solid var(--color-border-light);
		border-radius: var(--radius-md);
		padding: var(--space-sm) var(--space-md);
		font-size: var(--text-sm);
		color: var(--color-text);
		box-shadow: var(--shadow-lg);
		white-space: nowrap;
	}
</style>
