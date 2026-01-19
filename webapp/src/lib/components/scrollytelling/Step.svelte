<script lang="ts">
	interface Props {
		active?: boolean;
		index?: number;
		variant?: 'default' | 'quote' | 'comparison' | 'callout' | 'question';
		children?: import('svelte').Snippet;
		quote?: import('svelte').Snippet;
		citation?: import('svelte').Snippet;
		before?: import('svelte').Snippet;
		after?: import('svelte').Snippet;
	}

	let {
		active = false,
		index = 0,
		variant = 'default',
		children,
		quote,
		citation,
		before,
		after
	}: Props = $props();
</script>

<div
	class="scrolly-step"
	class:active
	data-step={index}
>
	<div class="step-content" class:variant-quote={variant === 'quote'} class:variant-comparison={variant === 'comparison'} class:variant-callout={variant === 'callout'} class:variant-question={variant === 'question'}>
		{#if variant === 'quote' && quote}
			<blockquote class="step-quote">
				<span class="quote-mark">"</span>
				{@render quote()}
				{#if citation}
					<cite class="quote-citation">{@render citation()}</cite>
				{/if}
			</blockquote>
			{#if children}
				<div class="quote-context">
					{@render children()}
				</div>
			{/if}
		{:else if variant === 'comparison' && before && after}
			<div class="step-comparison">
				<div class="comparison-side before">
					<span class="comparison-label">Before</span>
					{@render before()}
				</div>
				<div class="comparison-divider"></div>
				<div class="comparison-side after">
					<span class="comparison-label">After</span>
					{@render after()}
				</div>
			</div>
			{#if children}
				<div class="comparison-context">
					{@render children()}
				</div>
			{/if}
		{:else if variant === 'callout'}
			<div class="step-callout">
				<span class="callout-label">Key Finding</span>
				{#if children}
					{@render children()}
				{/if}
			</div>
		{:else if variant === 'question'}
			<div class="step-question">
				<span class="question-mark">?</span>
				{#if children}
					{@render children()}
				{/if}
			</div>
		{:else}
			{#if children}
				{@render children()}
			{/if}
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

	/* =========================
	   QUOTE VARIANT
	   ========================= */
	.variant-quote {
		background: linear-gradient(135deg, var(--color-surface) 0%, var(--color-surface-elevated) 100%);
		border-left: 4px solid var(--color-accent);
	}

	.step-quote {
		position: relative;
		margin: 0;
		padding: 0;
	}

	.quote-mark {
		position: absolute;
		top: -0.3em;
		left: -0.1em;
		font-family: var(--font-display);
		font-size: 4rem;
		font-weight: var(--font-bold);
		color: var(--color-accent);
		opacity: 0.3;
		line-height: 1;
		pointer-events: none;
	}

	.step-quote :global(p) {
		font-family: var(--font-display);
		font-size: var(--text-xl);
		font-weight: var(--font-medium);
		font-style: italic;
		line-height: 1.5;
		color: var(--color-text);
		margin: 0 0 var(--space-md) 0;
		padding-left: var(--space-lg);
	}

	.quote-citation {
		display: block;
		font-family: var(--font-body);
		font-size: var(--text-sm);
		font-style: normal;
		color: var(--color-text-muted);
		padding-left: var(--space-lg);
	}

	.quote-citation::before {
		content: '— ';
	}

	.quote-context {
		margin-top: var(--space-lg);
		padding-top: var(--space-md);
		border-top: 1px solid var(--color-border);
	}

	.quote-context :global(p) {
		font-size: var(--text-sm);
		color: var(--color-text-light);
	}

	/* =========================
	   COMPARISON VARIANT
	   ========================= */
	.variant-comparison {
		padding: var(--space-md);
	}

	.step-comparison {
		display: grid;
		grid-template-columns: 1fr auto 1fr;
		gap: var(--space-md);
		align-items: stretch;
	}

	.comparison-side {
		display: flex;
		flex-direction: column;
		text-align: center;
	}

	.comparison-label {
		display: block;
		font-size: var(--text-xs);
		font-weight: var(--font-semibold);
		text-transform: uppercase;
		letter-spacing: var(--tracking-wide);
		color: var(--color-text-muted);
		margin-bottom: var(--space-sm);
	}

	.comparison-side.before .comparison-label {
		color: var(--color-text-light);
	}

	.comparison-side.after .comparison-label {
		color: var(--color-accent);
	}

	.comparison-side :global(.stat) {
		font-size: var(--text-3xl);
		margin: var(--space-xs) 0;
	}

	.comparison-side :global(p) {
		font-size: var(--text-sm);
		margin: 0;
	}

	.comparison-divider {
		width: 2px;
		background: linear-gradient(180deg, transparent 0%, var(--color-border) 20%, var(--color-border) 80%, transparent 100%);
		min-height: 60px;
	}

	.comparison-context {
		margin-top: var(--space-lg);
		padding-top: var(--space-md);
		border-top: 1px solid var(--color-border);
	}

	.comparison-context :global(p) {
		font-size: var(--text-sm);
		color: var(--color-text-light);
		text-align: center;
	}

	/* =========================
	   CALLOUT VARIANT
	   ========================= */
	.variant-callout {
		background: var(--color-surface);
		border: 2px solid var(--color-accent);
		position: relative;
		overflow: visible;
	}

	.step-callout {
		position: relative;
	}

	.callout-label {
		position: absolute;
		top: calc(-1 * var(--space-sm) - 10px);
		left: var(--space-md);
		background: var(--color-accent);
		color: var(--color-bg);
		font-size: var(--text-xs);
		font-weight: var(--font-bold);
		text-transform: uppercase;
		letter-spacing: var(--tracking-wide);
		padding: var(--space-xs) var(--space-sm);
		border-radius: var(--radius-sm);
	}

	.step-callout :global(h3) {
		margin-top: var(--space-sm);
		color: var(--color-accent);
	}

	.step-callout :global(p) {
		font-size: var(--text-base);
	}

	.step-callout :global(.stat) {
		font-size: var(--text-3xl);
		color: var(--color-accent);
	}

	/* =========================
	   QUESTION VARIANT
	   ========================= */
	.variant-question {
		background: linear-gradient(135deg, var(--color-surface-elevated) 0%, var(--color-surface) 100%);
		border: 1px solid var(--color-border-light);
	}

	.step-question {
		position: relative;
		padding-left: 3.5rem;
	}

	.question-mark {
		position: absolute;
		top: 0;
		left: 0;
		font-family: var(--font-display);
		font-size: 3.5rem;
		font-weight: var(--font-bold);
		color: var(--color-accent);
		line-height: 1;
		opacity: 0.8;
	}

	.step-question :global(h3) {
		font-size: var(--text-xl);
		font-style: italic;
		color: var(--color-text);
		margin-bottom: var(--space-md);
	}

	.step-question :global(p) {
		font-size: var(--text-base);
		color: var(--color-text-light);
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

		/* Quote variant mobile */
		.quote-mark {
			font-size: 2.5rem;
		}

		.step-quote :global(p) {
			font-size: var(--text-lg);
			padding-left: var(--space-md);
		}

		.quote-citation {
			padding-left: var(--space-md);
		}

		/* Comparison variant mobile - stack vertically */
		.step-comparison {
			grid-template-columns: 1fr;
			grid-template-rows: auto auto auto;
			gap: var(--space-sm);
		}

		.comparison-divider {
			width: 100%;
			height: 2px;
			min-height: 2px;
			background: linear-gradient(90deg, transparent 0%, var(--color-border) 20%, var(--color-border) 80%, transparent 100%);
		}

		.comparison-side :global(.stat) {
			font-size: var(--text-2xl);
		}

		/* Callout variant mobile */
		.callout-label {
			position: static;
			display: inline-block;
			margin-bottom: var(--space-sm);
		}

		.step-callout :global(.stat) {
			font-size: var(--text-2xl);
		}

		/* Question variant mobile */
		.step-question {
			padding-left: 2.5rem;
		}

		.question-mark {
			font-size: 2.5rem;
		}

		.step-question :global(h3) {
			font-size: var(--text-lg);
		}
	}
</style>
