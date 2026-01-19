<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { ChoroplethMap } from '$lib/components/maps';
	import { BarChart, LineChart } from '$lib/components/charts';
	import { createLossScale, CATEGORY_COLORS, DIVERGING_COLORS, SEQUENTIAL_LOSS_COLORS } from '$lib/utils/colors';
	import { formatCompact, formatNumber, formatPercent, formatPercentChange } from '$lib/utils/format';

	const chapterNum = 3;
	const chapterTitle = 'The Shrinking Electorate';
	const totalSteps = 10;

	let currentStep = $state(0);
	let activeViz = $state<'line' | 'bar' | 'map' | 'circles' | 'demographic'>('line');
	let mapData = $state(new Map<string, number>());
	let loading = $state(true);

	// Data loaded from API
	interface ElectorateSeries {
		year: number;
		registered_voters: number;
		votes_cast: number;
		turnout_pct: number;
	}

	interface MunicipalityLoss {
		municipality: string;
		votes_2016: number;
		votes_2020: number;
		votes_2024: number;
		loss_total: number;
		loss_pct: number;
		population: number;
	}

	interface RepresentationImpact {
		current_resident_commissioner: number;
		if_state_reps_2004: number;
		if_state_reps_2024: number;
		electoral_college_2004: number;
		electoral_college_2024: number;
		population_loss_since_2004: number;
		disenfranchised_on_mainland: number;
	}

	interface DemographicShift {
		median_voter_age_2012: number;
		median_voter_age_2024: number;
		pct_under_35_2012: number;
		pct_under_35_2024: number;
		pct_over_65_2012: number;
		pct_over_65_2024: number;
	}

	interface ComparisonCircle {
		label: string;
		value: number;
		year: number;
	}

	let electorateSeries = $state<ElectorateSeries[]>([]);
	let municipalityLoss = $state<MunicipalityLoss[]>([]);
	let representationImpact = $state<RepresentationImpact | null>(null);
	let demographicShift = $state<DemographicShift | null>(null);
	let comparisonCircles = $state<ComparisonCircle[]>([]);

	// Load chapter data
	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/chapters/shrinking.json`);
			const data = await response.json();
			electorateSeries = data.electorate_series || [];
			municipalityLoss = data.municipality_vote_loss || [];
			representationImpact = data.representation_impact || null;
			demographicShift = data.demographic_shift || null;
			comparisonCircles = data.comparison_circles || [];
		} catch (err) {
			console.error('Failed to load shrinking data:', err);
		} finally {
			loading = false;
		}
	});

	// Derived data for line chart - registered voters over time
	let registeredVotersSeries = $derived([
		{
			id: 'registered',
			label: 'Registered Voters',
			data: electorateSeries.map(d => ({ x: d.year, y: d.registered_voters })),
			color: CATEGORY_COLORS[0]
		}
	]);

	// Dual series - registered vs votes cast
	let dualSeries = $derived([
		{
			id: 'registered',
			label: 'Registered Voters',
			data: electorateSeries.map(d => ({ x: d.year, y: d.registered_voters })),
			color: CATEGORY_COLORS[0]
		},
		{
			id: 'cast',
			label: 'Votes Cast',
			data: electorateSeries.map(d => ({ x: d.year, y: d.votes_cast })),
			color: CATEGORY_COLORS[3]
		}
	]);

	// Bar chart data - top municipality losses (absolute numbers)
	let topLossesAbsolute = $derived(
		municipalityLoss
			.slice(0, 8)
			.map(d => ({
				label: d.municipality,
				value: Math.abs(d.loss_total),
				color: DIVERGING_COLORS[0]
			}))
	);

	// Bar chart data - top municipality losses (percentage)
	let topLossesPercent = $derived(
		[...municipalityLoss]
			.sort((a, b) => a.loss_pct - b.loss_pct)
			.slice(0, 8)
			.map(d => ({
				label: d.municipality,
				value: Math.abs(d.loss_pct),
				color: DIVERGING_COLORS[1]
			}))
	);

	// Map data - vote loss by municipality
	function getMunicipalityVoteLossMap(): Map<string, number> {
		const map = new Map<string, number>();
		for (const muni of municipalityLoss) {
			map.set(muni.municipality, muni.loss_pct);
		}
		return map;
	}

	// Color scale for vote loss - sequential (light = less loss, dark red = severe loss)
	const voteLossColorScale = createLossScale([-35, -10]);

	// Demographic bar data
	let demographicBars = $derived(
		demographicShift ? [
			{ label: 'Under 35 (2012)', value: demographicShift.pct_under_35_2012, color: CATEGORY_COLORS[0] },
			{ label: 'Under 35 (2024)', value: demographicShift.pct_under_35_2024, color: CATEGORY_COLORS[0] + '80' },
			{ label: 'Over 65 (2012)', value: demographicShift.pct_over_65_2012, color: CATEGORY_COLORS[3] },
			{ label: 'Over 65 (2024)', value: demographicShift.pct_over_65_2024, color: CATEGORY_COLORS[3] + '80' }
		] : []
	);

	// Calculate voter loss statistics
	let voterLoss2004to2024 = $derived(() => {
		if (electorateSeries.length < 2) return 0;
		const first = electorateSeries[0];
		const last = electorateSeries[electorateSeries.length - 1];
		return first.registered_voters - last.registered_voters;
	});

	let voterLossPercent = $derived(() => {
		if (electorateSeries.length < 2) return 0;
		const first = electorateSeries[0];
		const last = electorateSeries[electorateSeries.length - 1];
		return ((last.registered_voters - first.registered_voters) / first.registered_voters) * 100;
	});

	function handleStepEnter(response: { index: number }) {
		currentStep = response.index;

		switch (response.index) {
			case 0:
				activeViz = 'line';
				break;
			case 1:
				activeViz = 'line';
				break;
			case 2:
				activeViz = 'circles';
				break;
			case 3:
				activeViz = 'map';
				mapData = getMunicipalityVoteLossMap();
				break;
			case 4:
				activeViz = 'bar';
				break;
			case 5:
				activeViz = 'demographic';
				break;
			case 6:
				activeViz = 'map';
				mapData = getMunicipalityVoteLossMap();
				break;
			case 7:
				activeViz = 'circles';
				break;
			case 8:
				activeViz = 'line';
				break;
			case 9:
				activeViz = 'bar';
				break;
		}
	}

	// Calculate circle sizes for proportional visualization
	function getCircleRadius(value: number, maxValue: number, maxRadius: number): number {
		return Math.sqrt(value / maxValue) * maxRadius;
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
				Between 2004 and 2024, Puerto Rico's voter rolls shrank by over <span class="stat">{formatCompact(voterLoss2004to2024())}</span>
				registered voters. This isn't just a number - it's a story of vanishing political power,
				an aging electorate, and a democracy losing its people.
			</p>
		</div>
	</header>

	<ScrollySection offset={0.6} onStepEnter={handleStepEnter}>
		{#snippet graphic()}
			<div class="viz-container">
				{#if loading}
					<p class="loading">Loading data...</p>
				{:else if activeViz === 'line'}
					<h3 class="viz-title">
						{currentStep <= 1 ? 'Registered Voters Over Time' : 'Registered vs. Votes Cast'}
					</h3>
					<LineChart
						series={currentStep <= 1 ? registeredVotersSeries : dualSeries}
						width={520}
						height={360}
						xLabel="Election Year"
						yLabel="Voters"
						xFormat={(v) => String(v)}
						yFormat={(v) => formatCompact(v)}
						showArea={true}
						showDots={true}
					/>
					{#if currentStep > 1}
						<div class="legend-inline">
							<span class="legend-item"><span class="swatch" style="background: {CATEGORY_COLORS[0]}"></span> Registered</span>
							<span class="legend-item"><span class="swatch" style="background: {CATEGORY_COLORS[3]}"></span> Votes Cast</span>
						</div>
					{/if}
				{:else if activeViz === 'circles'}
					<h3 class="viz-title">The Shrinking Electorate</h3>
					<div class="circles-container">
						{#each comparisonCircles as circle, i}
							{@const maxValue = comparisonCircles[0]?.value || 1}
							{@const radius = getCircleRadius(circle.value, maxValue, 100)}
							<div class="circle-wrapper" style="animation-delay: {i * 0.15}s">
								<svg width={220} height={220} class="proportional-circle">
									<circle
										cx={110}
										cy={110}
										r={radius}
										fill={CATEGORY_COLORS[i % CATEGORY_COLORS.length]}
										opacity="0.7"
										class="shrinking-circle"
										style="--target-r: {radius}"
									/>
									<text x={110} y={105} text-anchor="middle" class="circle-value">
										{formatCompact(circle.value)}
									</text>
									<text x={110} y={125} text-anchor="middle" class="circle-year">
										{circle.year}
									</text>
								</svg>
								<span class="circle-label">{circle.label}</span>
							</div>
						{/each}
					</div>
				{:else if activeViz === 'map'}
					<h3 class="viz-title">Vote Loss by Municipality (2016-2024)</h3>
					<ChoroplethMap
						data={mapData}
						colorScale={voteLossColorScale}
						tooltipFormat={(name, value) =>
							value !== undefined
								? `${name}: ${value.toFixed(1)}% change`
								: name
						}
					/>
					{#if mapData.size > 0}
						<div class="legend">
							<span class="legend-label">Voter loss</span>
							<div class="legend-scale">
								<span style="background: {voteLossColorScale(-32)}"></span>
								<span style="background: {voteLossColorScale(-22)}"></span>
								<span style="background: {voteLossColorScale(-12)}"></span>
							</div>
							<div class="legend-labels">
								<span>-32%</span>
								<span>-22%</span>
								<span>-12%</span>
							</div>
						</div>
					{/if}
				{:else if activeViz === 'bar'}
					<h3 class="viz-title">
						{currentStep === 4 ? 'Top Voter Losses (Absolute)' : 'Municipalities by Percentage Loss'}
					</h3>
					<BarChart
						data={currentStep === 4 ? topLossesAbsolute : topLossesPercent}
						width={480}
						height={340}
						horizontal={true}
						valueFormat={(v) => currentStep === 4 ? `-${formatCompact(v)}` : `-${v.toFixed(1)}%`}
					/>
				{:else if activeViz === 'demographic'}
					<h3 class="viz-title">Age Composition of Electorate</h3>
					<div class="demographic-grid">
						<div class="demo-section">
							<h4>Young Voters (Under 35)</h4>
							<div class="demo-comparison">
								<div class="demo-bar-container">
									<span class="demo-year">2012</span>
									<div class="demo-bar" style="width: {(demographicShift?.pct_under_35_2012 || 0) * 2}%; background: {CATEGORY_COLORS[0]}">
										<span class="demo-value">{demographicShift?.pct_under_35_2012}%</span>
									</div>
								</div>
								<div class="demo-bar-container">
									<span class="demo-year">2024</span>
									<div class="demo-bar shrink" style="width: {(demographicShift?.pct_under_35_2024 || 0) * 2}%; background: {CATEGORY_COLORS[0]}">
										<span class="demo-value">{demographicShift?.pct_under_35_2024}%</span>
									</div>
								</div>
							</div>
							<p class="demo-change decline">-{((demographicShift?.pct_under_35_2012 || 0) - (demographicShift?.pct_under_35_2024 || 0)).toFixed(1)} pts</p>
						</div>
						<div class="demo-section">
							<h4>Senior Voters (Over 65)</h4>
							<div class="demo-comparison">
								<div class="demo-bar-container">
									<span class="demo-year">2012</span>
									<div class="demo-bar" style="width: {(demographicShift?.pct_over_65_2012 || 0) * 2}%; background: {CATEGORY_COLORS[3]}">
										<span class="demo-value">{demographicShift?.pct_over_65_2012}%</span>
									</div>
								</div>
								<div class="demo-bar-container">
									<span class="demo-year">2024</span>
									<div class="demo-bar grow" style="width: {(demographicShift?.pct_over_65_2024 || 0) * 2}%; background: {CATEGORY_COLORS[3]}">
										<span class="demo-value">{demographicShift?.pct_over_65_2024}%</span>
									</div>
								</div>
							</div>
							<p class="demo-change increase">+{((demographicShift?.pct_over_65_2024 || 0) - (demographicShift?.pct_over_65_2012 || 0)).toFixed(1)} pts</p>
						</div>
						<div class="demo-note">
							<strong>Median voter age:</strong> {demographicShift?.median_voter_age_2012} (2012) to {demographicShift?.median_voter_age_2024} (2024)
						</div>
					</div>
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>The Rolls Are Shrinking</h3>
			<p>
				In 2004, Puerto Rico had <span class="stat">2.44 million</span> registered voters -
				a deeply engaged electorate for an island of 3.8 million people. Voting was a
				civic tradition, a family ritual, a statement of identity.
			</p>
			<p>
				Two decades later, the voter rolls tell a different story. Economic crisis, natural
				disaster, and mass exodus have combined to create an unprecedented contraction in
				the island's democratic base.
			</p>
			<p>
				By 2024, only <span class="stat">1.99 million</span> voters remained registered -
				a loss of nearly half a million in twenty years.
			</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>The Acceleration</h3>
			<p>
				The decline wasn't gradual. From 2004 to 2012, the electorate held relatively steady,
				losing about 60,000 voters over eight years. Then the floor gave way.
			</p>
			<p>
				Between 2012 and 2020, Puerto Rico lost <span class="stat">300,000</span> registered
				voters. Hurricane Maria in 2017 accelerated an already-existing trend, as entire
				families relocated to Florida, Texas, and the Northeast.
			</p>
			<p>
				Those who left were disproportionately working-age adults - the backbone of any
				electorate. They took their votes with them to states where, at least, those
				votes would count for president.
			</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>Visualizing the Loss</h3>
			<p>
				These circles represent the relative size of Puerto Rico's registered electorate
				across two decades. Each one is proportional to the number of registered voters.
			</p>
			<p>
				Notice how each successive circle <span class="highlight">shrinks visibly</span>.
				This isn't just a statistical abstraction - each missing pixel represents real
				people who are no longer part of the island's political community.
			</p>
			<p>
				From the largest circle in 2004 to the smallest in 2024, Puerto Rico has lost
				<span class="stat">{formatPercentChange(voterLossPercent())}</span> of its
				electoral base.
			</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>Geography of Loss</h3>
			<p>
				The voter drain wasn't evenly distributed. This map shows the percentage change
				in votes cast between 2016 and 2024 for each municipality.
			</p>
			<p>
				<span class="highlight">Darker colors</span> indicate steeper declines.
				While every municipality saw losses, some experienced dramatic collapses
				in electoral participation.
			</p>
			<p>
				The pattern reveals two Puerto Ricos: the metro San Juan area, which lost
				voters but maintained some base, and the rural interior, where the
				hemorrhaging was even more severe.
			</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>The Big Five</h3>
			<p>
				In absolute terms, the largest municipalities account for the bulk of voter loss.
				San Juan alone shed nearly <span class="stat">60,000 voters</span> between
				2016 and 2024.
			</p>
			<p>
				These five municipalities - San Juan, Bayamon, Ponce, Carolina, and Caguas -
				together lost over <span class="stat">150,000 voters</span>. That's more
				voters than many U.S. congressional districts contain.
			</p>
			<p>
				But the raw numbers don't tell the whole story. When you look at
				<em>proportional</em> losses, a different picture emerges.
			</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>An Aging Electorate</h3>
			<p>
				Who stayed behind? The data reveals a demographic transformation. Young voters
				left in droves, while older residents - with deeper roots, less mobility, and
				fewer mainland options - remained.
			</p>
			<p>
				In 2012, voters under 35 made up <span class="stat">28.5%</span> of the electorate.
				By 2024, that share had collapsed to just <span class="stat">18.2%</span>.
			</p>
			<p>
				Meanwhile, voters over 65 grew from <span class="stat">18.3%</span> to
				<span class="stat">27.1%</span> of all voters. The median voter aged
				nearly a decade in just twelve years.
			</p>
			<p>
				An older electorate tends to be more conservative, more focused on pensions
				and healthcare, and less concerned with the job creation and education
				issues that might bring young people back.
			</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>The Feedback Loop</h3>
			<p>
				Here's the cruel irony: fewer voters means less political power, which
				means less attention from Washington, which means worse conditions,
				which drives more people to leave.
			</p>
			<p>
				The cycle is self-reinforcing. As the electorate shrinks, so does
				Puerto Rico's ability to advocate for the federal resources and
				policy changes that might reverse the trend.
			</p>
			<p>
				If Puerto Rico were a state, its population would have meant
				<span class="stat">{representationImpact?.if_state_reps_2004 || 6}</span>
				House seats in 2004. Today, it would qualify for only
				<span class="stat">{representationImpact?.if_state_reps_2024 || 4}</span>.
			</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>The Representation Gap</h3>
			<p>
				Puerto Rico's shrinking electorate creates a troubling paradox. The island
				has one non-voting representative in Congress - the Resident Commissioner -
				regardless of whether it has 4 million people or 3 million.
			</p>
			<p>
				Meanwhile, the <span class="stat">5.7 million</span> Puerto Ricans living
				on the mainland can vote for president and are represented by voting
				members of Congress. Their political power grows as the island's shrinks.
			</p>
			<p>
				The result: decisions about Puerto Rico's future are increasingly made by
				people who don't live there, while those who remain have diminishing voice
				in their own governance.
			</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>Registered vs. Participating</h3>
			<p>
				The gap between registered voters and actual votes cast tells another
				troubling story. Even among those who remain registered, participation
				has declined.
			</p>
			<p>
				In 2004, <span class="stat">81.5%</span> of registered voters cast ballots.
				By 2024, that figure had dropped to <span class="stat">61.2%</span>.
			</p>
			<p>
				The gap between the two lines represents growing disengagement - voters
				who haven't left the island but have left the political process.
				Disillusionment, not just emigration, is thinning the electorate.
			</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>What Comes Next?</h3>
			<p>
				The trends show no sign of reversing. Every projection suggests Puerto Rico's
				population will continue to decline through at least 2050, and the
				electorate will shrink with it.
			</p>
			<p>
				For democracy to thrive, it needs participants. Puerto Rico faces a
				fundamental question: how does a democracy function when its people
				are leaving?
			</p>
			<p>
				The answer will depend on whether the island can break the feedback
				loop - creating conditions that make young Puerto Ricans want to stay,
				and giving those who remain a reason to believe their vote matters.
			</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>The Electoral Arithmetic</h2>
			<div class="stat-grid">
				<div class="stat-card">
					<span class="stat-value">-{formatCompact(voterLoss2004to2024())}</span>
					<span class="stat-label">Registered voters lost since 2004</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">{formatPercentChange(voterLossPercent())}</span>
					<span class="stat-label">Change in electoral base</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">+9 yrs</span>
					<span class="stat-label">Increase in median voter age</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">5</span>
					<span class="stat-label">Municipalities with 50%+ of voter loss</span>
				</div>
			</div>

			<div class="conclusion-text">
				<h3>Breaking the Cycle</h3>
				<p>
					Puerto Rico's shrinking electorate is not inevitable - it's the result of
					policy choices, economic conditions, and colonial status that could be
					changed. But reversing these trends requires understanding their depth.
				</p>
				<p>
					In the next chapter, we examine how these demographic shifts have
					reshaped the island's political battles over status - the plebiscites
					that ask whether Puerto Rico should become a state, gain independence,
					or maintain its current relationship with the United States.
				</p>
			</div>

			<div class="sources">
				<h3>Sources</h3>
				<ul>
					<li><a href="https://ww2.ceepur.org/Home/EventosElectorales" target="_blank" rel="noopener">Comision Estatal de Elecciones de Puerto Rico (CEE)</a> - Voter registration statistics 2000-2024</li>
					<li>Puerto Rico Office of the Comptroller - Electoral participation reports</li>
					<li><a href="https://www.census.gov/programs-surveys/popest.html" target="_blank" rel="noopener">U.S. Census Bureau</a> - Population estimates and projections for Puerto Rico</li>
					<li>Puerto Rico Institute of Statistics - Demographic trends analysis</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/turnout" class="nav-link prev">
					<span class="nav-direction">Previous</span>
					<span class="nav-title">Democracy Under Strain</span>
				</a>
				<a href="{base}/chapters/plebiscites" class="nav-link next">
					<span class="nav-direction">Next Chapter</span>
					<span class="nav-title">One Question, Two Decades</span>
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

	/* Legend styles */
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

	.legend-inline {
		display: flex;
		gap: var(--space-lg);
		margin-top: var(--space-md);
	}

	.legend-inline .legend-item {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.legend-inline .swatch {
		width: 12px;
		height: 12px;
		border-radius: var(--radius-sm);
	}

	/* Proportional circles visualization */
	.circles-container {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: var(--space-md);
		max-width: 500px;
	}

	.circle-wrapper {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-xs);
		animation: fadeIn 0.5s ease-out forwards;
		opacity: 0;
	}

	@keyframes fadeIn {
		to {
			opacity: 1;
		}
	}

	.proportional-circle {
		filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.15));
	}

	.shrinking-circle {
		transition: r 0.8s ease-out;
	}

	.circle-value {
		font-family: var(--font-display);
		font-size: var(--text-lg);
		font-weight: var(--font-bold);
		fill: var(--color-bg);
	}

	.circle-year {
		font-size: var(--text-sm);
		fill: var(--color-bg);
		opacity: 0.9;
	}

	.circle-label {
		font-size: var(--text-xs);
		color: var(--color-text-muted);
		text-align: center;
		max-width: 100px;
	}

	/* Demographic visualization */
	.demographic-grid {
		width: 100%;
		max-width: 450px;
		display: flex;
		flex-direction: column;
		gap: var(--space-xl);
	}

	.demo-section h4 {
		font-size: var(--text-sm);
		font-weight: var(--font-semibold);
		color: var(--color-text);
		margin-bottom: var(--space-sm);
	}

	.demo-comparison {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	.demo-bar-container {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
	}

	.demo-year {
		font-size: var(--text-xs);
		color: var(--color-text-muted);
		width: 40px;
		flex-shrink: 0;
	}

	.demo-bar {
		height: 28px;
		border-radius: var(--radius-sm);
		display: flex;
		align-items: center;
		justify-content: flex-end;
		padding-right: var(--space-sm);
		min-width: 50px;
		transition: width 0.8s ease-out;
	}

	.demo-bar.shrink {
		animation: shrinkBar 1s ease-out;
	}

	.demo-bar.grow {
		animation: growBar 1s ease-out;
	}

	@keyframes shrinkBar {
		from {
			width: 57%;
		}
	}

	@keyframes growBar {
		from {
			width: 36.6%;
		}
	}

	.demo-value {
		font-size: var(--text-sm);
		font-weight: var(--font-semibold);
		color: var(--color-bg);
	}

	.demo-change {
		font-size: var(--text-sm);
		font-weight: var(--font-bold);
		margin-top: var(--space-xs);
		text-align: right;
	}

	.demo-change.decline {
		color: var(--color-danger, #c9695a);
	}

	.demo-change.increase {
		color: var(--color-warning, #d4a373);
	}

	.demo-note {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		padding: var(--space-md);
		background: var(--color-surface);
		border-radius: var(--radius-md);
		text-align: center;
	}

	/* Chapter conclusion */
	.chapter-conclusion {
		padding: var(--space-3xl) 0;
		background: var(--color-surface);
	}

	.stat-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
		gap: var(--space-lg);
		margin: var(--space-xl) 0;
	}

	.stat-card {
		background: var(--color-surface-elevated);
		border-radius: var(--radius-lg);
		padding: var(--space-lg);
		text-align: center;
	}

	.stat-card .stat-value {
		display: block;
		font-family: var(--font-display);
		font-size: var(--text-3xl);
		font-weight: var(--font-bold);
		color: var(--color-accent);
		margin-bottom: var(--space-sm);
	}

	.stat-card .stat-label {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.conclusion-text {
		margin: var(--space-2xl) 0;
		padding: var(--space-xl);
		background: var(--color-bg);
		border-radius: var(--radius-lg);
		border-left: 4px solid var(--color-accent);
	}

	.conclusion-text h3 {
		margin-bottom: var(--space-md);
		color: var(--color-text);
	}

	.conclusion-text p {
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
	}

	.conclusion-text p:last-child {
		margin-bottom: 0;
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

	/* Sources section */
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

	.sources li a {
		color: var(--color-accent);
		text-decoration: underline;
		text-underline-offset: 2px;
	}

	.sources li a:hover {
		color: var(--color-accent-light, #e5c46d);
	}

	/* Responsive adjustments */
	@media (max-width: 768px) {
		.circles-container {
			flex-direction: column;
		}

		.stat-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}
</style>
