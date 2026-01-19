<script lang="ts">
	import '../app.css';
	import { base } from '$app/paths';
	import { language, type Language } from '$lib/stores/language';

	let { children } = $props();

	function toggleLanguage() {
		language.update(lang => lang === 'en' ? 'es' : 'en');
	}
</script>

<svelte:head>
	<meta property="og:title" content="Puerto Rico Elections | OpenDataPR" />
	<meta property="og:description" content="Interactive data journalism exploring Puerto Rico's electoral dynamics from 2012-2024" />
	<meta property="og:type" content="website" />
</svelte:head>

<header class="site-header">
	<nav class="container">
		<a href="{base}/" class="logo">
			<span class="logo-text">OpenData</span><span class="logo-accent">PR</span>
		</a>
		<div class="nav-links">
			<a href="{base}/#chapters">{$language === 'en' ? 'Chapters' : 'Capitulos'}</a>
			<a href="https://github.com/opendatapr/puerto-rico-elections-platform" target="_blank" rel="noopener">GitHub</a>
			<button class="lang-toggle" onclick={toggleLanguage} aria-label="Toggle language">
				<span class:active={$language === 'en'}>EN</span>
				<span class="divider">|</span>
				<span class:active={$language === 'es'}>ES</span>
			</button>
		</div>
	</nav>
</header>

<main>
	{@render children()}
</main>

<footer class="site-footer">
	<div class="container">
		<p class="footer-text">
			{#if $language === 'en'}
				A project by <a href="https://github.com/opendatapr">OpenDataPR</a> ·
				Data sourced from <a href="https://elecciones.cee.pr.gov" target="_blank" rel="noopener">CEE</a> and
				<a href="https://data.census.gov" target="_blank" rel="noopener">U.S. Census Bureau</a>
			{:else}
				Un proyecto de <a href="https://github.com/opendatapr">OpenDataPR</a> ·
				Datos de <a href="https://elecciones.cee.pr.gov" target="_blank" rel="noopener">CEE</a> y
				<a href="https://data.census.gov" target="_blank" rel="noopener">Censo de EE.UU.</a>
			{/if}
		</p>
		<p class="footer-license">
			{#if $language === 'en'}
				Licensed under <a href="https://www.gnu.org/licenses/gpl-3.0.html" target="_blank" rel="noopener">GPL-3.0</a>
			{:else}
				Licenciado bajo <a href="https://www.gnu.org/licenses/gpl-3.0.html" target="_blank" rel="noopener">GPL-3.0</a>
			{/if}
		</p>
	</div>
</footer>

<style>
	.site-header {
		position: sticky;
		top: 0;
		z-index: 100;
		height: var(--header-height);
		background: var(--color-surface-glass);
		backdrop-filter: blur(12px);
		border-bottom: 1px solid var(--color-border);
	}

	.site-header nav {
		display: flex;
		align-items: center;
		justify-content: space-between;
		height: 100%;
	}

	.logo {
		font-family: var(--font-display);
		font-size: var(--text-xl);
		font-weight: var(--font-semibold);
		text-decoration: none;
	}

	.logo-text {
		color: var(--color-text);
	}

	.logo-accent {
		color: var(--color-accent);
	}

	.nav-links {
		display: flex;
		gap: var(--space-lg);
	}

	.nav-links a {
		color: var(--color-text-muted);
		font-size: var(--text-sm);
		font-weight: var(--font-medium);
		transition: color var(--transition-fast);
	}

	.nav-links a:hover {
		color: var(--color-text);
	}

	.lang-toggle {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		background: transparent;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: var(--space-xs) var(--space-sm);
		cursor: pointer;
		font-size: var(--text-xs);
		font-weight: var(--font-medium);
		color: var(--color-text-muted);
		transition: all var(--transition-fast);
	}

	.lang-toggle:hover {
		border-color: var(--color-border-light);
		color: var(--color-text);
	}

	.lang-toggle span {
		transition: color var(--transition-fast);
	}

	.lang-toggle span.active {
		color: var(--color-accent);
		font-weight: var(--font-semibold);
	}

	.lang-toggle .divider {
		color: var(--color-border);
	}

	main {
		min-height: calc(100vh - var(--header-height) - 120px);
	}

	.site-footer {
		padding: var(--space-2xl) 0;
		border-top: 1px solid var(--color-border);
		text-align: center;
	}

	.footer-text {
		color: var(--color-text-muted);
		font-size: var(--text-sm);
	}

	.footer-license {
		color: var(--color-text-light);
		font-size: var(--text-xs);
		margin-top: var(--space-sm);
	}

	/* Mobile adjustments */
	@media (max-width: 640px) {
		.logo {
			font-size: var(--text-lg);
		}

		.nav-links {
			gap: var(--space-md);
		}

		.nav-links a {
			font-size: var(--text-xs);
		}

		.footer-text {
			font-size: var(--text-xs);
			line-height: var(--leading-relaxed);
		}

		.site-footer {
			padding: var(--space-xl) 0;
		}
	}
</style>
