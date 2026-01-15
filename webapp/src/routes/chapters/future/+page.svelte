<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { LineChart, BarChart } from '$lib/components/charts';
	import { CATEGORY_COLORS, PARTY_COLORS } from '$lib/utils/colors';

	const chapterNum = 12;
	const chapterTitle = "Puerto Rico's Electoral Future";
	const totalSteps = 8;

	let currentStep = $state(0);
	let loading = $state(true);
	let activeViz = $state<'population' | 'electorate' | 'parties' | 'age' | 'scenarios'>('population');
	let selectedScenario = $state<string | null>(null);

	// Data structures
	interface PopulationPoint {
		year: number;
		population: number;
		low?: number;
		high?: number;
	}

	interface ElectoratePoint {
		year: number;
		registered_voters: number;
		turnout_pct: number;
		votes_cast: number;
	}

	interface PartySharePoint {
		year: number;
		pnp: number;
		ppd: number;
		third_parties: number;
	}

	interface Scenario {
		name: string;
		probability: number;
		description: string;
		population_2040: number;
		voters_2040: number;
		turnout_2040: number;
		third_party_share: number;
		key_assumptions: string[];
	}

	let populationHistorical = $state<PopulationPoint[]>([]);
	let populationProjected = $state<PopulationPoint[]>([]);
	let electorateHistorical = $state<ElectoratePoint[]>([]);
	let electorateProjected = $state<ElectoratePoint[]>([]);
	let partyShareHistorical = $state<PartySharePoint[]>([]);
	let scenarios = $state<Record<string, Scenario>>({});
	let keyMetrics = $state<Record<string, number>>({});
	let medianVoterAge = $state<Array<{year: number; age: number; projected?: boolean}>>([]);
	let whatIfStatehood = $state<Record<string, any>>({});

	// Load data
	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/chapters/future.json`);
			const data = await response.json();

			populationHistorical = data.population_projection.historical || [];
			populationProjected = data.population_projection.projected || [];
			electorateHistorical = data.electorate_projection.historical || [];
			electorateProjected = data.electorate_projection.projected || [];
			partyShareHistorical = data.party_vote_share_trend.historical || [];
			scenarios = data.scenarios || {};
			keyMetrics = data.key_metrics_summary || {};
			medianVoterAge = data.demographic_shift.median_voter_age || [];
			whatIfStatehood = data.what_if_statehood || {};
		} catch (err) {
			console.error('Failed to load future data:', err);
		} finally {
			loading = false;
		}
	});

	// Derived data for population chart with projection band
	let populationSeries = $derived(() => {
		const historicalData = populationHistorical.map(p => ({ x: p.year, y: p.population }));
		const projectedData = populationProjected.map(p => ({ x: p.year, y: p.population }));
		const projectedLow = populationProjected.map(p => ({ x: p.year, y: p.low || p.population }));
		const projectedHigh = populationProjected.map(p => ({ x: p.year, y: p.high || p.population }));

		return [
			{ id: 'historical', label: 'Historical', color: CATEGORY_COLORS[0], data: historicalData },
			{ id: 'projected', label: 'Projected', color: CATEGORY_COLORS[1], data: projectedData },
		];
	});

	// Derived data for electorate chart
	let electorateSeries = $derived(() => {
		const historicalVoters = electorateHistorical.map(e => ({ x: e.year, y: e.registered_voters }));
		const projectedVoters = electorateProjected.map(e => ({ x: e.year, y: e.registered_voters }));
		const historicalVotes = electorateHistorical.map(e => ({ x: e.year, y: e.votes_cast }));
		const projectedVotes = electorateProjected.map(e => ({ x: e.year, y: e.votes_cast }));

		return [
			{ id: 'registered', label: 'Registered Voters', color: CATEGORY_COLORS[0], data: [...historicalVoters, ...projectedVoters] },
			{ id: 'actual', label: 'Actual Votes', color: CATEGORY_COLORS[3], data: [...historicalVotes, ...projectedVotes] },
		];
	});

	// Derived data for party share trends
	let partySeries = $derived(() => {
		const pnpData = partyShareHistorical.map(p => ({ x: p.year, y: p.pnp }));
		const ppdData = partyShareHistorical.map(p => ({ x: p.year, y: p.ppd }));
		const thirdData = partyShareHistorical.map(p => ({ x: p.year, y: p.third_parties }));

		return [
			{ id: 'pnp', label: 'PNP', color: PARTY_COLORS.PNP, data: pnpData },
			{ id: 'ppd', label: 'PPD', color: PARTY_COLORS.PPD, data: ppdData },
			{ id: 'third', label: 'Third Parties', color: PARTY_COLORS.MVC, data: thirdData },
		];
	});

	// Derived data for median age trend
	let ageSeries = $derived(() => {
		const historical = medianVoterAge.filter(a => !a.projected).map(a => ({ x: a.year, y: a.age }));
		const projected = medianVoterAge.filter(a => a.projected).map(a => ({ x: a.year, y: a.age }));

		// Connect historical to projected
		if (historical.length > 0 && projected.length > 0) {
			projected.unshift(historical[historical.length - 1]);
		}

		return [
			{ id: 'historical', label: 'Historical', color: CATEGORY_COLORS[0], data: historical },
			{ id: 'projected', label: 'Projected', color: CATEGORY_COLORS[1], data: projected },
		];
	});

	// Scenario bar data
	let scenarioBarData = $derived(() => {
		return Object.entries(scenarios).map(([key, s]) => ({
			label: s.name,
			value: s.probability,
			color: key === 'status_quo' ? CATEGORY_COLORS[0] :
			       key === 'statehood' ? CATEGORY_COLORS[2] :
			       key === 'independence' ? CATEGORY_COLORS[4] : CATEGORY_COLORS[3]
		}));
	});

	function handleStepEnter(response: { index: number }) {
		currentStep = response.index;

		// Map steps to visualizations
		if (response.index <= 1) {
			activeViz = 'population';
		} else if (response.index === 2) {
			activeViz = 'electorate';
		} else if (response.index === 3) {
			activeViz = 'age';
		} else if (response.index === 4) {
			activeViz = 'parties';
		} else {
			activeViz = 'scenarios';
		}
	}

	function formatPopulation(v: number): string {
		return `${(v / 1000000).toFixed(2)}M`;
	}

	function formatVoters(v: number): string {
		return `${(v / 1000000).toFixed(2)}M`;
	}

	function formatPercent(v: number): string {
		return `${v.toFixed(0)}%`;
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
				Throughout this series, we've examined Puerto Rico's electoral transformation:
				a shrinking population, an aging electorate, fragmenting parties, and
				declining engagement. Now we must ask: where does this lead?
			</p>
		</div>
	</header>

	<ScrollySection offset={0.6} onStepEnter={handleStepEnter}>
		{#snippet graphic()}
			<div class="viz-container">
				{#if loading}
					<p class="loading">Loading data...</p>
				{:else if activeViz === 'population'}
					<h3 class="viz-title">Population Trajectory</h3>
					<LineChart
						series={populationSeries()}
						width={500}
						height={340}
						xLabel="Year"
						yLabel="Population"
						xFormat={(v) => String(v)}
						yFormat={formatPopulation}
						showArea={true}
					/>
					<p class="viz-note">Dashed line indicates Census Bureau projections</p>
				{:else if activeViz === 'electorate'}
					<h3 class="viz-title">The Shrinking Electorate</h3>
					<LineChart
						series={electorateSeries()}
						width={500}
						height={340}
						xLabel="Year"
						yLabel="Voters"
						xFormat={(v) => String(v)}
						yFormat={formatVoters}
						showArea={false}
					/>
					<p class="viz-note">Gap between registered and actual voters widens</p>
				{:else if activeViz === 'age'}
					<h3 class="viz-title">Median Voter Age</h3>
					<LineChart
						series={ageSeries()}
						width={500}
						height={340}
						xLabel="Year"
						yLabel="Age"
						xFormat={(v) => String(v)}
						yFormat={(v) => `${v} years`}
						showArea={false}
					/>
					<p class="viz-note">The electorate ages as young people leave</p>
				{:else if activeViz === 'parties'}
					<h3 class="viz-title">Party Vote Share Evolution</h3>
					<LineChart
						series={partySeries()}
						width={500}
						height={340}
						xLabel="Year"
						yLabel="Vote Share"
						xFormat={(v) => String(v)}
						yFormat={formatPercent}
						showArea={false}
					/>
					<p class="viz-note">Third parties have grown from 5% to 28% in 12 years</p>
				{:else if activeViz === 'scenarios'}
					<h3 class="viz-title">Scenario Probability Assessment</h3>
					<BarChart
						data={scenarioBarData()}
						width={480}
						height={280}
						horizontal={true}
						valueFormat={(v) => `${v}%`}
					/>
					<p class="viz-note">Based on historical trends and expert assessment</p>
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>The Demographic Trajectory</h3>
			<p>
				Puerto Rico's population has declined by <span class="stat">600,000</span> people
				since 2010, a loss of 16% in just fourteen years. This isn't natural decline
				but exodus: hurricanes, economic collapse, and austerity have driven a
				generation to seek opportunity on the mainland.
			</p>
			<p>
				Census projections suggest the island could fall below <span class="stat">2.6 million</span>
				by 2040. Each departure removes not just a resident but a voter, a taxpayer,
				a voice in the democratic process. The feedback loop is vicious: fewer people
				means less federal funding, worse services, and more reasons to leave.
			</p>
			<p>
				Compare this to Florida, which gained 2.7 million residents in the same period.
				Many of those new Floridians are former Puerto Ricans who can now vote for
				President for the first time.
			</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>The Invisible Emigration</h3>
			<p>
				The people who leave aren't random. They're disproportionately young,
				educated, and working-age. A 28-year-old engineer who moves to Texas
				takes their productivity, their tax payments, and their potential
				40 years of civic participation with them.
			</p>
			<p>
				Those who stay tend to be older, with deeper roots or fewer options.
				Retirees on fixed incomes, older homeowners who can't sell,
				public employees with pensions tied to the island. This isn't just
				population decline; it's selective depletion of the workforce and electorate.
			</p>
			<p>
				The result is an accelerating age imbalance. Puerto Rico is becoming
				a retirement community without the tax base to support it.
			</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>The Shrinking Voter Pool</h3>
			<p>
				Registered voters have declined from <span class="stat">2.44 million</span> in
				2004 to <span class="stat">1.99 million</span> in 2024, a loss of nearly
				half a million eligible voters. But the damage runs deeper: actual votes
				cast fell from 1.99 million to 1.22 million over the same period.
			</p>
			<p>
				By 2028, projections suggest Puerto Rico may have fewer than
				<span class="stat">1.85 million</span> registered voters. By 2040,
				perhaps <span class="stat">1.46 million</span>. Elections that once
				mobilized two million people may see barely 800,000 ballots cast.
			</p>
			<p>
				This isn't voter suppression in the traditional sense. It's demographic
				attrition combined with civic disengagement, a slow-motion erosion of
				democratic participation that no single policy can reverse.
			</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>An Aging Electorate</h3>
			<p>
				The median voter in Puerto Rico was 42 years old in 2012. Today,
				they're <span class="stat">51</span>. By 2032, projections suggest
				the median voter could be 56. In a single generation, Puerto Rico's
				electorate has aged by nearly 15 years.
			</p>
			<p>
				Older electorates tend to favor stability, incremental change, and
				preservation of existing benefits. They're less likely to support
				systemic reform or accept short-term pain for long-term gain.
				Traditional parties often benefit from this dynamic.
			</p>
			<p>
				But this aging also concentrates political power among those with
				the strongest ties to the status quo, potentially blocking the very
				changes needed to reverse the island's decline. The young people
				most invested in Puerto Rico's future increasingly vote with their feet.
			</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>The Fragmenting Party System</h3>
			<p>
				For decades, Puerto Rican politics was a two-party affair. PNP and PPD
				together captured 95%+ of gubernatorial votes as recently as 2012.
				The status question dominated: statehood versus commonwealth,
				with independence a distant third.
			</p>
			<p>
				That duopoly is shattered. Third parties grew from <span class="stat">4.7%</span>
				in 2012 to <span class="stat">35%</span> in 2020. Even after partial
				consolidation in 2024, they held nearly 28% of the vote. Movimiento
				Victoria Ciudadana emerged from protests; Proyecto Dignidad represents
				conservative voters alienated by corruption scandals.
			</p>
			<p>
				If current trends continue, 2028 could see a truly three-way race.
				No party would hold a mandate. Coalition governance or minority rule
				would become the norm, fundamentally changing how Puerto Rico is governed.
			</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>The Status Question Persists</h3>
			<p>
				Puerto Rico has held multiple status referendums. In 2012, 61% voted
				for statehood, but turnout was limited. In 2017, 97% chose statehood,
				but only 23% participated due to boycotts. In 2020, 52.5% voted Yes
				on a simple statehood question with broader turnout.
			</p>
			<p>
				Congress has not acted. The Puerto Rico Status Act passed the House
				in 2022 but died in the Senate. Another attempt in 2024 failed to advance.
				Meanwhile, the island remains in limbo: citizens but not voters,
				taxed but not represented, American but not quite.
			</p>
			<p>
				With a shrinking, aging electorate, the mandate question becomes complex.
				Does 52% of a smaller turnout carry more or less weight than 48% of a
				larger one? How many people must vote for statehood before Congress acts?
				The status debate will outlive all of us.
			</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>Four Scenarios for 2040</h3>
			<p>
				<strong>Continuation (60% probability):</strong> Current trends persist.
				Population falls to 2.6 million, the electorate to 1.46 million.
				Third parties stabilize around 30%. Status remains unresolved.
				Puerto Rico muddles through, neither thriving nor collapsing.
			</p>
			<p>
				<strong>Statehood (15%):</strong> Congress acts. Federal investment flows.
				Migration stabilizes or reverses. Puerto Rico gains 5 electoral votes
				and 4 House seats, more representation than several existing states combined.
				Turnout rebounds as citizenship gains meaning.
			</p>
			<p>
				<strong>Accelerated Decline (20%):</strong> Climate disasters or economic
				shocks accelerate exodus. Population falls below 2 million by 2040.
				The electorate becomes geriatric. Infrastructure collapses.
				The island becomes economically unviable as an autonomous unit.
			</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>Why This Data Matters</h3>
			<p>
				This isn't just about statistics. Behind every number is a family deciding
				whether to stay or go, a young person weighing their future, an elder
				watching their community empty out. Elections are how democracies make
				collective decisions. When the electorate shrinks, so does democratic capacity.
			</p>
			<p>
				The data we've explored across these twelve chapters tells a story of
				transformation without resolution. Puerto Rico's political system is
				adapting to forces largely beyond its control: federal policy, global
				economics, climate change, and the accumulated weight of colonial status.
			</p>
			<p>
				Understanding these patterns is the first step to shaping them.
				<span class="highlight">The future is not yet written.</span> But it will
				be written by those who show up to vote, stay on the island, and engage
				with the political process. That's where you come in.
			</p>
		</Step>
	</ScrollySection>

	<!-- Key Metrics Dashboard -->
	<section class="dashboard-section">
		<div class="container">
			<h2>The Numbers at a Glance</h2>
			<div class="metrics-dashboard">
				<div class="metric-card">
					<span class="metric-value">{keyMetrics.population_change_2010_2024?.toFixed(1) || '-14.0'}%</span>
					<span class="metric-label">Population Change<br/>2010-2024</span>
				</div>
				<div class="metric-card">
					<span class="metric-value">{keyMetrics.voter_change_2004_2024?.toFixed(1) || '-18.6'}%</span>
					<span class="metric-label">Registered Voters<br/>2004-2024</span>
				</div>
				<div class="metric-card">
					<span class="metric-value">{keyMetrics.turnout_change_2004_2024?.toFixed(1) || '-24.9'}%</span>
					<span class="metric-label">Turnout Change<br/>2004-2024</span>
				</div>
				<div class="metric-card accent">
					<span class="metric-value">{keyMetrics.third_party_growth_2012_2024?.toFixed(0) || '492'}%</span>
					<span class="metric-label">Third Party Growth<br/>2012-2024</span>
				</div>
			</div>
		</div>
	</section>

	<!-- Scenario Cards -->
	<section class="scenarios-section">
		<div class="container">
			<h2>Scenarios for Puerto Rico's Future</h2>
			<p class="section-intro">
				Based on demographic trends, political dynamics, and external factors,
				we can model four potential futures for Puerto Rico by 2040.
			</p>
			<div class="scenario-cards">
				{#each Object.entries(scenarios) as [key, scenario]}
					<button
						class="scenario-card {selectedScenario === key ? 'selected' : ''}"
						onclick={() => selectedScenario = selectedScenario === key ? null : key}
					>
						<div class="scenario-header">
							<span class="scenario-name">{scenario.name}</span>
							<span class="scenario-probability">{scenario.probability}%</span>
						</div>
						<p class="scenario-description">{scenario.description}</p>
						{#if selectedScenario === key}
							<div class="scenario-details">
								<div class="scenario-stat">
									<span class="stat-value">{(scenario.population_2040 / 1000000).toFixed(1)}M</span>
									<span class="stat-label">Population</span>
								</div>
								<div class="scenario-stat">
									<span class="stat-value">{(scenario.voters_2040 / 1000000).toFixed(1)}M</span>
									<span class="stat-label">Voters</span>
								</div>
								<div class="scenario-stat">
									<span class="stat-value">{scenario.turnout_2040}%</span>
									<span class="stat-label">Turnout</span>
								</div>
								<div class="scenario-assumptions">
									<strong>Key Assumptions:</strong>
									<ul>
										{#each scenario.key_assumptions as assumption}
											<li>{assumption}</li>
										{/each}
									</ul>
								</div>
							</div>
						{/if}
					</button>
				{/each}
			</div>
		</div>
	</section>

	<!-- What If Statehood -->
	<section class="statehood-section">
		<div class="container content">
			<h2>What If: Statehood</h2>
			<p>
				If Puerto Rico became the 51st state, it would immediately become
				a significant player in American politics.
			</p>
			<div class="statehood-grid">
				<div class="statehood-stat">
					<span class="stat-number">{whatIfStatehood.electoral_votes || 5}</span>
					<span class="stat-desc">Electoral Votes</span>
				</div>
				<div class="statehood-stat">
					<span class="stat-number">{whatIfStatehood.house_seats || 4}</span>
					<span class="stat-desc">House Seats</span>
				</div>
				<div class="statehood-stat">
					<span class="stat-number">{whatIfStatehood.senators || 2}</span>
					<span class="stat-desc">Senators</span>
				</div>
			</div>
			<p class="statehood-comparison">
				{whatIfStatehood.comparison || "More than Wyoming, Vermont, Alaska, and DC combined"}
			</p>
		</div>
	</section>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>Thank You for Reading</h2>
			<p>
				This data journalism series was created using open data from the
				Puerto Rico State Elections Commission and the U.S. Census Bureau.
				All code, data, and methodology are available on GitHub for
				verification, reproduction, and extension.
			</p>
			<p>
				Democracy depends on informed citizens. We hope these visualizations
				have illuminated patterns that matter for Puerto Rico's future,
				and inspired you to engage with your community's political process,
				wherever you live.
			</p>

			<div class="cta-section">
				<a href="https://github.com/opendatapr/puerto-rico-elections-platform" class="cta-button" target="_blank" rel="noopener">
					Explore the Data
				</a>
				<a href="{base}/" class="cta-button secondary">
					Back to Start
				</a>
			</div>

			<div class="series-recap">
				<h3>The Complete Series</h3>
				<ol class="chapter-list">
					<li>The Shrinking Electorate</li>
					<li>The Exodus</li>
					<li>Turnout Collapse</li>
					<li>Geography of Power</li>
					<li>La Fortaleza</li>
					<li>78 Battlegrounds</li>
					<li>The Senate</li>
					<li>40 House Races</li>
					<li>The Future (You Are Here)</li>
				</ol>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/house" class="nav-link prev">
					<span class="nav-direction">Previous</span>
					<span class="nav-title">40 House Races</span>
				</a>
				<a href="{base}/" class="nav-link next">
					<span class="nav-direction">Return to</span>
					<span class="nav-title">Home</span>
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
	}

	.viz-note {
		font-size: var(--text-sm);
		color: var(--color-text-light);
		margin-top: var(--space-md);
		font-style: italic;
	}

	/* Dashboard Section */
	.dashboard-section {
		padding: var(--space-3xl) 0;
		background: var(--color-bg);
	}

	.dashboard-section h2 {
		text-align: center;
		margin-bottom: var(--space-xl);
	}

	.metrics-dashboard {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: var(--space-lg);
		max-width: 900px;
		margin: 0 auto;
	}

	.metric-card {
		background: var(--color-surface);
		border-radius: var(--radius-lg);
		padding: var(--space-xl);
		text-align: center;
		border: 1px solid var(--color-border);
		transition: transform var(--transition-base), box-shadow var(--transition-base);
	}

	.metric-card:hover {
		transform: translateY(-4px);
		box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
	}

	.metric-card.accent {
		background: var(--color-accent);
		border-color: var(--color-accent);
	}

	.metric-card.accent .metric-value,
	.metric-card.accent .metric-label {
		color: var(--color-bg);
	}

	.metric-value {
		display: block;
		font-family: var(--font-display);
		font-size: var(--text-3xl);
		font-weight: var(--font-bold);
		color: var(--color-text);
		margin-bottom: var(--space-sm);
	}

	.metric-label {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		line-height: 1.3;
	}

	/* Scenarios Section */
	.scenarios-section {
		padding: var(--space-3xl) 0;
		background: var(--color-surface);
	}

	.scenarios-section h2 {
		text-align: center;
		margin-bottom: var(--space-md);
	}

	.section-intro {
		text-align: center;
		max-width: 600px;
		margin: 0 auto var(--space-2xl);
		color: var(--color-text-muted);
	}

	.scenario-cards {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: var(--space-lg);
		max-width: 900px;
		margin: 0 auto;
	}

	.scenario-card {
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-lg);
		text-align: left;
		cursor: pointer;
		transition: all var(--transition-base);
	}

	.scenario-card:hover {
		border-color: var(--color-accent);
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
	}

	.scenario-card.selected {
		border-color: var(--color-accent);
		background: var(--color-surface-elevated);
	}

	.scenario-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--space-sm);
	}

	.scenario-name {
		font-family: var(--font-display);
		font-size: var(--text-lg);
		font-weight: var(--font-semibold);
		color: var(--color-text);
	}

	.scenario-probability {
		font-size: var(--text-xl);
		font-weight: var(--font-bold);
		color: var(--color-accent);
	}

	.scenario-description {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin: 0;
	}

	.scenario-details {
		margin-top: var(--space-lg);
		padding-top: var(--space-lg);
		border-top: 1px solid var(--color-border);
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: var(--space-md);
	}

	.scenario-stat {
		text-align: center;
	}

	.scenario-stat .stat-value {
		display: block;
		font-size: var(--text-xl);
		font-weight: var(--font-bold);
		color: var(--color-text);
	}

	.scenario-stat .stat-label {
		font-size: var(--text-xs);
		color: var(--color-text-muted);
	}

	.scenario-assumptions {
		grid-column: 1 / -1;
		margin-top: var(--space-md);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.scenario-assumptions ul {
		margin: var(--space-xs) 0 0;
		padding-left: var(--space-lg);
	}

	.scenario-assumptions li {
		margin: var(--space-xs) 0;
	}

	/* Statehood Section */
	.statehood-section {
		padding: var(--space-3xl) 0;
		background: linear-gradient(135deg, var(--color-surface) 0%, var(--color-bg) 100%);
	}

	.statehood-section h2 {
		margin-bottom: var(--space-lg);
	}

	.statehood-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: var(--space-xl);
		max-width: 500px;
		margin: var(--space-xl) 0;
	}

	.statehood-stat {
		text-align: center;
	}

	.stat-number {
		display: block;
		font-family: var(--font-display);
		font-size: var(--text-4xl);
		font-weight: var(--font-bold);
		color: var(--color-accent);
	}

	.stat-desc {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.statehood-comparison {
		font-style: italic;
		color: var(--color-text-muted);
		margin-top: var(--space-lg);
	}

	/* Conclusion Section */
	.chapter-conclusion {
		padding: var(--space-3xl) 0;
		background: var(--color-surface);
	}

	.cta-section {
		display: flex;
		gap: var(--space-md);
		margin: var(--space-xl) 0;
	}

	.cta-button {
		display: inline-flex;
		align-items: center;
		padding: var(--space-md) var(--space-xl);
		background: var(--color-accent);
		color: var(--color-bg);
		font-weight: var(--font-semibold);
		border-radius: var(--radius-md);
		text-decoration: none;
		transition: all var(--transition-base);
	}

	.cta-button:hover {
		background: var(--color-accent-light);
		transform: translateY(-2px);
	}

	.cta-button.secondary {
		background: var(--color-surface-elevated);
		color: var(--color-text);
	}

	.cta-button.secondary:hover {
		background: var(--color-border-light);
	}

	.series-recap {
		margin: var(--space-2xl) 0;
		padding: var(--space-xl);
		background: var(--color-bg);
		border-radius: var(--radius-lg);
	}

	.series-recap h3 {
		margin-bottom: var(--space-md);
	}

	.chapter-list {
		margin: 0;
		padding-left: var(--space-xl);
		columns: 2;
		column-gap: var(--space-2xl);
	}

	.chapter-list li {
		margin: var(--space-xs) 0;
		color: var(--color-text-muted);
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
		background: var(--color-bg);
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

	/* Responsive */
	@media (max-width: 768px) {
		.metrics-dashboard {
			grid-template-columns: repeat(2, 1fr);
		}

		.scenario-cards {
			grid-template-columns: 1fr;
		}

		.statehood-grid {
			max-width: 100%;
		}

		.chapter-list {
			columns: 1;
		}

		.cta-section {
			flex-direction: column;
		}
	}
</style>
