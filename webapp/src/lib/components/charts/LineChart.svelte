<script lang="ts">
	import * as d3 from 'd3';

	interface DataPoint {
		x: number | Date;
		y: number;
	}

	interface Series {
		id: string;
		label: string;
		data: DataPoint[];
		color?: string;
	}

	interface Props {
		series: Series[];
		width?: number;
		height?: number;
		xLabel?: string;
		yLabel?: string;
		showDots?: boolean;
		showArea?: boolean;
		xFormat?: (value: number | Date) => string;
		yFormat?: (value: number) => string;
		highlightSeries?: string | null;
	}

	let {
		series = [],
		width = 500,
		height = 300,
		xLabel = '',
		yLabel = '',
		showDots = true,
		showArea = false,
		xFormat = (v) => String(v),
		yFormat = (v) => v.toFixed(1),
		highlightSeries = null
	}: Props = $props();

	let hoveredSeries: string | null = $state(null);

	const margin = { top: 20, right: 20, bottom: 50, left: 60 };
	let innerWidth = $derived(width - margin.left - margin.right);
	let innerHeight = $derived(height - margin.top - margin.bottom);

	// Flatten all data points to get domain
	let allData = $derived(series.flatMap(s => s.data));

	let xExtent = $derived(d3.extent(allData, d => d.x) as [number | Date, number | Date]);
	let yMax = $derived(d3.max(allData, d => d.y) || 0);

	let xScale = $derived(
		d3.scaleLinear()
			.domain(xExtent.map(d => d instanceof Date ? d.getTime() : d) as [number, number])
			.range([0, innerWidth])
	);

	let yScale = $derived(
		d3.scaleLinear()
			.domain([0, yMax * 1.1])
			.range([innerHeight, 0])
	);

	let lineGenerator = $derived(
		d3.line<DataPoint>()
			.x(d => xScale(d.x instanceof Date ? d.x.getTime() : d.x))
			.y(d => yScale(d.y))
			.curve(d3.curveMonotoneX)
	);

	let areaGenerator = $derived(
		d3.area<DataPoint>()
			.x(d => xScale(d.x instanceof Date ? d.x.getTime() : d.x))
			.y0(innerHeight)
			.y1(d => yScale(d.y))
			.curve(d3.curveMonotoneX)
	);

	function getSeriesOpacity(s: Series): number {
		if (highlightSeries && s.id !== highlightSeries && s.id !== hoveredSeries) {
			return 0.3;
		}
		return 1;
	}

	function getSeriesColor(s: Series): string {
		return s.color || 'var(--color-accent)';
	}
</script>

<svg {width} {height} class="line-chart">
	<g transform="translate({margin.left}, {margin.top})">
		<!-- Grid lines -->
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
		</g>

		<!-- Area fills (if enabled) -->
		{#if showArea}
			{#each series as s}
				<path
					d={areaGenerator(s.data) || ''}
					fill={getSeriesColor(s)}
					fill-opacity={getSeriesOpacity(s) * 0.15}
					class="area"
				/>
			{/each}
		{/if}

		<!-- Lines -->
		{#each series as s}
			<g
				class="series"
				role="group"
				aria-label={s.label}
				onmouseenter={() => hoveredSeries = s.id}
				onmouseleave={() => hoveredSeries = null}
			>
				<path
					d={lineGenerator(s.data) || ''}
					fill="none"
					stroke={getSeriesColor(s)}
					stroke-width="2.5"
					stroke-opacity={getSeriesOpacity(s)}
					class="line"
				/>

				<!-- Dots -->
				{#if showDots}
					{#each s.data as point}
						<circle
							cx={xScale(point.x instanceof Date ? point.x.getTime() : point.x)}
							cy={yScale(point.y)}
							r="4"
							fill={getSeriesColor(s)}
							fill-opacity={getSeriesOpacity(s)}
							class="dot"
						>
							<title>{xFormat(point.x)}: {yFormat(point.y)}</title>
						</circle>
					{/each}
				{/if}
			</g>
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

<style>
	.line-chart {
		font-family: var(--font-body);
		overflow: visible;
	}

	.line {
		transition:
			stroke-opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1),
			stroke-width 0.2s ease,
			d 0.6s cubic-bezier(0.4, 0, 0.2, 1);
		stroke-linecap: round;
		stroke-linejoin: round;
	}

	.series:hover .line {
		stroke-width: 4;
		filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
	}

	.dot {
		transition:
			fill-opacity 0.3s ease,
			r 0.2s cubic-bezier(0.4, 0, 0.2, 1),
			transform 0.2s ease,
			cx 0.6s cubic-bezier(0.4, 0, 0.2, 1),
			cy 0.6s cubic-bezier(0.4, 0, 0.2, 1);
		cursor: pointer;
	}

	.dot:hover {
		r: 7;
		filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
	}

	.series:hover .dot {
		r: 5.5;
	}

	.area {
		transition:
			fill-opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1),
			d 0.6s cubic-bezier(0.4, 0, 0.2, 1);
	}

	.grid line {
		transition: stroke-opacity 0.3s ease;
	}

	.tick-label {
		font-size: var(--text-sm);
		fill: var(--color-text-muted);
		font-family: var(--font-body);
	}

	.axis-label {
		font-size: var(--text-base);
		fill: var(--color-text);
		font-weight: var(--font-semibold);
		letter-spacing: 0.01em;
	}
</style>
