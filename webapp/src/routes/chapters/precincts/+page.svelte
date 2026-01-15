<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { ChoroplethMap } from '$lib/components/maps';
	import { BarChart, ScatterPlot } from '$lib/components/charts';
	import { PARTY_COLORS, createDivergingScale, CATEGORY_COLORS } from '$lib/utils/colors';
	import { formatNumber, formatPercent, formatChange } from '$lib/utils/format';

	// Chapter metadata
	const chapterNum = 9;
	const chapterTitle = 'Down to the Precinct';
	const totalSteps = 10;

	// State
	let currentStep = $state(0);
	let loading = $state(true);
	let selectedMunicipality = $state<string | null>(null);

	// Data types
	interface PrecinctData {
		precinct: string;
		municipality: string;
		total_votes: number;
		pnp_pct: number;
		ppd_pct: number;
		margin: number;
		abs_margin: number;
		competitiveness: number;
	}

	interface MunicipalityVariation {
		municipality: string;
		num_precincts: number;
		min_pnp: number;
		max_pnp: number;
		spread: number;
		precincts: PrecinctData[];
	}

	interface ChapterData {
		year: number;
		total_precincts: number;
		total_municipalities: number;
		san_juan: {
			precincts: PrecinctData[];
			spread: number;
		};
		municipality_variation: MunicipalityVariation[];
		most_competitive: PrecinctData[];
		safe_seats: PrecinctData[];
		swing_targets: PrecinctData[];
		scatter_data: Array<{
			x: number;
			y: number;
			label: string;
			municipality: string;
			margin: number;
		}>;
		all_precincts: PrecinctData[];
	}

	// Loaded data
	let chapterData = $state<ChapterData | null>(null);

	// Current visualization type
	let currentViz = $state<'map' | 'bar' | 'scatter' | 'small-multiples' | 'boxplot'>('map');

	// Load chapter data
	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/chapters/precincts.json`);
			chapterData = await response.json();
		} catch (err) {
			console.error('Failed to load precincts data:', err);
		} finally {
			loading = false;
		}
	});

	// Derived data for visualizations

	// San Juan bar chart data
	let sanJuanBarData = $derived(() => {
		if (!chapterData?.san_juan?.precincts) return [];
		return chapterData.san_juan.precincts.map(p => ({
			label: p.precinct.replace('San Juan ', 'Precinct '),
			value: p.pnp_pct,
			color: p.pnp_pct > 35 ? PARTY_COLORS.PNP : p.pnp_pct < 30 ? PARTY_COLORS.PPD : CATEGORY_COLORS[5]
		}));
	});

	// Top variation municipalities for small multiples
	let topVariationMunis = $derived(() => {
		if (!chapterData?.municipality_variation) return [];
		return chapterData.municipality_variation.slice(0, 5);
	});

	// Most competitive bar data
	let competitiveBarData = $derived(() => {
		if (!chapterData?.most_competitive) return [];
		return chapterData.most_competitive.slice(0, 8).map(p => ({
			label: p.precinct,
			value: p.abs_margin,
			color: CATEGORY_COLORS[4]
		}));
	});

	// Swing targets bar data
	let swingTargetsData = $derived(() => {
		if (!chapterData?.swing_targets) return [];
		return chapterData.swing_targets.slice(0, 8).map(p => ({
			label: p.precinct,
			value: p.total_votes,
			color: p.margin > 0 ? PARTY_COLORS.PNP : PARTY_COLORS.PPD
		}));
	});

	// Scatter plot data for size vs competitiveness
	let scatterData = $derived(() => {
		if (!chapterData?.scatter_data) return [];
		return chapterData.scatter_data.map(p => ({
			x: p.x,
			y: p.y,
			label: p.label,
			color: p.margin < 5 ? CATEGORY_COLORS[4] : p.margin < 10 ? CATEGORY_COLORS[1] : CATEGORY_COLORS[3],
			size: 5
		}));
	});

	// Map data for municipality-level view
	let mapData = $state(new Map<string, number>());
	const colorScale = createDivergingScale([25, 35, 45]);

	// Color scale for variation viz
	const variationColorScale = createDivergingScale([0, 7, 14]);

	function handleStepEnter(response: { index: number }) {
		currentStep = response.index;

		switch (response.index) {
			case 0:
				// Opening - municipality illusion
				currentViz = 'map';
				mapData = new Map();
				break;
			case 1:
				// San Juan as case study
				currentViz = 'bar';
				selectedMunicipality = 'San Juan';
				break;
			case 2:
				// The precinct spectrum within San Juan
				currentViz = 'bar';
				break;
			case 3:
				// Small multiples - top varying municipalities
				currentViz = 'small-multiples';
				selectedMunicipality = null;
				break;
			case 4:
				// Scatter: size vs competitiveness
				currentViz = 'scatter';
				break;
			case 5:
				// Most competitive precincts
				currentViz = 'bar';
				break;
			case 6:
				// Safe seats
				currentViz = 'bar';
				break;
			case 7:
				// Campaign targeting - swing targets
				currentViz = 'bar';
				break;
			case 8:
				// What this means
				currentViz = 'scatter';
				break;
			case 9:
				// Ground game conclusion
				currentViz = 'map';
				break;
		}
	}

	// Key stats from data
	let sanJuanSpread = $derived(chapterData?.san_juan?.spread ?? 7.7);
	let lasPiedrasSpread = $derived(chapterData?.municipality_variation?.[0]?.spread ?? 13.1);
	let mostCompetitivePrecinct = $derived(chapterData?.most_competitive?.[0]?.precinct ?? 'Anasco 040');
	let totalPrecincts = $derived(chapterData?.total_precincts ?? 110);
</script>

<svelte:head>
	<title>Chapter {chapterNum}: {chapterTitle} | Puerto Rico Elections</title>
</svelte:head>

<Progress {currentStep} {totalSteps} chapterTitle={chapterTitle} />

<article class="chapter">
	<header class="chapter-header">
		<div class="container content">
			<span class="label">Chapter {chapterNum}</span>
			<div class="accent-line"></div>
			<h1>{chapterTitle}</h1>
			<p class="lead">
				Municipality averages hide enormous variation. Within San Juan alone,
				precincts range from 29% to 37% PNP support. The same city.
				Completely different political worlds.
			</p>
			<div class="lead-stats">
				<div class="stat-block">
					<span class="stat-value">{totalPrecincts}</span>
					<span class="stat-label">Electoral Precincts</span>
				</div>
				<div class="stat-block">
					<span class="stat-value">{formatChange(sanJuanSpread)}pp</span>
					<span class="stat-label">San Juan Spread</span>
				</div>
				<div class="stat-block">
					<span class="stat-value">{formatChange(lasPiedrasSpread)}pp</span>
					<span class="stat-label">Max Internal Variation</span>
				</div>
			</div>
		</div>
	</header>

	<ScrollySection offset={0.6} onStepEnter={handleStepEnter}>
		{#snippet graphic()}
			<div class="viz-container">
				{#if loading}
					<p class="loading">Loading precinct data...</p>
				{:else if currentViz === 'bar' && currentStep === 1}
					<!-- San Juan precinct intro -->
					<div class="zoom-metaphor">
						<div class="zoom-icon">
							<svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="2">
								<circle cx="11" cy="11" r="8"/>
								<path d="M21 21l-4.35-4.35"/>
								<path d="M11 8v6M8 11h6"/>
							</svg>
						</div>
						<h3 class="viz-title">Zooming Into San Juan</h3>
						<p class="viz-subtitle">From one number to five distinct stories</p>
					</div>
				{:else if currentViz === 'bar' && currentStep === 2}
					<!-- San Juan precincts bar chart -->
					<h3 class="viz-title">San Juan's Five Precincts</h3>
					<p class="viz-subtitle">PNP Vote Share (2020 Governor)</p>
					<div class="chart-container">
						<BarChart
							data={sanJuanBarData()}
							width={450}
							height={320}
							horizontal={true}
							valueFormat={(v) => `${v.toFixed(1)}%`}
						/>
					</div>
					<p class="chart-note">{formatChange(sanJuanSpread)} percentage point spread within one municipality</p>
				{:else if currentViz === 'small-multiples'}
					<!-- Small multiples showing variation in multiple municipalities -->
					<h3 class="viz-title">Within-Municipality Variation</h3>
					<p class="viz-subtitle">How precincts differ from their neighbors</p>
					<div class="small-multiples-container">
						{#each topVariationMunis() as muni}
							<div class="small-multiple">
								<h4>{muni.municipality}</h4>
								<div class="variation-bar">
									{#each muni.precincts as p}
										<div
											class="precinct-dot"
											style="left: {((p.pnp_pct - 20) / 40) * 100}%; background: {p.pnp_pct > 35 ? PARTY_COLORS.PNP : p.pnp_pct < 30 ? PARTY_COLORS.PPD : CATEGORY_COLORS[5]}"
											title="{p.precinct}: {p.pnp_pct}% PNP"
										></div>
									{/each}
									<div class="range-line" style="left: {((muni.min_pnp - 20) / 40) * 100}%; width: {((muni.max_pnp - muni.min_pnp) / 40) * 100}%"></div>
								</div>
								<div class="variation-stats">
									<span class="stat-small">{muni.min_pnp.toFixed(0)}%</span>
									<span class="spread-label">{formatChange(muni.spread)}pp spread</span>
									<span class="stat-small">{muni.max_pnp.toFixed(0)}%</span>
								</div>
							</div>
						{/each}
					</div>
					<div class="variation-legend">
						<span style="color: {PARTY_COLORS.PPD}">PPD-leaning</span>
						<span style="color: {CATEGORY_COLORS[5]}">Competitive</span>
						<span style="color: {PARTY_COLORS.PNP}">PNP-leaning</span>
					</div>
				{:else if currentViz === 'scatter'}
					<!-- Scatter: precinct size vs competitiveness -->
					<h3 class="viz-title">{currentStep === 8 ? 'The Full Picture' : 'Precinct Size vs. Competitiveness'}</h3>
					<p class="viz-subtitle">Large competitive precincts are the prize</p>
					<div class="chart-container">
						<ScatterPlot
							data={scatterData()}
							width={500}
							height={400}
							xLabel="Total Votes Cast"
							yLabel="Competitiveness Score"
							xFormat={(v) => formatNumber(Math.round(v))}
							yFormat={(v) => `${v.toFixed(0)}`}
							showRegression={false}
						/>
					</div>
					<p class="chart-note">100 = perfectly competitive (PNP vs PPD tied). Higher = more competitive.</p>
				{:else if currentViz === 'bar' && currentStep === 5}
					<!-- Most competitive precincts -->
					<h3 class="viz-title">The Battleground Precincts</h3>
					<p class="viz-subtitle">Margin between PNP and PPD (percentage points)</p>
					<div class="chart-container">
						<BarChart
							data={competitiveBarData()}
							width={500}
							height={350}
							horizontal={true}
							valueFormat={(v) => `${v.toFixed(1)}pp`}
						/>
					</div>
					<p class="chart-note">These precincts are decided by thin margins. Every vote matters.</p>
				{:else if currentViz === 'bar' && currentStep === 6}
					<!-- Safe seats -->
					<h3 class="viz-title">Safe Seats</h3>
					<p class="viz-subtitle">Precincts where outcomes are predetermined</p>
					<div class="chart-container">
						{#if chapterData?.safe_seats}
							<BarChart
								data={chapterData.safe_seats.slice(0, 8).map(p => ({
									label: p.precinct,
									value: p.abs_margin,
									color: p.margin > 0 ? PARTY_COLORS.PNP : PARTY_COLORS.PPD
								}))}
								width={500}
								height={350}
								horizontal={true}
								valueFormat={(v) => `${v.toFixed(1)}pp`}
							/>
						{/if}
					</div>
					<p class="chart-note">Margins over 15 points rarely flip. Campaigns rarely invest here.</p>
				{:else if currentViz === 'bar' && currentStep === 7}
					<!-- Swing targets -->
					<h3 class="viz-title">High-Value Targets</h3>
					<p class="viz-subtitle">Large precincts that are still competitive</p>
					<div class="chart-container">
						<BarChart
							data={swingTargetsData()}
							width={500}
							height={350}
							horizontal={true}
							valueFormat={(v) => formatNumber(v)}
						/>
					</div>
					<p class="chart-note">Total votes cast. Color indicates current lean.</p>
				{:else if currentViz === 'map'}
					<!-- Default map view -->
					<div class="microscope-intro">
						<svg class="microscope-icon" viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="currentColor" stroke-width="1.5">
							<circle cx="11" cy="11" r="8"/>
							<path d="M21 21l-4.35-4.35"/>
							<path d="M11 8v6M8 11h6"/>
						</svg>
						<h3 class="viz-title">The Microscope View</h3>
						<p class="viz-subtitle">What aggregate data hides, precinct data reveals</p>
					</div>
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>The Municipality Illusion</h3>
			<p>
				When we analyze Puerto Rico's elections, we typically look at the 78 municipalities.
				San Juan voted <span class="stat">33% PNP</span> in the 2020 governor's race.
				Bayamon: <span class="stat">34%</span>. Ponce: <span class="stat">32%</span>.
			</p>
			<p>
				These numbers are useful, but they're averages. And averages can deceive.
				They smooth over the sharp edges of political geography, hiding the real
				story of who votes where and why.
			</p>
			<p class="emphasis">
				To see the truth, we need to zoom in. Below the municipality level,
				Puerto Rico is divided into {totalPrecincts} electoral precincts.
			</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>Case Study: San Juan</h3>
			<p>
				San Juan, the capital and most populous municipality, isn't one political
				community. It's five precincts, each encompassing different neighborhoods
				with distinct demographics, histories, and voting patterns.
			</p>
			<p>
				<span class="highlight">Precinct 001</span> includes much of Old San Juan and
				Condado, areas with higher incomes and tourism infrastructure.
				<span class="highlight">Precinct 002</span> covers Santurce and parts of
				Hato Rey, with more mixed-income housing and a younger population.
			</p>
			<p>
				The voting patterns tell the rest of the story.
			</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>The Precinct Spectrum</h3>
			<p>
				Within San Juan, PNP support ranges from <span class="stat">29%</span> to
				<span class="stat">37%</span>. That's nearly an <span class="stat">8 percentage point</span> spread,
				all within what the census calls a single municipality.
			</p>
			<p>
				<span class="highlight">Precinct 001</span> was the most PNP-friendly,
				with <span class="stat">36.9%</span> support. This area tends to have
				higher homeownership rates and older residents.
			</p>
			<p>
				<span class="highlight">Precinct 002</span>, covering the Santurce arts
				district and surrounding neighborhoods, gave PNP only <span class="stat">29.2%</span>.
				Same city. Very different politics.
			</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>Not Just San Juan</h3>
			<p>
				San Juan's internal diversity isn't unique. Many municipalities show similar
				or even greater variation. <span class="highlight">Las Piedras</span> has
				the largest spread: <span class="stat">{formatChange(lasPiedrasSpread)} percentage points</span>
				between its two precincts.
			</p>
			<p>
				<span class="highlight">Coamo's</span> precincts differ by <span class="stat">8.9 points</span>.
				<span class="highlight">Barranquitas</span> shows <span class="stat">8.1 points</span> of variation.
				Even mid-sized municipalities contain multitudes.
			</p>
			<p>
				The chart shows the top five municipalities by internal variation. Each dot
				is a precinct; the line shows the range. These aren't uniform political units.
				They're coalitions of neighborhoods with different interests and identities.
			</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>Size Meets Competitiveness</h3>
			<p>
				For campaigns, not all precincts matter equally. A tiny safe precinct can
				be ignored. A large competitive one is a treasure. This scatter plot
				reveals where the action is.
			</p>
			<p>
				The <span class="highlight">upper right quadrant</span> is the prize:
				large precincts that are still competitive. These are the places where
				voter outreach, advertising, and get-out-the-vote operations deliver the
				highest return on investment.
			</p>
			<p>
				Notice the cluster of competitive precincts in the 20,000-30,000 vote range.
				These are the true battlegrounds of Puerto Rican elections.
			</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>The Battleground Precincts</h3>
			<p>
				Some precincts are decided by razor-thin margins. <span class="highlight">{mostCompetitivePrecinct}</span>
				was essentially tied in 2020, with PNP and PPD within a tenth of a percentage point.
			</p>
			<p>
				These ultra-competitive precincts are where elections can be won or lost.
				A few hundred votes in the right places can swing outcomes. Campaigns that
				understand this geography have a structural advantage.
			</p>
			<p>
				In these precincts, <span class="highlight">every voter matters</span>.
				Turnout operations become critical. A rainy election day could decide which
				party wins.
			</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>The Safe Seats</h3>
			<p>
				Not every precinct is competitive. <span class="highlight">Barranquitas 071</span>
				gave PNP a <span class="stat">21-point</span> margin. <span class="highlight">Guaynabo 007</span>
				was <span class="stat">19 points</span> toward PNP. These are safe seats
				where outcomes are virtually predetermined.
			</p>
			<p>
				For campaigns, these precincts require a different calculus. Persuasion
				is largely pointless. The goal becomes turnout: making sure your reliable
				voters actually show up.
			</p>
			<p>
				Safe seats also matter for <span class="highlight">candidate recruitment</span>.
				In deeply partisan areas, the real election is often the primary, not the general.
			</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>The Campaign Target List</h3>
			<p>
				Professional campaigns build target lists: which precincts to invest in,
				which to ignore. The ideal targets are <span class="highlight">large</span>,
				<span class="highlight">competitive</span>, and have room for persuasion
				or turnout gains.
			</p>
			<p>
				<span class="highlight">Caguas 083</span> cast nearly 30,000 votes and was
				decided by just 1.4 percentage points. <span class="highlight">San Juan 002</span>
				had 29,000 votes and a 0.2-point margin. These are the precincts where
				campaigns spend money.
			</p>
			<p>
				Knowing your precincts isn't just strategy. It's the difference between
				efficient resource allocation and wasted effort.
			</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>What Aggregate Data Hides</h3>
			<p>
				Municipal averages hide important details:
			</p>
			<p>
				<span class="highlight">Gerrymandering detection:</span> Precinct-level data
				reveals whether district lines unnaturally split or combine neighborhoods.
				You can't spot manipulation in aggregate data.
			</p>
			<p>
				<span class="highlight">Targeted mobilization:</span> Campaigns can identify
				exactly which neighborhoods need attention. Generic "get out the vote"
				messaging is replaced by block-by-block strategy.
			</p>
			<p>
				<span class="highlight">True competitiveness:</span> A municipality might
				look safe while containing fiercely contested precincts and vice versa.
			</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>The Ground Game</h3>
			<p>
				Puerto Rican elections are won on the ground, in neighborhoods, at
				community centers and front doors. The parties know this. Their
				precinct captains know every street, every family, every political lean.
			</p>
			<p>
				This granular knowledge is power. A campaign that understands that
				<span class="highlight">Precinct 001 leans PNP while Precinct 002 is more
				competitive</span> can allocate resources intelligently. One-size-fits-all
				strategies fail.
			</p>
			<p class="emphasis">
				The data is available. The patterns are clear. The only question is
				whether anyone is paying attention.
			</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>The Micro-Geography of Politics</h2>
			<p>
				Precinct-level analysis reveals the true texture of Puerto Rico's political
				landscape. What looks like a uniform municipality is actually a patchwork
				of distinct communities with their own political cultures.
			</p>
			<p>
				Within San Juan's 5 precincts, we found a {formatChange(sanJuanSpread)} percentage point
				spread in PNP support. In Las Piedras, the spread was {formatChange(lasPiedrasSpread)} points.
				These differences aren't noise. They're signal.
			</p>
			<p>
				Understanding precinct geography matters for anyone who cares about Puerto
				Rican democracy: campaigns trying to win elections, journalists trying to
				explain outcomes, and citizens trying to understand their neighbors.
			</p>

			<div class="key-takeaways">
				<h3>Key Takeaways</h3>
				<ul>
					<li>Puerto Rico has <span class="stat">{totalPrecincts} electoral precincts</span> across 78 municipalities</li>
					<li>San Juan's precincts range from 29% to 37% PNP support ({formatChange(sanJuanSpread)}pp spread)</li>
					<li>Las Piedras has the largest internal variation: <span class="stat">{formatChange(lasPiedrasSpread)}pp</span></li>
					<li><span class="stat">{mostCompetitivePrecinct}</span> was the most competitive precinct (0.0pp margin)</li>
					<li>Large competitive precincts like Caguas 083 (30K votes, 1.4pp margin) are key targets</li>
				</ul>
			</div>

			<div class="sources">
				<h3>Sources</h3>
				<ul>
					<li>Comision Estatal de Elecciones de Puerto Rico (CEE) - Precinct-level election results 2016-2024</li>
					<li>CEE - Precinct boundary definitions and voter registration by precinct</li>
					<li>U.S. Census Bureau - Block group population data for precinct analysis</li>
					<li>Puerto Rico Planning Board - Geographic information systems data</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/battlegrounds" class="nav-link prev">
					<span class="nav-direction">Previous</span>
					<span class="nav-title">78 Battlegrounds</span>
				</a>
				<a href="{base}/chapters/senate" class="nav-link next">
					<span class="nav-direction">Next Chapter</span>
					<span class="nav-title">The Senate Districts</span>
				</a>
			</nav>
		</div>
	</section>
</article>

<style>
	.chapter-header {
		min-height: 70vh;
		display: flex;
		align-items: center;
		padding: var(--space-3xl) 0;
		background: linear-gradient(180deg, var(--color-bg) 0%, var(--color-surface) 100%);
	}

	.chapter-header h1 {
		margin-bottom: var(--space-lg);
		font-size: var(--text-4xl);
	}

	.chapter-header .lead {
		font-size: var(--text-xl);
		line-height: 1.7;
		color: var(--color-text-light);
		max-width: 50ch;
	}

	.lead-stats {
		display: flex;
		gap: var(--space-2xl);
		margin-top: var(--space-2xl);
		padding-top: var(--space-xl);
		border-top: 1px solid var(--color-border);
	}

	.stat-block {
		display: flex;
		flex-direction: column;
	}

	.stat-value {
		font-family: var(--font-display);
		font-size: var(--text-3xl);
		font-weight: var(--font-bold);
		color: var(--color-text);
	}

	.stat-label {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		text-transform: uppercase;
		letter-spacing: var(--tracking-wide);
	}

	.viz-container {
		width: 100%;
		height: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: var(--space-lg);
	}

	.loading {
		color: var(--color-text-muted);
		font-style: italic;
	}

	.viz-title {
		font-size: var(--text-lg);
		font-weight: var(--font-medium);
		color: var(--color-text);
		margin-bottom: var(--space-xs);
		text-align: center;
	}

	.viz-subtitle {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
		text-align: center;
	}

	/* Zoom/microscope metaphor */
	.zoom-metaphor, .microscope-intro {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 300px;
		text-align: center;
	}

	.zoom-icon, .microscope-icon {
		color: var(--color-accent);
		margin-bottom: var(--space-lg);
		opacity: 0.8;
	}

	/* Chart container */
	.chart-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		width: 100%;
		max-width: 550px;
	}

	.chart-note {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin-top: var(--space-md);
		text-align: center;
		font-style: italic;
	}

	/* Small multiples visualization */
	.small-multiples-container {
		display: flex;
		flex-direction: column;
		gap: var(--space-lg);
		width: 100%;
		max-width: 500px;
	}

	.small-multiple {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
	}

	.small-multiple h4 {
		font-size: var(--text-sm);
		font-weight: var(--font-medium);
		color: var(--color-text);
		margin: 0;
	}

	.variation-bar {
		position: relative;
		height: 24px;
		background: var(--color-surface);
		border-radius: var(--radius-sm);
		border: 1px solid var(--color-border);
	}

	.precinct-dot {
		position: absolute;
		width: 12px;
		height: 12px;
		border-radius: 50%;
		top: 5px;
		transform: translateX(-50%);
		border: 2px solid var(--color-bg);
		z-index: 2;
		cursor: pointer;
	}

	.range-line {
		position: absolute;
		height: 4px;
		background: var(--color-border);
		top: 10px;
		border-radius: 2px;
		z-index: 1;
	}

	.variation-stats {
		display: flex;
		justify-content: space-between;
		font-size: var(--text-xs);
		color: var(--color-text-muted);
	}

	.stat-small {
		font-weight: var(--font-medium);
	}

	.spread-label {
		color: var(--color-accent);
		font-weight: var(--font-medium);
	}

	.variation-legend {
		display: flex;
		gap: var(--space-lg);
		margin-top: var(--space-lg);
		font-size: var(--text-sm);
	}

	/* Step content styling */
	:global(.step) h3 {
		font-size: var(--text-xl);
		margin-bottom: var(--space-md);
	}

	:global(.step) p {
		margin-bottom: var(--space-md);
		line-height: 1.7;
	}

	:global(.step) .stat {
		font-weight: var(--font-semibold);
		color: var(--color-accent);
	}

	:global(.step) .highlight {
		font-weight: var(--font-semibold);
		color: var(--color-text);
	}

	:global(.step) .emphasis {
		font-style: italic;
		color: var(--color-text-light);
		border-left: 3px solid var(--color-accent);
		padding-left: var(--space-md);
	}

	/* Chapter conclusion */
	.chapter-conclusion {
		padding: var(--space-3xl) 0;
		background: var(--color-surface);
	}

	.chapter-conclusion h2 {
		margin-bottom: var(--space-lg);
	}

	.chapter-conclusion p {
		margin-bottom: var(--space-md);
		line-height: 1.7;
	}

	.key-takeaways {
		margin-top: var(--space-2xl);
		padding: var(--space-xl);
		background: var(--color-surface-elevated);
		border-radius: var(--radius-lg);
	}

	.key-takeaways h3 {
		font-size: var(--text-lg);
		margin-bottom: var(--space-md);
	}

	.key-takeaways ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.key-takeaways li {
		padding: var(--space-sm) 0;
		border-bottom: 1px solid var(--color-border);
	}

	.key-takeaways li:last-child {
		border-bottom: none;
	}

	.key-takeaways .stat {
		font-weight: var(--font-semibold);
		color: var(--color-accent);
	}

	.chapter-nav {
		display: flex;
		justify-content: space-between;
		margin-top: var(--space-2xl);
		padding-top: var(--space-xl);
		border-top: 1px solid var(--color-border);
	}

	.nav-link {
		display: flex;
		flex-direction: column;
		padding: var(--space-md);
		border-radius: var(--radius-lg);
		text-decoration: none;
		transition: background var(--transition-fast);
	}

	.nav-link:hover {
		background: var(--color-surface-elevated);
	}

	.nav-link.next {
		text-align: right;
	}

	.nav-direction {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.nav-title {
		font-family: var(--font-display);
		font-size: var(--text-lg);
		font-weight: var(--font-semibold);
		color: var(--color-text);
	}

	.sources {
		margin-top: var(--space-2xl);
		padding-top: var(--space-xl);
		border-top: 1px solid var(--color-border);
	}

	.sources h3 {
		font-size: var(--text-lg);
		margin-bottom: var(--space-md);
		color: var(--color-text-muted);
	}

	.sources ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.sources li {
		font-size: var(--text-sm);
		color: var(--color-text-light);
		margin-bottom: var(--space-sm);
		padding-left: var(--space-md);
		border-left: 2px solid var(--color-border);
	}

	@media (max-width: 768px) {
		.lead-stats {
			flex-direction: column;
			gap: var(--space-lg);
		}

		.stat-value {
			font-size: var(--text-2xl);
		}

		.chart-container {
			max-width: 100%;
		}

		.small-multiples-container {
			max-width: 100%;
		}
	}
</style>
