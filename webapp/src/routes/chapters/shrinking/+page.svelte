<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { ChoroplethMap } from '$lib/components/maps';
	import { BarChart, LineChart } from '$lib/components/charts';
	import { createLossScale, CATEGORY_COLORS, DIVERGING_COLORS, SEQUENTIAL_LOSS_COLORS } from '$lib/utils/colors';
	import { formatCompact, formatNumber, formatPercent, formatPercentChange } from '$lib/utils/format';
	import { language } from '$lib/stores/language';

	const chapterNum = 3;
	const totalSteps = 10;

	// Bilingual content
	const t = {
		en: {
			chapterTitle: 'The Shrinking Electorate',
			lead: "Between 2004 and 2024, Puerto Rico's voter rolls shrank by over {voterLoss} registered voters. This isn't just a number - it's a story of vanishing political power, an aging electorate, and a democracy losing its people.",
			loading: 'Loading data...',
			// Viz titles
			vizRegisteredVoters: 'Registered Voters Over Time',
			vizRegisteredVsCast: 'Registered vs. Votes Cast',
			vizShrinkingElectorate: 'The Shrinking Electorate',
			vizVoteLossMap: 'Vote Loss by Municipality (2016-2024)',
			vizTopLossesAbsolute: 'Top Voter Losses (Absolute)',
			vizLossesByPercent: 'Municipalities by Percentage Loss',
			vizAgeComposition: 'Age Composition of Electorate',
			// Legend labels
			legendRegistered: 'Registered',
			legendVotesCast: 'Votes Cast',
			legendVoterLoss: 'Voter loss',
			// Demographic labels
			demoYoungVoters: 'Young Voters (Under 35)',
			demoSeniorVoters: 'Senior Voters (Over 65)',
			demoMedianAge: 'Median voter age:',
			// Step titles
			step0Title: 'The Rolls Are Shrinking',
			step1Title: 'The Acceleration',
			step2Title: 'Visualizing the Loss',
			step3Title: 'Geography of Loss',
			step4Title: 'The Big Five',
			step5Title: 'An Aging Electorate',
			step6Title: 'The Feedback Loop',
			step7Title: 'The Representation Gap',
			step8Title: 'Registered vs. Participating',
			step9Title: 'What Comes Next?',
			// Step 0 content
			step0p1: 'In 2004, Puerto Rico had <span class="stat">2.44 million</span> registered voters - a deeply engaged electorate for an island of 3.8 million people. Voting was a civic tradition, a family ritual, a statement of identity.',
			step0p2: 'Two decades later, the voter rolls tell a different story. Economic crisis, natural disaster, and mass exodus have combined to create an unprecedented contraction in the island\'s democratic base.',
			step0p3: 'By 2024, only <span class="stat">1.99 million</span> voters remained registered - a loss of nearly half a million in twenty years.',
			// Step 1 content
			step1p1: 'The decline wasn\'t gradual. From 2004 to 2012, the electorate held relatively steady, losing about 60,000 voters over eight years. Then the floor gave way.',
			step1p2: 'Between 2012 and 2020, Puerto Rico lost <span class="stat">300,000</span> registered voters. Hurricane Maria in 2017 accelerated an already-existing trend, as entire families relocated to Florida, Texas, and the Northeast.',
			step1p3: 'Those who left were disproportionately working-age adults - the backbone of any electorate. They took their votes with them to states where, at least, those votes would count for president.',
			// Step 2 content
			step2p1: 'These circles represent the relative size of Puerto Rico\'s registered electorate across two decades. Each one is proportional to the number of registered voters.',
			step2p2: 'Notice how each successive circle <span class="highlight">shrinks visibly</span>. This isn\'t just a statistical abstraction - each missing pixel represents real people who are no longer part of the island\'s political community.',
			step2p3: 'From the largest circle in 2004 to the smallest in 2024, Puerto Rico has lost {voterLossPercent} of its electoral base.',
			// Step 3 content
			step3p1: 'The voter drain wasn\'t evenly distributed. This map shows the percentage change in votes cast between 2016 and 2024 for each municipality.',
			step3p2: '<span class="highlight">Darker colors</span> indicate steeper declines. While every municipality saw losses, some experienced dramatic collapses in electoral participation.',
			step3p3: 'The pattern reveals two Puerto Ricos: the metro San Juan area, which lost voters but maintained some base, and the rural interior, where the hemorrhaging was even more severe.',
			// Step 4 content
			step4p1: 'In absolute terms, the largest municipalities account for the bulk of voter loss. San Juan alone shed nearly <span class="stat">60,000 voters</span> between 2016 and 2024.',
			step4p2: 'These five municipalities - San Juan, Bayamon, Ponce, Carolina, and Caguas - together lost over <span class="stat">150,000 voters</span>. That\'s more voters than many U.S. congressional districts contain.',
			step4p3: 'But the raw numbers don\'t tell the whole story. When you look at <em>proportional</em> losses, a different picture emerges.',
			// Step 5 content
			step5p1: 'Who stayed behind? The data reveals a demographic transformation. Young voters left in droves, while older residents - with deeper roots, less mobility, and fewer mainland options - remained.',
			step5p2: 'In 2012, voters under 35 made up <span class="stat">28.5%</span> of the electorate. By 2024, that share had collapsed to just <span class="stat">18.2%</span>.',
			step5p3: 'Meanwhile, voters over 65 grew from <span class="stat">18.3%</span> to <span class="stat">27.1%</span> of all voters. The median voter aged nearly a decade in just twelve years.',
			step5p4: 'An older electorate tends to be more conservative, more focused on pensions and healthcare, and less concerned with the job creation and education issues that might bring young people back.',
			// Step 6 content
			step6p1: 'Here\'s the cruel irony: fewer voters means less political power, which means less attention from Washington, which means worse conditions, which drives more people to leave.',
			step6p2: 'The cycle is self-reinforcing. As the electorate shrinks, so does Puerto Rico\'s ability to advocate for the federal resources and policy changes that might reverse the trend.',
			step6p3: 'If Puerto Rico were a state, its population would have meant {seatsOld} House seats in 2004. Today, it would qualify for only {seatsNew}.',
			// Step 7 content
			step7p1: 'Puerto Rico\'s shrinking electorate creates a troubling paradox. The island has one non-voting representative in Congress - the Resident Commissioner - regardless of whether it has 4 million people or 3 million.',
			step7p2: 'Meanwhile, the <span class="stat">5.7 million</span> Puerto Ricans living on the mainland can vote for president and are represented by voting members of Congress. Their political power grows as the island\'s shrinks.',
			step7p3: 'The result: decisions about Puerto Rico\'s future are increasingly made by people who don\'t live there, while those who remain have diminishing voice in their own governance.',
			// Step 8 content
			step8p1: 'The gap between registered voters and actual votes cast tells another troubling story. Even among those who remain registered, participation has declined.',
			step8p2: 'In 2004, <span class="stat">81.5%</span> of registered voters cast ballots. By 2024, that figure had dropped to <span class="stat">61.2%</span>.',
			step8p3: 'The gap between the two lines represents growing disengagement - voters who haven\'t left the island but have left the political process. Disillusionment, not just emigration, is thinning the electorate.',
			// Step 9 content
			step9p1: 'The trends show no sign of reversing. Every projection suggests Puerto Rico\'s population will continue to decline through at least 2050, and the electorate will shrink with it.',
			step9p2: 'For democracy to thrive, it needs participants. Puerto Rico faces a fundamental question: how does a democracy function when its people are leaving?',
			step9p3: 'The answer will depend on whether the island can break the feedback loop - creating conditions that make young Puerto Ricans want to stay, and giving those who remain a reason to believe their vote matters.',
			// Conclusion section
			conclusionTitle: 'The Electoral Arithmetic',
			statVotersLost: 'Registered voters lost since 2004',
			statElectoralBase: 'Change in electoral base',
			statMedianAge: 'Increase in median voter age',
			statTopMunis: 'Municipalities with 50%+ of voter loss',
			breakingCycleTitle: 'Breaking the Cycle',
			conclusionP1: 'Puerto Rico\'s shrinking electorate is not inevitable - it\'s the result of policy choices, economic conditions, and colonial status that could be changed. But reversing these trends requires understanding their depth.',
			conclusionP2: 'In the next chapter, we examine how these demographic shifts have reshaped the island\'s political battles over status - the plebiscites that ask whether Puerto Rico should become a state, gain independence, or maintain its current relationship with the United States.',
			// Sources
			sourcesTitle: 'Sources',
			sourceCEE: 'Voter registration statistics 2000-2024',
			sourceComptroller: 'Puerto Rico Office of the Comptroller - Electoral participation reports',
			sourceCensus: 'Population estimates and projections for Puerto Rico',
			sourceStats: 'Puerto Rico Institute of Statistics - Demographic trends analysis',
			// Navigation
			navPrevious: 'Previous',
			navPrevTitle: 'Democracy Under Strain',
			navNext: 'Next Chapter',
			navNextTitle: 'One Question, Two Decades'
		},
		es: {
			chapterTitle: 'El Electorado Menguante',
			lead: 'Entre 2004 y 2024, el padrón electoral de Puerto Rico se redujo por más de {voterLoss} votantes registrados. Esto no es solo un número - es una historia de poder político desvanecido, un electorado envejecido, y una democracia perdiendo a su gente.',
			loading: 'Cargando datos...',
			// Viz titles
			vizRegisteredVoters: 'Votantes Registrados a Través del Tiempo',
			vizRegisteredVsCast: 'Registrados vs. Votos Emitidos',
			vizShrinkingElectorate: 'El Electorado Menguante',
			vizVoteLossMap: 'Pérdida de Votos por Municipio (2016-2024)',
			vizTopLossesAbsolute: 'Mayores Pérdidas de Votantes (Absolutas)',
			vizLossesByPercent: 'Municipios por Porcentaje de Pérdida',
			vizAgeComposition: 'Composición por Edad del Electorado',
			// Legend labels
			legendRegistered: 'Registrados',
			legendVotesCast: 'Votos Emitidos',
			legendVoterLoss: 'Pérdida de votantes',
			// Demographic labels
			demoYoungVoters: 'Votantes Jóvenes (Menores de 35)',
			demoSeniorVoters: 'Votantes Mayores (Mayores de 65)',
			demoMedianAge: 'Edad mediana del votante:',
			// Step titles
			step0Title: 'El Padrón Se Reduce',
			step1Title: 'La Aceleración',
			step2Title: 'Visualizando la Pérdida',
			step3Title: 'Geografía de la Pérdida',
			step4Title: 'Los Cinco Grandes',
			step5Title: 'Un Electorado Envejecido',
			step6Title: 'El Ciclo Vicioso',
			step7Title: 'La Brecha de Representación',
			step8Title: 'Registrados vs. Participantes',
			step9Title: '¿Qué Viene Ahora?',
			// Step 0 content
			step0p1: 'En 2004, Puerto Rico tenía <span class="stat">2.44 millones</span> de votantes registrados - un electorado profundamente comprometido para una isla de 3.8 millones de personas. Votar era una tradición cívica, un ritual familiar, una declaración de identidad.',
			step0p2: 'Dos décadas después, el padrón electoral cuenta una historia diferente. La crisis económica, los desastres naturales y el éxodo masivo se combinaron para crear una contracción sin precedentes en la base democrática de la isla.',
			step0p3: 'Para 2024, solo <span class="stat">1.99 millones</span> de votantes permanecían registrados - una pérdida de casi medio millón en veinte años.',
			// Step 1 content
			step1p1: 'El declive no fue gradual. De 2004 a 2012, el electorado se mantuvo relativamente estable, perdiendo unos 60,000 votantes en ocho años. Luego el piso cedió.',
			step1p2: 'Entre 2012 y 2020, Puerto Rico perdió <span class="stat">300,000</span> votantes registrados. El Huracán María en 2017 aceleró una tendencia ya existente, mientras familias enteras se reubicaban en Florida, Texas y el Noreste.',
			step1p3: 'Los que se fueron eran desproporcionadamente adultos en edad laboral - la columna vertebral de cualquier electorado. Se llevaron sus votos a estados donde, al menos, esos votos contarían para presidente.',
			// Step 2 content
			step2p1: 'Estos círculos representan el tamaño relativo del electorado registrado de Puerto Rico a lo largo de dos décadas. Cada uno es proporcional al número de votantes registrados.',
			step2p2: 'Nota cómo cada círculo sucesivo <span class="highlight">se reduce visiblemente</span>. Esto no es solo una abstracción estadística - cada píxel faltante representa personas reales que ya no son parte de la comunidad política de la isla.',
			step2p3: 'Desde el círculo más grande en 2004 hasta el más pequeño en 2024, Puerto Rico ha perdido {voterLossPercent} de su base electoral.',
			// Step 3 content
			step3p1: 'La fuga de votantes no fue distribuida equitativamente. Este mapa muestra el cambio porcentual en votos emitidos entre 2016 y 2024 para cada municipio.',
			step3p2: '<span class="highlight">Colores más oscuros</span> indican declives más pronunciados. Aunque todos los municipios vieron pérdidas, algunos experimentaron colapsos dramáticos en la participación electoral.',
			step3p3: 'El patrón revela dos Puerto Ricos: el área metropolitana de San Juan, que perdió votantes pero mantuvo cierta base, y el interior rural, donde la hemorragia fue aún más severa.',
			// Step 4 content
			step4p1: 'En términos absolutos, los municipios más grandes representan la mayor parte de la pérdida de votantes. San Juan solo perdió casi <span class="stat">60,000 votantes</span> entre 2016 y 2024.',
			step4p2: 'Estos cinco municipios - San Juan, Bayamón, Ponce, Carolina y Caguas - juntos perdieron más de <span class="stat">150,000 votantes</span>. Eso es más votantes que muchos distritos congresionales de EE.UU.',
			step4p3: 'Pero los números crudos no cuentan toda la historia. Cuando miras las pérdidas <em>proporcionales</em>, emerge una imagen diferente.',
			// Step 5 content
			step5p1: '¿Quiénes se quedaron? Los datos revelan una transformación demográfica. Los votantes jóvenes se fueron en masa, mientras los residentes mayores - con raíces más profundas, menos movilidad y menos opciones en el continente - permanecieron.',
			step5p2: 'En 2012, los votantes menores de 35 años constituían el <span class="stat">28.5%</span> del electorado. Para 2024, esa proporción había colapsado a solo <span class="stat">18.2%</span>.',
			step5p3: 'Mientras tanto, los votantes mayores de 65 crecieron del <span class="stat">18.3%</span> al <span class="stat">27.1%</span> de todos los votantes. La edad mediana del votante aumentó casi una década en solo doce años.',
			step5p4: 'Un electorado más viejo tiende a ser más conservador, más enfocado en pensiones y salud, y menos preocupado por la creación de empleos y la educación que podrían traer a los jóvenes de vuelta.',
			// Step 6 content
			step6p1: 'Aquí está la cruel ironía: menos votantes significa menos poder político, lo que significa menos atención de Washington, lo que significa peores condiciones, lo que lleva a más gente a irse.',
			step6p2: 'El ciclo se autorrefuerza. A medida que el electorado se reduce, también lo hace la capacidad de Puerto Rico para abogar por los recursos federales y cambios de política que podrían revertir la tendencia.',
			step6p3: 'Si Puerto Rico fuera un estado, su población habría significado {seatsOld} escaños en la Cámara en 2004. Hoy, calificaría para solo {seatsNew}.',
			// Step 7 content
			step7p1: 'El electorado menguante de Puerto Rico crea una paradoja preocupante. La isla tiene un representante sin voto en el Congreso - el Comisionado Residente - independientemente de si tiene 4 millones de personas o 3 millones.',
			step7p2: 'Mientras tanto, los <span class="stat">5.7 millones</span> de puertorriqueños que viven en el continente pueden votar por presidente y están representados por miembros del Congreso con voto. Su poder político crece mientras el de la isla se reduce.',
			step7p3: 'El resultado: las decisiones sobre el futuro de Puerto Rico son cada vez más tomadas por personas que no viven allí, mientras que los que permanecen tienen cada vez menos voz en su propia gobernanza.',
			// Step 8 content
			step8p1: 'La brecha entre votantes registrados y votos emitidos cuenta otra historia preocupante. Incluso entre los que permanecen registrados, la participación ha disminuido.',
			step8p2: 'En 2004, el <span class="stat">81.5%</span> de los votantes registrados emitieron sus votos. Para 2024, esa cifra había caído al <span class="stat">61.2%</span>.',
			step8p3: 'La brecha entre las dos líneas representa un desapego creciente - votantes que no han dejado la isla pero han dejado el proceso político. La desilusión, no solo la emigración, está adelgazando el electorado.',
			// Step 9 content
			step9p1: 'Las tendencias no muestran signos de revertirse. Todas las proyecciones sugieren que la población de Puerto Rico continuará disminuyendo al menos hasta 2050, y el electorado se reducirá con ella.',
			step9p2: 'Para que la democracia prospere, necesita participantes. Puerto Rico enfrenta una pregunta fundamental: ¿cómo funciona una democracia cuando su gente se está yendo?',
			step9p3: 'La respuesta dependerá de si la isla puede romper el ciclo vicioso - creando condiciones que hagan que los jóvenes puertorriqueños quieran quedarse, y dando a los que permanecen una razón para creer que su voto importa.',
			// Conclusion section
			conclusionTitle: 'La Aritmética Electoral',
			statVotersLost: 'Votantes registrados perdidos desde 2004',
			statElectoralBase: 'Cambio en la base electoral',
			statMedianAge: 'Aumento en la edad mediana del votante',
			statTopMunis: 'Municipios con 50%+ de pérdida de votantes',
			breakingCycleTitle: 'Rompiendo el Ciclo',
			conclusionP1: 'El electorado menguante de Puerto Rico no es inevitable - es el resultado de decisiones de política, condiciones económicas y estatus colonial que podrían cambiarse. Pero revertir estas tendencias requiere entender su profundidad.',
			conclusionP2: 'En el próximo capítulo, examinamos cómo estos cambios demográficos han reconfigurado las batallas políticas de la isla sobre el estatus - los plebiscitos que preguntan si Puerto Rico debería convertirse en estado, obtener independencia, o mantener su relación actual con los Estados Unidos.',
			// Sources
			sourcesTitle: 'Fuentes',
			sourceCEE: 'Estadísticas de registro de votantes 2000-2024',
			sourceComptroller: 'Oficina del Contralor de Puerto Rico - Informes de participación electoral',
			sourceCensus: 'Estimados de población y proyecciones para Puerto Rico',
			sourceStats: 'Instituto de Estadísticas de Puerto Rico - Análisis de tendencias demográficas',
			// Navigation
			navPrevious: 'Anterior',
			navPrevTitle: 'Democracia Bajo Presión',
			navNext: 'Próximo Capítulo',
			navNextTitle: 'Una Pregunta, Dos Décadas'
		}
	};

	// Reactive content based on language
	let content = $derived(t[$language]);
	let chapterTitle = $derived(content.chapterTitle);

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
			label: $language === 'en' ? 'Registered Voters' : 'Votantes Registrados',
			data: electorateSeries.map(d => ({ x: d.year, y: d.registered_voters })),
			color: CATEGORY_COLORS[0]
		}
	]);

	// Dual series - registered vs votes cast
	let dualSeries = $derived([
		{
			id: 'registered',
			label: $language === 'en' ? 'Registered Voters' : 'Votantes Registrados',
			data: electorateSeries.map(d => ({ x: d.year, y: d.registered_voters })),
			color: CATEGORY_COLORS[0]
		},
		{
			id: 'cast',
			label: $language === 'en' ? 'Votes Cast' : 'Votos Emitidos',
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
	<title>{$language === 'en' ? 'Chapter' : 'Capítulo'} {chapterNum}: {chapterTitle} | Puerto Rico Elections</title>
</svelte:head>

<Progress {currentStep} {totalSteps} chapterTitle={chapterTitle} />

<article class="chapter">
	<header class="chapter-header">
		<div class="container content">
			<span class="label">{$language === 'en' ? 'Chapter' : 'Capítulo'} {chapterNum}</span>
			<div class="accent-line"></div>
			<h1>{chapterTitle}</h1>
			<p class="lead">
				{@html content.lead.replace('{voterLoss}', `<span class="stat">${formatCompact(voterLoss2004to2024())}</span>`)}
			</p>
		</div>
	</header>

	<ScrollySection offset={0.6} onStepEnter={handleStepEnter}>
		{#snippet graphic()}
			<div class="viz-container">
				{#if loading}
					<p class="loading">{content.loading}</p>
				{:else if activeViz === 'line'}
					<h3 class="viz-title">
						{currentStep <= 1 ? content.vizRegisteredVoters : content.vizRegisteredVsCast}
					</h3>
					<LineChart
						series={currentStep <= 1 ? registeredVotersSeries : dualSeries}
						width={520}
						height={360}
						xLabel={$language === 'en' ? 'Election Year' : 'Año Electoral'}
						yLabel={$language === 'en' ? 'Voters' : 'Votantes'}
						xFormat={(v) => String(v)}
						yFormat={(v) => formatCompact(v)}
						showArea={true}
						showDots={true}
					/>
					{#if currentStep > 1}
						<div class="legend-inline">
							<span class="legend-item"><span class="swatch" style="background: {CATEGORY_COLORS[0]}"></span> {content.legendRegistered}</span>
							<span class="legend-item"><span class="swatch" style="background: {CATEGORY_COLORS[3]}"></span> {content.legendVotesCast}</span>
						</div>
					{/if}
				{:else if activeViz === 'circles'}
					<h3 class="viz-title">{content.vizShrinkingElectorate}</h3>
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
					<h3 class="viz-title">{content.vizVoteLossMap}</h3>
					<ChoroplethMap
						data={mapData}
						colorScale={voteLossColorScale}
						tooltipFormat={(name, value) =>
							value !== undefined
								? `${name}: ${value.toFixed(1)}% ${$language === 'en' ? 'change' : 'cambio'}`
								: name
						}
					/>
					{#if mapData.size > 0}
						<div class="legend">
							<span class="legend-label">{content.legendVoterLoss}</span>
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
						{currentStep === 4 ? content.vizTopLossesAbsolute : content.vizLossesByPercent}
					</h3>
					<BarChart
						data={currentStep === 4 ? topLossesAbsolute : topLossesPercent}
						width={480}
						height={340}
						horizontal={true}
						valueFormat={(v) => currentStep === 4 ? `-${formatCompact(v)}` : `-${v.toFixed(1)}%`}
					/>
				{:else if activeViz === 'demographic'}
					<h3 class="viz-title">{content.vizAgeComposition}</h3>
					<div class="demographic-grid">
						<div class="demo-section">
							<h4>{content.demoYoungVoters}</h4>
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
							<h4>{content.demoSeniorVoters}</h4>
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
							<strong>{content.demoMedianAge}</strong> {demographicShift?.median_voter_age_2012} (2012) {$language === 'en' ? 'to' : 'a'} {demographicShift?.median_voter_age_2024} (2024)
						</div>
					</div>
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0} variant="callout">
			<h3>{content.step0Title}</h3>
			<p>{@html content.step0p1}</p>
			<p>{content.step0p2}</p>
			<p>{@html content.step0p3}</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>{content.step1Title}</h3>
			<p>{content.step1p1}</p>
			<p>{@html content.step1p2}</p>
			<p>{content.step1p3}</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>{content.step2Title}</h3>
			<p>{content.step2p1}</p>
			<p>{@html content.step2p2}</p>
			<p>
				{@html content.step2p3.replace('{voterLossPercent}', `<span class="stat">${formatPercentChange(voterLossPercent())}</span>`)}
			</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>{content.step3Title}</h3>
			<p>{content.step3p1}</p>
			<p>{@html content.step3p2}</p>
			<p>{content.step3p3}</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>{content.step4Title}</h3>
			<p>{@html content.step4p1}</p>
			<p>{@html content.step4p2}</p>
			<p>{@html content.step4p3}</p>
		</Step>

		<Step active={currentStep === 5} index={5} variant="callout">
			<h3>{content.step5Title}</h3>
			<p>{content.step5p1}</p>
			<p>{@html content.step5p2}</p>
			<p>{@html content.step5p3}</p>
			<p>{content.step5p4}</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>{content.step6Title}</h3>
			<p>{content.step6p1}</p>
			<p>{content.step6p2}</p>
			<p>
				{@html content.step6p3
					.replace('{seatsOld}', `<span class="stat">${representationImpact?.if_state_reps_2004 || 6}</span>`)
					.replace('{seatsNew}', `<span class="stat">${representationImpact?.if_state_reps_2024 || 4}</span>`)}
			</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>{content.step7Title}</h3>
			<p>{content.step7p1}</p>
			<p>{@html content.step7p2}</p>
			<p>{content.step7p3}</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>{content.step8Title}</h3>
			<p>{content.step8p1}</p>
			<p>{@html content.step8p2}</p>
			<p>{content.step8p3}</p>
		</Step>

		<Step active={currentStep === 9} index={9} variant="question">
			<h3>{content.step9Title}</h3>
			<p>{content.step9p1}</p>
			<p>{content.step9p2}</p>
			<p>{content.step9p3}</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>{content.conclusionTitle}</h2>
			<div class="stat-grid">
				<div class="stat-card">
					<span class="stat-value">-{formatCompact(voterLoss2004to2024())}</span>
					<span class="stat-label">{content.statVotersLost}</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">{formatPercentChange(voterLossPercent())}</span>
					<span class="stat-label">{content.statElectoralBase}</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">+9 {$language === 'en' ? 'yrs' : 'años'}</span>
					<span class="stat-label">{content.statMedianAge}</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">5</span>
					<span class="stat-label">{content.statTopMunis}</span>
				</div>
			</div>

			<div class="conclusion-text">
				<h3>{content.breakingCycleTitle}</h3>
				<p>{content.conclusionP1}</p>
				<p>{content.conclusionP2}</p>
			</div>

			<div class="sources">
				<h3>{content.sourcesTitle}</h3>
				<ul>
					<li><a href="https://ww2.ceepur.org/Home/EventosElectorales" target="_blank" rel="noopener">Comisión Estatal de Elecciones de Puerto Rico (CEE)</a> - {content.sourceCEE}</li>
					<li>{content.sourceComptroller}</li>
					<li><a href="https://www.census.gov/programs-surveys/popest.html" target="_blank" rel="noopener">U.S. Census Bureau</a> - {content.sourceCensus}</li>
					<li>{content.sourceStats}</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/turnout" class="nav-link prev">
					<span class="nav-direction">{content.navPrevious}</span>
					<span class="nav-title">{content.navPrevTitle}</span>
				</a>
				<a href="{base}/chapters/plebiscites" class="nav-link next">
					<span class="nav-direction">{content.navNext}</span>
					<span class="nav-title">{content.navNextTitle}</span>
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
