<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { LineChart, BarChart } from '$lib/components/charts';
	import { Legend } from '$lib/components/ui';
	import { PARTY_COLORS, CATEGORY_COLORS } from '$lib/utils/colors';
	import { formatNumber, formatPercent, formatCompact } from '$lib/utils/format';

	const chapterNum = 7;
	const chapterTitle = 'La Fortaleza';
	const totalSteps = 10;

	let currentStep = $state(0);
	let activeViz = $state<'line' | 'stacked' | 'margin' | 'third-party' | 'candidates'>('line');
	let loading = $state(true);

	// Data loaded from API
	interface CandidateResult {
		candidate: string;
		party: string;
		votes: number;
		percentage: number;
	}

	let resultsByYear = $state<Record<string, CandidateResult[]>>({});
	let availableYears = $state<number[]>([]);

	// Party abbreviations for display
	function getPartyAbbr(party: string): string {
		if (party.includes('NUEVO PROGRESISTA')) return 'PNP';
		if (party.includes('POPULAR DEMOCRÁTICO')) return 'PPD';
		if (party.includes('VICTORIA CIUDADANA')) return 'MVC';
		if (party.includes('INDEPENDENTISTA')) return 'PIP';
		if (party.includes('DIGNIDAD')) return 'PD';
		if (party.includes('INDEPENDIENTE')) return 'IND';
		return 'Other';
	}

	// Map party names to colors
	function getPartyColor(party: string): string {
		if (party.includes('NUEVO PROGRESISTA')) return PARTY_COLORS.PNP;
		if (party.includes('POPULAR DEMOCRÁTICO')) return PARTY_COLORS.PPD;
		if (party.includes('VICTORIA CIUDADANA')) return PARTY_COLORS.MVC;
		if (party.includes('INDEPENDENTISTA')) return PARTY_COLORS.PIP;
		if (party.includes('DIGNIDAD')) return PARTY_COLORS.PD;
		return PARTY_COLORS.IND;
	}

	// Load chapter data
	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/chapters/fortaleza.json`);
			const data = await response.json();
			resultsByYear = data.results_by_year || {};
			availableYears = data.years || [];
		} catch (err) {
			console.error('Failed to load fortaleza data:', err);
		} finally {
			loading = false;
		}
	});

	// Derive party trends from results
	let partyTrends = $derived(() => {
		const pnpData: Array<{x: number; y: number}> = [];
		const ppdData: Array<{x: number; y: number}> = [];
		const otherData: Array<{x: number; y: number}> = [];

		for (const year of availableYears) {
			const results = resultsByYear[String(year)] || [];
			let pnpPct = 0, ppdPct = 0, otherPct = 0;

			for (const r of results) {
				if (r.party.includes('NUEVO PROGRESISTA')) pnpPct += r.percentage;
				else if (r.party.includes('POPULAR DEMOCRÁTICO')) ppdPct += r.percentage;
				else otherPct += r.percentage;
			}

			pnpData.push({ x: year, y: pnpPct });
			ppdData.push({ x: year, y: ppdPct });
			otherData.push({ x: year, y: otherPct });
		}

		return [
			{ id: 'pnp', label: 'PNP', color: PARTY_COLORS.PNP, data: pnpData },
			{ id: 'ppd', label: 'PPD', color: PARTY_COLORS.PPD, data: ppdData },
			{ id: 'other', label: 'Third Parties', color: PARTY_COLORS.MVC, data: otherData },
		];
	});

	// Stacked bar data for year comparison
	let stackedBarData = $derived(() => {
		const data: Array<{label: string; value: number; color: string}> = [];

		for (const year of availableYears) {
			const results = resultsByYear[String(year)] || [];
			results.slice(0, 5).forEach(r => {
				data.push({
					label: `${year}: ${r.candidate.split(' ')[0]} (${getPartyAbbr(r.party)})`,
					value: r.percentage,
					color: getPartyColor(r.party)
				});
			});
		}
		return data;
	});

	// Margin of victory data
	let marginData = $derived(() => {
		const margins: Array<{label: string; value: number; color: string}> = [];

		for (const year of availableYears) {
			const results = resultsByYear[String(year)] || [];
			if (results.length >= 2) {
				const winner = results[0];
				const runnerUp = results[1];
				const margin = winner.percentage - runnerUp.percentage;
				margins.push({
					label: `${year}`,
					value: margin,
					color: getPartyColor(winner.party)
				});
			}
		}
		return margins;
	});

	// Third party breakdown for 2020
	let thirdPartyData = $derived(() => {
		const results2020 = resultsByYear['2020'] || [];
		return results2020
			.filter(r => !r.party.includes('NUEVO PROGRESISTA') && !r.party.includes('POPULAR DEMOCRÁTICO'))
			.map(r => ({
				label: `${r.candidate.split(' ')[0]} (${getPartyAbbr(r.party)})`,
				value: r.percentage,
				color: getPartyColor(r.party)
			}));
	});

	// Get specific candidate data for cards
	let candidates2016 = $derived(() => resultsByYear['2016'] || []);
	let candidates2020 = $derived(() => resultsByYear['2020'] || []);

	// Winner data for each year
	let winner2016 = $derived(() => candidates2016()[0]);
	let winner2020 = $derived(() => candidates2020()[0]);

	function handleStepEnter(response: { index: number }) {
		currentStep = response.index;

		// Map steps to visualizations
		if (response.index <= 1) {
			activeViz = 'line';
		} else if (response.index === 2) {
			activeViz = 'candidates';
		} else if (response.index === 3 || response.index === 4) {
			activeViz = 'margin';
		} else if (response.index === 5 || response.index === 6) {
			activeViz = 'stacked';
		} else if (response.index === 7) {
			activeViz = 'third-party';
		} else {
			activeViz = 'line';
		}
	}

	// Legend items for party colors
	const partyLegendItems = [
		{ label: 'PNP (Statehood)', color: PARTY_COLORS.PNP },
		{ label: 'PPD (Commonwealth)', color: PARTY_COLORS.PPD },
		{ label: 'MVC (Progressive)', color: PARTY_COLORS.MVC },
		{ label: 'PIP (Independence)', color: PARTY_COLORS.PIP },
		{ label: 'PD (Conservative)', color: PARTY_COLORS.PD },
	];
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
			<p class="subtitle">The Crumbling Duopoly</p>
			<p class="lead">
				La Fortaleza—the 16th-century fortress that serves as the Governor's mansion—has
				witnessed a political earthquake. For fifty years, two parties took turns governing.
				Now governors win with barely a third of the vote. This is the story of how
				Puerto Rico's political establishment came undone.
			</p>
		</div>
	</header>

	<ScrollySection offset={0.6} onStepEnter={handleStepEnter}>
		{#snippet graphic()}
			<div class="viz-container">
				{#if loading}
					<p class="loading">Loading data...</p>
				{:else if activeViz === 'line'}
					<h3 class="viz-title">The Duopoly's Decline: Party Vote Share</h3>
					<LineChart
						series={partyTrends()}
						width={500}
						height={340}
						xLabel="Election Year"
						yLabel="Vote Share %"
						xFormat={(v) => String(v)}
						yFormat={(v) => `${v.toFixed(0)}%`}
						showArea={true}
					/>
					<div class="viz-legend">
						<Legend items={partyLegendItems.slice(0, 3)} orientation="horizontal" />
					</div>
				{:else if activeViz === 'candidates'}
					<h3 class="viz-title">The Governors</h3>
					<div class="candidate-cards">
						{#if winner2016()}
							<div class="candidate-card" style="--party-color: {getPartyColor(winner2016().party)}">
								<div class="candidate-year">2016</div>
								<div class="candidate-name">{winner2016().candidate}</div>
								<div class="candidate-party">{getPartyAbbr(winner2016().party)}</div>
								<div class="candidate-result">
									<span class="votes">{formatNumber(winner2016().votes)}</span>
									<span class="percentage">{formatPercent(winner2016().percentage)}</span>
								</div>
								<div class="candidate-fate">Resigned in disgrace</div>
							</div>
						{/if}
						{#if winner2020()}
							<div class="candidate-card" style="--party-color: {getPartyColor(winner2020().party)}">
								<div class="candidate-year">2020</div>
								<div class="candidate-name">{winner2020().candidate}</div>
								<div class="candidate-party">{getPartyAbbr(winner2020().party)}</div>
								<div class="candidate-result">
									<span class="votes">{formatNumber(winner2020().votes)}</span>
									<span class="percentage">{formatPercent(winner2020().percentage)}</span>
								</div>
								<div class="candidate-fate">Minority mandate</div>
							</div>
						{/if}
					</div>
				{:else if activeViz === 'margin'}
					<h3 class="viz-title">Shrinking Mandates: Winner's Margin</h3>
					<BarChart
						data={marginData()}
						width={420}
						height={280}
						horizontal={false}
						valueFormat={(v) => `+${v.toFixed(1)}pp`}
					/>
					<p class="viz-note">Margin = Winner's % minus runner-up's %</p>
				{:else if activeViz === 'stacked'}
					<h3 class="viz-title">All Candidates by Year</h3>
					<BarChart
						data={stackedBarData()}
						width={480}
						height={420}
						horizontal={true}
						valueFormat={(v) => `${v.toFixed(1)}%`}
					/>
				{:else if activeViz === 'third-party'}
					<h3 class="viz-title">2020: The Third Party Breakthrough</h3>
					<BarChart
						data={thirdPartyData()}
						width={420}
						height={280}
						horizontal={true}
						valueFormat={(v) => `${v.toFixed(1)}%`}
					/>
					<div class="third-party-total">
						<span class="stat-label">Combined third party vote:</span>
						<span class="stat-value">
							{#if candidates2020().length > 0}
								{formatPercent(
									candidates2020()
										.filter(r => !r.party.includes('NUEVO PROGRESISTA') && !r.party.includes('POPULAR DEMOCRÁTICO'))
										.reduce((sum, r) => sum + r.percentage, 0)
								)}
							{/if}
						</span>
					</div>
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>The Golden Age of Bipartisanship</h3>
			<p>
				For half a century, Puerto Rico's politics operated like clockwork. The
				<span class="party-name pnp">Partido Nuevo Progresista (PNP)</span>, advocating
				for U.S. statehood, and the <span class="party-name ppd">Partido Popular
				Democrático (PPD)</span>, defending the commonwealth status quo, traded
				control of La Fortaleza with metronomic regularity.
			</p>
			<p>
				Together, they commanded overwhelming majorities—routinely capturing
				<span class="stat">95% or more</span> of the vote. The independence movement
				was marginalized. Independents were novelties. The system seemed unshakeable.
			</p>
			<p>
				Governors won with clear mandates, often exceeding 48% in closely contested
				races. Electoral legitimacy was rarely questioned.
			</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>The 2016 Fracture Begins</h3>
			<p>
				The cracks appeared suddenly. Puerto Rico was drowning in $72 billion of debt.
				PROMESA—the federal oversight board—had stripped the island of fiscal sovereignty.
				Austerity cuts slashed schools, hospitals, and pensions. The old parties offered
				no answers, only blame.
			</p>
			<p>
				Into this void stepped <strong>Alexandra Lúgaro</strong>, an attorney and
				entrepreneur running as an independent. Young, charismatic, and unapologetically
				critical of both parties, she captured <span class="stat">11.1%</span>—more than
				175,000 votes. No independent had come close to such numbers in generations.
			</p>
			<p>
				<strong>Ricardo Rosselló</strong> of the PNP won with just
				<span class="stat">41.8%</span>—the lowest winning percentage in modern history.
				The duopoly still held, but its foundations had cracked.
			</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>The Fall of Rosselló</h3>
			<p>
				Governor Ricardo Rosselló promised a "new generation" of leadership. What Puerto
				Rico got was scandal. In July 2019, nearly 900 pages of private chat messages
				leaked to the public. The "Telegramgate" revelations were devastating.
			</p>
			<p>
				In the chats, Rosselló and his inner circle mocked Hurricane Maria victims,
				made homophobic jokes about singer Ricky Martin, and called a former New York
				City councilwoman a "whore." The messages revealed casual corruption and
				breathtaking contempt for the people they governed.
			</p>
			<p>
				What followed was unprecedented: <span class="highlight">twelve consecutive days
				of massive street protests</span>. Hundreds of thousands marched through Old San
				Juan. Ricky Martin led crowds chanting "Ricky Renuncia!" On August 2, 2019,
				Rosselló resigned—the first governor in Puerto Rico history forced out by
				popular uprising.
			</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>Summer 2019: The Streets Rise</h3>
			<p>
				The protests that toppled Rosselló weren't just about a governor. They were
				about decades of accumulated grievances: the debt crisis, Hurricane Maria's
				botched response, corruption at every level, and a political class that seemed
				indifferent to suffering.
			</p>
			<p>
				Artists, students, labor unions, and ordinary citizens found common cause.
				Bad Bunny, Residente, and iLe released "Afilando Los Cuchillos" as an anthem
				of resistance. The protests crossed generational and ideological lines.
			</p>
			<p>
				From this uprising emerged <span class="party-name mvc">Movimiento Victoria
				Ciudadana (MVC)</span>—a new progressive party built on the energy of the
				streets. The two-party system would never be the same.
			</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>The Shrinking Mandate</h3>
			<p>
				Compare the margins. In 2016, Rosselló beat his PPD rival by
				<span class="stat">2.9 percentage points</span>—a narrow but workable margin.
				In 2020, Pedro Pierluisi's margin over Charlie Delgado collapsed to just
				<span class="stat">1.5 points</span>.
			</p>
			<p>
				But the real story isn't the head-to-head margin—it's the overall fragmentation.
				When a governor wins with 33% of the vote, two-thirds of the electorate voted
				against them. What does democratic legitimacy mean in such conditions?
			</p>
			<p>
				The implications ripple through governance: weakened mandates, fragile coalitions,
				and a permanent legitimacy deficit that shadows every major decision.
			</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>The 2020 Four-Way Race</h3>
			<p>
				The 2020 election shattered all precedents. <strong>Pedro Pierluisi</strong>,
				a PNP stalwart who briefly served as governor after Rosselló's resignation,
				claimed victory with just <span class="stat">{winner2020() ? formatPercent(winner2020().percentage) : '33.2%'}</span>
				—the lowest winning share in Puerto Rico's electoral history.
			</p>
			<p>
				<strong>Charlie Delgado</strong> of the PPD came agonizingly close at
				<span class="stat">31.8%</span>. But the story was the insurgents: Alexandra
				Lúgaro, now running under the MVC banner, took <span class="stat">14.0%</span>.
				Juan Dalmau of the PIP captured <span class="stat">13.6%</span>—the independence
				party's best showing in decades.
			</p>
			<p>
				Even more striking: <strong>Proyecto Dignidad</strong>, a socially conservative
				evangelical party that didn't exist until 2019, debuted at <span class="stat">6.8%</span>.
			</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>The New Political Arithmetic</h3>
			<p>
				Look at these numbers and understand: the old rules no longer apply. In 2016,
				PNP and PPD together claimed <span class="stat">80.7%</span>. By 2020, that
				combined share had fallen to <span class="stat">65.0%</span>—a collapse of
				nearly 16 percentage points in a single cycle.
			</p>
			<p>
				The erosion isn't limited to governor's races. Legislative elections show
				similar fragmentation. The two-party system that seemed eternal in 2012 now
				looks like a historical artifact.
			</p>
			<p>
				Puerto Rico has become, almost overnight, a genuinely competitive multi-party
				democracy—with all the opportunities and chaos that entails.
			</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>The Third Party Surge</h3>
			<p>
				The 2020 third-party vote tells a story of ideological diversity.
				<span class="party-name mvc">MVC</span> represents the progressive wing—young,
				urban, focused on corruption and social justice. <span class="party-name pip">PIP</span>
				carries the independence torch, finding new relevance as status debates intensify.
			</p>
			<p>
				<span class="party-name pd">Proyecto Dignidad</span> emerged from evangelical
				churches, mobilizing socially conservative voters who felt abandoned by both
				traditional parties. Together, these movements captured over
				<span class="stat">one-third</span> of the 2020 gubernatorial vote.
			</p>
			<p>
				This isn't protest voting. These are durable political movements with distinct
				constituencies, clear ideologies, and growing organizational capacity.
			</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>Governing Without Majorities</h3>
			<p>
				What happens when governors rule with minority mandates? The calculus of
				governance transforms entirely. Traditional party discipline erodes. Coalition
				building becomes essential—and coalitions in a four-party system are fragile.
			</p>
			<p>
				Legislative gridlock increases. Major reforms require cross-party deals that
				satisfy conflicting ideologies. The old pattern of single-party dominance—where
				one side controlled La Fortaleza and the Legislature for four years—may be gone
				forever.
			</p>
			<p>
				Some see opportunity: multi-party systems can force compromise and represent
				diverse views. Others see paralysis: how do you govern an island in crisis when
				no one has a mandate?
			</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>The Question Ahead</h3>
			<p>
				Puerto Rico's political earthquake raises profound questions. Is the two-party
				system's collapse a one-time reaction to crisis, or a permanent realignment?
				Will MVC and PIP consolidate, or will their voters return to major parties?
				Can Proyecto Dignidad maintain momentum without the novelty factor?
			</p>
			<p>
				Most critically: can Puerto Rico's institutions adapt to multi-party governance?
				The island's winner-take-all electoral system was designed for two parties.
				It may need fundamental reform to accommodate its new political reality.
			</p>
			<p>
				La Fortaleza has stood for 500 years. The political system that governed from
				within it may not survive another decade.
			</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>The Numbers Tell the Story</h2>

			<div class="stat-grid">
				<div class="stat-card highlight-card">
					<span class="stat-value" style="color: {PARTY_COLORS.PNP}">
						{winner2020() ? formatPercent(winner2020().percentage) : '33.2%'}
					</span>
					<span class="stat-label">2020 winning percentage—lowest ever</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">-15.7pp</span>
					<span class="stat-label">PNP+PPD share decline (2016-2020)</span>
				</div>
				<div class="stat-card">
					<span class="stat-value" style="color: {PARTY_COLORS.MVC}">35.0%</span>
					<span class="stat-label">Third party vote in 2020</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">12 days</span>
					<span class="stat-label">Of protests that ousted Rosselló</span>
				</div>
			</div>

			<div class="party-legend-section">
				<h3>The New Political Landscape</h3>
				<div class="party-grid">
					<div class="party-item">
						<span class="party-dot" style="background: {PARTY_COLORS.PNP}"></span>
						<div class="party-info">
							<strong>PNP</strong>
							<span>Pro-statehood, center-right</span>
						</div>
					</div>
					<div class="party-item">
						<span class="party-dot" style="background: {PARTY_COLORS.PPD}"></span>
						<div class="party-info">
							<strong>PPD</strong>
							<span>Commonwealth status quo, center</span>
						</div>
					</div>
					<div class="party-item">
						<span class="party-dot" style="background: {PARTY_COLORS.MVC}"></span>
						<div class="party-info">
							<strong>MVC</strong>
							<span>Progressive, anti-corruption</span>
						</div>
					</div>
					<div class="party-item">
						<span class="party-dot" style="background: {PARTY_COLORS.PIP}"></span>
						<div class="party-info">
							<strong>PIP</strong>
							<span>Independence, democratic socialist</span>
						</div>
					</div>
					<div class="party-item">
						<span class="party-dot" style="background: {PARTY_COLORS.PD}"></span>
						<div class="party-info">
							<strong>PD</strong>
							<span>Socially conservative, evangelical</span>
						</div>
					</div>
				</div>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/geography" class="nav-link prev">
					<span class="nav-direction">Previous</span>
					<span class="nav-title">Divided by Design</span>
				</a>
				<a href="{base}/chapters/battlegrounds" class="nav-link next">
					<span class="nav-direction">Next Chapter</span>
					<span class="nav-title">78 Battlegrounds</span>
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
		background:
			linear-gradient(180deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 100%),
			radial-gradient(ellipse at 50% 100%, var(--color-surface) 0%, var(--color-bg) 70%);
	}

	.subtitle {
		font-family: var(--font-display);
		font-size: var(--text-xl);
		font-weight: var(--font-medium);
		color: var(--color-accent);
		text-transform: uppercase;
		letter-spacing: var(--tracking-wide);
		margin-bottom: var(--space-md);
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

	.viz-legend {
		margin-top: var(--space-md);
	}

	.viz-note {
		font-size: var(--text-sm);
		color: var(--color-text-light);
		font-style: italic;
		margin-top: var(--space-sm);
	}

	/* Candidate Cards */
	.candidate-cards {
		display: flex;
		gap: var(--space-xl);
		flex-wrap: wrap;
		justify-content: center;
	}

	.candidate-card {
		background: var(--color-surface-elevated);
		border-radius: var(--radius-lg);
		padding: var(--space-xl);
		width: 200px;
		text-align: center;
		border-top: 4px solid var(--party-color, var(--color-primary));
		box-shadow: var(--shadow-md);
	}

	.candidate-year {
		font-family: var(--font-display);
		font-size: var(--text-3xl);
		font-weight: var(--font-bold);
		color: var(--party-color);
		margin-bottom: var(--space-xs);
	}

	.candidate-name {
		font-size: var(--text-md);
		font-weight: var(--font-semibold);
		color: var(--color-text);
		margin-bottom: var(--space-xs);
		line-height: 1.3;
	}

	.candidate-party {
		font-size: var(--text-sm);
		font-weight: var(--font-bold);
		color: var(--party-color);
		margin-bottom: var(--space-md);
	}

	.candidate-result {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
		padding: var(--space-md);
		background: var(--color-surface);
		border-radius: var(--radius-md);
		margin-bottom: var(--space-md);
	}

	.candidate-result .votes {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.candidate-result .percentage {
		font-family: var(--font-display);
		font-size: var(--text-2xl);
		font-weight: var(--font-bold);
		color: var(--color-text);
	}

	.candidate-fate {
		font-size: var(--text-sm);
		color: var(--color-text-light);
		font-style: italic;
	}

	/* Third party total */
	.third-party-total {
		margin-top: var(--space-lg);
		padding: var(--space-md) var(--space-lg);
		background: var(--color-surface-elevated);
		border-radius: var(--radius-md);
		display: flex;
		align-items: center;
		gap: var(--space-md);
	}

	.third-party-total .stat-label {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.third-party-total .stat-value {
		font-family: var(--font-display);
		font-size: var(--text-xl);
		font-weight: var(--font-bold);
		color: var(--color-accent);
	}

	/* Party name styling in text */
	.party-name {
		font-weight: var(--font-semibold);
	}

	.party-name.pnp { color: var(--color-text); }
	.party-name.ppd { color: var(--color-text); }
	.party-name.mvc { color: var(--color-text); }
	.party-name.pip { color: var(--color-text); }
	.party-name.pd { color: var(--color-text); }

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

	.stat-card.highlight-card {
		border: 2px solid var(--color-accent);
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

	/* Party legend section */
	.party-legend-section {
		margin: var(--space-2xl) 0;
	}

	.party-legend-section h3 {
		font-size: var(--text-lg);
		margin-bottom: var(--space-lg);
		color: var(--color-text);
	}

	.party-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: var(--space-md);
	}

	.party-item {
		display: flex;
		align-items: flex-start;
		gap: var(--space-sm);
		padding: var(--space-sm);
	}

	.party-dot {
		width: 16px;
		height: 16px;
		border-radius: 50%;
		flex-shrink: 0;
		margin-top: 2px;
	}

	.party-info {
		display: flex;
		flex-direction: column;
	}

	.party-info strong {
		font-size: var(--text-md);
		color: var(--color-text);
	}

	.party-info span {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
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
