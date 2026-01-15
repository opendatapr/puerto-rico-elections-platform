<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { LineChart, BarChart } from '$lib/components/charts';
	import { Legend } from '$lib/components/ui';
	import { PARTY_COLORS, CATEGORY_COLORS } from '$lib/utils/colors';
	import { formatPercent, formatPercentChange } from '$lib/utils/format';

	const chapterNum = 11;
	const chapterTitle = '40 Districts, 40 Stories';
	const totalSteps = 10;

	let currentStep = $state(0);
	let activeViz = $state<'competitiveness' | 'seatTrend' | 'marginDist' | 'closestRaces' | 'flipped' | 'thirdParty'>('competitiveness');
	let loading = $state(true);

	// Data types
	interface DistrictResult {
		district: string;
		district_num: number;
		winner: string;
		winner_party: string;
		winner_pct: number;
		runnerup: string;
		runnerup_party: string;
		runnerup_pct: number;
		margin: number;
		third_party_pct: number;
		total_candidates: number;
	}

	interface MarginShift {
		district: string;
		district_num: number;
		shift: number;
		margin_2016: number;
		margin_2020: number;
		winner_2016: string;
		winner_2020: string;
		flipped: boolean;
	}

	interface ThirdPartyDistrict {
		district: string;
		district_num: number;
		third_party_pct: number;
		winner: string;
	}

	// Data loaded from API
	let districtResults2020 = $state<DistrictResult[]>([]);
	let districtResults2016 = $state<DistrictResult[]>([]);
	let seatCounts = $state<Record<string, Record<string, number>>>({});
	let competitivenessData = $state<Record<string, {
		safe_pnp: number;
		lean_pnp: number;
		competitive: number;
		lean_ppd: number;
		safe_ppd: number;
		third_party_wins: number;
	}>>({});
	let closestRaces = $state<DistrictResult[]>([]);
	let marginDistribution = $state<Record<string, Record<string, number>>>({});
	let thirdPartyStrength = $state<ThirdPartyDistrict[]>([]);
	let marginShifts = $state<MarginShift[]>([]);
	let flippedDistricts = $state<MarginShift[]>([]);

	// Load chapter data
	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/chapters/house.json`);
			const data = await response.json();

			districtResults2020 = data.district_results_by_year?.['2020'] || [];
			districtResults2016 = data.district_results_by_year?.['2016'] || [];
			seatCounts = data.seat_counts_by_year || {};
			competitivenessData = data.competitiveness_by_year || {};
			closestRaces = data.closest_races_2020 || [];
			marginDistribution = data.margin_distribution || {};
			thirdPartyStrength = data.third_party_strength_2020 || [];
			marginShifts = data.margin_shifts || [];
			flippedDistricts = data.flipped_districts || [];
		} catch (err) {
			console.error('Failed to load house data:', err);
		} finally {
			loading = false;
		}
	});

	// District competitiveness bar data (2020)
	let competitivenessBarData = $derived(() => {
		const comp = competitivenessData['2020'];
		if (!comp) return [];
		return [
			{ label: 'Safe PNP (>10%)', value: comp.safe_pnp, color: PARTY_COLORS.PNP },
			{ label: 'Lean PNP (5-10%)', value: comp.lean_pnp, color: '#4a7ab8' },
			{ label: 'Tossup (<5%)', value: comp.competitive, color: CATEGORY_COLORS[5] },
			{ label: 'Lean PPD (5-10%)', value: comp.lean_ppd, color: '#d86060' },
			{ label: 'Safe PPD (>10%)', value: comp.safe_ppd, color: PARTY_COLORS.PPD },
		];
	});

	// Seat composition over time (line chart data)
	let seatTrendData = $derived(() => {
		const pnpData: Array<{x: number; y: number}> = [];
		const ppdData: Array<{x: number; y: number}> = [];

		for (const year of [2016, 2020]) {
			const counts = seatCounts[String(year)] || {};
			pnpData.push({ x: year, y: counts['PNP'] || 0 });
			ppdData.push({ x: year, y: counts['PPD'] || 0 });
		}

		return [
			{ id: 'pnp', label: 'PNP', color: PARTY_COLORS.PNP, data: pnpData },
			{ id: 'ppd', label: 'PPD', color: PARTY_COLORS.PPD, data: ppdData },
		];
	});

	// Margin distribution bar data (2020)
	let marginDistBarData = $derived(() => {
		const dist = marginDistribution['2020'];
		if (!dist) return [];
		return [
			{ label: '0-2%', value: dist['0-2'] || 0, color: '#c41e3a' },
			{ label: '2-5%', value: dist['2-5'] || 0, color: '#e8a87c' },
			{ label: '5-10%', value: dist['5-10'] || 0, color: CATEGORY_COLORS[4] },
			{ label: '10-20%', value: dist['10-20'] || 0, color: CATEGORY_COLORS[1] },
			{ label: '20%+', value: dist['20+'] || 0, color: CATEGORY_COLORS[0] },
		];
	});

	// Closest races bar data
	let closestRacesBarData = $derived(() => {
		return closestRaces.slice(0, 8).map(r => ({
			label: `D${r.district_num}`,
			value: r.margin,
			color: r.winner_party === 'PNP' ? PARTY_COLORS.PNP : PARTY_COLORS.PPD
		}));
	});

	// Flipped districts bar data
	let flippedBarData = $derived(() => {
		return flippedDistricts.map(d => ({
			label: `D${d.district_num}`,
			value: d.shift,
			color: d.shift > 0 ? PARTY_COLORS.PNP : PARTY_COLORS.PPD
		})).sort((a, b) => a.value - b.value);
	});

	// Third party strength bar data
	let thirdPartyBarData = $derived(() => {
		return thirdPartyStrength.slice(0, 8).map(d => ({
			label: `D${d.district_num}`,
			value: d.third_party_pct,
			color: PARTY_COLORS.MVC
		}));
	});

	// Statistics
	let stats = $derived(() => {
		const comp2020 = competitivenessData['2020'];
		const comp2016 = competitivenessData['2016'];
		const seats2020 = seatCounts['2020'] || {};
		const seats2016 = seatCounts['2016'] || {};

		return {
			totalTossups: comp2020?.competitive || 0,
			pnpSeats2020: seats2020['PNP'] || 0,
			ppdSeats2020: seats2020['PPD'] || 0,
			pnpSeats2016: seats2016['PNP'] || 0,
			ppdSeats2016: seats2016['PPD'] || 0,
			flippedCount: flippedDistricts.length,
			avgThirdParty: thirdPartyStrength.length > 0
				? thirdPartyStrength.reduce((sum, d) => sum + d.third_party_pct, 0) / thirdPartyStrength.length
				: 0,
			closestMargin: closestRaces.length > 0 ? closestRaces[0].margin : 0,
			seatSwing: (seats2020['PPD'] || 0) - (seats2016['PPD'] || 0)
		};
	});

	function handleStepEnter(response: { index: number }) {
		currentStep = response.index;

		switch (response.index) {
			case 0: // Intro
			case 1: // House vs Senate
				activeViz = 'competitiveness';
				break;
			case 2: // Competitiveness map
				activeViz = 'competitiveness';
				break;
			case 3: // Margin distribution
				activeViz = 'marginDist';
				break;
			case 4: // Closest races
				activeViz = 'closestRaces';
				break;
			case 5: // Seat composition trend
				activeViz = 'seatTrend';
				break;
			case 6: // Flipped districts
				activeViz = 'flipped';
				break;
			case 7: // Third party presence
				activeViz = 'thirdParty';
				break;
			case 8: // Local issues
				activeViz = 'competitiveness';
				break;
			case 9: // Path to majority
				activeViz = 'seatTrend';
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
				Puerto Rico's House of Representatives has 40 district seats, each representing
				a distinct slice of the island. Unlike the Senate's regional districts or the
				governor's island-wide race, House elections are intensely local affairs where
				a few hundred votes can decide who represents your community.
			</p>
		</div>
	</header>

	<ScrollySection offset={0.6} onStepEnter={handleStepEnter}>
		{#snippet graphic()}
			<div class="viz-container">
				{#if loading}
					<p class="loading">Loading data...</p>
				{:else if activeViz === 'competitiveness'}
					<h3 class="viz-title">District Competitiveness (2020)</h3>
					<BarChart
						data={competitivenessBarData()}
						width={420}
						height={300}
						horizontal={true}
						valueFormat={(v) => `${v} districts`}
						showValues={true}
					/>
					<Legend
						items={[
							{ label: 'PNP advantage', color: PARTY_COLORS.PNP },
							{ label: 'Tossup', color: CATEGORY_COLORS[5] },
							{ label: 'PPD advantage', color: PARTY_COLORS.PPD }
						]}
					/>
				{:else if activeViz === 'seatTrend'}
					<h3 class="viz-title">House Seat Composition</h3>
					<LineChart
						series={seatTrendData()}
						width={420}
						height={300}
						xLabel="Election Year"
						yLabel="Seats Won"
						xFormat={(v) => String(v)}
						yFormat={(v) => String(Math.round(v))}
						showArea={true}
					/>
					<p class="viz-note">
						PNP lost {stats().seatSwing > 0 ? stats().seatSwing : -stats().seatSwing} seats from 2016 to 2020
					</p>
				{:else if activeViz === 'marginDist'}
					<h3 class="viz-title">Victory Margins (2020)</h3>
					<BarChart
						data={marginDistBarData()}
						width={420}
						height={280}
						horizontal={false}
						valueFormat={(v) => `${v} races`}
						showValues={true}
					/>
					<p class="viz-note">
						{marginDistribution['2020']?.['0-2'] || 0} races decided by less than 2%
					</p>
				{:else if activeViz === 'closestRaces'}
					<h3 class="viz-title">Closest Races (2020)</h3>
					<BarChart
						data={closestRacesBarData()}
						width={420}
						height={320}
						horizontal={true}
						valueFormat={(v) => `${v.toFixed(1)}%`}
						showValues={true}
					/>
					<p class="viz-note">Margin of victory by district</p>
				{:else if activeViz === 'flipped'}
					<h3 class="viz-title">Districts That Flipped (2016-2020)</h3>
					<BarChart
						data={flippedBarData()}
						width={420}
						height={380}
						horizontal={true}
						valueFormat={(v) => `${v > 0 ? '+' : ''}${v.toFixed(1)}pp`}
						showValues={true}
					/>
					<p class="viz-note">PNP margin shift (negative = PPD gain)</p>
				{:else if activeViz === 'thirdParty'}
					<h3 class="viz-title">Third-Party Vote Share (2020)</h3>
					<BarChart
						data={thirdPartyBarData()}
						width={420}
						height={320}
						horizontal={true}
						valueFormat={(v) => `${v.toFixed(1)}%`}
						showValues={true}
					/>
					<p class="viz-note">Top districts by MVC/PIP/PD combined vote</p>
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>The Most Local Level</h3>
			<p>
				The House of Representatives is where Puerto Rico politics gets personal.
				Each of the 40 districts has roughly <span class="stat">45,000</span> residents,
				small enough that a representative might know their constituents by name in
				the smaller precincts. This is the chamber where neighborhood issues—potholes,
				school funding, water service—dominate the agenda.
			</p>
			<p>
				Unlike the Senate (which uses 8 larger senatorial districts) or the
				governor's race (island-wide), House districts reflect the hyper-local
				political landscape. A district might encompass a single large municipality
				or stitch together parts of several smaller ones.
			</p>
			<p>
				The result is <span class="highlight">40 distinct political stories</span>,
				each shaped by local demographics, economic conditions, and community ties
				that don't always align with island-wide party trends.
			</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>House vs. Senate: A Different Game</h3>
			<p>
				The Senate's 8 senatorial districts elect 2 senators each (16 total),
				plus 11 at-large senators—27 members total. The House's 40 single-member
				districts create a fundamentally different dynamic: <span class="highlight">
				winner-take-all in each district</span>.
			</p>
			<p>
				In the Senate, proportional representation ensures minority parties get
				some seats. But in House districts, coming in second means nothing. A party
				can win 49% of the vote and still get zero seats from that district.
			</p>
			<p>
				This makes the House more susceptible to <span class="highlight">wave elections</span>:
				when one party has a good year, they can sweep competitive districts and
				build large majorities. When the tide turns, those gains can evaporate just
				as quickly—as PNP learned in 2020.
			</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>The Competitiveness Landscape</h3>
			<p>
				Of Puerto Rico's 40 House districts, the 2020 election revealed a surprisingly
				competitive landscape. <span class="stat">{stats().totalTossups}</span> districts—
				more than half—were decided by margins under 5 percentage points.
			</p>
			<p>
				Only <span class="stat">{(competitivenessData['2020']?.safe_pnp || 0) +
				(competitivenessData['2020']?.safe_ppd || 0)}</span> districts were truly
				"safe" with margins over 10%. The rest are battlegrounds where turnout,
				candidate quality, and local issues can swing the outcome.
			</p>
			<p>
				This volatility reflects Puerto Rico's fragmenting party system. When voters
				are willing to consider third parties, even historically safe districts
				become competitive. The old certainties of the PNP-PPD duopoly no longer hold.
			</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>How Close Are These Races?</h3>
			<p>
				The margin distribution tells a stark story: House races in Puerto Rico are
				knife-edge affairs. In 2020, <span class="stat">{marginDistribution['2020']?.['0-2'] || 0}</span>
				races were decided by less than 2%—often just a few hundred votes out of
				thousands cast.
			</p>
			<p>
				Another <span class="stat">{marginDistribution['2020']?.['2-5'] || 0}</span>
				races fell in the 2-5% range. Combined, that's {((marginDistribution['2020']?.['0-2'] || 0) +
				(marginDistribution['2020']?.['2-5'] || 0))} races—nearly half the chamber—
				where the outcome was genuinely uncertain.
			</p>
			<p>
				For campaign strategists, this means <span class="highlight">turnout operations matter
				enormously</span>. In a district with 20,000 voters, a 2% margin is just 400 votes.
				A good get-out-the-vote effort can easily swing that many.
			</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>The Closest Calls</h3>
			<p>
				The tightest race in 2020 was decided by just <span class="stat">
				{formatPercent(stats().closestMargin, 1)}</span>—a margin so slim that
				a recount could theoretically change the outcome. These razor-thin contests
				represent the ultimate test of democratic participation: every vote,
				literally, could be the deciding one.
			</p>
			<p>
				Districts like {closestRaces[0]?.district || 'District 31'} and
				{closestRaces[1]?.district || 'District 18'} exemplify the volatility of
				House races. These aren't ideological battlegrounds fought over big issues;
				they're communities where both parties have roughly equal support and
				elections become tests of mobilization.
			</p>
			<p>
				For the representatives who win these races, governing is a constant
				campaign. A few hundred unhappy constituents could cost them their seat
				in the next election.
			</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>The 2020 Earthquake</h3>
			<p>
				The 2020 election fundamentally reshaped the House. PNP went from controlling
				<span class="stat">{stats().pnpSeats2016}</span> seats in 2016 to just
				<span class="stat">{stats().pnpSeats2020}</span> in 2020—a loss of
				<span class="stat">{stats().pnpSeats2016 - stats().pnpSeats2020}</span> seats.
				PPD correspondingly surged from {stats().ppdSeats2016} to {stats().ppdSeats2020}.
			</p>
			<p>
				This wasn't a gradual shift; it was a <span class="highlight">wave election</span>.
				Frustration with the PNP government after Hurricane Maria, the Rosselló
				protests, and the pandemic combined to create a perfect storm of anti-incumbent
				sentiment. Competitive districts that had leaned PNP broke decisively for PPD.
			</p>
			<p>
				The question for 2024: was this a permanent realignment, or will the pendulum
				swing back? History suggests Puerto Rican voters are willing to punish
				both parties when they feel let down.
			</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>The Districts That Flipped</h3>
			<p>
				<span class="stat">{stats().flippedCount}</span> districts changed party control
				between 2016 and 2020. These flips weren't random—they followed a geographic
				pattern, with western and rural districts leading the shift away from PNP.
			</p>
			<p>
				The magnitude of some shifts was remarkable. Districts that PNP had won by
				comfortable margins in 2016 swung 15-20 percentage points to hand PPD
				decisive victories. This kind of volatility is unusual even in Puerto Rico's
				historically competitive elections.
			</p>
			<p>
				What drove these flips? The data suggests a combination of factors:
				<span class="highlight">incumbent fatigue</span>, economic conditions,
				post-Maria recovery disparities, and the rise of younger voters more willing
				to abandon traditional party loyalties.
			</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>The Third-Party Factor</h3>
			<p>
				While no third party won a House district seat in 2020, their presence
				reshaped the competitive landscape. In the top districts, MVC, PIP, and
				Proyecto Dignidad combined for <span class="stat">{formatPercent(stats().avgThirdParty, 1)}</span>
				of the vote or more.
			</p>
			<p>
				This third-party vote doesn't distribute evenly. Urban, educated districts
				showed the strongest third-party presence, particularly for MVC. These are
				the districts where traditional PNP-PPD loyalty has weakened most dramatically.
			</p>
			<p>
				For the major parties, this creates a strategic dilemma. Do they move toward
				the center to capture third-party-curious voters? Or do they double down on
				their base, hoping third parties split the opposition? The answer may
				determine who controls the House in 2024.
			</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>Local Issues, Local Politics</h3>
			<p>
				House races are won and lost on local issues that rarely make the news.
				Infrastructure—roads, water, electricity—dominates constituent concerns
				in many districts. Post-Maria, these concerns became even more acute:
				which representative can actually deliver recovery funds?
			</p>
			<p>
				In rural districts, agricultural policy and land use matter. In urban districts,
				housing costs and public safety take precedence. Representatives who can
				credibly address these <span class="highlight">kitchen-table concerns</span>
				build personal brands that can survive island-wide party swings.
			</p>
			<p>
				This is why some representatives hold their seats for decades while others
				are one-and-done. The best House members understand that their job is
				part legislator, part social worker, part constituent services office.
				Those who treat it as just a stepping stone rarely last.
			</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>The Path to Majority</h3>
			<p>
				Control of the House requires <span class="stat">21 seats</span>—a simple
				majority of the 40 districts (plus at-large seats bring the total chamber
				to 51). With 23 tossup districts in 2020, the battleground is vast.
			</p>
			<p>
				For PNP, recovering their 2016 majority means winning back flipped districts
				while defending their remaining strongholds. For PPD, it means consolidating
				2020 gains and proving they can govern effectively. For third parties,
				the goal is breaking through to win actual seats, not just influence margins.
			</p>
			<p>
				The math is unforgiving: there are only so many truly competitive districts.
				Winning them all—or losing them all—is the difference between governing
				and opposition. In Puerto Rico's House, the battlefield is small, but the
				stakes are enormous.
			</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>40 Stories, One Chamber</h2>
			<p>
				Each of Puerto Rico's 40 House districts tells a unique political story.
				Some are PNP strongholds rooted in statehood sentiment and urban professional
				voters. Others are PPD bastions where autonomy politics and rural traditions
				hold sway. And increasingly, many are genuinely competitive spaces where
				either party—or emerging third parties—could win.
			</p>
			<p>
				Understanding the House requires zooming in: not just to districts, but to
				precincts, neighborhoods, and communities. It's the most granular level of
				Puerto Rican democracy, where every vote truly counts and local issues
				shape island-wide outcomes.
			</p>

			<!-- Summary Stats Box -->
			{#if !loading && stats()}
				<div class="stats-summary">
					<h3>House Elections: 2020 Snapshot</h3>
					<div class="stats-grid">
						<div class="stat-item">
							<span class="stat-value">{stats().totalTossups}</span>
							<span class="stat-label">Tossup Districts</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{stats().flippedCount}</span>
							<span class="stat-label">Districts Flipped</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{stats().pnpSeats2016 - stats().pnpSeats2020}</span>
							<span class="stat-label">PNP Seats Lost</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{formatPercent(stats().closestMargin, 1)}</span>
							<span class="stat-label">Closest Margin</span>
						</div>
					</div>
				</div>
			{/if}

			<!-- Party Legend -->
			<div class="party-legend">
				<div class="party-item">
					<span class="party-dot" style="background: {PARTY_COLORS.PNP}"></span>
					PNP: {stats().pnpSeats2020} seats (2020)
				</div>
				<div class="party-item">
					<span class="party-dot" style="background: {PARTY_COLORS.PPD}"></span>
					PPD: {stats().ppdSeats2020} seats (2020)
				</div>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/senate" class="nav-link prev">
					<span class="nav-direction">Previous</span>
					<span class="nav-title">The Senate Districts</span>
				</a>
				<a href="{base}/chapters/future" class="nav-link next">
					<span class="nav-direction">Next Chapter</span>
					<span class="nav-title">Puerto Rico's Electoral Future</span>
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

	.chapter-header h1 {
		margin-bottom: var(--space-lg);
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

	.viz-note {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin-top: var(--space-md);
		font-style: italic;
		text-align: center;
	}

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
		grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
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

	.party-legend {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: var(--space-md);
		margin: var(--space-xl) 0;
	}

	.party-item {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.party-dot {
		width: 12px;
		height: 12px;
		border-radius: 50%;
		flex-shrink: 0;
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
</style>
