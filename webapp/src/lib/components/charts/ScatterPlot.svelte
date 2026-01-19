<script lang="ts">
	import { onMount } from 'svelte';
	import * as d3 from 'd3';

	interface DataPoint {
		x: number;
		y: number;
		label: string;
		color?: string;
		size?: number;
	}

	interface Annotation {
		label: string;
		text: string;
		position?: 'top' | 'right' | 'left' | 'bottom';
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
		annotations?: Annotation[];
		loading?: boolean;
		animateOnMount?: boolean;
		tooltipFormat?: (point: DataPoint) => string;
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
		onPointHover = () => {},
		annotations = [],
		loading = false,
		animateOnMount = true,
		tooltipFormat = (p: DataPoint) => `<strong>${p.label}</strong><br/>${xLabel || 'X'}: ${xFormat(p.x)}<br/>${yLabel || 'Y'}: ${yFormat(p.y)}`
	}: Props = $props();

	let hoveredPoint: DataPoint | null = $state(null);
	let tooltipX = $state(0);
	let tooltipY = $state(0);
	let animationProgress = $state(animateOnMount ? 0 : 1);

	onMount(() => {
		if (animateOnMount) {
			const duration = 700;
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

	// Animated point position - scatter from center
	function getAnimatedCx(point: DataPoint): number {
		const targetX = xScale(point.x);
		const centerX = innerWidth / 2;
		const easedProgress = 1 - Math.pow(1 - animationProgress, 3);
		return centerX + (targetX - centerX) * easedProgress;
	}

	function getAnimatedCy(point: DataPoint): number {
		const targetY = yScale(point.y);
		const centerY = innerHeight / 2;
		const easedProgress = 1 - Math.pow(1 - animationProgress, 3);
		return centerY + (targetY - centerY) * easedProgress;
	}

	function getAnimatedPointOpacity(d: DataPoint): number {
		const baseOpacity = getPointOpacity(d);
		return baseOpacity * Math.min(1, animationProgress * 2);
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

	function getAnnotation(label: string): Annotation | undefined {
		return annotations.find(a => a.label === label);
	}
</script>

<div class="scatter-container">
	{#if loading}
		<div class="loading-overlay">
			<div class="loading-spinner"></div>
			<span class="loading-text">Loading data...</span>
		</div>
	{/if}

	<svg {width} {height} class="scatter-plot" class:loading>
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
			{#if showRegression && regression() && animationProgress > 0.5}
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
					opacity={Math.min(1, (animationProgress - 0.5) * 2) * 0.7}
					class="regression-line"
				/>
				<text
					x={innerWidth - 10}
					y="20"
					text-anchor="end"
					class="r-squared"
					opacity={Math.min(1, (animationProgress - 0.5) * 2)}
				>
					R² = {reg!.rSquared.toFixed(3)}
				</text>
			{/if}

			<!-- Points -->
			{#each data as point}
				{@const annotation = getAnnotation(point.label)}
				{@const cx = getAnimatedCx(point)}
				{@const cy = getAnimatedCy(point)}
				<circle
					{cx}
					{cy}
					r={getPointSize(point)}
					fill={getPointColor(point)}
					opacity={getAnimatedPointOpacity(point)}
					class="point"
					role="button"
					tabindex="0"
					aria-label="{point.label}: ({xFormat(point.x)}, {yFormat(point.y)})"
					onmousemove={(e) => handleMouseMove(e, point)}
					onmouseleave={handleMouseLeave}
					onclick={() => onPointClick(point)}
					onkeydown={(e) => e.key === 'Enter' && onPointClick(point)}
				/>
				<!-- Annotation callout -->
				{#if annotation && animationProgress > 0.8}
					<g class="annotation" transform="translate({cx}, {cy})">
						<line
							x1="0"
							y1="-8"
							x2="0"
							y2="-24"
							stroke={getPointColor(point)}
							stroke-width="1.5"
							stroke-dasharray="3,2"
						/>
						<rect
							x={-annotation.text.length * 4 - 8}
							y="-42"
							width={annotation.text.length * 8 + 16}
							height="18"
							fill="var(--color-surface-elevated)"
							stroke={getPointColor(point)}
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
			{@html tooltipFormat(hoveredPoint)}
		</div>
	{/if}
</div>

<style>
	.scatter-container {
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

	.scatter-plot.loading {
		opacity: 0.3;
	}

	.scatter-plot {
		font-family: var(--font-body);
		overflow: visible;
	}

	.point {
		cursor: pointer;
		transition:
			r 0.25s cubic-bezier(0.4, 0, 0.2, 1),
			opacity 0.3s ease,
			filter 0.2s ease;
	}

	.point:hover {
		filter: drop-shadow(0 3px 6px rgba(0, 0, 0, 0.4)) brightness(1.15);
	}

	.point:focus {
		outline: none;
	}

	.point:focus-visible {
		stroke: var(--color-accent);
		stroke-width: 3;
	}

	.regression-line {
		transition: opacity 0.4s ease;
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

	.r-squared {
		font-size: var(--text-base);
		fill: var(--color-accent);
		font-weight: var(--font-bold);
		text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
		transition: opacity 0.4s ease;
	}

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
