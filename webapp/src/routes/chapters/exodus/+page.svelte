<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { ChoroplethMap } from '$lib/components/maps';
	import { LineChart } from '$lib/components/charts';
	import { BarChart } from '$lib/components/charts';
	import { ScatterPlot } from '$lib/components/charts';
	import { createDivergingScale, DIVERGING_COLORS, CATEGORY_COLORS } from '$lib/utils/colors';
	import { formatPercent, formatCompact, formatNumber, formatPercentChange } from '$lib/utils/format';

	// Chapter metadata
	const chapterNum = 1;
	const chapterTitle = 'The Great Exodus';
	const totalSteps = 12;

	// State
	let currentStep = $state(0);
	let mapData = $state(new Map<string, number>());
	let mapTitle = $state('');
	let loading = $state(true);

	// Data types
	interface MunicipalityData {
		population_2010: number;
		population_2020: number;
		population_change: number;
		percent_change: number;
		median_income: number;
		poverty_rate: number;
	}

	interface TimelinePoint {
		year: number;
		population: number;
	}

	interface ExodusData {
		municipalities: Record<string, MunicipalityData>;
		island_timeline: {
			data: TimelinePoint[];
			peak_year: number;
			peak_population: number;
			current_population: number;
			total_loss: number;
			percent_decline: number;
		};
		summary_stats: {
			total_municipalities: number;
			municipalities_with_loss: number;
			municipalities_with_gain: number;
			average_percent_change: number;
			most_affected_municipality: string;
			most_affected_percent: number;
			least_affected_municipality: string;
			total_population_loss_2010_2020: number;
		};
		metro_san_juan: {
			municipalities: string[];
			combined_loss: number;
			combined_2010: number;
			combined_2020: number;
			percent_change: number;
		};
		post_maria_exodus: {
			estimated_departures_2017_2018: number;
			top_destinations: string[];
			florida_puerto_rican_pop_2020: number;
		};
		demographic_shifts: {
			median_age_2010: number;
			median_age_2020: number;
			working_age_decline_percent: number;
			elderly_growth_percent: number;
		};
	}

	// Loaded data
	let exodusData = $state<ExodusData | null>(null);

	// Animated counter state
	let displayedPopulation = $state(3826878);
	let counterAnimating = $state(false);

	// Current visualization type
	let currentViz = $state<'map' | 'line' | 'bar' | 'scatter'>('map');

	// Load chapter data
	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/chapters/exodus.json`);
			const data: ExodusData = await response.json();
			exodusData = data;
		} catch (err) {
			console.error('Failed to load exodus data:', err);
		} finally {
			loading = false;
		}
	});

	// Derived data for visualizations
	let populationChangeData = $derived(() => {
		if (!exodusData) return {};
		const result: Record<string, number> = {};
		for (const [muni, data] of Object.entries(exodusData.municipalities)) {
			result[muni] = data.percent_change;
		}
		return result;
	});

	let povertyData = $derived(() => {
		if (!exodusData) return {};
		const result: Record<string, number> = {};
		for (const [muni, data] of Object.entries(exodusData.municipalities)) {
			result[muni] = -data.poverty_rate; // Negative for color scale
		}
		return result;
	});

	// Metro municipalities data
	const metroMunicipalities = ['San Juan', 'Bayamon', 'Carolina', 'Guaynabo', 'Catano', 'Trujillo Alto'];

	let metroChangeData = $derived(() => {
		const allData = populationChangeData();
		const result: Record<string, number> = {};
		for (const muni of metroMunicipalities) {
			if (allData[muni] !== undefined) {
				result[muni] = allData[muni];
			}
		}
		return result;
	});

	// Line chart data - population timeline
	let timelineSeries = $derived(() => {
		if (!exodusData?.island_timeline?.data) return [];
		return [{
			id: 'population',
			label: 'Puerto Rico Population',
			data: exodusData.island_timeline.data.map(d => ({
				x: d.year,
				y: d.population
			})),
			color: CATEGORY_COLORS[0]
		}];
	});

	// Bar chart data - top 10 municipalities by loss
	let topLossMunicipalities = $derived(() => {
		if (!exodusData) return [];
		const sorted = Object.entries(exodusData.municipalities)
			.sort((a, b) => a[1].population_change - b[1].population_change)
			.slice(0, 10);
		return sorted.map(([name, data]) => ({
			label: name,
			value: Math.abs(data.population_change),
			color: DIVERGING_COLORS[0]
		}));
	});

	// Scatter plot data - poverty vs population loss
	let povertyVsLossData = $derived(() => {
		if (!exodusData) return [];
		return Object.entries(exodusData.municipalities).map(([name, data]) => ({
			x: data.poverty_rate,
			y: Math.abs(data.percent_change),
			label: name,
			color: CATEGORY_COLORS[0],
			size: Math.sqrt(data.population_2020) / 30
		}));
	});

	// Color scales
	const populationColorScale = createDivergingScale([-30, -12, 0]);
	const povertyColorScale = createDivergingScale([-65, -45, -20]);

	// Animate population counter
	function animateCounter(target: number, duration: number = 2000) {
		if (counterAnimating) return;
		counterAnimating = true;
		const start = displayedPopulation;
		const startTime = Date.now();

		function update() {
			const elapsed = Date.now() - startTime;
			const progress = Math.min(elapsed / duration, 1);
			// Ease out quad
			const eased = 1 - (1 - progress) * (1 - progress);
			displayedPopulation = Math.round(start + (target - start) * eased);

			if (progress < 1) {
				requestAnimationFrame(update);
			} else {
				counterAnimating = false;
			}
		}
		requestAnimationFrame(update);
	}

	// Handle step changes
	function handleStepEnter(response: { index: number }) {
		currentStep = response.index;

		switch (response.index) {
			case 0:
				// Opening - empty map, counter at peak
				mapData = new Map();
				mapTitle = '';
				currentViz = 'map';
				animateCounter(3826878, 1500);
				break;
			case 1:
				// Show population timeline
				currentViz = 'line';
				mapTitle = 'Puerto Rico Population 2000-2020';
				break;
			case 2:
				// Counter ticks down
				currentViz = 'map';
				mapData = new Map();
				mapTitle = '';
				animateCounter(3285874, 3000);
				break;
			case 3:
				// Full map with all municipalities
				mapData = new Map(Object.entries(populationChangeData()));
				mapTitle = 'Population Change by Municipality (2010-2020)';
				currentViz = 'map';
				break;
			case 4:
				// Highlight worst-hit municipalities
				currentViz = 'bar';
				mapTitle = 'Municipalities with Greatest Population Loss';
				break;
			case 5:
				// Metro San Juan focus
				mapData = new Map(Object.entries(metroChangeData()));
				mapTitle = 'Metro San Juan';
				currentViz = 'map';
				break;
			case 6:
				// Hurricane Maria step - show sharp decline
				currentViz = 'line';
				mapTitle = 'The Maria Cliff (2017-2018)';
				break;
			case 7:
				// Poverty correlation
				currentViz = 'scatter';
				mapTitle = 'Poverty Rate vs Population Loss';
				break;
			case 8:
				// Poverty map
				mapData = new Map(Object.entries(povertyData()));
				mapTitle = 'Poverty Rate by Municipality';
				currentViz = 'map';
				break;
			case 9:
				// Who left - demographic shift narrative
				currentViz = 'map';
				mapData = new Map(Object.entries(populationChangeData()));
				mapTitle = 'An Aging Island';
				break;
			case 10:
				// Destinations
				currentViz = 'bar';
				mapTitle = 'Where They Went';
				break;
			case 11:
				// Electoral implications
				mapData = new Map(Object.entries(populationChangeData()));
				mapTitle = 'The New Electoral Map';
				currentViz = 'map';
				break;
		}
	}

	// Dynamic stats from data
	let sanJuanLoss = $derived(exodusData?.municipalities['San Juan']?.percent_change ?? -14.3);
	let ponceLoss = $derived(exodusData?.municipalities['Ponce']?.population_change ?? -31651);
	let guanicaLoss = $derived(exodusData?.municipalities['Guanica']?.percent_change ?? -31.7);
	let totalLoss = $derived(exodusData?.summary_stats?.total_population_loss_2010_2020 ?? 439915);
	let avgLoss = $derived(exodusData?.summary_stats?.average_percent_change ?? -12.5);
	let metroLoss = $derived(exodusData?.metro_san_juan?.combined_loss ?? -125767);
	let mariaExodus = $derived(exodusData?.post_maria_exodus?.estimated_departures_2017_2018 ?? 130000);
	let medianAge2020 = $derived(exodusData?.demographic_shifts?.median_age_2020 ?? 43.8);
	let workingAgeDecline = $derived(exodusData?.demographic_shifts?.working_age_decline_percent ?? -18.5);
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
				Since 2006, Puerto Rico has hemorrhaged more than half a million residents.
				Every week for almost two decades, planes have carried families away from
				the island they called home. This is the story of the greatest population
				collapse in modern American history.
			</p>
			<div class="lead-stats">
				<div class="stat-block">
					<span class="stat-value">{formatNumber(541004)}</span>
					<span class="stat-label">People Left</span>
				</div>
				<div class="stat-block">
					<span class="stat-value">14.1%</span>
					<span class="stat-label">Population Decline</span>
				</div>
				<div class="stat-block">
					<span class="stat-value">77 of 78</span>
					<span class="stat-label">Municipalities Lost Residents</span>
				</div>
			</div>
		</div>
	</header>

	<ScrollySection
		offset={0.6}
		onStepEnter={handleStepEnter}
	>
		{#snippet graphic()}
			<div class="viz-container">
				{#if loading}
					<p class="loading">Loading data...</p>
				{:else if currentViz === 'map'}
					{#if currentStep === 0 || currentStep === 2}
						<!-- Animated counter display -->
						<div class="counter-display">
							<div class="counter-label">Puerto Rico Population</div>
							<div class="counter-value">{formatNumber(displayedPopulation)}</div>
							<div class="counter-year">{currentStep === 0 ? '2004 (Peak)' : '2020'}</div>
						</div>
					{:else}
						<h3 class="viz-title">{mapTitle}</h3>
						<ChoroplethMap
							data={mapData}
							colorScale={currentStep === 8 ? povertyColorScale : populationColorScale}
							tooltipFormat={(name, value) => {
								if (currentStep === 8) {
									return value !== undefined
										? `${name}: ${Math.abs(value).toFixed(1)}% poverty`
										: name;
								}
								return value !== undefined
									? `${name}: ${value > 0 ? '+' : ''}${value.toFixed(1)}%`
									: name;
							}}
						/>
						{#if mapData.size > 0}
							<div class="legend">
								<span class="legend-label">{currentStep === 8 ? 'Poverty rate' : 'Population change'}</span>
								<div class="legend-scale">
									{#if currentStep === 8}
										<span style="background: {povertyColorScale(-60)}"></span>
										<span style="background: {povertyColorScale(-45)}"></span>
										<span style="background: {povertyColorScale(-30)}"></span>
									{:else}
										<span style="background: {populationColorScale(-25)}"></span>
										<span style="background: {populationColorScale(-12)}"></span>
										<span style="background: {populationColorScale(-3)}"></span>
									{/if}
								</div>
								<div class="legend-labels">
									{#if currentStep === 8}
										<span>60%+</span>
										<span>45%</span>
										<span>30%</span>
									{:else}
										<span>-25%</span>
										<span>-12%</span>
										<span>0%</span>
									{/if}
								</div>
							</div>
						{/if}
					{/if}
				{:else if currentViz === 'line'}
					<h3 class="viz-title">{mapTitle}</h3>
					<div class="chart-container">
						<LineChart
							series={timelineSeries()}
							width={500}
							height={350}
							xLabel="Year"
							yLabel="Population"
							showArea={true}
							showDots={true}
							xFormat={(v) => String(v)}
							yFormat={(v) => formatCompact(v)}
						/>
					</div>
					{#if currentStep === 6}
						<div class="chart-annotation">
							<span class="annotation-marker">Hurricane Maria</span>
							<span class="annotation-text">Sept 2017: 130,000+ leave in following year</span>
						</div>
					{/if}
				{:else if currentViz === 'bar'}
					<h3 class="viz-title">{mapTitle}</h3>
					<div class="chart-container">
						{#if currentStep === 10}
							<!-- Destinations bar chart -->
							<BarChart
								data={[
									{ label: 'Florida', value: 1200000, color: CATEGORY_COLORS[0] },
									{ label: 'New York', value: 750000, color: CATEGORY_COLORS[1] },
									{ label: 'Pennsylvania', value: 320000, color: CATEGORY_COLORS[2] },
									{ label: 'Texas', value: 210000, color: CATEGORY_COLORS[3] },
									{ label: 'Connecticut', value: 180000, color: CATEGORY_COLORS[4] }
								]}
								width={500}
								height={350}
								horizontal={true}
								valueFormat={(v) => formatCompact(v)}
							/>
							<p class="chart-note">Puerto Rican population in US states (2020)</p>
						{:else}
							<BarChart
								data={topLossMunicipalities()}
								width={500}
								height={400}
								horizontal={true}
								valueFormat={(v) => formatNumber(v)}
							/>
							<p class="chart-note">Absolute population loss 2010-2020</p>
						{/if}
					</div>
				{:else if currentViz === 'scatter'}
					<h3 class="viz-title">{mapTitle}</h3>
					<div class="chart-container">
						<ScatterPlot
							data={povertyVsLossData()}
							width={500}
							height={400}
							xLabel="Poverty Rate (%)"
							yLabel="Population Loss (%)"
							showRegression={true}
							xFormat={(v) => `${v.toFixed(0)}%`}
							yFormat={(v) => `${v.toFixed(0)}%`}
						/>
					</div>
					<p class="chart-note">Each point is a municipality. Size indicates population.</p>
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>A Nation at Its Peak</h3>
			<p>
				In 2004, Puerto Rico reached its population zenith: <span class="stat">3,826,878</span> people
				called the island home. Families had deep roots here, some stretching back generations.
				Towns bustled with activity. Schools were full. The future seemed bright.
			</p>
			<p>
				Then came the unraveling. What began as a trickle would become a flood, as economic crisis,
				natural disaster, and years of austerity combined to trigger the largest peacetime
				population exodus in American history.
			</p>
			<p class="emphasis">
				Every number you'll see represents a family that made the agonizing choice to leave home.
			</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>Two Decades of Decline</h3>
			<p>
				The population line tells a stark story. After decades of growth, Puerto Rico's population
				began falling in 2006, coinciding with the end of federal tax incentives that had drawn
				manufacturing to the island. The pharmaceutical companies that once provided good jobs
				started closing factories and laying off workers.
			</p>
			<p>
				Year after year, the line slopes downward. Between <span class="stat">2006 and 2020</span>,
				the island lost over <span class="stat">{formatNumber(541004)}</span> residents,
				a decline of <span class="stat">14.1%</span>. No other American jurisdiction has
				experienced anything comparable.
			</p>
			<p>
				To put this in perspective: if New York State lost population at the same rate,
				it would lose 2.7 million people in 14 years.
			</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>The Countdown</h3>
			<p>
				Watch the counter. Every digit represents lives uprooted, communities fractured,
				families separated. The decline from <span class="stat">3.8 million</span> to
				<span class="stat">3.3 million</span> played out across countless individual dramas.
			</p>
			<p>
				A teacher who couldn't find work after school consolidations. A nurse recruited by
				a Florida hospital offering double the salary. A family fleeing after Hurricane Maria
				destroyed their home. A young professional seeking opportunities that the stagnant
				economy couldn't provide.
			</p>
			<p>
				The numbers are staggering, but behind each decimal point is a human story.
			</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>The Geography of Loss</h3>
			<p>
				The exodus touched every corner of the island, but not equally. The map reveals
				profound geographic disparities. Of Puerto Rico's <span class="stat">78 municipalities</span>,
				<span class="stat">77</span> lost population between 2010 and 2020.
			</p>
			<p>
				The darkest reds mark communities that lost more than a quarter of their residents
				in just a decade. <span class="highlight">Guanica</span> suffered the steepest decline:
				<span class="stat">{guanicaLoss}%</span>, or nearly one in three residents gone.
				Southern coastal towns and mountain communities were hit hardest.
			</p>
			<p>
				The average municipality lost <span class="stat">{formatPercentChange(avgLoss)}</span> of
				its population. Only <span class="highlight">Rincon</span>, a beach town popular with
				surfers and American expats, managed to grow.
			</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>The Biggest Losses</h3>
			<p>
				In absolute terms, the largest cities lost the most people, simply because they had
				more to lose. But these numbers represent urban cores hollowing out, neighborhoods
				becoming ghost towns, apartment buildings standing empty.
			</p>
			<p>
				<span class="highlight">San Juan</span>, the capital, lost <span class="stat">{formatNumber(56665)}</span> people,
				a decline of <span class="stat">{sanJuanLoss}%</span>. The historic city that once pulsed
				with nearly 400,000 residents now has barely 340,000. Entire barrios have depopulated.
			</p>
			<p>
				<span class="highlight">Ponce</span>, Puerto Rico's second city, lost <span class="stat">{formatNumber(Math.abs(ponceLoss))}</span> residents,
				nearly one in five. Its ornate plazas and historic center now serve a fraction of
				their former population.
			</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>The Metro Exodus</h3>
			<p>
				The San Juan metropolitan area, home to nearly half the island's population,
				experienced a devastating outflow. The six municipalities that make up metro
				San Juan lost a combined <span class="stat">{formatNumber(Math.abs(metroLoss))}</span> residents
				between 2010 and 2020.
			</p>
			<p>
				<span class="highlight">Catano</span>, a working-class municipality across the bay
				from San Juan, lost <span class="stat">19.1%</span> of its population. <span class="highlight">Carolina</span>,
				home to the international airport, lost <span class="stat">13.3%</span>. Even
				wealthy <span class="highlight">Guaynabo</span> lost <span class="stat">8.6%</span>.
			</p>
			<p>
				These weren't just numbers on a census form. Schools closed. Businesses shuttered.
				Property values collapsed. The urban fabric itself began to fray.
			</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>The Maria Cliff</h3>
			<p>
				On September 20, 2017, Hurricane Maria made landfall as a Category 4 storm,
				devastating the island's infrastructure. The power grid collapsed completely.
				Thousands died. And then came the second wave of destruction: the exodus.
			</p>
			<p>
				In the year following Maria, an estimated <span class="stat">{formatNumber(mariaExodus)}</span> people
				left Puerto Rico. Look at the chart: the population line takes its steepest plunge
				between 2017 and 2018. This wasn't ordinary migration. It was displacement on
				a scale more commonly associated with war zones.
			</p>
			<p>
				Flights to the mainland were packed. FEMA hotels in Florida filled with families
				who had lost everything. Many who left "temporarily" never returned.
			</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>Poverty's Push</h3>
			<p>
				The scatter plot reveals a troubling correlation: municipalities with higher
				poverty rates generally experienced greater population losses. The regression
				line slopes upward, suggesting that economic desperation drove people away.
			</p>
			<p>
				This makes intuitive sense. If you can't find work, if your children's schools
				are closing, if the hospital is understaffed, why stay? The poorest communities
				had the least capacity to hold onto their residents.
			</p>
			<p>
				But the relationship isn't perfect. Some poor mountain towns held on better than
				wealthier coastal areas. Community ties, family land, and sheer determination
				kept some people rooted despite economic hardship.
			</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>The Poverty Map</h3>
			<p>
				Puerto Rico's poverty rate of <span class="stat">43%</span> is more than triple
				that of Mississippi, the poorest US state. The map shows this burden is not
				evenly distributed. Mountain municipalities like <span class="highlight">Guanica</span> (<span class="stat">64.8%</span> poverty),
				<span class="highlight">Adjuntas</span> (<span class="stat">62%</span>), and
				<span class="highlight">Vieques</span> (<span class="stat">59.5%</span>) face
				grinding, persistent deprivation.
			</p>
			<p>
				These are the communities most likely to lose young people seeking opportunity
				elsewhere. They're also the communities least able to provide services to the
				older, poorer population that remains behind.
			</p>
			<p>
				The exodus and poverty form a vicious cycle: people leave because of poverty,
				and their departure deepens the poverty of those who stay.
			</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>Who Left Behind</h3>
			<p>
				The exodus wasn't random. Working-age adults with education and skills were
				most likely to leave, seeking opportunities on the mainland. The island's
				median age jumped from <span class="stat">{exodusData?.demographic_shifts?.median_age_2010 ?? 36.9}</span> years
				in 2010 to <span class="stat">{medianAge2020}</span> years in 2020.
			</p>
			<p>
				The working-age population (25-54) declined by <span class="stat">{formatPercentChange(workingAgeDecline)}</span>,
				while the elderly population grew by <span class="stat">22.3%</span>. Puerto Rico
				is rapidly becoming one of the oldest jurisdictions in the United States.
			</p>
			<p>
				This demographic inversion creates its own problems: fewer workers to support
				more retirees, fewer tax dollars for public services, fewer young families to
				keep schools open and communities vibrant.
			</p>
		</Step>

		<Step active={currentStep === 10} index={10}>
			<h3>New Puerto Rican Capitals</h3>
			<p>
				Where did they go? Florida became the primary destination, its Puerto Rican
				population swelling to <span class="stat">1.2 million</span> by 2020. Central
				Florida in particular saw explosive growth, transforming the I-4 corridor
				into a major Puerto Rican population center.
			</p>
			<p>
				Traditional destinations like New York and Connecticut continued to draw
				migrants, while newer paths led to Pennsylvania and Texas. The Puerto Rican
				diaspora now outnumbers the island population, with over 5.8 million
				Puerto Ricans living on the mainland.
			</p>
			<p>
				These new communities maintain strong ties to the island. Remittances flow
				back. Family visits fill holiday flights. But the center of gravity of
				Puerto Rican life has shifted, perhaps permanently.
			</p>
		</Step>

		<Step active={currentStep === 11} index={11}>
			<h3>Electoral Implications</h3>
			<p>
				Population loss translates directly into political power loss. Between 2012
				and 2020, voter registration in Puerto Rico dropped by over <span class="stat">400,000</span>.
				The electorate that remains is older, poorer, and more rural.
			</p>
			<p>
				This demographic shift has profound implications for Puerto Rico's political
				future. Which municipalities will retain enough population to hold political
				sway? How will the remaining voters reshape the island's politics?
			</p>
			<p>
				The exodus didn't just empty neighborhoods. It rewrote the political map
				of Puerto Rico, changing the balance of power in ways that will take
				years to fully understand.
			</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>What We've Learned</h2>
			<p>
				Puerto Rico's population collapse is unprecedented in modern American history.
				Over half a million people left the island between 2006 and 2020, driven by
				economic crisis, natural disaster, and the accumulated weight of decades of
				disinvestment.
			</p>
			<p>
				The exodus was not uniform. Mountain communities and southern coastal towns
				suffered the deepest losses. The poorest municipalities lost the most. Those
				who left were disproportionately young and working-age, leaving behind an
				older, more vulnerable population.
			</p>
			<p>
				The political implications are profound. A smaller, older, poorer electorate
				will shape Puerto Rico's future. The next chapter examines how these
				demographic shifts have affected voter turnout and civic participation across
				the island.
			</p>

			<div class="key-takeaways">
				<h3>Key Takeaways</h3>
				<ul>
					<li><span class="stat">{formatNumber(541004)}</span> people left Puerto Rico since 2004</li>
					<li>77 of 78 municipalities lost population between 2010-2020</li>
					<li>Hurricane Maria triggered <span class="stat">{formatNumber(mariaExodus)}</span> departures in one year</li>
					<li>Poverty and population loss are strongly correlated</li>
					<li>The median age rose from 36.9 to {medianAge2020} years</li>
				</ul>
			</div>

			<div class="sources">
				<h3>Sources</h3>
				<ul>
					<li>U.S. Census Bureau - Decennial Census 2010, 2020; Population Estimates Program 2004-2020</li>
					<li>American Community Survey 5-Year Estimates - Poverty rates, demographic characteristics by municipality</li>
					<li>Puerto Rico Institute of Statistics - Migration data and demographic trends</li>
					<li>Pew Research Center - "Puerto Rican Population Declines on Island, Grows on U.S. Mainland" (2022)</li>
					<li>Center for Puerto Rican Studies - Post-Hurricane Maria migration analysis (2018)</li>
					<li>Federal Reserve Bank of New York - Economic conditions in Puerto Rico (2014-2020)</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/" class="nav-link prev">
					<span class="nav-direction">Back to</span>
					<span class="nav-title">Home</span>
				</a>
				<a href="{base}/chapters/turnout" class="nav-link next">
					<span class="nav-direction">Next Chapter</span>
					<span class="nav-title">Democracy Under Strain</span>
				</a>
			</nav>
		</div>
	</section>
</article>

<style>
	.chapter-header {
		min-height: 80vh;
		display: flex;
		align-items: center;
		padding: var(--space-3xl) 0;
		background: linear-gradient(180deg, var(--color-bg) 0%, var(--color-surface) 100%);
	}

	.chapter-header h1 {
		margin-bottom: var(--space-lg);
		font-size: var(--text-4xl);
	}

	.chapter-header .lead {
		font-size: var(--text-xl);
		line-height: 1.7;
		color: var(--color-text-light);
		max-width: 50ch;
	}

	.lead-stats {
		display: flex;
		gap: var(--space-2xl);
		margin-top: var(--space-2xl);
		padding-top: var(--space-xl);
		border-top: 1px solid var(--color-border);
	}

	.stat-block {
		display: flex;
		flex-direction: column;
	}

	.stat-value {
		font-family: var(--font-display);
		font-size: var(--text-3xl);
		font-weight: var(--font-bold);
		color: var(--color-text);
	}

	.stat-label {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		text-transform: uppercase;
		letter-spacing: var(--tracking-wide);
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

	/* Counter display styles */
	.counter-display {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 400px;
	}

	.counter-label {
		font-size: var(--text-lg);
		color: var(--color-text-muted);
		margin-bottom: var(--space-sm);
	}

	.counter-value {
		font-family: var(--font-mono, monospace);
		font-size: 4rem;
		font-weight: var(--font-bold);
		color: var(--color-text);
		letter-spacing: -0.02em;
		transition: color 0.3s ease;
	}

	.counter-year {
		font-size: var(--text-md);
		color: var(--color-text-light);
		margin-top: var(--space-sm);
	}

	/* Chart container */
	.chart-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		width: 100%;
		max-width: 550px;
	}

	.chart-annotation {
		display: flex;
		flex-direction: column;
		align-items: center;
		margin-top: var(--space-md);
		padding: var(--space-md);
		background: var(--color-surface-elevated);
		border-radius: var(--radius-md);
		border-left: 3px solid #c41e3a;
	}

	.annotation-marker {
		font-weight: var(--font-semibold);
		color: #c41e3a;
	}

	.annotation-text {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.chart-note {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin-top: var(--space-md);
		text-align: center;
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

	/* Step content styling */
	:global(.step) h3 {
		font-size: var(--text-xl);
		margin-bottom: var(--space-md);
	}

	:global(.step) p {
		margin-bottom: var(--space-md);
		line-height: 1.7;
	}

	:global(.step) .stat {
		font-weight: var(--font-semibold);
		color: var(--color-accent);
	}

	:global(.step) .highlight {
		font-weight: var(--font-semibold);
		color: var(--color-text);
	}

	:global(.step) .emphasis {
		font-style: italic;
		color: var(--color-text-light);
		border-left: 3px solid var(--color-accent);
		padding-left: var(--space-md);
	}

	.chapter-conclusion {
		padding: var(--space-3xl) 0;
		background: var(--color-surface);
	}

	.chapter-conclusion h2 {
		margin-bottom: var(--space-lg);
	}

	.chapter-conclusion p {
		margin-bottom: var(--space-md);
		line-height: 1.7;
	}

	.key-takeaways {
		margin-top: var(--space-2xl);
		padding: var(--space-xl);
		background: var(--color-surface-elevated);
		border-radius: var(--radius-lg);
	}

	.key-takeaways h3 {
		font-size: var(--text-lg);
		margin-bottom: var(--space-md);
	}

	.key-takeaways ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.key-takeaways li {
		padding: var(--space-sm) 0;
		border-bottom: 1px solid var(--color-border);
	}

	.key-takeaways li:last-child {
		border-bottom: none;
	}

	.key-takeaways .stat {
		font-weight: var(--font-semibold);
		color: var(--color-accent);
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

	@media (max-width: 768px) {
		.lead-stats {
			flex-direction: column;
			gap: var(--space-lg);
		}

		.stat-value {
			font-size: var(--text-2xl);
		}

		.counter-value {
			font-size: 2.5rem;
		}

		.chart-container {
			max-width: 100%;
		}
	}
</style>
