<script lang="ts">
	import { onMount } from 'svelte';
	import * as d3 from 'd3';

	interface DataPoint {
		label: string;
		value: number;
		color?: string;
	}

	interface Annotation {
		label: string;
		text: string;
		position?: 'top' | 'right' | 'left';
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
		annotations?: Annotation[];
		loading?: boolean;
		tooltipFormat?: (d: DataPoint) => string;
		animateOnMount?: boolean;
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
		onBarHover = () => {},
		annotations = [],
		loading = false,
		tooltipFormat = (d: DataPoint) => `<strong>${d.label}</strong><br/>Value: ${valueFormat(d.value)}`,
		animateOnMount = true
	}: Props = $props();

	let hoveredLabel: string | null = $state(null);
	let hoveredData: DataPoint | null = $state(null);
	let tooltipX = $state(0);
	let tooltipY = $state(0);
	let animationProgress = $state(animateOnMount ? 0 : 1);

	onMount(() => {
		if (animateOnMount) {
			const duration = 600;
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
		return d.color || 'var(--color-accent)';
	}

	function getBarOpacity(d: DataPoint): number {
		if (highlightLabel && d.label !== highlightLabel && d.label !== hoveredLabel) {
			return 0.4;
		}
		return 1;
	}

	// Animated bar dimensions with easing
	function getAnimatedBarHeight(d: DataPoint, index: number): number {
		const baseHeight = getBarHeight(d);
		const staggerDelay = index * 0.05;
		const adjustedProgress = Math.max(0, Math.min(1, (animationProgress - staggerDelay) / (1 - staggerDelay * data.length / (data.length + 1))));
		const easedProgress = 1 - Math.pow(1 - adjustedProgress, 3);
		return baseHeight * easedProgress;
	}

	function getAnimatedBarWidth(d: DataPoint, index: number): number {
		const baseWidth = getBarWidth(d);
		if (!horizontal) return baseWidth;
		const staggerDelay = index * 0.05;
		const adjustedProgress = Math.max(0, Math.min(1, (animationProgress - staggerDelay) / (1 - staggerDelay * data.length / (data.length + 1))));
		const easedProgress = 1 - Math.pow(1 - adjustedProgress, 3);
		return baseWidth * easedProgress;
	}

	function getAnimatedBarY(d: DataPoint, index: number): number {
		if (horizontal) return getBarY(d);
		const baseY = getBarY(d);
		const baseHeight = getBarHeight(d);
		const animatedHeight = getAnimatedBarHeight(d, index);
		return baseY + (baseHeight - animatedHeight);
	}

	function handleMouseMove(event: MouseEvent, d: DataPoint) {
		hoveredLabel = d.label;
		hoveredData = d;
		tooltipX = event.clientX + 12;
		tooltipY = event.clientY - 12;
		onBarHover(d.label);
	}

	function handleMouseLeave() {
		hoveredLabel = null;
		hoveredData = null;
		onBarHover(null);
	}

	function getAnnotation(label: string): Annotation | undefined {
		return annotations.find(a => a.label === label);
	}
</script>

<div class="bar-chart-container">
	{#if loading}
		<div class="loading-overlay">
			<div class="loading-spinner"></div>
			<span class="loading-text">Loading data...</span>
		</div>
	{/if}

	<svg {width} {height} class="bar-chart" class:loading>
		<g transform="translate({margin.left}, {margin.top})">
			<!-- Bars -->
			{#each data as d, i}
				{@const annotation = getAnnotation(d.label)}
				<g
					class="bar-group"
					role="button"
					tabindex="0"
					aria-label="{d.label}: {valueFormat(d.value)}"
					onmousemove={(e) => handleMouseMove(e, d)}
					onmouseleave={handleMouseLeave}
					onclick={() => onBarClick(d.label, d.value)}
					onkeydown={(e) => e.key === 'Enter' && onBarClick(d.label, d.value)}
				>
					<rect
						x={getBarX(d)}
						y={getAnimatedBarY(d, i)}
						width={horizontal ? getAnimatedBarWidth(d, i) : getBarWidth(d)}
						height={horizontal ? getBarHeight(d) : getAnimatedBarHeight(d, i)}
						fill={getBarColor(d)}
						opacity={getBarOpacity(d)}
						rx="3"
						class="bar"
					/>
					{#if showValues && animationProgress > 0.5}
						<text
							x={horizontal ? getBarX(d) + getAnimatedBarWidth(d, i) + 8 : getBarX(d) + getBarWidth(d) / 2}
							y={horizontal ? getBarY(d) + getBarHeight(d) / 2 : getAnimatedBarY(d, i) - 8}
							text-anchor={horizontal ? 'start' : 'middle'}
							dominant-baseline={horizontal ? 'middle' : 'auto'}
							class="bar-value"
							opacity={getBarOpacity(d) * Math.min(1, (animationProgress - 0.5) * 2)}
						>
							{valueFormat(d.value)}
						</text>
					{/if}

					<!-- Annotation callout -->
					{#if annotation && animationProgress > 0.8}
						{@const barCenterX = horizontal ? getAnimatedBarWidth(d, i) / 2 : getBarX(d) + getBarWidth(d) / 2}
						{@const barTopY = getAnimatedBarY(d, i)}
						<g class="annotation" transform="translate({barCenterX}, {barTopY - 24})">
							<line
								x1="0"
								y1="12"
								x2="0"
								y2="20"
								stroke="var(--color-accent)"
								stroke-width="1.5"
								stroke-dasharray="3,2"
							/>
							<rect
								x={-annotation.text.length * 4 - 8}
								y="-12"
								width={annotation.text.length * 8 + 16}
								height="24"
								fill="var(--color-surface-elevated)"
								stroke="var(--color-accent)"
								stroke-width="1"
								rx="4"
							/>
							<text
								x="0"
								y="4"
								text-anchor="middle"
								class="annotation-text"
							>
								{annotation.text}
							</text>
						</g>
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

	<!-- Tooltip -->
	{#if hoveredData}
		<div class="tooltip" style="left: {tooltipX}px; top: {tooltipY}px;">
			{@html tooltipFormat(hoveredData)}
		</div>
	{/if}
</div>

<style>
	.bar-chart-container {
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

	.bar-chart.loading {
		opacity: 0.3;
	}

	.bar-chart {
		font-family: var(--font-body);
		overflow: visible;
	}

	.bar {
		transition:
			opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1),
			filter 0.2s ease;
	}

	.bar-group {
		cursor: pointer;
	}

	.bar-group:hover .bar {
		filter: brightness(1.2) saturate(1.1);
	}

	.bar-group:focus {
		outline: none;
	}

	.bar-group:focus-visible .bar {
		stroke: var(--color-accent);
		stroke-width: 2;
	}

	.bar-value {
		font-size: var(--text-sm);
		fill: var(--color-text);
		font-weight: var(--font-semibold);
		transition: opacity 0.3s ease;
	}

	.bar-group:hover .bar-value {
		fill: var(--color-accent);
	}

	.tick-label {
		font-size: var(--text-sm);
		fill: var(--color-text-muted);
		font-family: var(--font-body);
		font-variant-numeric: tabular-nums;
		letter-spacing: 0.01em;
	}

	.axis text {
		transition: fill 0.2s ease;
	}

	.axis text:hover {
		fill: var(--color-text);
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
