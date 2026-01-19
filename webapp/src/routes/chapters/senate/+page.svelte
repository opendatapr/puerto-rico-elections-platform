<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { BarChart, LineChart } from '$lib/components/charts';
	import { PARTY_COLORS, CATEGORY_COLORS } from '$lib/utils/colors';
	import { formatPercent, formatNumber, formatPercentChange } from '$lib/utils/format';

	const chapterNum = 10;
	const chapterTitle = 'The At-Large Experiment';
	const totalSteps = 10;

	let currentStep = $state(0);
	let activeViz = $state<'hemicycle' | 'topVotes' | 'partyShare' | 'composition' | 'thirdParty'>('hemicycle');
	let loading = $state(true);
	let selectedYear = $state('2020');

	// Data loaded from JSON
	interface CandidateResult {
		candidate: string;
		party: string;
		votes: number;
		percentage: number;
	}

	interface PartyShare {
		party: string;
		votes: number;
		percentage: number;
	}

	interface SenateData {
		at_large_by_year: Record<string, CandidateResult[]>;
		party_vote_share: Record<string, PartyShare[]>;
		historical_composition: Record<string, Record<string, number>>;
		years: number[];
	}

	let senateData = $state<SenateData | null>(null);

	// Historical composition for all years (combining data + known historical records)
	const historicalComposition: Record<string, Record<string, number>> = {
		'2008': { PNP: 22, PPD: 4, PIP: 1 },
		'2012': { PNP: 16, PPD: 10, PIP: 1 },
		'2016': { PNP: 21, PPD: 5, PIP: 1 },
		'2020': { PNP: 9, PPD: 8, MVC: 2, PIP: 2, PD: 1, IND: 1 },
		'2024': { PPD: 13, PNP: 9, MVC: 2, PIP: 1, PD: 1, IND: 1 }
	};

	// Load chapter data
	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/chapters/senate.json`);
			const data = await response.json();
			senateData = data;
		} catch (err) {
			console.error('Failed to load senate data:', err);
		} finally {
			loading = false;
		}
	});

	// Map party names to abbreviations
	function getPartyAbbrev(party: string): string {
		if (party.includes('NUEVO PROGRESISTA')) return 'PNP';
		if (party.includes('POPULAR DEMOCRÁTICO')) return 'PPD';
		if (party.includes('VICTORIA CIUDADANA')) return 'MVC';
		if (party.includes('INDEPENDENTISTA')) return 'PIP';
		if (party.includes('DIGNIDAD')) return 'PD';
		if (party.includes('INDEPENDIENTE')) return 'IND';
		return 'Other';
	}

	// Get party color
	function getPartyColor(party: string): string {
		const abbrev = getPartyAbbrev(party);
		return PARTY_COLORS[abbrev] || PARTY_COLORS.IND;
	}

	// Hemicycle seat data for a given year
	function getHemicycleSeats(year: string): Array<{ party: string; color: string; count: number }> {
		const composition = historicalComposition[year] || historicalComposition['2020'];
		return Object.entries(composition)
			.map(([party, count]) => ({
				party,
				color: PARTY_COLORS[party] || PARTY_COLORS.IND,
				count
			}))
			.sort((a, b) => b.count - a.count);
	}

	// Get top vote-getters for bar chart
	let topVotesBarData = $derived(() => {
		if (!senateData?.at_large_by_year) return [];
		const results = senateData.at_large_by_year[selectedYear] || [];
		return results.slice(0, 11).map((r, i) => ({
			label: `${i + 1}. ${r.candidate.split(' ')[0]}`,
			value: r.votes / 1000, // In thousands for readability
			color: getPartyColor(r.party)
		}));
	});

	// Party vote share bar data
	let partyShareBarData = $derived(() => {
		if (!senateData?.party_vote_share) return [];
		const shares = senateData.party_vote_share[selectedYear] || [];
		return shares.slice(0, 6).map(s => ({
			label: getPartyAbbrev(s.party),
			value: s.percentage,
			color: PARTY_COLORS[getPartyAbbrev(s.party)] || PARTY_COLORS.IND
		}));
	});

	// Historical composition line data
	let compositionLineData = $derived(() => {
		const years = ['2008', '2012', '2016', '2020', '2024'];
		const parties = ['PNP', 'PPD', 'PIP', 'MVC', 'PD', 'IND'];

		return parties.map(party => ({
			id: party,
			label: party,
			color: PARTY_COLORS[party] || PARTY_COLORS.IND,
			data: years.map(year => ({
				x: parseInt(year),
				y: historicalComposition[year]?.[party] || 0
			})).filter(d => d.y > 0 || party === 'PNP' || party === 'PPD') // Include zeros for major parties
		})).filter(series => series.data.some(d => d.y > 0));
	});

	// Third party growth data
	let thirdPartyLineData = $derived(() => {
		const years = ['2008', '2012', '2016', '2020', '2024'];

		// Calculate two-party vs third-party seats
		const twoPartyData = years.map(year => {
			const comp = historicalComposition[year] || {};
			const twoParty = (comp.PNP || 0) + (comp.PPD || 0);
			return { x: parseInt(year), y: twoParty };
		});

		const thirdPartyData = years.map(year => {
			const comp = historicalComposition[year] || {};
			const total = Object.values(comp).reduce((a, b) => a + b, 0);
			const twoParty = (comp.PNP || 0) + (comp.PPD || 0);
			return { x: parseInt(year), y: total - twoParty };
		});

		return [
			{ id: 'twoparty', label: 'PNP + PPD', color: '#666666', data: twoPartyData },
			{ id: 'third', label: 'Third Parties + Ind', color: PARTY_COLORS.MVC, data: thirdPartyData }
		];
	});

	// Compute statistics
	let stats = $derived(() => {
		if (!senateData) return null;

		const results2020 = senateData.at_large_by_year['2020'] || [];
		const results2016 = senateData.at_large_by_year['2016'] || [];

		// Count elected by party in 2020 (top 11)
		const elected2020 = results2020.slice(0, 11);
		const partyCount2020: Record<string, number> = {};
		for (const r of elected2020) {
			const abbrev = getPartyAbbrev(r.party);
			partyCount2020[abbrev] = (partyCount2020[abbrev] || 0) + 1;
		}

		// Top vote-getter
		const topCandidate = results2020[0];

		// Vote difference between 11th and 12th place
		const cutoffMargin = results2020.length >= 12
			? results2020[10].votes - results2020[11].votes
			: 0;

		return {
			partyCount2020,
			topCandidate,
			cutoffMargin,
			totalCandidates2020: results2020.length,
			totalCandidates2016: results2016.length
		};
	});

	function handleStepEnter(response: { index: number }) {
		currentStep = response.index;

		switch (response.index) {
			case 0: // Intro - show 2020 hemicycle
				activeViz = 'hemicycle';
				selectedYear = '2020';
				break;
			case 1: // How voting works
				activeViz = 'hemicycle';
				selectedYear = '2020';
				break;
			case 2: // Top vote-getters 2020
				activeViz = 'topVotes';
				selectedYear = '2020';
				break;
			case 3: // Party vote share
				activeViz = 'partyShare';
				selectedYear = '2020';
				break;
			case 4: // Historical composition
				activeViz = 'composition';
				break;
			case 5: // 2016 supermajority
				activeViz = 'hemicycle';
				selectedYear = '2016';
				break;
			case 6: // 2020 fragmentation
				activeViz = 'hemicycle';
				selectedYear = '2020';
				break;
			case 7: // Third party breakthrough
				activeViz = 'thirdParty';
				break;
			case 8: // Minority protection
				activeViz = 'hemicycle';
				selectedYear = '2024';
				break;
			case 9: // 2024 and future
				activeViz = 'hemicycle';
				selectedYear = '2024';
				break;
		}
	}

	// Generate hemicycle arc positions
	function generateHemicyclePositions(seats: Array<{ party: string; color: string; count: number }>) {
		const totalSeats = seats.reduce((sum, s) => sum + s.count, 0);
		const rows = 3;
		const baseRadius = 140;
		const rowGap = 28;
		const seatRadius = 10;

		const positions: Array<{ x: number; y: number; color: string; party: string; row: number }> = [];

		// Distribute seats across rows (more in outer rows)
		const seatsPerRow = [Math.floor(totalSeats * 0.28), Math.floor(totalSeats * 0.34), Math.ceil(totalSeats * 0.38)];

		let seatIndex = 0;
		const flatSeats = seats.flatMap(s => Array(s.count).fill({ color: s.color, party: s.party }));

		for (let row = 0; row < rows; row++) {
			const rowRadius = baseRadius + row * rowGap;
			const seatsInRow = seatsPerRow[row];
			const angleStep = Math.PI / (seatsInRow + 1);

			for (let i = 0; i < seatsInRow && seatIndex < totalSeats; i++) {
				const angle = Math.PI - angleStep * (i + 1);
				const x = 200 + rowRadius * Math.cos(angle);
				const y = 180 - rowRadius * Math.sin(angle);

				if (flatSeats[seatIndex]) {
					positions.push({
						x,
						y,
						color: flatSeats[seatIndex].color,
						party: flatSeats[seatIndex].party,
						row
					});
				}
				seatIndex++;
			}
		}

		return positions;
	}

	let hemicyclePositions = $derived(() => {
		const seats = getHemicycleSeats(selectedYear);
		return generateHemicyclePositions(seats);
	});
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
				Puerto Rico's Senate operates under a unique system: all 11 at-large senators
				are elected island-wide, making it one of the few legislatures where every
				voter votes for every seat. This design produces distinctive dynamics around
				representation, minority protections, and the rise of third parties.
			</p>
		</div>
	</header>

	<ScrollySection offset={0.6} onStepEnter={handleStepEnter}>
		{#snippet graphic()}
			<div class="viz-container">
				{#if loading}
					<p class="loading">Loading data...</p>
				{:else if activeViz === 'hemicycle'}
					<h3 class="viz-title">Senate Composition: {selectedYear}</h3>
					<svg width="400" height="220" class="hemicycle">
						<!-- Hemicycle arc background -->
						<path
							d="M 30 180 A 170 170 0 0 1 370 180"
							fill="none"
							stroke="var(--color-border)"
							stroke-width="2"
							opacity="0.3"
						/>

						<!-- Seat dots -->
						{#each hemicyclePositions() as seat, i}
							<circle
								cx={seat.x}
								cy={seat.y}
								r="10"
								fill={seat.color}
								stroke="var(--color-bg)"
								stroke-width="1.5"
								opacity="0.9"
							>
								<title>{seat.party}</title>
							</circle>
						{/each}

						<!-- Center label -->
						<text x="200" y="200" text-anchor="middle" class="seat-count">
							27 Seats
						</text>
					</svg>

					<!-- Party legend -->
					<div class="party-legend">
						{#each getHemicycleSeats(selectedYear) as party}
							<div class="legend-item">
								<span class="legend-dot" style="background: {party.color}"></span>
								<span class="legend-label">{party.party}: {party.count}</span>
							</div>
						{/each}
					</div>
				{:else if activeViz === 'topVotes'}
					<h3 class="viz-title">Top 11 At-Large Vote-Getters ({selectedYear})</h3>
					<BarChart
						data={topVotesBarData()}
						width={450}
						height={380}
						horizontal={true}
						valueFormat={(v) => `${formatNumber(Math.round(v * 1000))}`}
					/>
					<p class="viz-note">Vote totals in thousands</p>
				{:else if activeViz === 'partyShare'}
					<h3 class="viz-title">Party Vote Share: At-Large Senate ({selectedYear})</h3>
					<BarChart
						data={partyShareBarData()}
						width={400}
						height={280}
						horizontal={false}
						valueFormat={(v) => formatPercent(v)}
					/>
				{:else if activeViz === 'composition'}
					<h3 class="viz-title">Senate Composition Over Time</h3>
					<LineChart
						series={compositionLineData()}
						width={480}
						height={320}
						xLabel="Election Year"
						yLabel="Seats Won"
						xFormat={(v) => String(v)}
						yFormat={(v) => String(Math.round(v))}
						showDots={true}
						showArea={false}
					/>
				{:else if activeViz === 'thirdParty'}
					<h3 class="viz-title">Two-Party vs Third-Party Seats</h3>
					<LineChart
						series={thirdPartyLineData()}
						width={480}
						height={320}
						xLabel="Election Year"
						yLabel="Total Seats"
						xFormat={(v) => String(v)}
						yFormat={(v) => String(Math.round(v))}
						showDots={true}
						showArea={true}
					/>
					<p class="viz-note">The rise of MVC, PIP, and independents since 2016</p>
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>A Unique Electoral Experiment</h3>
			<p>
				Puerto Rico's 27-member Senate is divided into two components: 16 district senators
				(two from each of 8 senatorial districts) and <span class="highlight">11 at-large senators</span>
				elected island-wide. This at-large system is virtually unique in American politics.
			</p>
			<p>
				The at-large design was intentional: framers wanted senators who would represent
				all of Puerto Rico, not just their district. In theory, this creates legislators
				with broader perspectives and reduces parochialism. In practice, it rewards
				name recognition, tests party loyalty, and makes vote accumulation an art form.
			</p>
			<p>
				The 2020 Senate shows the system in action: <span class="stat">6 parties</span> won
				representation, the most fragmented Senate in Puerto Rican history.
			</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>How At-Large Voting Works</h3>
			<p>
				Each voter casts <span class="highlight">up to 11 votes</span> for at-large senator,
				one for each seat. You can vote for candidates from different parties, split your
				ticket, or vote a straight party line. The 11 candidates with the most votes win.
			</p>
			<p>
				This creates unique incentives. Unlike single-member districts where one candidate
				wins, at-large races reward broad appeal. A candidate who is everyone's second
				choice might accumulate more votes than someone who is polarizing. Personal
				popularity matters enormously.
			</p>
			<p>
				The result: at-large senate races often produce <span class="highlight">surprising
				individual winners</span> who outperform their party. Independent candidates like
				Dr. Jose Vargas Vidot have won seats by building personal coalitions that transcend
				party lines.
			</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>The Top Vote-Getters</h3>
			<p>
				In 2020, the top vote-getter was <span class="highlight">Maria de Lourdes Santiago</span>
				(PIP) with nearly <span class="stat">269,000</span> votes, outpacing candidates from
				both major parties. Her success shows how the at-large system can elevate
				candidates with strong personal brands.
			</p>
			<p>
				The bar chart shows the top 11 elected senators by total votes. Notice the color
				diversity: candidates from <span style="color: {PARTY_COLORS.PIP}">PIP</span>,
				<span style="color: {PARTY_COLORS.MVC}">MVC</span>,
				<span style="color: {PARTY_COLORS.PD}">Proyecto Dignidad</span>, and independents
				all made the cut alongside traditional major-party candidates.
			</p>
			<p>
				The gap between 11th and 12th place was only <span class="stat">{formatNumber(stats()?.cutoffMargin || 0)}</span> votes,
				showing how competitive these races are. A few thousand votes in either direction
				would have changed the Senate's composition.
			</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>Party Vote Share</h3>
			<p>
				Looking at aggregate party vote share tells a different story than individual
				candidate success. In 2020, <span style="color: {PARTY_COLORS.PNP}">PNP</span>
				still led with about 33% of at-large senate votes, followed closely by
				<span style="color: {PARTY_COLORS.PPD}">PPD</span> at 31%.
			</p>
			<p>
				But the real story is fragmentation. Third parties combined captured over
				<span class="stat">35%</span> of the vote. <span style="color: {PARTY_COLORS.PIP}">PIP</span>
				surged to 11%, <span style="color: {PARTY_COLORS.MVC}">MVC</span> won 11%, and
				<span style="color: {PARTY_COLORS.PD}">Proyecto Dignidad</span> emerged with 7%.
			</p>
			<p>
				This fragmentation doesn't translate directly to seats because of winner-take-all
				dynamics. But the at-large system is more proportional than district elections,
				allowing smaller parties to win representation they might not get in single-member
				districts.
			</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>A Generation of Change</h3>
			<p>
				The line chart tracks Senate composition across five election cycles. The pattern
				is dramatic: from near-total <span style="color: {PARTY_COLORS.PNP}">PNP</span>
				dominance in 2008 (22 seats) to a fragmented chamber in 2020 where no party
				controls a majority.
			</p>
			<p>
				The 2016 election was the peak of PNP power: they won <span class="stat">21 of 27</span>
				seats, enough to override any veto. But by 2020, that supermajority collapsed to
				just 9 seats. <span style="color: {PARTY_COLORS.PPD}">PPD</span> recovered somewhat,
				but the real winners were the emerging parties.
			</p>
			<p>
				2024 saw <span style="color: {PARTY_COLORS.PPD}">PPD</span> take the lead with 13 seats,
				while <span style="color: {PARTY_COLORS.MVC}">MVC</span> and
				<span style="color: {PARTY_COLORS.PIP}">PIP</span> maintained their foothold.
				The two-party system hasn't returned, and may never fully recover.
			</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>The 2016 Supermajority</h3>
			<p>
				The 2016 hemicycle shows PNP at the height of its power. With 21 seats, they held
				a <span class="highlight">constitutional supermajority</span>, able to override
				gubernatorial vetoes and control every committee.
			</p>
			<p>
				This dominance came during the PROMESA fiscal crisis. Voters, exhausted by PPD's
				handling of the debt crisis, swung decisively toward PNP. The opposition was
				reduced to just 5 PPD senators and 1 PIP senator: Maria de Lourdes Santiago,
				who would later become the top vote-getter in 2020.
			</p>
			<p>
				But supermajorities breed complacency. The Rossello administration's scandals and
				the 2019 protests set the stage for a dramatic reversal.
			</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>The 2020 Fragmentation</h3>
			<p>
				By 2020, the Senate looked completely different. PNP collapsed from 21 to
				<span class="stat">9 seats</span>. PPD recovered to 8. But the real story was
				the emergence of four new players: <span style="color: {PARTY_COLORS.MVC}">MVC</span>
				(2 seats), <span style="color: {PARTY_COLORS.PIP}">PIP</span> (2 seats),
				<span style="color: {PARTY_COLORS.PD}">Proyecto Dignidad</span> (1), and
				an independent (1).
			</p>
			<p>
				For the first time in memory, neither major party controlled a majority. Governing
				required coalition-building. The Senate president's election became a negotiation
				rather than a formality. Every vote mattered.
			</p>
			<p>
				This is what multi-party democracy looks like in a legislature designed for two
				parties. The at-large system, by allowing more proportional representation,
				accelerated the transition.
			</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>Third-Party Breakthrough</h3>
			<p>
				This chart shows the structural shift in stark terms. Before 2016, third parties
				and independents held at most <span class="stat">1-2 seats</span>. The two-party
				system captured 95%+ of Senate representation.
			</p>
			<p>
				The breakthrough came suddenly. In 2020, non-traditional parties and independents
				won <span class="stat">6 of 27 seats</span>: 22% of the chamber. MVC's Ana Irma
				Rivera Lassen and Rafael Bernabe became the party's first-ever senators.
				Proyecto Dignidad's Joanne Rodriguez Veve won her seat in her first election.
			</p>
			<p>
				The at-large system enabled this breakthrough. In district-only elections, these
				candidates might have won nothing. But island-wide voting allowed them to accumulate
				support from pockets across Puerto Rico, reaching the threshold for victory.
			</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>The Minority Protection Clause</h3>
			<p>
				Puerto Rico's constitution contains a remarkable provision: if any party wins more
				than two-thirds of legislative seats, <span class="highlight">additional seats are
				created</span> for the minority. This "minority representation" clause ensures
				opposition voices are always heard.
			</p>
			<p>
				The clause was triggered in 2008, when PNP's dominance required expanding the
				Senate to preserve PPD representation. It's a structural check against one-party
				rule that few other jurisdictions have.
			</p>
			<p>
				In the current multi-party environment, the clause is less relevant, no single
				party comes close to two-thirds. But it remains a safeguard against future
				supermajorities, ensuring Puerto Rico's democracy always includes opposition voices.
			</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>The New Senate Politics</h3>
			<p>
				Looking at the 2024 composition, the transformation is complete.
				<span style="color: {PARTY_COLORS.PPD}">PPD</span> now leads with 13 seats, but
				still lacks a majority. <span style="color: {PARTY_COLORS.PNP}">PNP</span> holds 9.
				The remaining 5 seats are split among third parties and independents.
			</p>
			<p>
				This creates a new kind of legislative politics. The Senate president needs
				cross-party support. Major legislation requires coalition-building. Individual
				senators, especially independents, wield outsized influence as potential
				swing votes.
			</p>
			<p>
				The at-large experiment has produced exactly what its designers feared and
				hoped for: a legislature that reflects Puerto Rico's political diversity,
				including voices that the two-party system had marginalized for decades.
			</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>The Island-Wide Chamber</h2>
			<p>
				Puerto Rico's at-large Senate system is an experiment in representation. By
				requiring candidates to seek island-wide support, it produces senators with
				broader constituencies than district-based elections. By allowing proportional
				outcomes, it gives voice to parties that might otherwise be shut out.
			</p>
			<p>
				The 2020 election marked a watershed: the definitive end of two-party dominance
				in the Senate. Whether this fragmentation leads to gridlock or innovation depends
				on how legislators adapt to coalition politics. But one thing is clear: Puerto
				Rico's Senate will never look like it did in 2016 again.
			</p>

			<!-- Summary Stats Box -->
			{#if stats()}
				<div class="stats-summary">
					<h3>Key Statistics: 2020 At-Large Senate</h3>
					<div class="stats-grid">
						<div class="stat-item">
							<span class="stat-value">6</span>
							<span class="stat-label">Parties Represented</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{formatNumber(stats().topCandidate?.votes || 0)}</span>
							<span class="stat-label">Top Vote-Getter</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{stats().totalCandidates2020}</span>
							<span class="stat-label">Candidates Running</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{formatNumber(stats().cutoffMargin)}</span>
							<span class="stat-label">11th-12th Place Gap</span>
						</div>
					</div>
				</div>
			{/if}

			<!-- Historical Composition Table -->
			<div class="composition-table-container">
				<h3>Senate Composition by Year</h3>
				<table class="composition-table">
					<thead>
						<tr>
							<th>Year</th>
							<th><span class="party-label" style="background: {PARTY_COLORS.PNP}">PNP</span></th>
							<th><span class="party-label" style="background: {PARTY_COLORS.PPD}">PPD</span></th>
							<th><span class="party-label" style="background: {PARTY_COLORS.PIP}">PIP</span></th>
							<th><span class="party-label" style="background: {PARTY_COLORS.MVC}">MVC</span></th>
							<th>Other</th>
						</tr>
					</thead>
					<tbody>
						{#each ['2008', '2012', '2016', '2020', '2024'] as year}
							<tr>
								<td class="year-cell">{year}</td>
								<td>{historicalComposition[year]?.PNP || 0}</td>
								<td>{historicalComposition[year]?.PPD || 0}</td>
								<td>{historicalComposition[year]?.PIP || 0}</td>
								<td>{historicalComposition[year]?.MVC || 0}</td>
								<td>{(historicalComposition[year]?.PD || 0) + (historicalComposition[year]?.IND || 0)}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>

			<div class="sources">
				<h3>Sources</h3>
				<ul>
					<li><a href="https://ww2.ceepur.org/Home/EventosElectorales" target="_blank" rel="noopener">Comision Estatal de Elecciones de Puerto Rico (CEE)</a> - Senate election results 2000-2024</li>
					<li><a href="https://senado.pr.gov/" target="_blank" rel="noopener">Senado de Puerto Rico</a> - Historical composition and party affiliation data</li>
					<li>Puerto Rico Constitution - Senate structure and at-large seat requirements</li>
					<li>University of Puerto Rico - Political Science Department electoral analysis</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/precincts" class="nav-link prev">
					<span class="nav-direction">Previous</span>
					<span class="nav-title">Down to the Precinct</span>
				</a>
				<a href="{base}/chapters/house" class="nav-link next">
					<span class="nav-direction">Next Chapter</span>
					<span class="nav-title">40 House Races</span>
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
		color: var(--color-text-muted);
		margin-top: var(--space-md);
		font-style: italic;
	}

	/* Hemicycle styles */
	.hemicycle {
		margin: var(--space-md) 0;
	}

	.seat-count {
		font-family: var(--font-display);
		font-size: var(--text-sm);
		fill: var(--color-text-muted);
		font-weight: var(--font-medium);
	}

	.party-legend {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: var(--space-md);
		margin-top: var(--space-lg);
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
	}

	.legend-dot {
		width: 14px;
		height: 14px;
		border-radius: 50%;
	}

	.legend-label {
		font-size: var(--text-sm);
		color: var(--color-text);
	}

	/* Chapter conclusion */
	.chapter-conclusion {
		padding: var(--space-3xl) 0;
		background: var(--color-surface);
	}

	.chapter-conclusion h2 {
		margin-bottom: var(--space-lg);
	}

	.stats-summary {
		background: var(--color-bg);
		border-radius: var(--radius-lg);
		padding: var(--space-xl);
		margin: var(--space-2xl) 0;
	}

	.stats-summary h3 {
		font-size: var(--text-lg);
		margin-bottom: var(--space-lg);
		color: var(--color-text-muted);
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		gap: var(--space-lg);
	}

	.stat-item {
		text-align: center;
	}

	.stat-value {
		display: block;
		font-family: var(--font-display);
		font-size: var(--text-2xl);
		font-weight: var(--font-bold);
		color: var(--color-accent);
	}

	.stat-label {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	/* Composition table */
	.composition-table-container {
		margin: var(--space-2xl) 0;
	}

	.composition-table-container h3 {
		font-size: var(--text-lg);
		margin-bottom: var(--space-lg);
		color: var(--color-text-muted);
	}

	.composition-table {
		width: 100%;
		border-collapse: collapse;
		font-size: var(--text-sm);
	}

	.composition-table th,
	.composition-table td {
		padding: var(--space-sm) var(--space-md);
		text-align: center;
		border-bottom: 1px solid var(--color-border);
	}

	.composition-table th {
		font-weight: var(--font-medium);
		color: var(--color-text-muted);
	}

	.party-label {
		display: inline-block;
		padding: 2px 8px;
		border-radius: var(--radius-sm);
		color: white;
		font-size: var(--text-xs);
		font-weight: var(--font-medium);
	}

	.year-cell {
		font-weight: var(--font-semibold);
		color: var(--color-text);
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
</style>
