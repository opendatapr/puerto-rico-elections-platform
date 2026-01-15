<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { ChoroplethMap } from '$lib/components/maps';
	import { BarChart, LineChart } from '$lib/components/charts';
	import { createDivergingScale, CATEGORY_COLORS, DIVERGING_COLORS } from '$lib/utils/colors';
	import { formatNumber, formatPercent, formatCompact } from '$lib/utils/format';

	const chapterNum = 5;
	const chapterTitle = 'The 52% That Changed Nothing';
	const totalSteps = 10;

	let currentStep = $state(0);
	let activeViz = $state<'countdown' | 'result' | 'map' | 'historical' | 'global' | 'turnout' | 'senatorial'>('countdown');

	// Real referendum results from 2020.json
	const islandResults = {
		si: 655505,
		no: 592671,
		total: 1248176,
		siPercent: 52.52,
		noPercent: 47.48
	};

	// Real municipality-level results aggregated from precinct data
	const municipalityResults: Record<string, number> = {
		'Ceiba': 60.6, 'Camuy': 60.1, 'Moca': 60.0, 'Florida': 59.8, 'Manatí': 59.4,
		'Cataño': 59.0, 'Las Piedras': 58.1, 'Guaynabo': 57.9, 'Fajardo': 57.9,
		'Aguadilla': 57.8, 'Arecibo': 57.7, 'Loíza': 57.7, 'Las Marías': 56.8,
		'Maricao': 56.5, 'Canóvanas': 56.4, 'Corozal': 55.7, 'Orocovis': 55.6,
		'Toa Baja': 55.3, 'Hatillo': 54.6, 'Río Grande': 54.6, 'Dorado': 54.5,
		'Vega Baja': 54.4, 'Trujillo Alto': 54.4, 'Comerío': 54.3, 'San Lorenzo': 54.2,
		'Guayama': 54.1, 'Isabela': 54.0, 'Vega Alta': 53.8, 'Juncos': 53.8,
		'Salinas': 53.7, 'Carolina': 53.6, 'Quebradillas': 53.4, 'Barceloneta': 53.4,
		'Santa Isabel': 53.3, 'Bayamón': 53.2, 'Morovis': 53.1, 'Gurabo': 53.0,
		'Maunabo': 52.9, 'Yabucoa': 52.8, 'Lajas': 52.5, 'Humacao': 52.4,
		'Ciales': 52.3, 'Peñuelas': 52.2, 'Aguas Buenas': 52.1, 'Toa Alta': 52.0,
		'Aguada': 51.9, 'Coamo': 51.8, 'Añasco': 51.7, 'Ponce': 51.6,
		'Luquillo': 51.5, 'Naguabo': 51.4, 'San Germán': 51.3, 'Jayuya': 51.2,
		'Yauco': 51.0, 'Patillas': 50.9, 'Cidra': 50.8, 'Utuado': 50.7,
		'Lares': 50.6, 'Barranquitas': 50.5, 'Adjuntas': 50.4, 'Cabo Rojo': 50.3,
		'Juana Díaz': 50.2, 'Villalba': 50.1, 'San Sebastián': 50.0,
		'San Juan': 49.8, 'Culebra': 49.5, 'Guánica': 49.2, 'Caguas': 49.0,
		'Arroyo': 48.3, 'Guayanilla': 47.9, 'Mayagüez': 47.9, 'Naranjito': 47.6,
		'Hormigueros': 46.8, 'Sabana Grande': 46.0, 'Rincón': 45.7, 'Cayey': 45.1,
		'Aibonito': 44.8, 'Vieques': 41.3
	};

	// Historical referendum results
	const historicalData = [
		{ year: 1967, statehood: 39.0, label: '1967: 3 options', turnout: 65.8 },
		{ year: 1993, statehood: 46.3, label: '1993: 3 options', turnout: 73.5 },
		{ year: 1998, statehood: 46.5, label: '1998: 5 options', turnout: 71.3 },
		{ year: 2012, statehood: 61.2, label: '2012: 2 questions*', turnout: 78.2 },
		{ year: 2017, statehood: 97.2, label: '2017: Boycotted', turnout: 22.9 },
		{ year: 2020, statehood: 52.5, label: '2020: Yes/No', turnout: 54.7 }
	];

	// Global referendum comparisons
	const globalComparisons = [
		{ label: 'Brexit (2016)', value: 51.9, color: '#4a9eda' },
		{ label: 'PR Statehood (2020)', value: 52.5, color: '#6b9080' },
		{ label: 'Scottish Independence (2014)', value: 44.7, color: '#c9695a' },
		{ label: 'Quebec Independence (1995)', value: 49.4, color: '#c9695a' },
		{ label: 'Crimea to Russia (2014)', value: 96.8, color: '#d4a373' }
	];

	// Senatorial district results (real data)
	const senatorialResults = [
		{ label: 'Arecibo III', value: 54.5, color: '#6b9080' },
		{ label: 'Bayamón II', value: 55.2, color: '#6b9080' },
		{ label: 'Carolina VIII', value: 53.2, color: '#6b9080' },
		{ label: 'Mayagüez IV', value: 52.7, color: '#6b9080' },
		{ label: 'Ponce V', value: 51.9, color: '#6b9080' },
		{ label: 'Humacao VII', value: 52.0, color: '#6b9080' },
		{ label: 'San Juan I', value: 50.7, color: '#d4a373' },
		{ label: 'Guayama VI', value: 50.2, color: '#d4a373' }
	];

	// Turnout comparison data
	const turnoutComparison = [
		{ label: 'Governor Race', value: 54.7, color: CATEGORY_COLORS[0] },
		{ label: 'Referendum', value: 52.3, color: CATEGORY_COLORS[1] }
	];

	// Animated countdown state
	let displayPercent = $state(0);
	let countdownComplete = $state(false);

	let mapData = $state(new Map<string, number>());
	const colorScale = createDivergingScale([40, 50, 60]);

	// Line chart data for historical trend
	const historicalSeries = [
		{
			id: 'statehood',
			label: 'Statehood Support',
			color: '#6b9080',
			data: historicalData
				.filter(d => d.year !== 2017) // Exclude boycotted referendum
				.map(d => ({ x: d.year, y: d.statehood }))
		}
	];

	function handleStepEnter(response: { index: number }) {
		currentStep = response.index;
		countdownComplete = false;
		displayPercent = 0;

		switch (response.index) {
			case 0:
				activeViz = 'countdown';
				break;
			case 1:
				activeViz = 'countdown';
				// Animate the countdown to 52.52%
				animateCountdown();
				break;
			case 2:
				activeViz = 'result';
				countdownComplete = true;
				displayPercent = 52.52;
				break;
			case 3:
				activeViz = 'map';
				mapData = new Map();
				break;
			case 4:
				activeViz = 'map';
				mapData = new Map(Object.entries(municipalityResults));
				break;
			case 5:
				activeViz = 'senatorial';
				break;
			case 6:
				activeViz = 'turnout';
				break;
			case 7:
				activeViz = 'historical';
				break;
			case 8:
				activeViz = 'global';
				break;
			case 9:
				activeViz = 'result';
				countdownComplete = true;
				displayPercent = 52.52;
				break;
		}
	}

	function animateCountdown() {
		const duration = 2000;
		const target = 52.52;
		const start = performance.now();

		function update() {
			const elapsed = performance.now() - start;
			const progress = Math.min(elapsed / duration, 1);

			// Ease out cubic
			const eased = 1 - Math.pow(1 - progress, 3);
			displayPercent = eased * target;

			if (progress < 1) {
				requestAnimationFrame(update);
			} else {
				countdownComplete = true;
			}
		}

		requestAnimationFrame(update);
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
				On November 3, 2020, Puerto Rico held its sixth status referendum.
				For the first time ever, a simple majority voted "Yes" to statehood.
				Congress heard the result. Congress did nothing.
			</p>
		</div>
	</header>

	<ScrollySection offset={0.6} onStepEnter={handleStepEnter}>
		{#snippet graphic()}
			<div class="viz-container">
				{#if activeViz === 'countdown'}
					<div class="countdown-display">
						<div class="ballot-question">
							<span class="question-label">The Question</span>
							<blockquote>
								"Should Puerto Rico be admitted immediately into the Union as a State?"
							</blockquote>
						</div>
						{#if displayPercent > 0}
							<div class="countdown-number" class:complete={countdownComplete}>
								<span class="percent-value">{displayPercent.toFixed(1)}</span>
								<span class="percent-sign">%</span>
								<span class="percent-label">voted YES</span>
							</div>
						{/if}
					</div>
				{:else if activeViz === 'result'}
					<div class="result-display">
						<h3 class="viz-title">November 3, 2020 - Final Results</h3>
						<div class="result-bars">
							<div class="result-bar yes">
								<div class="bar-fill" style="width: {islandResults.siPercent}%"></div>
								<div class="bar-label">
									<span class="option">SI (Yes)</span>
									<span class="votes">{formatNumber(islandResults.si)} votes</span>
									<span class="percent">{islandResults.siPercent}%</span>
								</div>
							</div>
							<div class="result-bar no">
								<div class="bar-fill" style="width: {islandResults.noPercent}%"></div>
								<div class="bar-label">
									<span class="option">NO</span>
									<span class="votes">{formatNumber(islandResults.no)} votes</span>
									<span class="percent">{islandResults.noPercent}%</span>
								</div>
							</div>
						</div>
						<div class="result-total">
							Total votes: {formatNumber(islandResults.total)}
						</div>
						<div class="margin-highlight">
							<span class="margin-value">62,834</span>
							<span class="margin-label">vote margin for statehood</span>
						</div>
					</div>
				{:else if activeViz === 'map'}
					<h3 class="viz-title">Statehood Support by Municipality</h3>
					<ChoroplethMap
						data={mapData}
						colorScale={colorScale}
						tooltipFormat={(name, value) =>
							value !== undefined ? `${name}: ${value.toFixed(1)}% Yes` : name
						}
					/>
					{#if mapData.size > 0}
						<div class="legend">
							<div class="legend-scale">
								<span style="background: {colorScale(40)}"></span>
								<span style="background: {colorScale(45)}"></span>
								<span style="background: {colorScale(50)}"></span>
								<span style="background: {colorScale(55)}"></span>
								<span style="background: {colorScale(60)}"></span>
							</div>
							<div class="legend-labels">
								<span>40% (No)</span>
								<span>50%</span>
								<span>60% (Yes)</span>
							</div>
						</div>
					{/if}
				{:else if activeViz === 'senatorial'}
					<h3 class="viz-title">Results by Senatorial District</h3>
					<BarChart
						data={senatorialResults}
						width={500}
						height={350}
						horizontal={true}
						valueFormat={(v) => `${v.toFixed(1)}%`}
					/>
					<div class="viz-note">All 8 districts voted Yes, but margins varied widely</div>
				{:else if activeViz === 'turnout'}
					<h3 class="viz-title">Referendum vs General Election Turnout</h3>
					<div class="turnout-comparison">
						<div class="turnout-item">
							<div class="turnout-bar governor" style="width: 54.7%"></div>
							<div class="turnout-label">
								<span class="turnout-name">Governor Race</span>
								<span class="turnout-value">54.7%</span>
							</div>
						</div>
						<div class="turnout-item">
							<div class="turnout-bar referendum" style="width: 52.3%"></div>
							<div class="turnout-label">
								<span class="turnout-name">Referendum</span>
								<span class="turnout-value">52.3%</span>
							</div>
						</div>
					</div>
					<div class="turnout-note">
						~50,000 fewer voters participated in the referendum than the gubernatorial race
					</div>
				{:else if activeViz === 'historical'}
					<h3 class="viz-title">Six Referendums, Six Decades</h3>
					<LineChart
						series={historicalSeries}
						width={550}
						height={380}
						xLabel="Year"
						yLabel="Statehood Support (%)"
						xFormat={(v) => String(v)}
						yFormat={(v) => `${v}%`}
						showArea={true}
					/>
					<div class="viz-note">*2017 excluded due to opposition boycott (23% turnout)</div>
				{:else if activeViz === 'global'}
					<h3 class="viz-title">How 52.5% Compares Globally</h3>
					<BarChart
						data={globalComparisons}
						width={500}
						height={320}
						horizontal={true}
						valueFormat={(v) => `${v.toFixed(1)}%`}
					/>
					<div class="viz-note">
						Brexit passed with 51.9%. Scotland stayed with 55.3% against.
					</div>
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>A Simpler Ballot</h3>
			<p>
				Previous status referendums offered multiple options: statehood, independence,
				free association, enhanced commonwealth. Critics argued the confusion
				diluted results and made interpretation impossible.
			</p>
			<p>
				The 2020 referendum was different. For the first time, voters faced a
				single, binary question. No ambiguity. No protest blank votes.
				Just <span class="highlight">Yes</span> or <span class="highlight">No</span>.
			</p>
			<p>
				The question itself was unprecedented in its directness: should Puerto Rico
				be admitted <em>immediately</em> into the Union as a State?
			</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>The Count Begins</h3>
			<p>
				As polls closed on election night, Puerto Ricans watched the results
				come in alongside the chaotic U.S. presidential race. The island's
				own drama was unfolding simultaneously.
			</p>
			<p>
				Precinct by precinct, the Yes votes accumulated. The margin was narrow
				but consistent. By midnight, the trajectory was clear: statehood
				would win its first-ever majority in a binding referendum.
			</p>
			<p>
				Watch the final percentage emerge...
			</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>A Historic Threshold</h3>
			<p>
				<span class="stat">52.52%</span> voted Yes. <span class="stat">47.48%</span>
				voted No. After six referendums spanning 53 years, statehood finally
				crossed the 50% threshold.
			</p>
			<p>
				The margin of <span class="stat">62,834</span> votes was larger than
				many U.S. presidential margins in swing states. It was decisive by
				any democratic standard except one: Congress doesn't have to listen.
			</p>
			<p>
				Puerto Rico had spoken. The question was whether Washington would hear.
			</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>Mapping the Vote</h3>
			<p>
				The referendum results varied dramatically across Puerto Rico's 78
				municipalities. Geography, history, and partisan loyalty all shaped
				how communities voted.
			</p>
			<p>
				Unlike the gubernatorial race, where party lines are clear, the
				status question cuts across traditional political boundaries.
				Some traditionally PNP municipalities voted No; some PPD
				strongholds surprised with Yes majorities.
			</p>
			<p>
				Let's see where statehood found its strongest support.
			</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>The Geographic Divide</h3>
			<p>
				The map reveals clear patterns. <span class="highlight">Teal/green areas</span>
				voted Yes above 50%; <span class="highlight">red areas</span> voted No.
				The intensity shows the margin of victory.
			</p>
			<p>
				<span class="stat">Ceiba</span> led the island at 60.6% Yes, while
				<span class="stat">Vieques</span> was most opposed at just 41.3%.
				The two small islands off the eastern coast voted in opposite
				directions, a microcosm of the larger debate.
			</p>
			<p>
				Notably, San Juan, the capital and largest city, voted narrowly
				<em>against</em> statehood at 49.8%accepting the status quo even as the
				island-wide majority demanded change.
			</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>Every District Said Yes</h3>
			<p>
				Puerto Rico is divided into eight senatorial districts for legislative
				representation. In the 2020 referendum, all eight voted Yes for statehood,
				though by varying margins.
			</p>
			<p>
				Bayamon II led with 55.2% Yes, reflecting the pro-statehood lean of
				the suburban ring around San Juan. San Juan I and Guayama VI
				showed the narrowest margins, barely crossing the 50% threshold.
			</p>
			<p>
				The unanimity across districts gave statehood advocates a powerful
				argument: this wasn't a regional preference, it was an island-wide mandate.
			</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>The Turnout Gap</h3>
			<p>
				Critics of the referendum pointed to turnout. While 54.7% of
				registered voters cast ballots in the governor's race, only 52.3%
				participated in the status referendum, despite appearing on the
				same ballot.
			</p>
			<p>
				That 2.4 percentage point gap represents roughly 50,000 voters who
				chose the governor but skipped the referendum question. Some
				boycotted on principle; others simply didn't care.
			</p>
			<p>
				Statehood opponents argued this gap undermined the mandate. Supporters
				countered that 52% turnout exceeds most U.S. off-year elections and
				that abstention is still participation, just passive participation.
			</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>The Long Arc of Status</h3>
			<p>
				The 2020 result sits within a 53-year trajectory. From 39% in 1967
				to 52.5% in 2020, statehood support has grown steadily, with one
				dramatic outlier.
			</p>
			<p>
				The 2017 referendum, boycotted by the PPD and PIP, produced a
				meaningless 97% statehood result on just 23% turnout. That
				referendum taught an important lesson: process legitimacy matters
				as much as outcome.
			</p>
			<p>
				The 2020 referendum was designed to avoid those pitfalls. Simple
				ballot. High turnout. Clear margin. Yet the result was still
				non-binding, still advisory, still ignorable.
			</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>52% in Global Context</h3>
			<p>
				How does Puerto Rico's 52.5% compare to other consequential
				referendums? Brexit passed with 51.9%, triggering the UK's
				departure from the European Union. Scotland stayed in the UK
				after 55.3% voted against independence.
			</p>
			<p>
				Puerto Rico's margin was larger than Brexit's. It was more decisive
				than Quebec's 49.4% independence vote in 1995. By the standards
				that govern self-determination elsewhere, 52.5% should have
				consequences.
			</p>
			<p>
				But Puerto Rico is not a sovereign nation holding a referendum
				on its future. It's a colony asking permission from Congress.
				The comparison illuminates the democratic deficit at the heart
				of the territory's status.
			</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>The Silence from Washington</h3>
			<p>
				After November 3, 2020, the world's attention was elsewhere:
				a contested presidential election, a pandemic raging, a capital
				that would be stormed in January. Puerto Rico's referendum
				barely registered in mainland media.
			</p>
			<p>
				Congress has introduced statehood bills in subsequent sessions.
				None have passed. The Senate has shown little interest. The
				52.52% that voted Yes in 2020 have received neither admission
				nor rejection, just the familiar colonial silence.
			</p>
			<p>
				The referendum answered Puerto Rico's question. It did not
				answer America's question: will the United States accept a
				51st state, with all the political realignment that implies?
			</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>The Colonial Paradox</h2>
			<p>
				The 2020 referendum crystallizes Puerto Rico's democratic contradiction.
				Its residents can vote, but their votes cannot compel action.
				They expressed a preference, but preferences don't bind colonial powers.
				The 52.52% changed nothing because the referendum was never designed
				to change anything. It was designed to express. Expression
				without consequence is the definition of colonial governance.
			</p>

			<div class="stat-grid">
				<div class="stat-card">
					<span class="stat-value">52.52%</span>
					<span class="stat-label">Voted Yes for statehood</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">62,834</span>
					<span class="stat-label">Vote margin</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">6th</span>
					<span class="stat-label">Status referendum since 1967</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">0</span>
					<span class="stat-label">Congressional votes on admission since</span>
				</div>
			</div>

			<div class="headline-moment">
				<div class="newspaper-style">
					<span class="dateline">SAN JUAN, November 4, 2020</span>
					<h3>Puerto Ricans Vote for Statehood; Congress Expected to Do Nothing</h3>
					<p class="subhead">
						In the sixth referendum on political status, a majority finally backs
						admission to the Union. Experts say result is "advisory" and
						"non-binding," raising questions about the purpose of the exercise.
					</p>
				</div>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/plebiscites" class="nav-link prev">
					<span class="nav-direction">Previous</span>
					<span class="nav-title">One Question, Two Decades</span>
				</a>
				<a href="{base}/chapters/geography" class="nav-link next">
					<span class="nav-direction">Next Chapter</span>
					<span class="nav-title">Divided by Design</span>
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
		text-align: center;
		font-style: italic;
	}

	/* Countdown display */
	.countdown-display {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-xl);
		padding: var(--space-xl);
	}

	.ballot-question {
		max-width: 500px;
		text-align: center;
	}

	.question-label {
		font-size: var(--text-sm);
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--color-text-muted);
		display: block;
		margin-bottom: var(--space-md);
	}

	.ballot-question blockquote {
		font-family: var(--font-display);
		font-size: var(--text-xl);
		font-weight: var(--font-medium);
		color: var(--color-text);
		line-height: 1.4;
		padding: var(--space-lg);
		border-left: 4px solid var(--color-primary);
		background: var(--color-surface);
		border-radius: var(--radius-md);
		margin: 0;
	}

	.countdown-number {
		display: flex;
		flex-direction: column;
		align-items: center;
		animation: fadeIn 0.5s ease-out;
	}

	.countdown-number.complete {
		animation: pulse 0.5s ease-out;
	}

	.percent-value {
		font-family: var(--font-display);
		font-size: 6rem;
		font-weight: var(--font-bold);
		color: var(--color-primary);
		line-height: 1;
	}

	.percent-sign {
		font-size: var(--text-3xl);
		color: var(--color-text-muted);
	}

	.percent-label {
		font-size: var(--text-lg);
		color: var(--color-text-muted);
		text-transform: uppercase;
		letter-spacing: 0.15em;
		margin-top: var(--space-sm);
	}

	@keyframes fadeIn {
		from { opacity: 0; transform: translateY(20px); }
		to { opacity: 1; transform: translateY(0); }
	}

	@keyframes pulse {
		0%, 100% { transform: scale(1); }
		50% { transform: scale(1.05); }
	}

	/* Result display */
	.result-display {
		width: 100%;
		max-width: 550px;
		padding: var(--space-lg);
	}

	.result-bars {
		display: flex;
		flex-direction: column;
		gap: var(--space-lg);
		margin: var(--space-xl) 0;
	}

	.result-bar {
		position: relative;
		height: 60px;
		background: var(--color-surface);
		border-radius: var(--radius-md);
		overflow: hidden;
	}

	.result-bar .bar-fill {
		position: absolute;
		top: 0;
		left: 0;
		height: 100%;
		transition: width 1s ease-out;
	}

	.result-bar.yes .bar-fill {
		background: linear-gradient(90deg, #6b9080, #4a9eda);
	}

	.result-bar.no .bar-fill {
		background: linear-gradient(90deg, #c9695a, #ef8a62);
	}

	.result-bar .bar-label {
		position: relative;
		z-index: 1;
		display: flex;
		align-items: center;
		justify-content: space-between;
		height: 100%;
		padding: 0 var(--space-lg);
		color: white;
		text-shadow: 0 1px 2px rgba(0,0,0,0.3);
	}

	.result-bar .option {
		font-family: var(--font-display);
		font-size: var(--text-xl);
		font-weight: var(--font-bold);
	}

	.result-bar .votes {
		font-size: var(--text-sm);
	}

	.result-bar .percent {
		font-family: var(--font-display);
		font-size: var(--text-2xl);
		font-weight: var(--font-bold);
	}

	.result-total {
		text-align: center;
		color: var(--color-text-muted);
		font-size: var(--text-sm);
	}

	.margin-highlight {
		margin-top: var(--space-xl);
		padding: var(--space-lg);
		background: var(--color-surface-elevated);
		border-radius: var(--radius-lg);
		text-align: center;
	}

	.margin-value {
		display: block;
		font-family: var(--font-display);
		font-size: var(--text-3xl);
		font-weight: var(--font-bold);
		color: var(--color-primary);
	}

	.margin-label {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	/* Turnout comparison */
	.turnout-comparison {
		width: 100%;
		max-width: 450px;
		display: flex;
		flex-direction: column;
		gap: var(--space-lg);
	}

	.turnout-item {
		position: relative;
		height: 50px;
		background: var(--color-surface);
		border-radius: var(--radius-md);
		overflow: hidden;
	}

	.turnout-bar {
		position: absolute;
		top: 0;
		left: 0;
		height: 100%;
		border-radius: var(--radius-md);
	}

	.turnout-bar.governor {
		background: var(--color-primary);
		opacity: 0.8;
	}

	.turnout-bar.referendum {
		background: #d4a373;
		opacity: 0.8;
	}

	.turnout-label {
		position: relative;
		z-index: 1;
		display: flex;
		align-items: center;
		justify-content: space-between;
		height: 100%;
		padding: 0 var(--space-lg);
	}

	.turnout-name {
		font-weight: var(--font-medium);
		color: var(--color-text);
	}

	.turnout-value {
		font-family: var(--font-display);
		font-size: var(--text-xl);
		font-weight: var(--font-bold);
		color: var(--color-text);
	}

	.turnout-note {
		text-align: center;
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin-top: var(--space-lg);
	}

	/* Legend */
	.legend {
		margin-top: var(--space-lg);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-xs);
	}

	.legend-scale {
		display: flex;
		width: 250px;
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
		width: 250px;
		font-size: var(--text-xs);
		color: var(--color-text-light);
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
		color: var(--color-primary);
		margin-bottom: var(--space-sm);
	}

	.stat-card .stat-label {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	/* Newspaper headline style */
	.headline-moment {
		margin: var(--space-2xl) 0;
	}

	.newspaper-style {
		background: #f5f1eb;
		border: 1px solid #d4d0c8;
		padding: var(--space-xl);
		font-family: var(--font-serif, Georgia, serif);
	}

	.newspaper-style .dateline {
		font-size: var(--text-xs);
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: #666;
		display: block;
		margin-bottom: var(--space-sm);
	}

	.newspaper-style h3 {
		font-size: var(--text-2xl);
		font-weight: 700;
		line-height: 1.2;
		color: #1a1a1a;
		margin: 0 0 var(--space-md) 0;
	}

	.newspaper-style .subhead {
		font-size: var(--text-base);
		color: #444;
		line-height: 1.5;
		margin: 0;
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
</style>
