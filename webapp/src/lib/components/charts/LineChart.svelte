<script lang="ts">
	import { onMount } from 'svelte';
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

	interface Annotation {
		seriesId: string;
		x: number | Date;
		text: string;
		position?: 'top' | 'right' | 'left' | 'bottom';
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
		annotations?: Annotation[];
		loading?: boolean;
		animateOnMount?: boolean;
		tooltipFormat?: (series: Series, point: DataPoint) => string;
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
		highlightSeries = null,
		annotations = [],
		loading = false,
		animateOnMount = true,
		tooltipFormat = (s: Series, p: DataPoint) => `<strong>${s.label}</strong><br/>${xLabel || 'X'}: ${xFormat(p.x)}<br/>${yLabel || 'Y'}: ${yFormat(p.y)}`
	}: Props = $props();

	let hoveredSeries: string | null = $state(null);
	let hoveredPoint: { series: Series; point: DataPoint } | null = $state(null);
	let tooltipX = $state(0);
	let tooltipY = $state(0);
	let animationProgress = $state(animateOnMount ? 0 : 1);

	onMount(() => {
		if (animateOnMount) {
			const duration = 800;
			const startTime = performance.now();

			function animate(currentTime: number) {
				const elapsed = currentTime - startTime;
				animationProgress = Math.min(elapsed / duration, 1);

				if (animationProgress < 1) {
					requestAnimationFrame(animate);
				}
			}

			requestAnimationFrame(animate);
		}
	});

	const margin = { top: 20, right: 20, bottom: 50, left: 60 };
	let innerWidth = $derived(width - margin.left - margin.right);
	let innerHeight = $derived(height - margin.top - margin.bottom);

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

	function getAnimatedLinePath(s: Series): string {
		if (animationProgress >= 1) return lineGenerator(s.data) || '';

		const animatedPointCount = Math.ceil(s.data.length * animationProgress);
		const animatedData = s.data.slice(0, Math.max(1, animatedPointCount));

		return lineGenerator(animatedData) || '';
	}

	function getAnimatedAreaPath(s: Series): string {
		if (animationProgress >= 1) return areaGenerator(s.data) || '';

		const animatedPointCount = Math.ceil(s.data.length * animationProgress);
		const animatedData = s.data.slice(0, Math.max(1, animatedPointCount));

		return areaGenerator(animatedData) || '';
	}

	function handleDotMouseMove(event: MouseEvent, s: Series, point: DataPoint) {
		hoveredSeries = s.id;
		hoveredPoint = { series: s, point };
		tooltipX = event.clientX + 12;
		tooltipY = event.clientY - 12;
	}

	function handleDotMouseLeave() {
		hoveredSeries = null;
		hoveredPoint = null;
	}

	function getAnnotationForPoint(seriesId: string, x: number | Date): Annotation | undefined {
		const xVal = x instanceof Date ? x.getTime() : x;
		return annotations.find(a => {
			const aX = a.x instanceof Date ? a.x.getTime() : a.x;
			return a.seriesId === seriesId && aX === xVal;
		});
	}

	function getAnimatedPointCount(s: Series): number {
		return Math.ceil(s.data.length * animationProgress);
	}
</script>

