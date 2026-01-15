<script lang="ts">
	import * as d3 from 'd3';

	interface DataPoint {
		x: number;
		y: number;
		label: string;
		color?: string;
		size?: number;
	}

	interface Props {
		data: DataPoint[];
		width?: number;
		height?: number;
		xLabel?: string;
		yLabel?: string;
		xFormat?: (value: number) => string;
		yFormat?: (value: number) => string;
		showRegression?: boolean;
		highlightLabel?: string | null;
		onPointClick?: (point: DataPoint) => void;
		onPointHover?: (point: DataPoint | null) => void;
	}

	let {
		data = [],
		width = 500,
		height = 400,
		xLabel = '',
		yLabel = '',
		xFormat = (v) => v.toFixed(1),
		yFormat = (v) => v.toFixed(1),
		showRegression = false,
		highlightLabel = null,
		onPointClick = () => {},
		onPointHover = () => {}
	}: Props = $props();

	let hoveredPoint: DataPoint | null = $state(null);
	let tooltipX = $state(0);
	let tooltipY = $state(0);

	const margin = { top: 20, right: 20, bottom: 50, left: 60 };
	let innerWidth = $derived(width - margin.left - margin.right);
	let innerHeight = $derived(height - margin.top - margin.bottom);

	let xExtent = $derived(d3.extent(data, d => d.x) as [number, number]);
	let yExtent = $derived(d3.extent(data, d => d.y) as [number, number]);

	let xScale = $derived(
		d3.scaleLinear()
			.domain([xExtent[0] * 0.95, xExtent[1] * 1.05])
			.range([0, innerWidth])
	);

	let yScale = $derived(
		d3.scaleLinear()
			.domain([yExtent[0] * 0.95, yExtent[1] * 1.05])
			.range([innerHeight, 0])
	);

	// Linear regression calculation
	let regression = $derived(() => {
		if (!showRegression || data.length < 2) return null;

		const n = data.length;
		const sumX = d3.sum(data, d => d.x);
		const sumY = d3.sum(data, d => d.y);
		const sumXY = d3.sum(data, d => d.x * d.y);
		const sumX2 = d3.sum(data, d => d.x * d.x);

		const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
		const intercept = (sumY - slope * sumX) / n;

		// R-squared
		const yMean = sumY / n;
		const ssTotal = d3.sum(data, d => Math.pow(d.y - yMean, 2));
		const ssResidual = d3.sum(data, d => Math.pow(d.y - (slope * d.x + intercept), 2));
		const rSquared = 1 - ssResidual / ssTotal;

		return { slope, intercept, rSquared };
	});

	function getPointOpacity(d: DataPoint): number {
		if (highlightLabel && d.label !== highlightLabel && d !== hoveredPoint) {
			return 0.3;
		}
		return 0.8;
	}

	function getPointColor(d: DataPoint): string {
		return d.color || 'var(--color-accent)';
	}

	function getPointSize(d: DataPoint): number {
		const baseSize = d.size || 6;
		return d === hoveredPoint ? baseSize * 1.5 : baseSize;
	}

	function handleMouseMove(event: MouseEvent, point: DataPoint) {
		hoveredPoint = point;
		tooltipX = event.clientX + 10;
		tooltipY = event.clientY - 10;
		onPointHover(point);
	}

	function handleMouseLeave() {
		hoveredPoint = null;
		onPointHover(null);
	}
</script>

