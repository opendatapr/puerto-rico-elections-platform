<script lang="ts">
	interface Props {
		currentStep: number;
		totalSteps: number;
		chapterTitle?: string;
	}

	let { currentStep, totalSteps, chapterTitle = '' }: Props = $props();

	let progress = $derived((currentStep / Math.max(totalSteps - 1, 1)) * 100);
</script>

<div class="progress-container">
	<div class="progress-bar">
		<div class="progress-fill" style="width: {progress}%"></div>
	</div>
	<div class="progress-info">
		{#if chapterTitle}
			<span class="progress-title">{chapterTitle}</span>
		{/if}
		<span class="progress-count">{currentStep + 1} / {totalSteps}</span>
	</div>
</div>

<style>
	.progress-container {
		position: fixed;
		top: var(--header-height);
		left: 0;
		right: 0;
		z-index: 90;
		padding: var(--space-sm) var(--space-lg);
		background: var(--color-surface-glass);
		backdrop-filter: blur(8px);
		border-bottom: 1px solid var(--color-border);
	}

	.progress-bar {
		height: 3px;
		background: var(--color-border);
		border-radius: var(--radius-full);
		overflow: hidden;
		margin-bottom: var(--space-xs);
	}

	.progress-fill {
		height: 100%;
		background: linear-gradient(90deg, var(--color-accent), var(--color-accent));
		border-radius: var(--radius-full);
		transition: width var(--transition-base);
	}

	.progress-info {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.progress-title {
		font-size: var(--text-sm);
		font-weight: var(--font-medium);
		color: var(--color-text);
	}

	.progress-count {
		font-family: var(--font-mono);
		font-size: var(--text-xs);
		color: var(--color-text-muted);
	}

	/* Mobile adjustments */
	@media (max-width: 640px) {
		.progress-container {
			padding: var(--space-xs) var(--space-md);
		}

		.progress-title {
			font-size: var(--text-xs);
			max-width: 60%;
			overflow: hidden;
			text-overflow: ellipsis;
			white-space: nowrap;
		}
	}
</style>
