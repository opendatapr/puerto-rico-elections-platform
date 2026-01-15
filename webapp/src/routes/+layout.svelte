<script lang="ts">
	import '../app.css';
	import { base } from '$app/paths';

	let { children } = $props();
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
			<a href="{base}/#chapters">Chapters</a>
			<a href="https://github.com/opendatapr/puerto-rico-elections-platform" target="_blank" rel="noopener">GitHub</a>
		</div>
	</nav>
</header>

<main>
	{@render children()}
</main>

<footer class="site-footer">
	<div class="container">
		<p class="footer-text">
			A project by <a href="https://github.com/opendatapr">OpenDataPR</a> ·
			Data sourced from <a href="https://elecciones.cee.pr.gov" target="_blank" rel="noopener">CEE</a> and
			<a href="https://data.census.gov" target="_blank" rel="noopener">U.S. Census Bureau</a>
		</p>
		<p class="footer-license">
			Licensed under <a href="https://www.gnu.org/licenses/gpl-3.0.html" target="_blank" rel="noopener">GPL-3.0</a>
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
</style>