<div class="scatter-container">
	<svg {width} {height} class="scatter-plot">
		<g transform="translate({margin.left}, {margin.top})">
			<!-- Grid -->
			<g class="grid">
				{#each yScale.ticks(5) as tick}
					<line
						x1="0"
						x2={innerWidth}
						y1={yScale(tick)}
						y2={yScale(tick)}
						stroke="var(--color-border)"
						stroke-opacity="0.5"
					/>
				{/each}
				{#each xScale.ticks(5) as tick}
					<line
						x1={xScale(tick)}
						x2={xScale(tick)}
						y1="0"
						y2={innerHeight}
						stroke="var(--color-border)"
						stroke-opacity="0.3"
					/>
				{/each}
			</g>

			<!-- Regression line -->
			{#if showRegression && regression()}
				{@const reg = regression()}
				{@const x1 = xExtent[0]}
				{@const x2 = xExtent[1]}
				{@const y1 = reg!.slope * x1 + reg!.intercept}
				{@const y2 = reg!.slope * x2 + reg!.intercept}
				<line
					x1={xScale(x1)}
					y1={yScale(y1)}
					x2={xScale(x2)}
					y2={yScale(y2)}
					stroke="var(--color-accent)"
					stroke-width="2"
					stroke-dasharray="6,4"
					opacity="0.7"
				/>
				<text
					x={innerWidth - 10}
					y="20"
					text-anchor="end"
					class="r-squared"
				>
					R² = {reg!.rSquared.toFixed(3)}
				</text>
			{/if}

			<!-- Points -->
			{#each data as point}
				<circle
					cx={xScale(point.x)}
					cy={yScale(point.y)}
					r={getPointSize(point)}
					fill={getPointColor(point)}
					opacity={getPointOpacity(point)}
					class="point"
					role="button"
					tabindex="0"
					aria-label="{point.label}: ({xFormat(point.x)}, {yFormat(point.y)})"
					onmousemove={(e) => handleMouseMove(e, point)}
					onmouseleave={handleMouseLeave}
					onclick={() => onPointClick(point)}
					onkeydown={(e) => e.key === 'Enter' && onPointClick(point)}
				/>
			{/each}

			<!-- X Axis -->
			<g transform="translate(0, {innerHeight})" class="axis x-axis">
				<line x2={innerWidth} stroke="var(--color-border-light)" />
				{#each xScale.ticks(5) as tick}
					<g transform="translate({xScale(tick)}, 0)">
						<line y2="6" stroke="var(--color-border-light)" />
						<text y="20" text-anchor="middle" class="tick-label">{xFormat(tick)}</text>
					</g>
				{/each}
				{#if xLabel}
					<text x={innerWidth / 2} y="40" text-anchor="middle" class="axis-label">{xLabel}</text>
				{/if}
			</g>

			<!-- Y Axis -->
			<g class="axis y-axis">
				<line y2={innerHeight} stroke="var(--color-border-light)" />
				{#each yScale.ticks(5) as tick}
					<g transform="translate(0, {yScale(tick)})">
						<line x2="-6" stroke="var(--color-border-light)" />
						<text x="-10" text-anchor="end" dominant-baseline="middle" class="tick-label">{yFormat(tick)}</text>
					</g>
				{/each}
				{#if yLabel}
					<text
						transform="rotate(-90)"
						x={-innerHeight / 2}
						y="-45"
						text-anchor="middle"
						class="axis-label"
					>{yLabel}</text>
				{/if}
			</g>
		</g>
	</svg>

	{#if hoveredPoint}
		<div class="tooltip" style="left: {tooltipX}px; top: {tooltipY}px;">
			<strong>{hoveredPoint.label}</strong><br />
			{xLabel || 'X'}: {xFormat(hoveredPoint.x)}<br />
			{yLabel || 'Y'}: {yFormat(hoveredPoint.y)}
		</div>
	{/if}
</div>

<style>
	.scatter-container {
		position: relative;
	}

	.scatter-plot {
		font-family: var(--font-body);
	}

	.point {
		cursor: pointer;
		transition: r var(--transition-fast), opacity var(--transition-fast);
	}

	.point:focus {
		outline: none;
	}

	.point:focus-visible {
		stroke: var(--color-accent);
		stroke-width: 2;
	}

	.tick-label {
		font-size: var(--text-xs);
		fill: var(--color-text-muted);
	}

	.axis-label {
		font-size: var(--text-sm);
		fill: var(--color-text);
		font-weight: var(--font-medium);
	}

	.r-squared {
		font-size: var(--text-sm);
		fill: var(--color-accent);
		font-weight: var(--font-medium);
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
	}
</style>
