<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import scrollama from 'scrollama';

	interface Props {
		offset?: number;
		debug?: boolean;
		onStepEnter?: (response: { index: number; element: HTMLElement; direction: string }) => void;
		onStepExit?: (response: { index: number; element: HTMLElement; direction: string }) => void;
		onStepProgress?: (response: { index: number; progress: number }) => void;
		children?: import('svelte').Snippet;
		graphic?: import('svelte').Snippet;
	}

	let {
		offset = 0.5,
		debug = false,
		onStepEnter = () => {},
		onStepExit = () => {},
		onStepProgress,
		children,
		graphic
	}: Props = $props();

	let container: HTMLElement;
	let scroller: ReturnType<typeof scrollama> | null = null;

	onMount(() => {
		scroller = scrollama();

		const options: scrollama.ScrollamaOptions = {
			step: '.scrolly-step',
			offset,
			debug
		};

		scroller.setup(options)
			.onStepEnter(onStepEnter)
			.onStepExit(onStepExit);

		if (onStepProgress) {
			scroller.onStepProgress(onStepProgress);
		}

		// Handle resize
		const resizeObserver = new ResizeObserver(() => {
			scroller?.resize();
		});
		resizeObserver.observe(container);

		return () => {
			resizeObserver.disconnect();
		};
	});

	onDestroy(() => {
		scroller?.destroy();
	});
</script>

<section class="scrolly-container" bind:this={container}>
	<div class="scrolly-graphic">
		<div class="scrolly-graphic-inner">
			{#if graphic}
				{@render graphic()}
			{/if}
		</div>
	</div>
	<div class="scrolly-steps">
		{#if children}
			{@render children()}
		{/if}
	</div>
</section>

<style>
	.scrolly-container {
		position: relative;
		display: flex;
	}

	.scrolly-graphic {
		position: sticky;
		top: var(--header-height);
		height: calc(100vh - var(--header-height));
		width: 55%;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-bg);
	}

	.scrolly-graphic-inner {
		width: 100%;
		height: 100%;
		padding: var(--space-lg);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.scrolly-steps {
		width: 45%;
		padding: var(--space-2xl) var(--space-lg);
	}

	@media (max-width: 900px) {
		.scrolly-container {
			flex-direction: column;
		}

		.scrolly-graphic {
			position: sticky;
			top: var(--header-height);
			height: 50vh;
			width: 100%;
		}

		.scrolly-steps {
			width: 100%;
			background: var(--color-bg);
		}
	}
</style>