<div class="line-chart-container">
	{#if loading}
		<div class="loading-overlay">
			<div class="loading-spinner"></div>
			<span class="loading-text">Loading data...</span>
		</div>
	{/if}

	<svg {width} {height} class="line-chart" class:loading>
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
						d={getAnimatedAreaPath(s)}
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
					onmouseleave={() => { if (!hoveredPoint) hoveredSeries = null; }}
				>
					<path
						d={getAnimatedLinePath(s)}
						fill="none"
						stroke={getSeriesColor(s)}
						stroke-width="2.5"
						stroke-opacity={getSeriesOpacity(s)}
						class="line"
					/>

					<!-- Dots -->
					{#if showDots}
						{@const pointCount = getAnimatedPointCount(s)}
						{#each s.data.slice(0, pointCount) as point}
							{@const annotation = getAnnotationForPoint(s.id, point.x)}
							{@const cx = xScale(point.x instanceof Date ? point.x.getTime() : point.x)}
							{@const cy = yScale(point.y)}
							{@const isHovered = hoveredPoint?.point === point}
							<circle
								{cx}
								{cy}
								r={isHovered ? 7 : 4}
								fill={getSeriesColor(s)}
								fill-opacity={getSeriesOpacity(s)}
								class="dot"
								class:hovered={isHovered}
								role="graphics-symbol"
								aria-label="{s.label}: {xFormat(point.x)}, {yFormat(point.y)}"
								onmousemove={(e) => handleDotMouseMove(e, s, point)}
								onmouseleave={handleDotMouseLeave}
							/>
							<!-- Annotation callout -->
							{#if annotation && animationProgress > 0.8}
								<g class="annotation" transform="translate({cx}, {cy})">
									<line
										x1="0"
										y1="-8"
										x2="0"
										y2="-24"
										stroke={getSeriesColor(s)}
										stroke-width="1.5"
										stroke-dasharray="3,2"
									/>
									<rect
										x={-annotation.text.length * 4 - 8}
										y="-42"
										width={annotation.text.length * 8 + 16}
										height="18"
										fill="var(--color-surface-elevated)"
										stroke={getSeriesColor(s)}
										stroke-width="1"
										rx="4"
									/>
									<text
										x="0"
										y="-30"
										text-anchor="middle"
										class="annotation-text"
									>
										{annotation.text}
									</text>
								</g>
							{/if}
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

	<!-- Tooltip -->
	{#if hoveredPoint}
		<div class="tooltip" style="left: {tooltipX}px; top: {tooltipY}px;">
			{@html tooltipFormat(hoveredPoint.series, hoveredPoint.point)}
		</div>
	{/if}
</div>

<style>
	.line-chart-container {
		position: relative;
		display: inline-block;
	}

	.loading-overlay {
		position: absolute;
		inset: 0;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		background: var(--color-surface);
		background: linear-gradient(135deg, var(--color-surface) 0%, var(--color-surface-elevated) 100%);
		border-radius: var(--radius-md);
		z-index: 10;
	}

	.loading-spinner {
		width: 32px;
		height: 32px;
		border: 3px solid var(--color-border);
		border-top-color: var(--color-accent);
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	.loading-text {
		margin-top: var(--space-sm);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}

	.line-chart.loading {
		opacity: 0.3;
	}

	.line-chart {
		font-family: var(--font-body);
		overflow: visible;
	}

	.line {
		transition:
			stroke-opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1),
			stroke-width 0.2s ease;
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
			filter 0.2s ease;
		cursor: pointer;
	}

	.dot:hover,
	.dot.hovered {
		filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
	}

	.series:hover .dot {
		r: 5.5;
	}

	.area {
		transition: fill-opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1);
	}

	.grid line {
		transition: stroke-opacity 0.3s ease;
	}

	.tick-label {
		font-size: var(--text-sm);
		fill: var(--color-text-muted);
		font-family: var(--font-body);
		font-variant-numeric: tabular-nums;
		letter-spacing: 0.01em;
	}

	.axis-label {
		font-size: var(--text-base);
		fill: var(--color-text);
		font-weight: var(--font-semibold);
		letter-spacing: 0.01em;
	}

	/* Tooltip styles */
	.tooltip {
		position: fixed;
		z-index: 1000;
		pointer-events: none;
		background: var(--color-surface-elevated);
		border: 1px solid var(--color-border-light);
		border-radius: var(--radius-md);
		padding: var(--space-sm) var(--space-md);
		font-size: var(--text-sm);
		color: var(--color-text);
		box-shadow: var(--shadow-xl);
		backdrop-filter: blur(8px);
		animation: tooltipFadeIn 0.15s ease-out;
		max-width: 240px;
	}

	@keyframes tooltipFadeIn {
		from {
			opacity: 0;
			transform: translateY(4px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.tooltip :global(strong) {
		color: var(--color-accent);
		font-weight: var(--font-semibold);
	}

	/* Annotation styles */
	.annotation {
		animation: annotationFadeIn 0.4s ease-out;
	}

	@keyframes annotationFadeIn {
		from {
			opacity: 0;
			transform: translateY(8px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.annotation-text {
		font-size: var(--text-xs);
		fill: var(--color-text);
		font-weight: var(--font-medium);
	}
</style>
