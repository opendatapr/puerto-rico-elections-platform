<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { ChoroplethMap } from '$lib/components/maps';
	import { BarChart, ScatterPlot } from '$lib/components/charts';
	import { createDivergingScale, createSequentialScale, CATEGORY_COLORS, PARTY_COLORS } from '$lib/utils/colors';

	const chapterNum = 6;
	const chapterTitle = 'Divided by Design';
	const totalSteps = 12;

	let currentStep = $state(0);
	let mapTitle = $state('');
	let loading = $state(true);

	// Data from chapter JSON
	interface Municipality {
		name: string;
		population: number;
		vap: number;
		precincts: number;
		pnp_share_2016: number;
		ppd_share_2016: number;
		margin_2016: number;
		house_districts: number[];
		senate_district: number;
		senate_name: string;
		region: string;
		classification: string;
		median_income: number | null;
		poverty_rate: number | null;
		bachelors_or_higher: number | null;
		pop_share: number;
	}

	interface Region {
		name: string;
		municipalities: number;
		population: number;
		pnp_share: number;
		ppd_share: number;
	}

	interface SenateDistrict {
		district: number;
		name: string;
		municipalities: number;
		population: number;
		pnp_share: number;
	}

	interface ChapterData {
		municipalities: Municipality[];
		regions: Region[];
		senate_districts: SenateDistrict[];
		stats: {
			total_municipalities: number;
			total_population: number;
			total_precincts: number;
			total_house_districts: number;
			total_senate_districts: number;
			urban_count: number;
			rural_count: number;
			largest_municipality: string;
			smallest_municipality: string;
			most_pro_pnp: string;
			most_pro_ppd: string;
		};
		classification_breakdown: {
			urban: string[];
			suburban: string[];
			town: string[];
			rural: string[];
		};
	}

	let chapterData = $state<ChapterData | null>(null);

	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/chapters/geography.json`);
			chapterData = await response.json();
		} catch (err) {
			console.error('Failed to load geography data:', err);
		} finally {
			loading = false;
		}
	});

	// Different color scales for different visualizations
	const marginScale = createDivergingScale([-20, 0, 20]);
	const populationScale = createSequentialScale([0, 400000]);
	const povertyScale = createSequentialScale([30, 60]);

	// Classification colors
	const classificationColors: Record<string, string> = {
		'urban': CATEGORY_COLORS[0],      // Blue
		'suburban': CATEGORY_COLORS[4],   // Teal
		'town': CATEGORY_COLORS[1],       // Gold
		'rural': CATEGORY_COLORS[2]       // Green
	};

	// Active visualization type
	type VizType = 'blank' | 'partisan' | 'population' | 'classification' | 'senate' | 'scatter' | 'regions' | 'size';
	let activeViz = $state<VizType>('blank');

	// Map data computed from chapterData
	let mapData = $derived(() => {
		if (!chapterData) return new Map<string, number>();
		const map = new Map<string, number>();

		switch (activeViz) {
			case 'partisan':
				for (const m of chapterData.municipalities) {
					map.set(m.name, m.margin_2016);
				}
				break;
			case 'population':
				for (const m of chapterData.municipalities) {
					map.set(m.name, m.population);
				}
				break;
			case 'classification':
				for (const m of chapterData.municipalities) {
					// Map classification to numeric for color scale
					const classVal = m.classification === 'urban' ? 3 :
									 m.classification === 'suburban' ? 2 :
									 m.classification === 'town' ? 1 : 0;
					map.set(m.name, classVal);
				}
				break;
			case 'senate':
				for (const m of chapterData.municipalities) {
					map.set(m.name, m.senate_district);
				}
				break;
		}
		return map;
	});

	// Current color scale based on viz type
	let currentColorScale = $derived(() => {
		switch (activeViz) {
			case 'partisan':
				return marginScale;
			case 'population':
				return populationScale;
			case 'classification':
				return (v: number) => {
					const classes = ['rural', 'town', 'suburban', 'urban'];
					return classificationColors[classes[v]] || 'var(--color-surface-elevated)';
				};
			case 'senate':
				return (v: number) => CATEGORY_COLORS[(v - 1) % CATEGORY_COLORS.length];
			default:
				return () => 'var(--color-surface-elevated)';
		}
	});

	// Scatter plot data: Income vs PNP share
	let scatterData = $derived(() => {
		if (!chapterData) return [];
		return chapterData.municipalities
			.filter(m => m.median_income !== null)
			.map(m => ({
				x: m.median_income!,
				y: m.pnp_share_2016,
				label: m.name,
				color: m.margin_2016 > 0 ? PARTY_COLORS.PNP : PARTY_COLORS.PPD,
				size: Math.sqrt(m.population) / 80
			}));
	});

	// Region bar chart data
	let regionBarData = $derived(() => {
		if (!chapterData) return [];
		return chapterData.regions.map(r => ({
			label: r.name.split('/')[0],
			value: r.pnp_share - 50,
			color: r.pnp_share > 50 ? PARTY_COLORS.PNP : PARTY_COLORS.PPD
		}));
	});

	// Population size comparison
	let sizeComparisonData = $derived(() => {
		if (!chapterData) return [];
		return chapterData.municipalities.slice(0, 10).map(m => ({
			label: m.name,
			value: m.population,
			color: m.margin_2016 > 0 ? PARTY_COLORS.PNP : PARTY_COLORS.PPD
		}));
	});

	// Urban/rural breakdown bars
	let classificationData = $derived(() => {
		if (!chapterData) return [];
		const cb = chapterData.classification_breakdown;
		return [
			{ label: 'Urban', value: cb.urban.length, color: classificationColors.urban },
			{ label: 'Suburban', value: cb.suburban.length, color: classificationColors.suburban },
			{ label: 'Town', value: cb.town.length, color: classificationColors.town },
			{ label: 'Rural', value: cb.rural.length, color: classificationColors.rural }
		];
	});

	function handleStepEnter(response: { index: number }) {
		currentStep = response.index;

		switch (response.index) {
			case 0:
				activeViz = 'blank';
				mapTitle = '';
				break;
			case 1:
				activeViz = 'blank';
				mapTitle = '78 Municipalities of Puerto Rico';
				break;
			case 2:
				activeViz = 'partisan';
				mapTitle = 'Partisan Lean (2016 Governor)';
				break;
			case 3:
			case 4:
				activeViz = 'population';
				mapTitle = 'Population Distribution';
				break;
			case 5:
				activeViz = 'classification';
				mapTitle = 'Urban-Rural Classification';
				break;
			case 6:
				activeViz = 'scatter';
				mapTitle = 'Income vs. PNP Vote Share';
				break;
			case 7:
				activeViz = 'regions';
				mapTitle = 'Regional Partisan Balance';
				break;
			case 8:
				activeViz = 'senate';
				mapTitle = 'Senate Districts';
				break;
			case 9:
				activeViz = 'senate';
				mapTitle = 'Senate Districts';
				break;
			case 10:
				activeViz = 'size';
				mapTitle = 'Top 10 Municipalities by Population';
				break;
			case 11:
				activeViz = 'partisan';
				mapTitle = 'The Electoral Map';
				break;
		}
	}

	function getTooltip(name: string, value: number | undefined): string {
		if (!chapterData || value === undefined) return name;
		const muni = chapterData.municipalities.find(m => m.name === name);
		if (!muni) return name;

		switch (activeViz) {
			case 'partisan':
				return `${name}: ${muni.margin_2016 > 0 ? 'PNP' : 'PPD'} +${Math.abs(muni.margin_2016).toFixed(1)}%`;
			case 'population':
				return `${name}: ${muni.population.toLocaleString()} residents`;
			case 'classification':
				return `${name}: ${muni.classification} (pop. ${muni.population.toLocaleString()})`;
			case 'senate':
				return `${name}: District ${muni.senate_district} (${muni.senate_name})`;
			default:
				return name;
		}
	}
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
				Puerto Rico's electoral geography is not an accident. Carved from colonial legacies
				and shaped by decades of migration, these 78 municipalities are the building blocks
				of political power. Where you live shapes how you vote, and the map itself
				becomes a battleground.
			</p>
		</div>
	</header>

	<ScrollySection offset={0.6} onStepEnter={handleStepEnter}>
		{#snippet graphic()}
			<div class="viz-container">
				{#if loading}
					<p class="loading">Loading geographic data...</p>
				{:else if mapTitle}
					<h3 class="viz-title">{mapTitle}</h3>
				{/if}

				{#if activeViz === 'scatter' && chapterData}
					<ScatterPlot
						data={scatterData()}
						width={520}
						height={360}
						xLabel="Median Household Income ($)"
						yLabel="PNP Vote Share (%)"
						xFormat={(v) => `$${(v/1000).toFixed(0)}k`}
						yFormat={(v) => `${v.toFixed(0)}%`}
						showRegression={true}
					/>
				{:else if activeViz === 'regions' && chapterData}
					<div class="bar-container">
						<BarChart
							data={regionBarData()}
							width={440}
							height={300}
							horizontal={true}
							valueFormat={(v) => `${v > 0 ? '+' : ''}${v.toFixed(1)}%`}
						/>
						<p class="viz-note">Deviation from 50-50 (positive = PNP lean)</p>
					</div>
				{:else if activeViz === 'size' && chapterData}
					<BarChart
						data={sizeComparisonData()}
						width={480}
						height={320}
						horizontal={true}
						valueFormat={(v) => `${(v/1000).toFixed(0)}k`}
					/>
				{:else if !loading}
					<ChoroplethMap
						data={mapData()}
						colorScale={currentColorScale()}
						width={600}
						height={400}
						tooltipFormat={getTooltip}
					/>

					{#if activeViz === 'classification'}
						<div class="legend-row">
							<div class="legend-item">
								<span class="legend-swatch" style="background: {classificationColors.urban}"></span>
								<span>Urban ({chapterData?.classification_breakdown.urban.length})</span>
							</div>
							<div class="legend-item">
								<span class="legend-swatch" style="background: {classificationColors.suburban}"></span>
								<span>Suburban ({chapterData?.classification_breakdown.suburban.length})</span>
							</div>
							<div class="legend-item">
								<span class="legend-swatch" style="background: {classificationColors.town}"></span>
								<span>Town ({chapterData?.classification_breakdown.town.length})</span>
							</div>
							<div class="legend-item">
								<span class="legend-swatch" style="background: {classificationColors.rural}"></span>
								<span>Rural ({chapterData?.classification_breakdown.rural.length})</span>
							</div>
						</div>
					{/if}

					{#if activeViz === 'partisan'}
						<div class="legend-row">
							<div class="legend-item">
								<span class="legend-swatch" style="background: {PARTY_COLORS.PPD}"></span>
								<span>PPD Lean</span>
							</div>
							<div class="legend-item">
								<span class="legend-swatch" style="background: #f7f7f7; border: 1px solid var(--color-border)"></span>
								<span>Even</span>
							</div>
							<div class="legend-item">
								<span class="legend-swatch" style="background: {PARTY_COLORS.PNP}"></span>
								<span>PNP Lean</span>
							</div>
						</div>
					{/if}

					{#if activeViz === 'senate'}
						<div class="legend-row legend-wrap">
							{#each chapterData?.senate_districts || [] as sd}
								<div class="legend-item">
									<span class="legend-swatch" style="background: {CATEGORY_COLORS[(sd.district - 1) % CATEGORY_COLORS.length]}"></span>
									<span>D{sd.district}: {sd.name}</span>
								</div>
							{/each}
						</div>
					{/if}
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>The Map is Not the Territory</h3>
			<p>
				Every election night, the map of Puerto Rico lights up in red and blue.
				Municipalities flip, margins shift, and pundits draw sweeping conclusions
				from the colored shapes on screen.
			</p>
			<p>
				But what are these shapes? Where did they come from? And why do they matter
				so much to Puerto Rican politics? The answers reveal how <span class="highlight">geography
				itself becomes a political actor</span>.
			</p>
			<p>
				This chapter examines how Puerto Rico's electoral geography was designed,
				how it divides the island, and what it means for representation.
			</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>78 Pieces of a Colonial Puzzle</h3>
			<p>
				Puerto Rico's <span class="stat">78 municipalities</span> trace their origins to
				the Spanish colonial era. Unlike American counties, which were often drawn on
				gridlines across empty land, Puerto Rico's boundaries followed rivers,
				mountain ridges, and the practical limits of 18th-century governance.
			</p>
			<p>
				When the United States took control in 1898, these Spanish administrative
				units remained intact. The island's rugged terrain and dispersed population
				made them practical for governance. A municipality centered on each town plaza,
				radiating outward to the next mountain range.
			</p>
			<p>
				This colonial inheritance means Puerto Rico's political geography predates
				modern transportation, communication, and demographic patterns. The map was
				designed for a different island.
			</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>The Partisan Divide</h3>
			<p>
				When we color each municipality by its partisan lean, a pattern emerges.
				<span style="color: {PARTY_COLORS.PNP}">Blue municipalities</span> lean toward
				the pro-statehood PNP, while <span style="color: {PARTY_COLORS.PPD}">red municipalities</span>
				favor the pro-commonwealth PPD.
			</p>
			<p>
				In 2016, {chapterData?.stats.most_pro_pnp || 'Loiza'} was the most pro-PNP municipality,
				while {chapterData?.stats.most_pro_ppd || 'Cayey'} leaned most heavily toward PPD.
				These aren't random variations; they reflect deep structural differences in
				demographics, economics, and political culture.
			</p>
			<p>
				The clustering is striking: neighboring municipalities tend to vote alike,
				creating <span class="highlight">regional blocs</span> that persist across
				multiple elections.
			</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>Where the People Are</h3>
			<p>
				But the map lies. A municipality's size on the map has nothing to do with
				its political importance. <span class="highlight">Population</span> determines
				votes, and Puerto Rico's population is concentrated in a few urban centers.
			</p>
			<p>
				<span class="stat">{chapterData?.municipalities[0]?.name || 'San Juan'}</span> alone
				holds {((chapterData?.municipalities[0]?.pop_share || 10) ).toFixed(1)}% of the
				island's population. The San Juan metro area, a ring of municipalities around
				the capital, contains over a third of all Puerto Ricans.
			</p>
			<p>
				This means the sprawling rural municipalities of the interior, which dominate
				the map visually, are politically marginalized by their small populations.
			</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>The Population Paradox</h3>
			<p>
				Consider this: <span class="stat">{chapterData?.stats.largest_municipality || 'San Juan'}</span>
				has {chapterData?.municipalities[0]?.population.toLocaleString() || '395,000'} residents,
				while <span class="stat">{chapterData?.stats.smallest_municipality || 'Culebra'}</span>
				has just {chapterData?.municipalities[chapterData.municipalities.length - 1]?.population.toLocaleString() || '1,800'}.
			</p>
			<p>
				That's a ratio of over <span class="highlight">200 to 1</span>. Yet on most maps,
				these municipalities appear roughly similar in size. Equal-area maps distort
				political reality, making rural regions seem more important than they are
				electorally.
			</p>
			<p>
				When journalists and analysts use standard maps, they inadvertently reinforce
				the illusion that Puerto Rico's politics is evenly distributed across space.
			</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>Urban vs. Rural</h3>
			<p>
				Puerto Rico's municipalities fall into distinct categories that shape their
				political character. Only <span class="stat">{chapterData?.stats.urban_count || 5}</span>
				qualify as fully urban with populations over 100,000.
			</p>
			<p>
				The <span style="color: {classificationColors.urban}">urban core</span> includes
				San Juan, Bayamon, Carolina, Ponce, and Caguas. These municipalities have
				diverse economies, higher incomes, and professional workforces that vote
				differently from the rest of the island.
			</p>
			<p>
				<span style="color: {classificationColors.rural}">Rural municipalities</span> in
				the central mountains and western coast maintain agricultural traditions,
				face higher poverty rates, and often support different candidates than the metro areas.
			</p>
			<p>
				This urban-rural divide cuts across the statehood-commonwealth debate, creating
				cross-cutting cleavages that complicate Puerto Rico's political coalitions.
			</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>The Class Dimension</h3>
			<p>
				Plotting each municipality's median household income against its PNP vote share
				reveals a striking pattern: <span class="highlight">wealthier municipalities
				tend to vote more for PNP</span>.
			</p>
			<p>
				The trendline shows a positive correlation (R-squared indicates the strength
				of this relationship). While not deterministic, income is one of the strongest
				predictors of partisan lean at the municipal level.
			</p>
			<p>
				This class dimension helps explain why the pro-statehood movement, despite
				advocating for full U.S. citizenship rights, draws more support from
				economically advantaged areas where residents may benefit from federal
				programs and economic integration.
			</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>Regional Coalitions</h3>
			<p>
				Puerto Rico's eight Senate districts roughly correspond to historical regions
				with distinct political cultures. Each bar shows how far that region deviates
				from a 50-50 partisan split.
			</p>
			<p>
				The <span class="highlight">San Juan Metro</span> and <span class="highlight">Bayamon/North</span>
				regions tilt toward PNP, while the <span class="highlight">Mayaguez/West</span> and
				<span class="highlight">Ponce/South</span> regions lean PPD.
			</p>
			<p>
				These regional patterns have proven durable across elections. A municipality's geographic
				location predicts its partisan lean better than most demographic variables.
				Your neighbors shape your politics, and regional identity reinforces
				party loyalty across generations.
			</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>At-Large vs. District: The Senate</h3>
			<p>
				Puerto Rico elects its legislature through a mixed system. The <span class="stat">8
				Senate districts</span>, shown here, each elect 2 senators by district.
				An additional 11 senators are elected at-large, island-wide.
			</p>
			<p>
				This hybrid system creates interesting dynamics. District senators must
				represent specific geographic areas with particular concerns, while
				at-large senators can appeal to the entire island.
			</p>
			<p>
				The district boundaries matter enormously. Each colored region on this map
				sends 2 senators to San Juan, regardless of whether it contains 300,000
				or 500,000 people. Malapportionment gives some regions more representation
				per capita than others.
			</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>The House: 40 Districts</h3>
			<p>
				The House of Representatives has <span class="stat">40 districts</span>,
				each electing a single representative, plus 11 at-large seats. These
				districts are smaller than Senate districts, sometimes splitting
				municipalities.
			</p>
			<p>
				Large municipalities like San Juan span <span class="highlight">5 House
				districts</span>, meaning the capital's residents are represented by
				multiple district representatives with potentially different agendas.
				Smaller municipalities share a representative with their neighbors.
			</p>
			<p>
				This arrangement means campaigns must be intensely local. A candidate in
				House District 3 (part of San Juan) faces entirely different voters than
				someone in District 4, even though both are technically in the same city.
			</p>
		</Step>

		<Step active={currentStep === 10} index={10}>
			<h3>The Population Giants</h3>
			<p>
				The top 10 municipalities by population illustrate the concentration of
				political power. Together, they hold over <span class="stat">50%</span>
				of Puerto Rico's total population.
			</p>
			<p>
				Winning elections means winning these urban centers, or at least limiting
				losses there. A candidate who sweeps the San Juan metro but loses the
				rural interior can still win island-wide, while the reverse is nearly impossible.
			</p>
			<p>
				This population concentration explains why Puerto Rico's political debates
				often center on urban issues: traffic, public services, economic development,
				and professional employment. Rural concerns, from agricultural policy to
				infrastructure investment, take a back seat.
			</p>
		</Step>

		<Step active={currentStep === 11} index={11}>
			<h3>The Stakes of the Map</h3>
			<p>
				Puerto Rico's electoral geography matters because
				<span class="highlight">the map itself is contested terrain</span>.
				Proposals to consolidate municipalities, redraw district lines, or change
				the at-large vs. district balance would reshape political power.
			</p>
			<p>
				The current system favors parties that can build broad geographic coalitions
				while maintaining strong urban cores. It disadvantages parties concentrated
				in a few regions, and it gives smaller municipalities outsized influence
				in some legislative races.
			</p>
			<p>
				As Puerto Rico debates its future, from statehood to independence, the
				question of how to draw the map, and who decides, remains as politically
				charged as the debates over the island's ultimate status.
			</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>The Geography of Power</h2>
			<p>
				Puerto Rico's electoral map tells a story of colonial inheritance, urban
				concentration, and regional identity. The 78 municipalities, 8 Senate districts,
				and 40 House districts create a complex terrain where geography shapes
				political outcomes.
			</p>

			<div class="key-takeaways">
				<h3>Key Takeaways</h3>
				<ul>
					<li><strong>Colonial Legacy:</strong> Municipality boundaries date to Spanish rule and no longer reflect modern population patterns</li>
					<li><strong>Population Concentration:</strong> Over half the population lives in just 10 municipalities, making urban areas decisive</li>
					<li><strong>Regional Blocs:</strong> Neighboring municipalities vote alike, creating persistent geographic coalitions</li>
					<li><strong>Class Geography:</strong> Wealthier areas lean PNP; poorer areas lean PPD, with exceptions</li>
					<li><strong>Mixed Representation:</strong> The combination of district and at-large seats creates complex campaign incentives</li>
				</ul>
			</div>

			<div class="sources">
				<h3>Sources</h3>
				<ul>
					<li>Comision Estatal de Elecciones de Puerto Rico (CEE) - Municipality-level election results 2016-2024</li>
					<li>U.S. Census Bureau - Puerto Rico geographic definitions and TIGER/Line shapefiles</li>
					<li>Puerto Rico Planning Board - Regional classifications and urban/rural definitions</li>
					<li>American Community Survey - Population and demographic data by municipality</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/referendum-2020" class="nav-link prev">
					<span class="nav-direction">Previous</span>
					<span class="nav-title">The 52.5% Threshold</span>
				</a>
				<a href="{base}/chapters/fortaleza" class="nav-link next">
					<span class="nav-direction">Next Chapter</span>
					<span class="nav-title">La Fortaleza</span>
				</a>
			</nav>
		</div>
	</section>
</article>

<style>
	.chapter-header {
		min-height: 60vh;
		display: flex;
		align-items: center;
		padding: var(--space-3xl) 0;
		background: radial-gradient(ellipse at 50% 100%, var(--color-surface) 0%, var(--color-bg) 70%);
	}

	.viz-container {
		width: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: var(--space-lg);
	}

	.loading {
		color: var(--color-text-muted);
		font-style: italic;
	}

	.viz-title {
		font-size: var(--text-lg);
		font-weight: var(--font-medium);
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
		text-align: center;
	}

	.viz-note {
		font-size: var(--text-sm);
		color: var(--color-text-light);
		margin-top: var(--space-md);
		font-style: italic;
	}

	.bar-container {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.legend-row {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-md);
		margin-top: var(--space-lg);
		justify-content: center;
	}

	.legend-wrap {
		max-width: 500px;
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.legend-swatch {
		width: 16px;
		height: 16px;
		border-radius: var(--radius-sm);
	}

	.chapter-conclusion {
		padding: var(--space-3xl) 0;
		background: var(--color-surface);
	}

	.key-takeaways {
		margin: var(--space-xl) 0;
		padding: var(--space-lg);
		background: var(--color-bg);
		border-radius: var(--radius-lg);
		border-left: 4px solid var(--color-accent);
	}

	.key-takeaways h3 {
		font-size: var(--text-md);
		font-weight: var(--font-semibold);
		margin-bottom: var(--space-md);
		color: var(--color-text);
	}

	.key-takeaways ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.key-takeaways li {
		padding: var(--space-sm) 0;
		border-bottom: 1px solid var(--color-border);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.key-takeaways li:last-child {
		border-bottom: none;
	}

	.key-takeaways strong {
		color: var(--color-text);
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

	.nav-link:hover { background: var(--color-bg); }
	.nav-link.next { text-align: right; }
	.nav-direction { font-size: var(--text-sm); color: var(--color-text-muted); }
	.nav-title { font-family: var(--font-display); font-size: var(--text-lg); font-weight: var(--font-semibold); color: var(--color-text); }

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
</style>
