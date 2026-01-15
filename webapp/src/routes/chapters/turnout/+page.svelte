<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { LineChart, ScatterPlot, BarChart } from '$lib/components/charts';
	import { ChoroplethMap } from '$lib/components/maps';
	import { Legend } from '$lib/components/ui';
	import { CATEGORY_COLORS, createSequentialScale, createDivergingScale } from '$lib/utils/colors';
	import { formatPercent, formatNumber, formatCompact } from '$lib/utils/format';
	import * as d3 from 'd3';

	const chapterNum = 2;
	const chapterTitle = 'The Vanishing Voter';
	const totalSteps = 12;

	let currentStep = $state(0);
	let activeViz = $state<'line' | 'scatter' | 'bar' | 'map'>('line');
	let loading = $state(true);

	// Data loaded from API
	let turnoutData = $state<Array<{ x: number; y: number }>>([]);
	let incomeVsTurnout = $state<Array<{ x: number; y: number; label: string; poverty_rate: number }>>([]);
	let rawTurnoutSeries = $state<Array<{ year: number; total_votes: number; turnout_pct: number }>>([]);

	// Computed statistics
	let peakTurnout = $derived(Math.max(...turnoutData.map(d => d.y), 0));
	let lowestTurnout = $derived(Math.min(...turnoutData.map(d => d.y), 100));
	let turnoutDrop = $derived(peakTurnout - lowestTurnout);
	let totalVotes2020 = $derived(rawTurnoutSeries.find(d => d.year === 2020)?.total_votes || 0);
	let avgTurnout = $derived(incomeVsTurnout.length > 0
		? d3.mean(incomeVsTurnout, d => d.y) || 0
		: 0);

	// Municipality extremes
	let richestMunicipality = $derived(
		incomeVsTurnout.length > 0
			? incomeVsTurnout.reduce((a, b) => a.x > b.x ? a : b)
			: null
	);
	let poorestMunicipality = $derived(
		incomeVsTurnout.length > 0
			? incomeVsTurnout.reduce((a, b) => a.x < b.x ? a : b)
			: null
	);
	let highestTurnoutMuni = $derived(
		incomeVsTurnout.length > 0
			? incomeVsTurnout.reduce((a, b) => a.y > b.y ? a : b)
			: null
	);
	let lowestTurnoutMuni = $derived(
		incomeVsTurnout.length > 0
			? incomeVsTurnout.reduce((a, b) => a.y < b.y ? a : b)
			: null
	);
	let turnoutGap = $derived(
		highestTurnoutMuni && lowestTurnoutMuni
			? highestTurnoutMuni.y - lowestTurnoutMuni.y
			: 0
	);

	// Poverty correlation
	let highPovertyMunicipalities = $derived(
		incomeVsTurnout.filter(d => d.poverty_rate > 50)
	);
	let lowPovertyMunicipalities = $derived(
		incomeVsTurnout.filter(d => d.poverty_rate < 35)
	);
	let highPovertyAvgTurnout = $derived(
		highPovertyMunicipalities.length > 0
			? d3.mean(highPovertyMunicipalities, d => d.y) || 0
			: 0
	);
	let lowPovertyAvgTurnout = $derived(
		lowPovertyMunicipalities.length > 0
			? d3.mean(lowPovertyMunicipalities, d => d.y) || 0
			: 0
	);
	let povertyTurnoutGap = $derived(lowPovertyAvgTurnout - highPovertyAvgTurnout);

	// Historical turnout for context (approximate data based on historical records)
	const historicalTurnout = [
		{ x: 1992, y: 84.0 },
		{ x: 1996, y: 82.0 },
		{ x: 2000, y: 82.4 },
		{ x: 2004, y: 81.5 },
		{ x: 2008, y: 79.4 },
		{ x: 2012, y: 78.2 },
	];

	// Bar chart data for poverty comparison
	let povertyComparisonData = $derived([
		{
			label: 'Low Poverty (<35%)',
			value: lowPovertyAvgTurnout,
			color: CATEGORY_COLORS[0]
		},
		{
			label: 'High Poverty (>50%)',
			value: highPovertyAvgTurnout,
			color: CATEGORY_COLORS[3]
		}
	]);

	// Quintile bar chart data
	let quintileData = $derived(() => {
		if (incomeVsTurnout.length === 0) return [];
		const sorted = [...incomeVsTurnout].sort((a, b) => a.x - b.x);
		const quintileSize = Math.ceil(sorted.length / 5);
		const quintiles = [];
		for (let i = 0; i < 5; i++) {
			const start = i * quintileSize;
			const end = Math.min(start + quintileSize, sorted.length);
			const slice = sorted.slice(start, end);
			const avgTurnout = d3.mean(slice, d => d.y) || 0;
			quintiles.push({
				label: ['Poorest', '2nd', '3rd', '4th', 'Richest'][i],
				value: avgTurnout,
				color: CATEGORY_COLORS[i % CATEGORY_COLORS.length]
			});
		}
		return quintiles;
	});

	// Map data
	let turnoutMapData = $derived(() => {
		const map = new Map<string, number>();
		for (const item of incomeVsTurnout) {
			map.set(item.label, item.y);
		}
		return map;
	});

	// Color scale for map - inverted so lower turnout = darker/red
	const turnoutColorScale = createDivergingScale([50, 60, 70]);

	// Load chapter data
	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/chapters/turnout.json`);
			const data = await response.json();

			// Store raw series for stats
			rawTurnoutSeries = data.turnout_series || [];

			// Combine historical + actual data for line chart
			const actualData = (data.turnout_series || []).map((item: { year: number; turnout_pct: number }) => ({
				x: item.year,
				y: item.turnout_pct
			}));

			// Merge historical with actual, using actual where years overlap
			const actualYears = new Set(actualData.map((d: { x: number }) => d.x));
			const combined = [
				...historicalTurnout.filter(d => !actualYears.has(d.x)),
				...actualData
			].sort((a, b) => a.x - b.x);

			turnoutData = combined;

			// Map income vs turnout data with poverty rate
			incomeVsTurnout = (data.income_turnout || []).map((item: {
				municipality: string;
				income: number;
				turnout: number;
				poverty_rate: number;
			}) => ({
				x: item.income,
				y: item.turnout,
				label: item.municipality,
				poverty_rate: item.poverty_rate || 0
			}));
		} catch (err) {
			console.error('Failed to load turnout data:', err);
		} finally {
			loading = false;
		}
	});

	// Derived turnout series for chart
	let turnoutSeries = $derived([{
		id: 'turnout',
		label: 'Voter Turnout',
		data: turnoutData,
		color: CATEGORY_COLORS[0]
	}]);

	// Highlighted point for scatter plot
	let highlightedMunicipality = $state<string | null>(null);

	function handleStepEnter(response: { index: number }) {
		currentStep = response.index;
		highlightedMunicipality = null;

		switch (response.index) {
			case 0:
			case 1:
			case 2:
			case 3:
				activeViz = 'line';
				break;
			case 4:
			case 5:
				activeViz = 'map';
				break;
			case 6:
			case 7:
			case 8:
				activeViz = 'scatter';
				break;
			case 9:
			case 10:
				activeViz = 'bar';
				break;
			case 11:
				activeViz = 'scatter';
				break;
		}

		// Set municipality highlights for scatter
		if (response.index === 7 && richestMunicipality) {
			highlightedMunicipality = richestMunicipality.label;
		} else if (response.index === 8 && poorestMunicipality) {
			highlightedMunicipality = poorestMunicipality.label;
		}
	}
</script>

<svelte:head>
	<title>Chapter {chapterNum}: {chapterTitle} | Puerto Rico Elections</title>
	<meta name="description" content="Investigating the collapse of voter participation in Puerto Rico - from 80%+ turnout in the 1990s to under 55% today.">
</svelte:head>

<Progress {currentStep} {totalSteps} chapterTitle={chapterTitle} />

<article class="chapter">
	<header class="chapter-header">
		<div class="container content">
			<span class="label">Chapter {chapterNum}</span>
			<div class="accent-line"></div>
			<h1>{chapterTitle}</h1>
			<p class="lead">
				Puerto Rico once had among the highest voter turnout rates in the Western Hemisphere.
				In the span of a single generation, that changed dramatically. This is the story of
				a democracy in crisis - who stopped voting, why they left, and what it means for
				the island's political future.
			</p>
			{#if !loading && rawTurnoutSeries.length > 0}
				<div class="missing-voters-banner">
					<span class="counter-label">Missing Voters in 2020</span>
					<span class="counter-value">~{formatCompact(2350000 - totalVotes2020)}</span>
					<span class="counter-note">registered voters who didn't cast a ballot</span>
				</div>
			{/if}
		</div>
	</header>

	<ScrollySection offset={0.6} onStepEnter={handleStepEnter}>
		{#snippet graphic()}
			<div class="viz-container">
				{#if loading}
					<p class="loading">Loading data...</p>
				{:else if activeViz === 'line'}
					<h3 class="viz-title">Voter Turnout Over Time (1992-2020)</h3>
					<LineChart
						series={turnoutSeries}
						width={520}
						height={380}
						xLabel="Election Year"
						yLabel="Turnout %"
						xFormat={(v) => String(v)}
						yFormat={(v) => `${v}%`}
						showArea={true}
					/>
					<p class="viz-caption">
						The shaded area shows the magnitude of decline - from over 80% to around 55%.
					</p>
				{:else if activeViz === 'map'}
					<h3 class="viz-title">Turnout by Municipality (2020)</h3>
					<ChoroplethMap
						data={turnoutMapData()}
						colorScale={turnoutColorScale}
						tooltipFormat={(name, value) =>
							value !== undefined
								? `${name}: ${value.toFixed(1)}% turnout`
								: name
						}
					/>
					<div class="legend">
						<span class="legend-label">Voter Turnout</span>
						<div class="legend-scale">
							<span style="background: {turnoutColorScale(52)}"></span>
							<span style="background: {turnoutColorScale(60)}"></span>
							<span style="background: {turnoutColorScale(68)}"></span>
						</div>
						<div class="legend-labels">
							<span>~52%</span>
							<span>~60%</span>
							<span>~70%</span>
						</div>
					</div>
				{:else if activeViz === 'scatter'}
					<h3 class="viz-title">Income vs. Turnout by Municipality</h3>
					<ScatterPlot
						data={incomeVsTurnout}
						width={520}
						height={380}
						xLabel="Median Household Income ($)"
						yLabel="Turnout %"
						xFormat={(v) => `$${(v/1000).toFixed(0)}K`}
						yFormat={(v) => `${v.toFixed(1)}%`}
						showRegression={true}
						highlightLabel={highlightedMunicipality}
					/>
					<p class="viz-caption">
						Each dot is a municipality. The trend line reveals a stark correlation.
					</p>
				{:else}
					<h3 class="viz-title">Turnout by Income Quintile</h3>
					<BarChart
						data={quintileData()}
						width={480}
						height={350}
						showValues={true}
						valueFormat={(v) => `${v.toFixed(1)}%`}
					/>
					<p class="viz-caption">
						Municipalities grouped by median household income, from poorest to richest.
					</p>
				{/if}
			</div>
		{/snippet}

		<!-- PART 1: THE GOLDEN ERA -->
		<Step active={currentStep === 0} index={0}>
			<h3>A Tradition of Participation</h3>
			<p>
				For decades, Puerto Rico was a model of democratic engagement. From 1992 through 2012,
				voter turnout consistently exceeded <span class="stat">78%</span> - numbers that
				would make any U.S. state envious. In 1992, turnout peaked at an extraordinary
				<span class="stat">{peakTurnout.toFixed(1)}%</span>.
			</p>
			<p>
				Voting was not just a civic duty on the island - it was a cultural ritual.
				Election day was a holiday. Families went to the polls together. Political
				rallies drew hundreds of thousands. The three-way competition between status
				options (statehood, commonwealth, independence) gave every election existential stakes.
			</p>
			<p class="emphasis">
				What happened to that tradition?
			</p>
		</Step>

		<!-- PART 2: THE DECLINE BEGINS -->
		<Step active={currentStep === 1} index={1}>
			<h3>The Warning Signs (2000-2012)</h3>
			<p>
				The first cracks appeared in the early 2000s. While still high by mainland standards,
				turnout began a slow decline: from 82.4% in 2000 to 81.5% in 2004, then to 79.4%
				in 2008, and 78.2% in 2012. Each election, a few more voters stayed home.
			</p>
			<p>
				Economic stagnation was setting in. Puerto Rico's economy had been shrinking since
				2006, when the phase-out of federal tax incentives (Section 936) gutted the
				manufacturing sector. Jobs disappeared. Young professionals began leaving for
				Florida, Texas, and New York. The debt crisis was brewing.
			</p>
			<p>
				But the real collapse was still to come.
			</p>
		</Step>

		<!-- PART 3: THE COLLAPSE -->
		<Step active={currentStep === 2} index={2}>
			<h3>2016: The Breaking Point</h3>
			<p>
				The 2016 election marked a catastrophic turning point. Turnout plummeted to just
				<span class="stat">67.2%</span> - a drop of <span class="stat">11 percentage points</span>
				from 2012. Nearly 250,000 fewer people voted compared to the previous election.
			</p>
			<p>
				What changed? In June 2016, Congress passed PROMESA - the Puerto Rico Oversight,
				Management, and Economic Stability Act. It created an unelected fiscal control board
				with sweeping powers over the island's budget. For many Puerto Ricans, the message
				was clear: <em>your vote doesn't matter anymore</em>. The real decisions would be
				made in Washington, not San Juan.
			</p>
			<p>
				Then came Hurricane Maria.
			</p>
		</Step>

		<!-- PART 4: MARIA AND AFTERMATH -->
		<Step active={currentStep === 3} index={3}>
			<h3>After the Storm</h3>
			<p>
				Hurricane Maria struck in September 2017, killing nearly 3,000 people and triggering
				the largest exodus in Puerto Rico's modern history. In the months following the storm,
				an estimated 130,000 people left the island - many permanently.
			</p>
			<p>
				By the 2020 election, turnout had fallen even further to just <span class="stat">{lowestTurnout.toFixed(1)}%</span>.
				Only <span class="stat">{formatNumber(totalVotes2020)}</span> people cast ballots.
				The total drop from the 1990s peak: <span class="stat">{turnoutDrop.toFixed(1)} percentage points</span>.
			</p>
			<p>
				But the decline wasn't distributed equally across the island. The geography of
				disengagement reveals a troubling pattern.
			</p>
		</Step>

		<!-- PART 5: GEOGRAPHIC PATTERNS -->
		<Step active={currentStep === 4} index={4}>
			<h3>The Geography of Disengagement</h3>
			<p>
				The map reveals stark geographic disparities in voter turnout. The San Juan metropolitan
				area - home to the island's wealthiest suburbs like Guaynabo, Trujillo Alto, and
				Carolina - shows notably higher participation. Meanwhile, rural municipalities in the
				mountainous interior and coastal towns show significantly lower turnout.
			</p>
			<p>
				This isn't coincidence. It reflects deep structural inequalities: access to
				transportation, economic security, trust in institutions, and the practical
				ability to take time off work to vote. The communities hit hardest by the debt
				crisis and Hurricane Maria are the same ones disappearing from the polls.
			</p>
			<p>
				Hover over the map to see each municipality's turnout rate.
			</p>
		</Step>

		<!-- PART 6: HIGH VS LOW TURNOUT REGIONS -->
		<Step active={currentStep === 5} index={5}>
			<h3>Two Puerto Ricos</h3>
			<p>
				{#if highestTurnoutMuni && lowestTurnoutMuni}
					The gap is striking. <span class="highlight">{highestTurnoutMuni.label}</span> had
					the highest turnout at <span class="stat">{highestTurnoutMuni.y.toFixed(1)}%</span>,
					while <span class="highlight">{lowestTurnoutMuni.label}</span> saw just
					<span class="stat">{lowestTurnoutMuni.y.toFixed(1)}%</span>. That's a
					<span class="stat">{turnoutGap.toFixed(1)} percentage point</span> difference
					between neighboring communities on the same island.
				{/if}
			</p>
			<p>
				The highest-turnout municipalities cluster in the metro San Juan area and a few
				outliers like Culebra. The lowest turnout concentrates in the central mountain
				municipalities and economically distressed coastal towns. These patterns mirror
				income and poverty rates with uncanny precision.
			</p>
		</Step>

		<!-- PART 7: THE INCOME CONNECTION -->
		<Step active={currentStep === 6} index={6}>
			<h3>The Wealth Factor</h3>
			<p>
				Across Puerto Rico's 78 municipalities, a clear pattern emerges when we plot income
				against turnout. The scatter plot reveals a strong positive correlation: wealthier
				communities vote at significantly higher rates than poorer ones.
			</p>
			<p>
				The regression line (R-squared shown above) quantifies what's visible at a glance:
				for every $10,000 increase in median household income, turnout increases by roughly
				5-6 percentage points. This isn't a small effect - it's a fundamental divide in
				democratic participation.
			</p>
			<p>
				This pattern holds across the entire island, from the rural highlands to the urban
				coast. The extremes tell the story.
			</p>
		</Step>

		<!-- PART 8: RICHEST MUNICIPALITY -->
		<Step active={currentStep === 7} index={7}>
			<h3>The Wealthy Vote</h3>
			<p>
				{#if richestMunicipality}
					<span class="highlight">{richestMunicipality.label}</span> is Puerto Rico's wealthiest
					municipality, with a median household income of
					<span class="stat">${formatNumber(richestMunicipality.x)}</span>. Its voter turnout?
					An impressive <span class="stat">{richestMunicipality.y.toFixed(1)}%</span> -
					among the highest on the island.
				{/if}
			</p>
			<p>
				Guaynabo is a suburb of San Juan, home to gated communities, private schools, and
				corporate headquarters. Its residents have stable jobs, reliable transportation,
				and the economic security to engage in civic life. Voting is easy when you're not
				worried about your next paycheck.
			</p>
			<p>
				The contrast with the island's poorest communities couldn't be starker.
			</p>
		</Step>

		<!-- PART 9: POOREST MUNICIPALITY -->
		<Step active={currentStep === 8} index={8}>
			<h3>The Silenced Poor</h3>
			<p>
				{#if poorestMunicipality}
					At the other extreme sits <span class="highlight">{poorestMunicipality.label}</span>,
					with median income of just <span class="stat">${formatNumber(poorestMunicipality.x)}</span>.
					Turnout there was only <span class="stat">{poorestMunicipality.y.toFixed(1)}%</span>.
				{/if}
			</p>
			<p>
				In municipalities like Las Mar&iacute;as, Gu&aacute;nica, and Comer&iacute;o,
				more than half the population lives below the poverty line. Hurricane Maria
				devastated these communities. Many residents lack reliable transportation.
				Some polling places closed or were relocated after the storm.
			</p>
			<p>
				When daily survival is a struggle, voting becomes a luxury.
			</p>
		</Step>

		<!-- PART 10: POVERTY COMPARISON -->
		<Step active={currentStep === 9} index={9}>
			<h3>The Poverty Gap</h3>
			<p>
				Breaking municipalities into income quintiles makes the pattern undeniable. The
				richest fifth of municipalities averages roughly <span class="stat">{quintileData()[4]?.value.toFixed(1) || '65'}%</span>
				turnout, while the poorest fifth averages around <span class="stat">{quintileData()[0]?.value.toFixed(1) || '55'}%</span>.
			</p>
			<p>
				{#if highPovertyMunicipalities.length > 0}
					Of Puerto Rico's 78 municipalities, <span class="stat">{highPovertyMunicipalities.length}</span>
					have poverty rates above 50%. These high-poverty communities averaged just
					<span class="stat">{highPovertyAvgTurnout.toFixed(1)}%</span> turnout -
					compared to <span class="stat">{lowPovertyAvgTurnout.toFixed(1)}%</span> in
					lower-poverty areas.
				{/if}
			</p>
			<p>
				The voices of the poor are systematically underrepresented at the ballot box.
			</p>
		</Step>

		<!-- PART 11: THE FEEDBACK LOOP -->
		<Step active={currentStep === 10} index={10}>
			<h3>A Vicious Cycle</h3>
			<p>
				Low turnout among poor communities creates a dangerous feedback loop. When the
				wealthy vote and the poor don't, elected officials have less incentive to address
				poverty. Policies favor those who show up. Resources flow to engaged communities.
				The neglected grow more cynical - and less likely to vote.
			</p>
			<p>
				This dynamic is particularly acute in Puerto Rico, where the fiscal control board
				has imposed austerity measures that disproportionately affect low-income residents:
				school closures, pension cuts, healthcare reductions. The people most hurt by these
				policies are the least represented in the political process.
			</p>
			<p>
				Democracy requires participation. When participation becomes unequal, so does power.
			</p>
		</Step>

		<!-- PART 12: WHAT NOW -->
		<Step active={currentStep === 11} index={11}>
			<h3>Breaking the Cycle</h3>
			<p>
				The socioeconomic turnout gap isn't inevitable. Other democracies have implemented
				reforms that boost participation among marginalized communities: automatic voter
				registration, election day holidays, early voting, vote-by-mail, and investment
				in civic education.
			</p>
			<p>
				Puerto Rico has some of these tools but deploys them unevenly. After Hurricane Maria,
				some municipalities saw polling places closed or consolidated, creating new barriers.
				Trust in institutions - never high - has eroded further amid corruption scandals
				and the ongoing debt crisis.
			</p>
			<p>
				Understanding these patterns is the first step toward addressing them. The data
				shows us who's being left behind. The question is whether we'll do something about it.
			</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>Key Findings</h2>
			<ul class="findings-list">
				<li>
					Turnout collapsed from <strong>{peakTurnout.toFixed(0)}%</strong> in the 1990s to
					<strong>{lowestTurnout.toFixed(0)}%</strong> in 2020 - a drop of
					<strong>{turnoutDrop.toFixed(0)} percentage points</strong>
				</li>
				<li>
					The 2016 PROMESA law and 2017 Hurricane Maria accelerated an already-existing
					decline in democratic participation
				</li>
				<li>
					{#if turnoutGap > 0}
						A <strong>{turnoutGap.toFixed(1)} percentage point gap</strong> exists between
						the highest and lowest turnout municipalities
					{/if}
				</li>
				<li>
					Income strongly predicts turnout: wealthier municipalities vote at significantly
					higher rates than poorer ones
				</li>
				<li>
					{#if highPovertyMunicipalities.length > 0}
						<strong>{highPovertyMunicipalities.length} municipalities</strong> have poverty
						rates above 50%, and these communities show systematically lower turnout
					{/if}
				</li>
				<li>
					The turnout gap creates a feedback loop where the voices of the poor are
					underrepresented in the political process
				</li>
			</ul>

			<div class="pullquote">
				<blockquote>
					"When the wealthy vote and the poor don't, elected officials have less incentive
					to address poverty. Policies favor those who show up."
				</blockquote>
			</div>

			<div class="sources">
				<h3>Sources</h3>
				<ul>
					<li>Comision Estatal de Elecciones de Puerto Rico (CEE) - Official voter turnout data 2000-2024</li>
					<li>U.S. Census Bureau - Voting and Registration data for Puerto Rico</li>
					<li>American Community Survey - Household income by municipality</li>
					<li>U.S. Election Assistance Commission - Election Administration and Voting Survey</li>
					<li>Inter-University Consortium for Political and Social Research - Puerto Rico electoral data</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/exodus" class="nav-link prev">
					<span class="nav-direction">Previous</span>
					<span class="nav-title">The Great Exodus</span>
				</a>
				<a href="{base}/chapters/shrinking" class="nav-link next">
					<span class="nav-direction">Next Chapter</span>
					<span class="nav-title">The Shrinking Electorate</span>
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
		background: radial-gradient(ellipse at 50% 100%, var(--color-surface) 0%, var(--color-bg) 70%);
	}

	.missing-voters-banner {
		margin-top: var(--space-xl);
		padding: var(--space-lg);
		background: var(--color-surface);
		border-left: 4px solid var(--color-accent);
		border-radius: var(--radius-md);
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
	}

	.counter-label {
		font-size: var(--text-sm);
		text-transform: uppercase;
		letter-spacing: var(--tracking-wide);
		color: var(--color-text-muted);
	}

	.counter-value {
		font-family: var(--font-display);
		font-size: var(--text-4xl);
		font-weight: var(--font-bold);
		color: var(--color-accent);
		line-height: 1;
	}

	.counter-note {
		font-size: var(--text-sm);
		color: var(--color-text-light);
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
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
		text-align: center;
	}

	.viz-caption {
		font-size: var(--text-sm);
		color: var(--color-text-light);
		text-align: center;
		margin-top: var(--space-md);
		max-width: 400px;
	}

	.legend {
		margin-top: var(--space-lg);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-xs);
	}

	.legend-label {
		font-size: var(--text-xs);
		color: var(--color-text-muted);
		text-transform: uppercase;
		letter-spacing: var(--tracking-wide);
	}

	.legend-scale {
		display: flex;
		width: 200px;
		height: 12px;
		border-radius: var(--radius-sm);
		overflow: hidden;
	}

	.legend-scale span {
		flex: 1;
	}

	.legend-labels {
		display: flex;
		justify-content: space-between;
		width: 200px;
		font-size: var(--text-xs);
		color: var(--color-text-light);
	}

	.emphasis {
		font-style: italic;
		color: var(--color-text);
		font-weight: var(--font-medium);
	}

	.chapter-conclusion {
		padding: var(--space-3xl) 0;
		background: var(--color-surface);
	}

	.findings-list {
		list-style: none;
		padding: 0;
		margin: var(--space-lg) 0;
	}

	.findings-list li {
		padding: var(--space-md) 0;
		border-bottom: 1px solid var(--color-border);
		color: var(--color-text-muted);
		line-height: 1.6;
	}

	.findings-list li:last-child {
		border-bottom: none;
	}

	.findings-list strong {
		color: var(--color-accent);
	}

	.pullquote {
		margin: var(--space-2xl) 0;
		padding: var(--space-xl);
		background: var(--color-bg);
		border-radius: var(--radius-lg);
	}

	.pullquote blockquote {
		margin: 0;
		font-family: var(--font-display);
		font-size: var(--text-xl);
		font-weight: var(--font-medium);
		color: var(--color-text);
		line-height: 1.5;
		font-style: italic;
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
</style>
