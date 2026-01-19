<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { ChoroplethMap } from '$lib/components/maps';
	import { BarChart, ScatterPlot } from '$lib/components/charts';
	import { Legend } from '$lib/components/ui';
	import { PARTY_COLORS, createDivergingScale, createSequentialScale } from '$lib/utils/colors';
	import { formatPercent, formatNumber, formatPercentChange } from '$lib/utils/format';

	const chapterNum = 8;
	const chapterTitle = '78 Battlegrounds';
	const totalSteps = 11;

	let currentStep = $state(0);
	let activeViz = $state<'swingMap' | 'competitivenessMap' | 'scatter' | 'bar' | 'historicalBar'>('swingMap');
	let loading = $state(true);
	let yearsCompared = $state<number[]>([2016, 2020]);

	// Data loaded from API
	let swingData = $state<Record<string, number>>({});
	let margins2016 = $state<Record<string, number>>({});
	let margins2020 = $state<Record<string, number>>({});
	let topSwing = $state<Array<{ municipality: string; swing: number; direction: string }>>([]);

	// Municipality population data (approximate for weighting)
	const populationData: Record<string, number> = {
		'San Juan': 342259, 'Bayamón': 169269, 'Carolina': 146984, 'Ponce': 132502,
		'Caguas': 124606, 'Guaynabo': 83728, 'Arecibo': 82880, 'Mayagüez': 71083,
		'Toa Baja': 68767, 'Trujillo Alto': 62852, 'Aguadilla': 53298, 'Vega Baja': 51876,
		'Humacao': 51675, 'Toa Alta': 50142, 'Fajardo': 48892, 'Canóvanas': 47304,
		'Yauco': 45105, 'Guayama': 41706, 'Cayey': 44530, 'Río Grande': 46274,
		'Isabela': 40423, 'Manatí': 38570, 'Dorado': 36141, 'Hatillo': 37610,
		'Cabo Rojo': 46538, 'Juncos': 39128, 'Vega Alta': 37005, 'Coamo': 37597,
		'San Sebastián': 36853, 'Salinas': 26510, 'Las Piedras': 36113, 'Cidra': 39675,
		'Gurabo': 38477, 'Camuy': 31463, 'Yabucoa': 30426, 'Aguada': 37516,
		'San Lorenzo': 35961, 'Aibonito': 23457, 'Naguabo': 26584, 'Guánica': 14740,
		'Corozal': 33894, 'Naranjito': 28557, 'Patillas': 16962, 'Loíza': 24553,
		'Barranquitas': 27725, 'Maunabo': 10699, 'Añasco': 24853, 'Juana Díaz': 43982,
		'Villalba': 21651, 'Ciales': 15828, 'Quebradillas': 22643, 'Moca': 35343,
		'Arroyo': 16888, 'Santa Isabel': 21245, 'Hormigueros': 14858, 'Orocovis': 19696,
		'San Germán': 30227, 'Utuado': 26778, 'Florida': 11317, 'Barceloneta': 21809,
		'Morovis': 29509, 'Peñuelas': 19178, 'Aguas Buenas': 25648, 'Jayuya': 14043,
		'Ceiba': 11307, 'Lajas': 22659, 'Lares': 24927, 'Rincón': 13897,
		'Luquillo': 17665, 'Adjuntas': 17269, 'Vieques': 8249, 'Guayanilla': 17623,
		'Las Marías': 8347, 'Cataño': 22066, 'Culebra': 1818, 'Maricao': 5361,
		'Sabana Grande': 21427
	};

	// Load chapter data
	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/chapters/battlegrounds.json`);
			const data = await response.json();

			swingData = data.swing_by_municipality || {};
			margins2016 = data.margins_by_year?.['2016'] || {};
			margins2020 = data.margins_by_year?.['2020'] || {};
			topSwing = data.top_swing || [];
			yearsCompared = data.years_compared || [2016, 2020];
		} catch (err) {
			console.error('Failed to load battlegrounds data:', err);
		} finally {
			loading = false;
		}
	});

	// Color scales
	const swingColorScale = createDivergingScale([-15, 0, 15]);
	const competitivenessColorScale = createSequentialScale([0, 20]);

	// Computed statistics
	let stats = $derived(() => {
		const swingValues = Object.values(swingData);
		const margin2020Values = Object.values(margins2020);

		// Count by competitiveness bands
		const tossups = margin2020Values.filter(m => Math.abs(m) < 5).length;
		const lean = margin2020Values.filter(m => Math.abs(m) >= 5 && Math.abs(m) < 10).length;
		const safe = margin2020Values.filter(m => Math.abs(m) >= 10).length;

		// Count PNP vs PPD winners in 2020
		const pnpWins = margin2020Values.filter(m => m > 0).length;
		const ppdWins = margin2020Values.filter(m => m < 0).length;

		// Average swing
		const avgSwing = swingValues.length > 0
			? swingValues.reduce((a, b) => a + b, 0) / swingValues.length
			: 0;

		// Count municipalities that flipped
		const flipped = Object.keys(swingData).filter(muni => {
			const m2016 = margins2016[muni];
			const m2020 = margins2020[muni];
			if (m2016 === undefined || m2020 === undefined) return false;
			return (m2016 > 0 && m2020 < 0) || (m2016 < 0 && m2020 > 0);
		}).length;

		// Big swings (>10pp)
		const bigSwings = swingValues.filter(s => Math.abs(s) > 10).length;

		return { tossups, lean, safe, pnpWins, ppdWins, avgSwing, flipped, bigSwings };
	});

	// Map data for different visualizations
	let mapData = $state(new Map<string, number>());
	let mapTitle = $state('');

	// Competitiveness data (based on 2020 margin)
	function getCompetitivenessData(): Record<string, number> {
		const result: Record<string, number> = {};
		for (const [muni, margin] of Object.entries(margins2020)) {
			// Map absolute margin to competitiveness (lower = more competitive)
			result[muni] = Math.abs(margin);
		}
		return result;
	}

	// "Decider" municipalities - large AND competitive
	function getDeciderMunicipalities(): string[] {
		const threshold = 30000; // Population threshold
		const marginThreshold = 8; // Margin threshold
		return Object.keys(margins2020).filter(muni => {
			const pop = populationData[muni] || 0;
			const margin = Math.abs(margins2020[muni] || 100);
			return pop >= threshold && margin <= marginThreshold;
		}).sort((a, b) => (populationData[b] || 0) - (populationData[a] || 0));
	}

	// Top swing bar chart data
	let topSwingBarData = $derived(() => {
		return topSwing.slice(0, 10).map(item => ({
			label: item.municipality,
			value: Math.abs(item.swing),
			color: item.direction === 'PNP' ? PARTY_COLORS.PNP : PARTY_COLORS.PPD
		}));
	});

	// Scatter plot data: population vs margin
	let scatterData = $derived(() => {
		return Object.keys(margins2020)
			.filter(muni => populationData[muni])
			.map(muni => {
				const margin = margins2020[muni];
				const pop = populationData[muni];
				return {
					x: pop / 1000, // Population in thousands
					y: Math.abs(margin),
					label: muni,
					color: margin > 0 ? PARTY_COLORS.PNP : PARTY_COLORS.PPD,
					size: Math.abs(swingData[muni] || 0) / 2 + 4 // Size by swing
				};
			});
	});

	// Flipped municipalities for highlighting
	let flippedMunis = $derived(() => {
		return Object.keys(swingData).filter(muni => {
			const m2016 = margins2016[muni];
			const m2020 = margins2020[muni];
			if (m2016 === undefined || m2020 === undefined) return false;
			return (m2016 > 0 && m2020 < 0) || (m2016 < 0 && m2020 > 0);
		});
	});

	// Historical comparison bar data (PPD gains on one side, PNP on other)
	let historicalBarData = $derived(() => {
		const sorted = [...topSwing].sort((a, b) => a.swing - b.swing);
		const ppdGains = sorted.filter(s => s.swing < 0).slice(0, 5);
		const pnpGains = sorted.filter(s => s.swing > 0).slice(-5).reverse();

		return [...ppdGains, ...pnpGains].map(item => ({
			label: item.municipality,
			value: item.swing,
			color: item.direction === 'PNP' ? PARTY_COLORS.PNP : PARTY_COLORS.PPD
		}));
	});

	// Decider municipalities data for highlighting
	let deciderMunis = $derived(getDeciderMunicipalities());

	// Legend items for competitiveness
	const competitivenessLegendItems = [
		{ label: 'Tossup (<5%)', color: '#4a9eda' },
		{ label: 'Lean (5-10%)', color: '#8fc4eb' },
		{ label: 'Safe (>10%)', color: '#d1e5f0' }
	];

	function handleStepEnter(response: { index: number }) {
		currentStep = response.index;

		switch (response.index) {
			case 0: // Intro
				activeViz = 'swingMap';
				mapData = new Map();
				mapTitle = '';
				break;
			case 1: // What is swing
				activeViz = 'swingMap';
				mapData = new Map();
				mapTitle = 'Understanding Swing';
				break;
			case 2: // Show full swing map
				activeViz = 'swingMap';
				mapData = new Map(Object.entries(swingData));
				mapTitle = `PNP Swing: ${yearsCompared[0]} → ${yearsCompared[1]}`;
				break;
			case 3: // Western shift
				activeViz = 'swingMap';
				mapData = new Map(Object.entries(swingData));
				mapTitle = 'The Western Shift';
				break;
			case 4: // Competitiveness classification
				activeViz = 'competitivenessMap';
				mapData = new Map(Object.entries(getCompetitivenessData()));
				mapTitle = 'Competitiveness: 2020 Margins';
				break;
			case 5: // The deciders
				activeViz = 'scatter';
				mapTitle = 'The Deciders: Size vs. Competitiveness';
				break;
			case 6: // Scatter intro
				activeViz = 'scatter';
				mapTitle = 'Electoral Weight Analysis';
				break;
			case 7: // Top swing bar
				activeViz = 'bar';
				mapTitle = 'Biggest Swings 2016-2020';
				break;
			case 8: // Flipped municipalities
				activeViz = 'historicalBar';
				mapTitle = 'Who Flipped? PPD vs PNP Gains';
				break;
			case 9: // Third party dimension
				activeViz = 'competitivenessMap';
				mapData = new Map(Object.entries(getCompetitivenessData()));
				mapTitle = 'The Three-Way Race';
				break;
			case 10: // Conclusion
				activeViz = 'swingMap';
				mapData = new Map(Object.entries(swingData));
				mapTitle = 'The 2024 Battlefield';
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
				Puerto Rico has 78 municipalities, each with its own political character.
				Some are strongholds where campaigns barely bother; others are swing towns
				where elections are won and lost. Think like a campaign strategist:
				where would you spend your final weekend before Election Day?
			</p>
		</div>
	</header>

	<ScrollySection offset={0.6} onStepEnter={handleStepEnter}>
		{#snippet graphic()}
			<div class="viz-container">
				{#if loading}
					<p class="loading">Loading data...</p>
				{:else if activeViz === 'swingMap'}
					<h3 class="viz-title">{mapTitle}</h3>
					<ChoroplethMap
						data={mapData}
						colorScale={swingColorScale}
						tooltipFormat={(name, value) =>
							value !== undefined
								? `${name}: ${value > 0 ? '+' : ''}${value.toFixed(1)}pp swing`
								: name
						}
					/>
					{#if mapData.size > 0}
						<div class="legend">
							<div class="legend-scale">
								<span style="background: {swingColorScale(-12)}"></span>
								<span style="background: {swingColorScale(-6)}"></span>
								<span style="background: {swingColorScale(0)}"></span>
								<span style="background: {swingColorScale(6)}"></span>
								<span style="background: {swingColorScale(12)}"></span>
							</div>
							<div class="legend-labels">
								<span>PPD +12</span>
								<span>No change</span>
								<span>PNP +12</span>
							</div>
						</div>
					{/if}
				{:else if activeViz === 'competitivenessMap'}
					<h3 class="viz-title">{mapTitle}</h3>
					<ChoroplethMap
						data={mapData}
						colorScale={(v) => {
							if (v < 5) return '#c41e3a';
							if (v < 10) return '#e8a87c';
							return '#f7f7f7';
						}}
						tooltipFormat={(name, value) =>
							value !== undefined
								? `${name}: ${value.toFixed(1)}% margin (${value < 5 ? 'Tossup' : value < 10 ? 'Lean' : 'Safe'})`
								: name
						}
					/>
					<div class="legend">
						<Legend
							items={[
								{ label: 'Tossup (<5%)', color: '#c41e3a' },
								{ label: 'Lean (5-10%)', color: '#e8a87c' },
								{ label: 'Safe (>10%)', color: '#f7f7f7' }
							]}
							title="Competitiveness"
						/>
					</div>
				{:else if activeViz === 'scatter'}
					<h3 class="viz-title">{mapTitle}</h3>
					<ScatterPlot
						data={scatterData()}
						width={450}
						height={350}
						xLabel="Population (thousands)"
						yLabel="Margin of Victory (%)"
						xFormat={(v) => v.toFixed(0) + 'K'}
						yFormat={(v) => v.toFixed(1) + '%'}
						showRegression={true}
					/>
					<p class="viz-note">
						Bubble size = swing magnitude | Color = winner
					</p>
				{:else if activeViz === 'bar'}
					<h3 class="viz-title">{mapTitle}</h3>
					<BarChart
						data={topSwingBarData()}
						width={420}
						height={320}
						horizontal={true}
						valueFormat={(v) => `${v.toFixed(1)}pp`}
					/>
				{:else if activeViz === 'historicalBar'}
					<h3 class="viz-title">{mapTitle}</h3>
					<BarChart
						data={historicalBarData()}
						width={420}
						height={320}
						horizontal={true}
						valueFormat={(v) => `${v > 0 ? '+' : ''}${v.toFixed(1)}pp`}
					/>
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>The Campaign Strategist's View</h3>
			<p>
				Every election cycle, campaign managers face the same question:
				<span class="highlight">where do we invest our limited resources?</span>
				The answer lies in understanding which municipalities truly decide elections.
			</p>
			<p>
				Not all municipalities are created equal. Some have voted the same way for
				decades—they're "banked" votes that won't change. Others swing wildly between
				elections, shifting by 10 or even 15 percentage points in a single cycle.
			</p>
			<p>
				This chapter maps Puerto Rico's electoral battlefield: the strongholds,
				the swing towns, and the "deciders" that determine who governs from La Fortaleza.
			</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>What Makes a Municipality "Swing"?</h3>
			<p>
				A swing municipality isn't just one where the margin is close—it's one where
				<span class="highlight">voter preferences change significantly between elections</span>.
				A town with a 2% margin that stays at 2% isn't swing; it's a stable tossup.
			</p>
			<p>
				True swing municipalities show volatility: perhaps they went PNP +8 in one election,
				then PPD +4 in the next. This 12-point swing signals that voters there are
				persuadable—or that mobilization can make the difference.
			</p>
			<p>
				Campaign strategists separate municipalities into three categories: safe (margin &gt; 10%),
				lean (5-10%), and tossup (&lt; 5%). But within tossups, some are stable while others
				are genuinely volatile.
			</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>The {yearsCompared[0]}-{yearsCompared[1]} Swing Map</h3>
			<p>
				This map shows how each municipality's PNP margin changed between {yearsCompared[0]}
				and {yearsCompared[1]}. <span style="color: {PARTY_COLORS.PNP}">Blue</span> indicates
				the PNP gained ground; <span style="color: {PARTY_COLORS.PPD}">red</span> shows PPD gains.
			</p>
			<p>
				{#if stats()}
					The data reveals a striking pattern: <span class="stat">{stats().bigSwings}</span> municipalities
					swung by more than 10 percentage points—unprecedented volatility that suggests
					a realigning electorate. The average swing was <span class="stat">{formatPercentChange(stats().avgSwing)}</span>
					toward PPD.
				{/if}
			</p>
			<p>
				Most dramatically, <span class="stat">{stats()?.flipped || 0}</span> municipalities
				actually flipped parties—switching from PNP-leaning to PPD-leaning or vice versa.
				These flips aren't random; they tell us where the political winds are blowing.
			</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>The Western Shift</h3>
			<p>
				The most dramatic swings occurred in Puerto Rico's western municipalities.
				Towns like <span class="highlight">Lares (-16pp)</span>, <span class="highlight">Isabela (-16pp)</span>,
				and <span class="highlight">Aguadilla (-14pp)</span> showed massive movement toward PPD—or
				more accurately, away from the incumbent PNP.
			</p>
			<p>
				This western shift wasn't just partisan realignment. These municipalities also showed
				the strongest growth for third parties like Movimiento Victoria Ciudadana and Proyecto Dignidad.
				In a traditional two-party system, a 16-point swing means PNP lost and PPD gained.
				But in 2020, much of that "swing" went to emerging parties.
			</p>
			<p>
				The geographic clustering suggests common factors at play: economic conditions,
				post-Maria recovery, and the rise of a new political generation that rejects
				the traditional PNP/PPD binary.
			</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>Classifying the Battlefield</h3>
			<p>
				Beyond swing, strategists need to know current competitiveness. This map
				classifies each municipality by its 2020 margin of victory:
				<span style="color: #c41e3a">Tossup</span> (&lt; 5%),
				<span style="color: #e8a87c">Lean</span> (5-10%),
				and <span style="color: #f7f7f7">Safe</span> (&gt; 10%).
			</p>
			<p>
				{#if stats()}
					In 2020, <span class="stat">{stats().tossups}</span> municipalities were true tossups,
					<span class="stat">{stats().lean}</span> leaned one way, and <span class="stat">{stats().safe}</span>
					were safely in one camp. PNP won <span class="stat">{stats().pnpWins}</span> municipalities
					outright; PPD took <span class="stat">{stats().ppdWins}</span>.
				{/if}
			</p>
			<p>
				The tossup municipalities—places like <span class="highlight">Juncos</span>,
				<span class="highlight">Coamo</span>, and <span class="highlight">Vega Alta</span>—are
				where 2024 will be decided. A candidate who sweeps the tossups while holding
				their base wins the governorship.
			</p>
		</Step>

		<Step active={currentStep === 5} index={5} variant="callout">
			<h3>The Deciders</h3>
			<p>
				Some municipalities matter more than others—not because of margins, but because
				of size. The "deciders" are municipalities that are both
				<span class="highlight">large enough to matter</span> and
				<span class="highlight">competitive enough to swing</span>.
			</p>
			<p>
				{#if deciderMunis.length > 0}
					<span class="stat">{deciderMunis.length}</span> decider municipalities identified:
					{deciderMunis.slice(0, 5).join(', ')}{deciderMunis.length > 5 ? '...' : ''}.
					Populations over 30,000, margins under 8%.
				{/if}
			</p>
			<p>
				If you're running for governor with one week left before Election Day,
				this is your target list.
			</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>Electoral Weight Analysis</h3>
			<p>
				This scatter plot visualizes the strategic landscape. The X-axis shows population
				(how many voters a municipality has), and the Y-axis shows margin (how competitive it is).
				Each dot is sized by how much it swung in 2016-2020.
			</p>
			<p>
				The <span class="highlight">bottom-right quadrant</span> is campaign gold: large populations
				with tight margins. Points in this zone—San Juan, Carolina, Caguas—are where elections
				are won. The top-right quadrant (large but safe) can be taken for granted;
				the left side (small populations) won't move the needle regardless of competitiveness.
			</p>
			<p>
				Notice how the biggest bubbles (largest swings) cluster in the middle-left:
				smaller municipalities with moderate margins. These towns are volatile but
				don't have enough votes to be decisive on their own.
			</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>The Biggest Swings</h3>
			<p>
				Here are the ten municipalities with the largest swings from 2016 to 2020.
				The direction tells the story: <span style="color: {PARTY_COLORS.PPD}">red bars</span>
				show PPD gains, <span style="color: {PARTY_COLORS.PNP}">blue bars</span> show PNP gains.
			</p>
			<p>
				The asymmetry is striking. Nine of the top ten swings favored PPD—a wave election
				that swept across traditionally PNP-leaning towns. Only <span class="highlight">Patillas</span>
				(+13pp) bucked the trend with a massive PNP swing, flipping from PPD to PNP.
			</p>
			<p>
				What drove these swings? Post-Maria frustration, economic decline, corruption scandals,
				and the rise of third-party alternatives all played roles. The question for 2024:
				will these shifts stick, or will the pendulum swing back?
			</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>Who Actually Flipped?</h3>
			<p>
				Swing is one thing; actually flipping from one party to another is more dramatic.
				{#if flippedMunis.length > 0}
					<span class="stat">{flippedMunis.length}</span> municipalities changed hands between
					2016 and 2020, shifting from PNP-leaning to PPD-leaning or vice versa.
				{/if}
			</p>
			<p>
				Notable flips include <span class="highlight">Isabela</span> (PNP +2 to PPD +14),
				<span class="highlight">Barceloneta</span> (PNP +0.3 to PPD +8), and
				<span class="highlight">Aguadilla</span> (PNP +14 to dead even). These weren't
				marginal shifts—they represent complete reversals of political identity.
			</p>
			<p>
				Flipped municipalities are the canaries in the coal mine. They signal where
				realignment is happening and often predict broader trends. Watch these towns
				closely in 2024.
			</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>Beyond the Binary: Three-Way Races</h3>
			<p>
				Traditional swing analysis assumes a two-party system: votes move between PNP and PPD.
				But 2020 broke that model. Third parties—particularly
				<span style="color: {PARTY_COLORS.MVC}">MVC</span> and
				<span style="color: {PARTY_COLORS.PD}">Proyecto Dignidad</span>—captured
				significant vote shares, especially among younger voters.
			</p>
			<p>
				This creates a new dimension of "swing." A municipality can now shift in multiple
				directions: PNP↔PPD (traditional swing), major party↔third party (protest swing),
				or even between third parties (ideological sorting). The old maps don't capture
				this complexity.
			</p>
			<p>
				In 2024, strategists must ask not just "will this municipality swing?" but
				"swing to whom?" A frustrated PNP voter might go PPD, MVC, PD, or stay home.
				Understanding these flows is the new frontier of Puerto Rican electoral analysis.
			</p>
		</Step>

		<Step active={currentStep === 10} index={10}>
			<h3>The 2024 Battlefield</h3>
			<p>
				Looking ahead to 2024, the battleground map has shifted. The western municipalities
				that swung hard toward PPD in 2020 may now be PPD strongholds—or they may swing back
				if conditions change. The metropolitan San Juan area, with its mix of competitive
				suburbs, remains the decisive theater.
			</p>
			<p>
				Key municipalities to watch: <span class="highlight">Carolina</span> (the largest
				tossup), <span class="highlight">Caguas</span> (central mountain bellwether),
				<span class="highlight">Bayamón</span> (suburban swing), and <span class="highlight">Ponce</span>
				(southern anchor). Whoever wins three of these four likely wins the governorship.
			</p>
			<p>
				The fundamental question: was 2020 a realigning election that reshaped Puerto Rico's
				political geography, or a wave election that will recede? The battleground municipalities
				will give us the answer.
			</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>The Strategic Map</h2>
			<p>
				Puerto Rico's 78 municipalities each tell a political story. Some are
				reliable strongholds, delivering predictable margins election after election.
				Others are volatile swing towns where campaigns are won and lost in the final days.
				This geography matters to anyone who wants to predict—or influence—Puerto Rican elections.
			</p>
			<p>
				But municipality-level analysis only goes so far. Within large municipalities,
				individual precincts can vary by 30 or more percentage points. The next chapter
				goes deeper, exploring the precinct-level patterns that reveal Puerto Rico's
				true electoral fabric.
			</p>

			<!-- Summary Stats Box -->
			{#if stats()}
				<div class="stats-summary">
					<h3>Key Statistics: {yearsCompared[0]}-{yearsCompared[1]}</h3>
					<div class="stats-grid">
						<div class="stat-item">
							<span class="stat-value">{stats().flipped}</span>
							<span class="stat-label">Municipalities Flipped</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{stats().bigSwings}</span>
							<span class="stat-label">Swung >10pp</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{stats().tossups}</span>
							<span class="stat-label">Tossups in 2020</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{formatPercentChange(stats().avgSwing)}</span>
							<span class="stat-label">Average Swing (toward PPD)</span>
						</div>
					</div>
				</div>
			{/if}

			<div class="sources">
			<h3>Sources</h3>
			<ul>
				<li><a href="https://ww2.ceepur.org/Home/EventosElectorales" target="_blank" rel="noopener">Comision Estatal de Elecciones de Puerto Rico (CEE)</a> - Municipality-level gubernatorial results 2016, 2020, 2024</li>
				<li><a href="https://www.census.gov/programs-surveys/popest.html" target="_blank" rel="noopener">U.S. Census Bureau</a> - Population estimates by municipality</li>
				<li>Puerto Rico Planning Board - Demographic and economic indicators by region</li>
				<li>Analysis methodology: Swing calculated as change in winning margin between elections</li>
			</ul>
		</div>

		<nav class="chapter-nav">
				<a href="{base}/chapters/fortaleza" class="nav-link prev">
					<span class="nav-direction">Previous</span>
					<span class="nav-title">La Fortaleza</span>
				</a>
				<a href="{base}/chapters/precincts" class="nav-link next">
					<span class="nav-direction">Next Chapter</span>
					<span class="nav-title">Down to the Precinct</span>
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
		animation: vizFadeIn 0.4s ease-out;
	}

	@keyframes vizFadeIn {
		from {
			opacity: 0;
			transform: scale(0.98);
		}
		to {
			opacity: 1;
			transform: scale(1);
		}
	}

	.loading {
		color: var(--color-text-muted);
		font-style: italic;
	}

	.viz-title {
		font-size: var(--text-xl);
		font-family: var(--font-display);
		font-weight: var(--font-semibold);
		color: var(--color-text);
		margin-bottom: var(--space-lg);
		text-align: center;
	}

	.viz-note {
		font-size: var(--text-sm);
		color: var(--color-text-light);
		margin-top: var(--space-lg);
		padding: var(--space-sm) var(--space-md);
		background: var(--color-surface-elevated);
		border-radius: var(--radius-md);
		line-height: 1.5;
	}

	.legend {
		margin-top: var(--space-xl);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-md);
		background: var(--color-surface-elevated);
		border-radius: var(--radius-md);
	}

	.legend-scale {
		display: flex;
		width: 260px;
		height: 14px;
		border-radius: var(--radius-sm);
		overflow: hidden;
		box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
	}

	.legend-scale span {
		flex: 1;
		transition: transform 0.2s ease;
	}

	.legend-scale span:hover {
		transform: scaleY(1.2);
	}

	.legend-labels {
		display: flex;
		justify-content: space-between;
		width: 260px;
		font-size: var(--text-sm);
		color: var(--color-text-light);
		font-weight: var(--font-medium);
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
