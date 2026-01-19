<script lang="ts">
	interface LegendItem {
		label: string;
		color: string;
	}

	interface Props {
		items: LegendItem[];
		title?: string;
		orientation?: 'horizontal' | 'vertical';
		onItemClick?: (label: string) => void;
		highlightedItem?: string | null;
	}

	let {
		items = [],
		title = '',
		orientation = 'horizontal',
		onItemClick,
		highlightedItem = null
	}: Props = $props();

	function getItemOpacity(item: LegendItem): number {
		if (highlightedItem && item.label !== highlightedItem) {
			return 0.4;
		}
		return 1;
	}
</script>

<div class="legend" class:vertical={orientation === 'vertical'}>
	{#if title}
		<span class="legend-title">{title}</span>
	{/if}
	<div class="legend-items">
		{#each items as item}
			<button
				class="legend-item"
				class:clickable={!!onItemClick}
				class:active={item.label === highlightedItem}
				style="opacity: {getItemOpacity(item)}"
				onclick={() => onItemClick?.(item.label)}
				disabled={!onItemClick}
			>
				<span class="legend-swatch" style="background-color: {item.color}"></span>
				<span class="legend-label">{item.label}</span>
			</button>
		{/each}
	</div>
</div>

<style>
	.legend {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	.legend-title {
		font-size: var(--text-xs);
		font-weight: var(--font-semibold);
		text-transform: uppercase;
		letter-spacing: var(--tracking-wide);
		color: var(--color-text-muted);
	}

	.legend-items {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-md);
	}

	.vertical .legend-items {
		flex-direction: column;
		gap: var(--space-sm);
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		background: none;
		border: none;
		padding: 0;
		font: inherit;
		color: inherit;
		transition: opacity var(--transition-fast);
	}

	.legend-item.clickable {
		cursor: pointer;
	}

	.legend-item.clickable:hover {
		opacity: 1 !important;
	}

	.legend-item.active {
		opacity: 1 !important;
	}

	.legend-swatch {
		width: 12px;
		height: 12px;
		border-radius: var(--radius-sm);
		flex-shrink: 0;
	}

	.legend-label {
		font-size: var(--text-sm);
		color: var(--color-text);
	}

	/* Mobile adjustments */
	@media (max-width: 640px) {
		.legend-items {
			gap: var(--space-sm);
		}

		.legend-swatch {
			width: 10px;
			height: 10px;
		}

		.legend-label {
			font-size: var(--text-xs);
		}
	}
</style>
