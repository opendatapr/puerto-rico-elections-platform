<script lang="ts">
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import * as d3 from 'd3';
	import * as topojson from 'topojson-client';
	import type { Topology, GeometryCollection } from 'topojson-specification';

	interface Props {
		data?: Map<string, number>;
		colorScale?: (value: number) => string;
		width?: number;
		height?: number;
		tooltipFormat?: (name: string, value: number | undefined) => string;
		highlightId?: string | null;
		onMunicipalityClick?: (id: string, name: string) => void;
		onMunicipalityHover?: (id: string | null, name: string | null) => void;
	}

	let {
		data = new Map(),
		colorScale = d3.scaleSequential(d3.interpolateBlues).domain([0, 100]),
		width = 600,
		height = 400,
		tooltipFormat = (name, value) => `${name}: ${value?.toFixed(1) ?? 'N/A'}`,
		highlightId = null,
		onMunicipalityClick = () => {},
		onMunicipalityHover = () => {}
	}: Props = $props();

	let svg: SVGSVGElement;
	let municipalities: any[] = $state([]);
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

	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/geo/municipalities.topojson`);
			if (!response.ok) {
				console.warn('TopoJSON not found, using placeholder');
				return;
			}
			const topo: Topology = await response.json();
			const geo = topojson.feature(
				topo,
				topo.objects.municipalities as GeometryCollection
			);
			municipalities = (geo as any).features;
		} catch (error) {
			console.error('Failed to load map data:', error);
		}
	});

	function getMunicipalityName(feature: any): string {
		return feature.properties.Municipio || feature.properties.MUNICIPIO || feature.properties.NAME || 'Unknown';
	}

	function handleMouseMove(event: MouseEvent, feature: any) {
		const id = getMunicipalityName(feature);
		const value = data.get(id);
		hoveredId = id;
		tooltipContent = tooltipFormat(id, value);
		tooltipX = event.clientX + 10;
		tooltipY = event.clientY - 10;
		showTooltip = true;
		onMunicipalityHover(id, id);
	}

	function handleMouseLeave() {
		hoveredId = null;
		showTooltip = false;
		onMunicipalityHover(null, null);
	}

	function handleClick(feature: any) {
		const id = getMunicipalityName(feature);
		onMunicipalityClick(id, id);
	}

	function getFill(feature: any): string {
		const id = getMunicipalityName(feature);
		const value = data.get(id);
		if (value === undefined) return 'var(--color-surface-elevated)';
		return colorScale(value);
	}

	function getStroke(feature: any): string {
		const id = getMunicipalityName(feature);
		if (id === highlightId || id === hoveredId) {
			return 'var(--color-accent)';
		}
		return 'var(--color-border)';
	}

	function getStrokeWidth(feature: any): number {
		const id = getMunicipalityName(feature);
		if (id === highlightId || id === hoveredId) {
			return 2;
		}
		return 0.5;
	}
</script>

<div class="map-container">
	<svg
		bind:this={svg}
		viewBox="0 0 {width} {height}"
		preserveAspectRatio="xMidYMid meet"
	>
		<g class="municipalities">
			{#each municipalities as feature}
				<path
					d={pathGenerator(feature)}
					fill={getFill(feature)}
					stroke={getStroke(feature)}
					stroke-width={getStrokeWidth(feature)}
					class="municipality"
					role="button"
					tabindex="0"
					aria-label={getMunicipalityName(feature)}
					onmousemove={(e) => handleMouseMove(e, feature)}
					onmouseleave={handleMouseLeave}
					onclick={() => handleClick(feature)}
					onkeydown={(e) => e.key === 'Enter' && handleClick(feature)}
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

	.municipality {
		cursor: pointer;
		transition:
			fill var(--transition-fast),
			stroke var(--transition-fast),
			stroke-width var(--transition-fast);
	}

	.municipality:hover {
		filter: brightness(1.1);
	}

	.municipality:focus {
		outline: none;
	}

	.municipality:focus-visible {
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
