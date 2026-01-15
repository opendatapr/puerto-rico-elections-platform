<script lang="ts">
	import { onMount } from 'svelte';
	import * as d3 from 'd3';

	interface DataPoint {
		label: string;
		value: number;
		color?: string;
	}

	interface Props {
		data: DataPoint[];
		width?: number;
		height?: number;
		horizontal?: boolean;
		showValues?: boolean;
		valueFormat?: (value: number) => string;
		highlightLabel?: string | null;
		onBarClick?: (label: string, value: number) => void;
		onBarHover?: (label: string | null) => void;
	}

	let {
		data = [],
		width = 500,
		height = 300,
		horizontal = false,
		showValues = true,
		valueFormat = (v) => v.toFixed(1),
		highlightLabel = null,
		onBarClick = () => {},
		onBarHover = () => {}
	}: Props = $props();

	let hoveredLabel: string | null = $state(null);

	// Margins
	let margin = $derived({ top: 20, right: 20, bottom: horizontal ? 40 : 60, left: horizontal ? 120 : 40 });
	let innerWidth = $derived(width - margin.left - margin.right);
	let innerHeight = $derived(height - margin.top - margin.bottom);

	// Scales
	let xScale = $derived(
		horizontal
			? d3.scaleLinear()
				.domain([0, d3.max(data, d => d.value) || 0])
				.range([0, innerWidth])
			: d3.scaleBand<string>()
				.domain(data.map(d => d.label))
				.range([0, innerWidth])
				.padding(0.2)
	);

	let yScale = $derived(
		horizontal
			? d3.scaleBand<string>()
				.domain(data.map(d => d.label))
				.range([0, innerHeight])
				.padding(0.2)
			: d3.scaleLinear()
				.domain([0, d3.max(data, d => d.value) || 0])
				.range([innerHeight, 0])
	);

	function getBarX(d: DataPoint): number {
		if (horizontal) return 0;
		return (xScale as d3.ScaleBand<string>)(d.label) || 0;
	}

	function getBarY(d: DataPoint): number {
		if (horizontal) return (yScale as d3.ScaleBand<string>)(d.label) || 0;
		return (yScale as d3.ScaleLinear<number, number>)(d.value);
	}

	function getBarWidth(d: DataPoint): number {
		if (horizontal) return (xScale as d3.ScaleLinear<number, number>)(d.value);
		return (xScale as d3.ScaleBand<string>).bandwidth();
	}

	function getBarHeight(d: DataPoint): number {
		if (horizontal) return (yScale as d3.ScaleBand<string>).bandwidth();
		return innerHeight - (yScale as d3.ScaleLinear<number, number>)(d.value);
	}

	function getBarColor(d: DataPoint): string {
		return d.color || 'var(--color-primary)';
	}

	function getBarOpacity(d: DataPoint): number {
		if (highlightLabel && d.label !== highlightLabel && d.label !== hoveredLabel) {
			return 0.4;
		}
		return 1;
	}
</script>

<svg {width} {height} class="bar-chart">
	<g transform="translate({margin.left}, {margin.top})">
		<!-- Bars -->
		{#each data as d}
			<g
				class="bar-group"
				role="button"
				tabindex="0"
				aria-label="{d.label}: {valueFormat(d.value)}"
				onmouseenter={() => { hoveredLabel = d.label; onBarHover(d.label); }}
				onmouseleave={() => { hoveredLabel = null; onBarHover(null); }}
				onclick={() => onBarClick(d.label, d.value)}
				onkeydown={(e) => e.key === 'Enter' && onBarClick(d.label, d.value)}
			>
				<rect
					x={getBarX(d)}
					y={getBarY(d)}
					width={getBarWidth(d)}
					height={getBarHeight(d)}
					fill={getBarColor(d)}
					opacity={getBarOpacity(d)}
					rx="2"
					class="bar"
				/>
				{#if showValues}
					<text
						x={horizontal ? getBarX(d) + getBarWidth(d) + 8 : getBarX(d) + getBarWidth(d) / 2}
						y={horizontal ? getBarY(d) + getBarHeight(d) / 2 : getBarY(d) - 8}
						text-anchor={horizontal ? 'start' : 'middle'}
						dominant-baseline={horizontal ? 'middle' : 'auto'}
						class="bar-value"
						opacity={getBarOpacity(d)}
					>
						{valueFormat(d.value)}
					</text>
				{/if}
			</g>
		{/each}

		<!-- X Axis -->
		<g transform="translate(0, {innerHeight})" class="axis x-axis">
			{#if horizontal}
				{#each (xScale as d3.ScaleLinear<number, number>).ticks(5) as tick}
					<g transform="translate({(xScale as d3.ScaleLinear<number, number>)(tick)}, 0)">
						<line y2="6" stroke="var(--color-border-light)" />
						<text y="20" text-anchor="middle" class="tick-label">{tick}</text>
					</g>
				{/each}
			{:else}
				{#each data as d}
					<g transform="translate({(xScale as d3.ScaleBand<string>)(d.label)! + (xScale as d3.ScaleBand<string>).bandwidth() / 2}, 0)">
						<text y="20" text-anchor="middle" class="tick-label">{d.label}</text>
					</g>
				{/each}
			{/if}
		</g>

		<!-- Y Axis -->
		<g class="axis y-axis">
			{#if horizontal}
				{#each data as d}
					<g transform="translate(0, {(yScale as d3.ScaleBand<string>)(d.label)! + (yScale as d3.ScaleBand<string>).bandwidth() / 2})">
						<text x="-8" text-anchor="end" dominant-baseline="middle" class="tick-label">{d.label}</text>
					</g>
				{/each}
			{:else}
				{#each (yScale as d3.ScaleLinear<number, number>).ticks(5) as tick}
					<g transform="translate(0, {(yScale as d3.ScaleLinear<number, number>)(tick)})">
						<line x2="-6" stroke="var(--color-border-light)" />
						<text x="-10" text-anchor="end" dominant-baseline="middle" class="tick-label">{tick}</text>
					</g>
				{/each}
			{/if}
		</g>
	</g>
</svg>

<style>
	.bar-chart {
		font-family: var(--font-body);
	}

	.bar {
		transition: opacity var(--transition-fast);
	}

	.bar-group {
		cursor: pointer;
	}

	.bar-group:hover .bar {
		filter: brightness(1.15);
	}

	.bar-group:focus {
		outline: none;
	}

	.bar-group:focus-visible .bar {
		stroke: var(--color-accent);
		stroke-width: 2;
	}

	.bar-value {
		font-size: var(--text-xs);
		fill: var(--color-text-muted);
		font-weight: var(--font-medium);
	}

	.tick-label {
		font-size: var(--text-xs);
		fill: var(--color-text-muted);
	}
</style>
