<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { BarChart, LineChart } from '$lib/components/charts';
	import { CATEGORY_COLORS, PARTY_COLORS } from '$lib/utils/colors';

	const chapterNum = 4;
	const chapterTitle = '50 Years of Asking the Same Question';
	const totalSteps = 12;

	let currentStep = $state(0);
	let loading = $state(true);

	// Plebiscite data types
	interface Plebiscite {
		year: number;
		statehood: number;
		commonwealth: number;
		independence: number;
		freeAssociation?: number;
		noneOfAbove?: number;
		turnout: number;
		totalVotes: number;
		statehoodVotes: number;
		question: string;
		boycott: boolean;
		boycottParty?: string;
		context: string;
		winner: string;
		congressResponse: string;
		ballotOptions: string[];
	}

	interface ChapterData {
		plebiscites: Plebiscite[];
		statusColors: Record<string, string>;
		summary: {
			totalReferendums: number;
			yearsOfDebate: number;
			congressionalActions: number;
		};
	}

	let plebiscites = $state<Plebiscite[]>([]);

	// Status options colors - consistent theming
	let STATUS_COLORS = $state<Record<string, string>>({
		statehood: '#1e4d8c',      // PNP blue
		commonwealth: '#c41e3a',   // PPD red
		independence: '#228b22',   // PIP green
		freeAssociation: '#9b59b6', // Purple
		noneOfAbove: '#6b7280',    // Gray
		blank: '#d4a373'          // Tan
	});

	// Load data from JSON
	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/chapters/plebiscites.json`);
			const data: ChapterData = await response.json();
			plebiscites = data.plebiscites;
			STATUS_COLORS = data.statusColors;
		} catch (err) {
			console.error('Failed to load plebiscites data:', err);
		} finally {
			loading = false;
		}
	});

	let activeYear = $state(1967);
	let activePlebiscite = $derived(plebiscites.find(p => p.year === activeYear) || plebiscites[0]);
	let activeViz = $state<'timeline' | 'results' | 'turnout' | 'ballot'>('timeline');

	// Bar data for results visualization
	let resultsBarData = $derived(() => {
		const p = activePlebiscite;
		const data = [
			{ label: 'Statehood', value: p.statehood, color: STATUS_COLORS.statehood }
		];

		if (p.commonwealth > 0) {
			data.push({ label: 'Commonwealth', value: p.commonwealth, color: STATUS_COLORS.commonwealth });
		}
		if (p.independence > 0) {
			data.push({ label: 'Independence', value: p.independence, color: STATUS_COLORS.independence });
		}
		if (p.freeAssociation && p.freeAssociation > 0) {
			data.push({ label: 'Free Association', value: p.freeAssociation, color: STATUS_COLORS.freeAssociation });
		}
		if (p.noneOfAbove && p.noneOfAbove > 0) {
			data.push({ label: 'None of Above', value: p.noneOfAbove, color: STATUS_COLORS.noneOfAbove });
		}

		return data.sort((a, b) => b.value - a.value);
	});

	// Turnout comparison data
	let turnoutData = $derived(
		plebiscites.map(p => ({
			label: String(p.year),
			value: p.turnout,
			color: p.boycott ? STATUS_COLORS.noneOfAbove : CATEGORY_COLORS[0]
		}))
	);

	// Statehood trend line data
	let statehoodTrendData = $derived([{
		id: 'statehood',
		label: 'Statehood Support',
		color: STATUS_COLORS.statehood,
		data: plebiscites.map(p => ({ x: p.year, y: p.statehood }))
	}]);

	function handleStepEnter(response: { index: number }) {
		currentStep = response.index;
		switch (response.index) {
			case 0:
				activeViz = 'timeline';
				activeYear = 1967;
				break;
			case 1:
				activeViz = 'ballot';
				activeYear = 1967;
				break;
			case 2:
				activeViz = 'results';
				activeYear = 1993;
				break;
			case 3:
				activeViz = 'ballot';
				activeYear = 1998;
				break;
			case 4:
				activeViz = 'results';
				activeYear = 1998;
				break;
			case 5:
				activeViz = 'ballot';
				activeYear = 2012;
				break;
			case 6:
				activeViz = 'results';
				activeYear = 2012;
				break;
			case 7:
				activeViz = 'turnout';
				activeYear = 2017;
				break;
			case 8:
				activeViz = 'results';
				activeYear = 2017;
				break;
			case 9:
				activeViz = 'ballot';
				activeYear = 2020;
				break;
			case 10:
				activeViz = 'results';
				activeYear = 2020;
				break;
			case 11:
				activeViz = 'timeline';
				activeYear = 2020;
				break;
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
				Since 1967, Puerto Rico has held six referendums on its political status.
				Statehood. Commonwealth. Independence. The question never changes.
				Neither does Congress's answer: silence.
			</p>
			<div class="header-stats">
				<div class="stat-box">
					<span class="stat-number">6</span>
					<span class="stat-label">Referendums</span>
				</div>
				<div class="stat-box">
					<span class="stat-number">53</span>
					<span class="stat-label">Years of Debate</span>
				</div>
				<div class="stat-box">
					<span class="stat-number">0</span>
					<span class="stat-label">Congressional Actions</span>
				</div>
			</div>
		</div>
	</header>

	<ScrollySection offset={0.6} onStepEnter={handleStepEnter}>
		{#snippet graphic()}
			<div class="viz-container">
				{#if loading}
					<p class="loading">Loading data...</p>
				{:else if activeViz === 'timeline'}
					<h3 class="viz-title">Six Referendums, Six Decades</h3>
					<div class="timeline-viz">
						{#each plebiscites as p}
							<button
								class="timeline-node"
								class:active={p.year === activeYear}
								class:boycott={p.boycott}
								onclick={() => activeYear = p.year}
							>
								<span class="node-year">{p.year}</span>
								<span class="node-dot"></span>
								<span class="node-result">{p.statehood.toFixed(0)}%</span>
								<span class="node-label">{p.winner}</span>
							</button>
						{/each}
						<div class="timeline-line"></div>
					</div>
					<div class="timeline-legend">
						<span class="legend-item"><span class="dot active"></span> Normal Turnout</span>
						<span class="legend-item"><span class="dot boycott"></span> Boycotted</span>
					</div>
				{:else if activeViz === 'results'}
					<h3 class="viz-title">{activePlebiscite.year} Plebiscite Results</h3>
					<div class="viz-subtitle">
						{activePlebiscite.question} format
						{#if activePlebiscite.boycott}
							<span class="boycott-badge">Boycotted by {activePlebiscite.boycottParty}</span>
						{/if}
					</div>
					<BarChart
						data={resultsBarData()}
						width={420}
						height={280}
						horizontal={true}
						valueFormat={(v) => `${v.toFixed(1)}%`}
					/>
					<div class="result-meta">
						<span class="meta-item">Turnout: <strong>{activePlebiscite.turnout}%</strong></span>
						<span class="meta-item">Total Votes: <strong>{activePlebiscite.totalVotes.toLocaleString()}</strong></span>
					</div>
				{:else if activeViz === 'turnout'}
					<h3 class="viz-title">Turnout Across All Plebiscites</h3>
					<div class="viz-subtitle">Gray bars indicate boycotted elections</div>
					<BarChart
						data={turnoutData}
						width={500}
						height={300}
						horizontal={false}
						valueFormat={(v) => `${v.toFixed(0)}%`}
						highlightLabel={String(activeYear)}
					/>
				{:else if activeViz === 'ballot'}
					<h3 class="viz-title">{activePlebiscite.year} Ballot</h3>
					<div class="ballot-recreation">
						<div class="ballot-header">
							<div class="ballot-seal">PR</div>
							<div class="ballot-title">
								<span class="ballot-office">PLEBISCITO</span>
								<span class="ballot-year">{activePlebiscite.year}</span>
							</div>
						</div>
						<div class="ballot-question">
							{#if activePlebiscite.year === 2020}
								"Should Puerto Rico be admitted immediately into the Union as a State?"
							{:else if activePlebiscite.year === 2012}
								Q1: "Do you agree that Puerto Rico should continue to have its present form of territorial political status?"
							{:else}
								"Vote for your preferred political status option:"
							{/if}
						</div>
						<div class="ballot-options">
							{#each activePlebiscite.ballotOptions as option, i}
								<div class="ballot-option">
									<div class="ballot-checkbox"></div>
									<span class="ballot-option-text">{option}</span>
								</div>
							{/each}
						</div>
						{#if activePlebiscite.year === 2012}
							<div class="ballot-divider"></div>
							<div class="ballot-question">
								Q2: "Which status would you prefer?"
							</div>
							<div class="ballot-options">
								<div class="ballot-option">
									<div class="ballot-checkbox"></div>
									<span class="ballot-option-text">Statehood</span>
								</div>
								<div class="ballot-option">
									<div class="ballot-checkbox"></div>
									<span class="ballot-option-text">Sovereign Free Associated State</span>
								</div>
								<div class="ballot-option">
									<div class="ballot-checkbox"></div>
									<span class="ballot-option-text">Independence</span>
								</div>
							</div>
						{/if}
					</div>
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>The Endless Question</h3>
			<p>
				Puerto Rico's political status has been contested since 1898, when the island became
				a U.S. territory after the Spanish-American War. For over a century, three options
				have dominated the debate: statehood (becoming the 51st state), independence (full
				sovereignty), and commonwealth (the current territorial arrangement).
			</p>
			<p>
				Since 1967, Puerto Rico has held <span class="stat">six</span> official referendums
				on this question. The results vary wildly depending on how the question is asked,
				who boycotts, and what options appear on the ballot.
			</p>
			<p>
				One constant: Congress has never acted on any result.
			</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>1967: The First Vote</h3>
			<p>
				The inaugural plebiscite offered voters three clear choices: statehood, commonwealth,
				or independence. The political context was specific: the Cold War made independence
				seem radical, and the island's economy depended on federal programs.
			</p>
			<p>
				Commonwealth won decisively with <span class="stat">60.4%</span> of the vote.
				Statehood received just 39%. Independence, associated with socialist movements,
				garnered less than 1%.
			</p>
			<p>
				The PPD, which had governed Puerto Rico since 1949 under the commonwealth model,
				claimed vindication. But statehood supporters noted that turnout was just 65.8%,
				lower than typical elections. The question wasn't settled; it was merely deferred.
			</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>1993: Statehood Rising</h3>
			<p>
				Twenty-six years later, the political landscape had shifted. The PNP (pro-statehood)
				had governed for much of the intervening period. Puerto Rico's economy had grown,
				but so had concerns about federal tax benefits that might disappear with statehood.
			</p>
			<p>
				The result was the closest race yet: commonwealth squeaked by with <span class="stat">48.6%</span>,
				while statehood surged to 46.3%. Independence remained marginal at 4.4%.
			</p>
			<p>
				For the first time, the status quo felt precarious. The 2-point margin suggested
				that one more election cycle might tip the balance. Puerto Rico was changing.
			</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>1998: The Boycott Strategy</h3>
			<p>
				The 1998 plebiscite introduced a new element: the boycott. The PPD, unhappy with
				how their preferred option was defined on the ballot, called on supporters to
				vote for "None of the Above" instead of the listed commonwealth option.
			</p>
			<p>
				The ballot itself was unprecedented: five options including "None of the Above."
				This made the vote more a protest than a mandate.
			</p>
			<p>
				The PPD's strategy worked brilliantly. "None of the Above" won with <span class="stat">50.3%</span>,
				while statehood received 46.5%. The result delegitimized the entire exercise.
				Congress could claim there was no clear mandate for any change.
			</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>A Meaningless Majority</h3>
			<p>
				The 1998 result established a template that would haunt future plebiscites:
				a boycott could invalidate even a strong showing by one side.
			</p>
			<p>
				Statehood supporters pointed out that 46.5% voted for their option, while
				only 0.1% voted for the commonwealth option on the ballot. But the
				<span class="highlight">"None of the Above"</span> vote absorbed most commonwealth
				supporters, making the result uninterpretable.
			</p>
			<p>
				The lesson was clear: how the question is asked matters as much as the answer.
			</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>2012: The Two-Question Gambit</h3>
			<p>
				After a 14-year hiatus, Governor Luis Fortuño (PNP) called another plebiscite.
				This time, the ballot used a clever two-question format designed to separate
				satisfaction with the status quo from preference among alternatives.
			</p>
			<p>
				Question 1: Do you want to maintain the current territorial status?
			</p>
			<p>
				Question 2: Which non-territorial option do you prefer: statehood, sovereignty
				in free association, or independence?
			</p>
			<p>
				The format meant that even those who voted "No" on Q1 could choose statehood on Q2.
				Critics called it a <span class="highlight">rigged ballot</span>.
			</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>The Blank Ballot Controversy</h3>
			<p>
				The results looked like a statehood landslide: <span class="stat">61.2%</span>
				chose statehood on Question 2. But there was a catch.
			</p>
			<p>
				Over <span class="highlight">500,000 voters</span> left Question 2 blank. They
				voted on Question 1, but refused to choose among alternatives they found
				inadequate. When you counted blank ballots as votes against statehood,
				the majority evaporated.
			</p>
			<p>
				Congress responded by... requesting funds for a future binding referendum.
				That referendum never happened. The pattern held: vote, then wait for
				nothing.
			</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>2017: The Ghost Plebiscite</h3>
			<p>
				The 2017 plebiscite will be remembered for one number: <span class="stat">23%</span>.
				That was the turnout, the lowest in Puerto Rico's electoral history.
			</p>
			<p>
				Both the PPD (pro-commonwealth) and PIP (pro-independence) called for a boycott.
				They objected to ballot design, timing, and the lack of federal commitment to
				honor the results.
			</p>
			<p>
				The boycott was devastatingly effective. In a normal election, Puerto Rico sees
				turnout of 70-80%. This time, barely one in four registered voters participated.
			</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>97% of Almost Nobody</h3>
			<p>
				Among those who did vote, statehood won overwhelmingly: <span class="stat">97.2%</span>.
				It was the highest percentage ever recorded for any status option.
			</p>
			<p>
				It was also the most meaningless. When three-quarters of the electorate stays
				home, a "win" carries no democratic legitimacy. Congress dismissed the results
				immediately.
			</p>
			<p>
				The 2017 plebiscite became a cautionary tale: you can't achieve political
				change through a vote your opponents refuse to recognize.
			</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>2020: The Simple Question</h3>
			<p>
				After the farce of 2017, Puerto Rico tried something different. The 2020
				referendum posed the simplest possible question:
			</p>
			<p class="quote">
				"Should Puerto Rico be admitted immediately into the Union as a State?
				<strong>Yes</strong> or <strong>No</strong>."
			</p>
			<p>
				No complex ballot. No multiple options. No room for "None of the Above."
				Just a direct question about statehood, run alongside the general election
				to ensure turnout.
			</p>
		</Step>

		<Step active={currentStep === 10} index={10}>
			<h3>The Narrow Yes</h3>
			<p>
				For the first time, a simple majority voted <span class="stat">Yes</span> on a
				straightforward statehood question. The margin: 52.5% to 47.5%.
			</p>
			<p>
				655,505 Puerto Ricans voted Yes. 592,671 voted No. The difference:
				<span class="highlight">62,834 votes</span>, about 2.5 percentage points.
			</p>
			<p>
				There was no boycott. Turnout (54.7%) was lower than the concurrent gubernatorial
				election, but not dramatically so. For statehood supporters, this was the
				cleanest mandate yet.
			</p>
		</Step>

		<Step active={currentStep === 11} index={11}>
			<h3>The Pattern Holds</h3>
			<p>
				Congress introduced HR 1522, a bill to admit Puerto Rico as a state based on
				the referendum result. It did not pass. The Senate took no action. The
				pattern held.
			</p>
			<p>
				Since 1967, Puerto Rico has asked the same question six times. The answers
				have varied: 39% for statehood, 46%, 47%, 61%, 97%, 52.5%. What hasn't
				varied is the federal response.
			</p>
			<p>
				After 53 years of asking, Puerto Rico is still waiting for an answer.
			</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>The Numbers Don't Lie, But They Don't Decide</h2>

			<div class="summary-table">
				<div class="table-header">
					<span class="col-year">Year</span>
					<span class="col-result">Statehood</span>
					<span class="col-turnout">Turnout</span>
					<span class="col-note">Note</span>
					<span class="col-congress">Congress</span>
				</div>
				{#each plebiscites as p}
					<div class="table-row" class:boycott={p.boycott}>
						<span class="col-year">{p.year}</span>
						<span class="col-result">{p.statehood.toFixed(1)}%</span>
						<span class="col-turnout">{p.turnout}%</span>
						<span class="col-note">{p.context}</span>
						<span class="col-congress">{p.congressResponse}</span>
					</div>
				{/each}
			</div>

			<div class="key-takeaways">
				<h3>Key Takeaways</h3>
				<ul>
					<li>
						<strong>Format matters:</strong> Results swing wildly based on ballot design.
						The 2012 two-question format yielded 61% for statehood; the 2020 Yes/No format
						yielded 52.5%.
					</li>
					<li>
						<strong>Boycotts work:</strong> When the PPD boycotted in 1998 and 2017,
						they effectively nullified the results. A referendum without broad
						participation has no legitimacy.
					</li>
					<li>
						<strong>Trend is upward:</strong> Statehood support has grown from 39% (1967)
						to 52.5% (2020). Generational change and economic crisis have shifted
						preferences.
					</li>
					<li>
						<strong>Congress decides:</strong> Ultimately, no referendum is binding.
						Puerto Rico can vote however it wants; admission requires an act of Congress.
					</li>
				</ul>
			</div>

			<div class="sources">
				<h3>Sources</h3>
				<ul>
					<li><a href="https://ww2.ceepur.org/Home/EventosElectorales" target="_blank" rel="noopener">Comision Estatal de Elecciones de Puerto Rico (CEE)</a> - Official plebiscite results 1967-2020</li>
					<li><a href="https://www.gao.gov/" target="_blank" rel="noopener">U.S. Government Accountability Office</a> - "Puerto Rico: Information on How Statehood Would Potentially Affect Selected Federal Programs and Revenue Sources" (2014)</li>
					<li><a href="https://crsreports.congress.gov/" target="_blank" rel="noopener">Congressional Research Service</a> - "Political Status of Puerto Rico: Options for Congress" (2017)</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/shrinking" class="nav-link prev">
					<span class="nav-direction">Previous</span>
					<span class="nav-title">The Shrinking Electorate</span>
				</a>
				<a href="{base}/chapters/referendum-2020" class="nav-link next">
					<span class="nav-direction">Next Chapter</span>
					<span class="nav-title">The 52.5% Threshold</span>
				</a>
			</nav>
		</div>
	</section>
</article>

<style>
	.loading {
		color: var(--color-text-muted);
		font-style: italic;
	}

	.chapter-header {
		min-height: 70vh;
		display: flex;
		align-items: center;
		padding: var(--space-3xl) 0;
		background: radial-gradient(ellipse at 50% 100%, var(--color-surface) 0%, var(--color-bg) 70%);
	}

	.header-stats {
		display: flex;
		gap: var(--space-xl);
		margin-top: var(--space-2xl);
	}

	.stat-box {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: var(--space-lg);
		background: var(--color-surface-elevated);
		border-radius: var(--radius-lg);
		min-width: 100px;
	}

	.stat-number {
		font-family: var(--font-display);
		font-size: var(--text-4xl);
		font-weight: var(--font-bold);
		color: var(--color-accent);
		line-height: 1;
	}

	.stat-label {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin-top: var(--space-xs);
	}

	.viz-container {
		width: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: var(--space-lg);
	}

	.viz-title {
		font-size: var(--text-xl);
		font-weight: var(--font-semibold);
		color: var(--color-text);
		margin-bottom: var(--space-xs);
	}

	.viz-subtitle {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin-bottom: var(--space-lg);
		display: flex;
		align-items: center;
		gap: var(--space-sm);
	}

	.boycott-badge {
		background: #c41e3a;
		color: white;
		padding: var(--space-xs) var(--space-sm);
		border-radius: var(--radius-sm);
		font-size: var(--text-xs);
		font-weight: var(--font-medium);
	}

	/* Timeline Visualization */
	.timeline-viz {
		position: relative;
		display: flex;
		justify-content: space-between;
		align-items: center;
		width: 100%;
		max-width: 600px;
		padding: var(--space-xl) 0;
	}

	.timeline-line {
		position: absolute;
		top: 50%;
		left: 0;
		right: 0;
		height: 2px;
		background: var(--color-border);
		z-index: 0;
	}

	.timeline-node {
		position: relative;
		z-index: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-xs);
		background: none;
		border: none;
		cursor: pointer;
		padding: var(--space-sm);
		transition: transform var(--transition-fast);
	}

	.timeline-node:hover {
		transform: scale(1.1);
	}

	.timeline-node .node-year {
		font-family: var(--font-display);
		font-size: var(--text-sm);
		font-weight: var(--font-bold);
		color: var(--color-text-muted);
	}

	.timeline-node .node-dot {
		width: 16px;
		height: 16px;
		border-radius: 50%;
		background: var(--color-accent);
		border: 3px solid var(--color-bg);
		box-shadow: 0 0 0 2px var(--color-accent);
	}

	.timeline-node.boycott .node-dot {
		background: #6b7280;
		box-shadow: 0 0 0 2px #6b7280;
	}

	.timeline-node.active .node-dot {
		width: 20px;
		height: 20px;
		box-shadow: 0 0 0 3px var(--color-accent);
	}

	.timeline-node .node-result {
		font-size: var(--text-lg);
		font-weight: var(--font-bold);
		color: var(--color-text);
	}

	.timeline-node .node-label {
		font-size: var(--text-xs);
		color: var(--color-text-muted);
		white-space: nowrap;
	}

	.timeline-legend {
		display: flex;
		gap: var(--space-lg);
		margin-top: var(--space-lg);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
	}

	.legend-item .dot {
		width: 10px;
		height: 10px;
		border-radius: 50%;
	}

	.legend-item .dot.active {
		background: var(--color-accent);
	}

	.legend-item .dot.boycott {
		background: #6b7280;
	}

	/* Ballot Recreation */
	.ballot-recreation {
		background: #fffef8;
		border: 2px solid #1a1a1a;
		border-radius: var(--radius-md);
		padding: var(--space-xl);
		max-width: 400px;
		width: 100%;
		box-shadow: var(--shadow-lg);
	}

	.ballot-header {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		margin-bottom: var(--space-lg);
		padding-bottom: var(--space-md);
		border-bottom: 2px solid #1a1a1a;
	}

	.ballot-seal {
		width: 48px;
		height: 48px;
		border: 2px solid #1a1a1a;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-family: var(--font-display);
		font-weight: var(--font-bold);
		font-size: var(--text-lg);
		color: #1a1a1a;
	}

	.ballot-title {
		display: flex;
		flex-direction: column;
	}

	.ballot-office {
		font-family: var(--font-display);
		font-size: var(--text-lg);
		font-weight: var(--font-bold);
		color: #1a1a1a;
		letter-spacing: 0.1em;
	}

	.ballot-year {
		font-size: var(--text-sm);
		color: #666;
	}

	.ballot-question {
		font-size: var(--text-sm);
		color: #1a1a1a;
		margin-bottom: var(--space-md);
		font-style: italic;
		line-height: 1.5;
	}

	.ballot-options {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	.ballot-option {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-sm);
		background: #f5f5f0;
		border-radius: var(--radius-sm);
	}

	.ballot-checkbox {
		width: 18px;
		height: 18px;
		border: 2px solid #1a1a1a;
		border-radius: 2px;
		flex-shrink: 0;
	}

	.ballot-option-text {
		font-size: var(--text-sm);
		color: #1a1a1a;
	}

	.ballot-divider {
		height: 1px;
		background: #ccc;
		margin: var(--space-lg) 0;
	}

	/* Result metadata */
	.result-meta {
		display: flex;
		gap: var(--space-xl);
		margin-top: var(--space-lg);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.meta-item strong {
		color: var(--color-text);
	}

	/* Quote styling */
	.quote {
		font-size: var(--text-lg);
		font-style: italic;
		color: var(--color-text);
		background: var(--color-surface-elevated);
		padding: var(--space-md) var(--space-lg);
		border-left: 4px solid var(--color-accent);
		border-radius: 0 var(--radius-md) var(--radius-md) 0;
		margin: var(--space-md) 0;
	}

	/* Chapter Conclusion */
	.chapter-conclusion {
		padding: var(--space-3xl) 0;
		background: var(--color-surface);
	}

	.summary-table {
		margin: var(--space-xl) 0;
		background: var(--color-surface-elevated);
		border-radius: var(--radius-lg);
		overflow: hidden;
	}

	.table-header {
		display: grid;
		grid-template-columns: 80px 100px 90px 1fr 120px;
		gap: var(--space-md);
		padding: var(--space-md);
		background: var(--color-bg);
		font-size: var(--text-sm);
		font-weight: var(--font-semibold);
		color: var(--color-text-muted);
	}

	.table-row {
		display: grid;
		grid-template-columns: 80px 100px 90px 1fr 120px;
		gap: var(--space-md);
		padding: var(--space-md);
		border-top: 1px solid var(--color-border);
		font-size: var(--text-sm);
	}

	.table-row.boycott {
		background: rgba(107, 114, 128, 0.1);
	}

	.col-year {
		font-family: var(--font-display);
		font-weight: var(--font-bold);
		color: var(--color-accent);
	}

	.col-result {
		font-weight: var(--font-semibold);
	}

	.col-turnout {
		color: var(--color-text-muted);
	}

	.col-note {
		color: var(--color-text);
	}

	.col-congress {
		color: var(--color-text-muted);
		font-size: var(--text-xs);
	}

	.key-takeaways {
		margin-top: var(--space-2xl);
	}

	.key-takeaways h3 {
		font-family: var(--font-display);
		font-size: var(--text-xl);
		margin-bottom: var(--space-md);
	}

	.key-takeaways ul {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
		list-style: none;
		padding: 0;
	}

	.key-takeaways li {
		padding: var(--space-md);
		background: var(--color-surface-elevated);
		border-radius: var(--radius-md);
		border-left: 4px solid var(--color-accent);
	}

	.key-takeaways li strong {
		color: var(--color-accent);
	}

	/* Navigation */
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

	/* Sources */
	.sources {
		margin-top: var(--space-2xl);
		padding-top: var(--space-xl);
		border-top: 1px solid var(--color-border);
	}

	.sources h3 {
		font-size: var(--text-sm);
		font-weight: var(--font-semibold);
		color: var(--color-text-muted);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: var(--space-md);
	}

	.sources ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.sources li {
		font-size: var(--text-sm);
		color: var(--color-text-light);
		padding: var(--space-xs) 0;
	}

	.sources li a {
		color: var(--color-accent);
		text-decoration: underline;
		text-underline-offset: 2px;
	}

	.sources li a:hover {
		color: var(--color-accent-light, #e5c46d);
	}

	/* Responsive */
	@media (max-width: 768px) {
		.header-stats {
			flex-direction: column;
			gap: var(--space-md);
		}

		.timeline-viz {
			flex-wrap: wrap;
			justify-content: center;
			gap: var(--space-lg);
		}

		.timeline-line {
			display: none;
		}

		.table-header,
		.table-row {
			grid-template-columns: 60px 70px 60px 1fr;
		}

		.col-congress {
			display: none;
		}
	}
</style>
