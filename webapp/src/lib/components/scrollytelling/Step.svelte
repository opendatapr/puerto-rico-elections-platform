<script lang="ts">
	interface Props {
		active?: boolean;
		index?: number;
		children?: import('svelte').Snippet;
	}

	let {
		active = false,
		index = 0,
		children
	}: Props = $props();
</script>

<div
	class="scrolly-step"
	class:active
	data-step={index}
>
	<div class="step-content">
		{#if children}
			{@render children()}
		{/if}
	</div>
</div>

<style>
	.scrolly-step {
		min-height: 80vh;
		display: flex;
		align-items: center;
		opacity: 0.3;
		transition: opacity var(--transition-slow);
	}

	.scrolly-step.active {
		opacity: 1;
	}

	.scrolly-step:first-child {
		margin-top: 30vh;
	}

	.scrolly-step:last-child {
		margin-bottom: 50vh;
	}

	.step-content {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-lg);
		max-width: 400px;
		box-shadow: var(--shadow-md);
		transition: all var(--transition-base);
	}

	.scrolly-step.active .step-content {
		border-color: var(--color-border-light);
		box-shadow: var(--shadow-lg);
	}

	.step-content :global(h3) {
		font-size: var(--text-lg);
		margin-bottom: var(--space-sm);
	}

	.step-content :global(p) {
		font-size: var(--text-base);
		color: var(--color-text-muted);
		margin: 0;
	}

	.step-content :global(p + p) {
		margin-top: var(--space-md);
	}

	.step-content :global(.highlight) {
		color: var(--color-accent);
		font-weight: var(--font-semibold);
	}

	.step-content :global(.stat) {
		font-family: var(--font-display);
		font-size: var(--text-2xl);
		font-weight: var(--font-bold);
		color: var(--color-accent);
		display: block;
		margin: var(--space-sm) 0;
	}

	/* Tablet breakpoint */
	@media (max-width: 1024px) {
		.step-content {
			max-width: 340px;
			padding: var(--space-md);
		}

		.step-content :global(h3) {
			font-size: var(--text-base);
		}

		.step-content :global(p) {
			font-size: var(--text-sm);
		}
	}

	/* Mobile breakpoint */
	@media (max-width: 640px) {
		.scrolly-step {
			min-height: 50vh;
		}

		.scrolly-step:first-child {
			margin-top: 5vh;
		}

		.scrolly-step:last-child {
			margin-bottom: 30vh;
		}

		.step-content {
			max-width: none;
			margin: 0;
			padding: var(--space-md);
		}

		.step-content :global(.stat) {
			font-size: var(--text-xl);
		}
	}
</style>
