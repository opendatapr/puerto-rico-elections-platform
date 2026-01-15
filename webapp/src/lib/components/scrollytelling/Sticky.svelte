<script lang="ts">
	interface Props {
		children?: import('svelte').Snippet;
	}

	let { children }: Props = $props();
</script>

<div class="sticky-viz">
	{#if children}
		{@render children()}
	{/if}
</div>

<style>
	.sticky-viz {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
	}

	.sticky-viz :global(svg) {
		max-width: 100%;
		max-height: 100%;
	}

	.sticky-viz :global(.chart-container) {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
	}
</style>
