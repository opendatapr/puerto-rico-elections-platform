<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { ChoroplethMap } from '$lib/components/maps';
	import { BarChart, LineChart } from '$lib/components/charts';
	import { createDivergingScale, CATEGORY_COLORS, DIVERGING_COLORS } from '$lib/utils/colors';
	import { formatNumber, formatPercent, formatCompact } from '$lib/utils/format';
	import { language } from '$lib/stores/language';

	const chapterNum = 5;
	const totalSteps = 10;

	// Bilingual content
	const t = {
		en: {
			chapterTitle: 'The 52% That Changed Nothing',
			chapter: 'Chapter',
			lead: 'On November 3, 2020, Puerto Rico held its sixth status referendum. For the first time ever, a simple majority voted "Yes" to statehood. Congress heard the result. Congress did nothing.',
			loading: 'Loading data...',
			// Viz titles and labels
			theQuestion: 'The Question',
			ballotQuestion: 'Should Puerto Rico be admitted immediately into the Union as a State?',
			votedYes: 'voted YES',
			finalResults: 'November 3, 2020 - Final Results',
			siYes: 'SI (Yes)',
			no: 'NO',
			votes: 'votes',
			totalVotes: 'Total votes',
			voteMargin: 'vote margin for statehood',
			statehoodSupport: 'Statehood Support by Municipality',
			legendNo: '40% (No)',
			legendMid: '50%',
			legendYes: '60% (Yes)',
			senatorialResults: 'Results by Senatorial District',
			senatorialNote: 'All 8 districts voted Yes, but margins varied widely',
			turnoutComparison: 'Referendum vs General Election Turnout',
			governorRace: 'Governor Race',
			referendum: 'Referendum',
			turnoutNote: '~50,000 fewer voters participated in the referendum than the gubernatorial race',
			historicalTitle: 'Six Referendums, Six Decades',
			historicalNote: '*2017 excluded due to opposition boycott (23% turnout)',
			globalTitle: 'How 52.5% Compares Globally',
			globalNote: 'Brexit passed with 51.9%. Scotland stayed with 55.3% against.',
			statehoodSupportLabel: 'Statehood Support',
			year: 'Year',
			// Step titles and content
			step0Title: 'A Simpler Ballot',
			step0p1: 'Previous status referendums offered multiple options: statehood, independence, free association, enhanced commonwealth. Critics argued the confusion diluted results and made interpretation impossible.',
			step0p2: 'The 2020 referendum was different. For the first time, voters faced a single, binary question. No ambiguity. No protest blank votes.',
			step0p2b: 'Just',
			step0p2c: 'or',
			step0p3: 'The question itself was unprecedented in its directness: should Puerto Rico be admitted',
			step0p3b: 'into the Union as a State?',
			immediately: 'immediately',
			yes: 'Yes',
			step1Title: 'The Count Begins',
			step1p1: 'As polls closed on election night, Puerto Ricans watched the results come in alongside the chaotic U.S. presidential race. The island\'s own drama was unfolding simultaneously.',
			step1p2: 'Precinct by precinct, the Yes votes accumulated. The margin was narrow but consistent. By midnight, the trajectory was clear: statehood would win its first-ever majority in a binding referendum.',
			step1p3: 'Watch the final percentage emerge...',
			step2Title: 'A Historic Threshold',
			step2p1pre: '',
			step2p1mid: 'voted Yes.',
			step2p1b: 'voted No. After six referendums spanning 53 years, statehood finally crossed the 50% threshold.',
			step2p2pre: 'The margin of',
			step2p2mid: 'votes was larger than many U.S. presidential margins in swing states. It was decisive by any democratic standard except one: Congress doesn\'t have to listen.',
			step2p3: 'Puerto Rico had spoken. The question was whether Washington would hear.',
			step3Title: 'Mapping the Vote',
			step3p1: 'The referendum results varied dramatically across Puerto Rico\'s 78 municipalities. Geography, history, and partisan loyalty all shaped how communities voted.',
			step3p2: 'Unlike the gubernatorial race, where party lines are clear, the status question cuts across traditional political boundaries. Some traditionally PNP municipalities voted No; some PPD strongholds surprised with Yes majorities.',
			step3p3: 'The map shows where statehood found its strongest support.',
			step4Title: 'The Geographic Divide',
			step4p1pre: 'The map reveals clear patterns.',
			step4p1a: 'Teal/green areas',
			step4p1b: 'voted Yes above 50%;',
			step4p1c: 'red areas',
			step4p1d: 'voted No. The intensity shows the margin of victory.',
			step4p2pre: '',
			step4p2a: 'led the island at 60.6% Yes, while',
			step4p2b: 'was most opposed at just 41.3%. The two small islands off the eastern coast voted in opposite directions, a microcosm of the larger debate.',
			step4p3pre: 'Notably, San Juan, the capital and largest city, voted narrowly',
			step4p3a: 'against',
			step4p3b: 'statehood at 49.8%, accepting the status quo even as the island-wide majority demanded change.',
			step5Title: 'Every District Said Yes',
			step5p1: 'Puerto Rico is divided into eight senatorial districts for legislative representation. In the 2020 referendum, all eight voted Yes for statehood, though by varying margins.',
			step5p2: 'Bayamon II led with 55.2% Yes, reflecting the pro-statehood lean of the suburban ring around San Juan. San Juan I and Guayama VI showed the narrowest margins, barely crossing the 50% threshold.',
			step5p3: 'The unanimity across districts gave statehood advocates a powerful argument: this wasn\'t a regional preference, it was an island-wide mandate.',
			step6Title: 'The Turnout Gap',
			step6p1: 'Critics of the referendum pointed to turnout. While 54.7% of registered voters cast ballots in the governor\'s race, only 52.3% participated in the status referendum, despite appearing on the same ballot.',
			step6p2: 'That 2.4 percentage point gap represents roughly 50,000 voters who chose the governor but skipped the referendum question. Some boycotted on principle; others simply didn\'t care.',
			step6p3: 'Statehood opponents argued this gap undermined the mandate. Supporters countered that 52% turnout exceeds most U.S. off-year elections and that abstention is still participation, just passive participation.',
			step7Title: 'The Long Arc of Status',
			step7p1: 'The 2020 result sits within a 53-year trajectory. From 39% in 1967 to 52.5% in 2020, statehood support has grown steadily, with one dramatic outlier.',
			step7p2: 'The 2017 referendum, boycotted by the PPD and PIP, produced a meaningless 97% statehood result on just 23% turnout. That referendum taught an important lesson: process legitimacy matters as much as outcome.',
			step7p3: 'The 2020 referendum was designed to avoid those pitfalls. Simple ballot. High turnout. Clear margin. Yet the result was still non-binding, still advisory, still ignorable.',
			step8Title: '52% in Global Context',
			step8p1: 'How does Puerto Rico\'s 52.5% compare to other consequential referendums? Brexit passed with 51.9%, triggering the UK\'s departure from the European Union. Scotland stayed in the UK after 55.3% voted against independence.',
			step8p2: 'Puerto Rico\'s margin was larger than Brexit\'s. It was more decisive than Quebec\'s 49.4% independence vote in 1995. By the standards that govern self-determination elsewhere, 52.5% should have consequences.',
			step8p3: 'But Puerto Rico is not a sovereign nation holding a referendum on its future. It\'s a colony asking permission from Congress. The comparison illuminates the democratic deficit at the heart of the territory\'s status.',
			step9Title: 'The Silence from Washington',
			step9p1: 'After November 3, 2020, the world\'s attention was elsewhere: a contested presidential election, a pandemic raging, a capital that would be stormed in January. Puerto Rico\'s referendum barely registered in mainland media.',
			step9p2: 'Congress has introduced statehood bills in subsequent sessions. None have passed. The Senate has shown little interest. The 52.52% that voted Yes in 2020 have received neither admission nor rejection, just the familiar colonial silence.',
			step9p3: 'The referendum answered Puerto Rico\'s question. It did not answer America\'s question: will the United States accept a 51st state, with all the political realignment that implies?',
			// Conclusion
			conclusionTitle: 'The Colonial Paradox',
			conclusionP1: 'The 2020 referendum crystallizes Puerto Rico\'s democratic contradiction. Its residents can vote, but their votes cannot compel action. They expressed a preference, but preferences don\'t bind colonial powers. The 52.52% changed nothing because the referendum was never designed to change anything. It was designed to express. Expression without consequence is the definition of colonial governance.',
			statVotedYes: 'Voted Yes for statehood',
			statVoteMargin: 'Vote margin',
			statReferendum: 'Status referendum since 1967',
			statCongressVotes: 'Congressional votes on admission since',
			// Newspaper headline
			dateline: 'SAN JUAN, November 4, 2020',
			headline: 'Puerto Ricans Vote for Statehood; Congress Expected to Do Nothing',
			subhead: 'In the sixth referendum on political status, a majority finally backs admission to the Union. Experts say result is "advisory" and "non-binding," raising questions about the purpose of the exercise.',
			// Sources
			sources: 'Sources',
			sourceCEE: '2020 Referendum results by municipality',
			sourceCensus: 'Puerto Rico population and demographic data',
			sourceBrexit: 'Brexit referendum data (2016)',
			sourceScotland: 'Scottish Independence referendum data (2014)',
			// Navigation
			previous: 'Previous',
			nextChapter: 'Next Chapter',
			prevTitle: 'One Question, Two Decades',
			nextTitle: 'Divided by Design'
		},
		es: {
			chapterTitle: 'El 52% Que No Cambio Nada',
			chapter: 'Capitulo',
			lead: 'El 3 de noviembre de 2020, Puerto Rico celebro su sexto referendum de estatus. Por primera vez en la historia, una mayoria simple voto "Si" a la estadidad. El Congreso escucho el resultado. El Congreso no hizo nada.',
			loading: 'Cargando datos...',
			// Viz titles and labels
			theQuestion: 'La Pregunta',
			ballotQuestion: 'Debe Puerto Rico ser admitido inmediatamente en la Union como un Estado?',
			votedYes: 'votaron SI',
			finalResults: '3 de noviembre de 2020 - Resultados Finales',
			siYes: 'SI',
			no: 'NO',
			votes: 'votos',
			totalVotes: 'Votos totales',
			voteMargin: 'votos de margen a favor de la estadidad',
			statehoodSupport: 'Apoyo a la Estadidad por Municipio',
			legendNo: '40% (No)',
			legendMid: '50%',
			legendYes: '60% (Si)',
			senatorialResults: 'Resultados por Distrito Senatorial',
			senatorialNote: 'Los 8 distritos votaron Si, pero los margenes variaron ampliamente',
			turnoutComparison: 'Participacion: Referendum vs Eleccion General',
			governorRace: 'Carrera de Gobernador',
			referendum: 'Referendum',
			turnoutNote: '~50,000 votantes menos participaron en el referendum que en la carrera de gobernador',
			historicalTitle: 'Seis Referendums, Seis Decadas',
			historicalNote: '*2017 excluido debido al boicot de la oposicion (23% de participacion)',
			globalTitle: 'Como se Compara el 52.5% Globalmente',
			globalNote: 'Brexit paso con 51.9%. Escocia se quedo con 55.3% en contra.',
			statehoodSupportLabel: 'Apoyo a la Estadidad',
			year: 'Ano',
			// Step titles and content
			step0Title: 'Una Papeleta Mas Simple',
			step0p1: 'Los referendums de estatus anteriores ofrecian multiples opciones: estadidad, independencia, libre asociacion, estado libre asociado mejorado. Los criticos argumentaban que la confusion diluia los resultados y hacia imposible la interpretacion.',
			step0p2: 'El referendum de 2020 fue diferente. Por primera vez, los votantes enfrentaron una sola pregunta binaria. Sin ambiguedad. Sin votos de protesta en blanco.',
			step0p2b: 'Solo',
			step0p2c: 'o',
			step0p3: 'La pregunta en si era sin precedentes en su franqueza: debe Puerto Rico ser admitido',
			step0p3b: 'en la Union como Estado?',
			immediately: 'inmediatamente',
			yes: 'Si',
			step1Title: 'El Conteo Comienza',
			step1p1: 'Cuando cerraron las urnas en la noche de elecciones, los puertorriquenos observaban los resultados llegar junto con la caotica carrera presidencial estadounidense. El drama propio de la isla se desarrollaba simultaneamente.',
			step1p2: 'Precinto por precinto, los votos de Si se acumulaban. El margen era estrecho pero consistente. Para la medianoche, la trayectoria era clara: la estadidad ganaria su primera mayoria en un referendum vinculante.',
			step1p3: 'Observa el porcentaje final emerger...',
			step2Title: 'Un Umbral Historico',
			step2p1pre: '',
			step2p1mid: 'voto Si.',
			step2p1b: 'voto No. Despues de seis referendums abarcando 53 anos, la estadidad finalmente cruzo el umbral del 50%.',
			step2p2pre: 'El margen de',
			step2p2mid: 'votos fue mayor que muchos margenes presidenciales estadounidenses en estados clave. Fue decisivo por cualquier estandar democratico excepto uno: el Congreso no tiene que escuchar.',
			step2p3: 'Puerto Rico habia hablado. La pregunta era si Washington escucharia.',
			step3Title: 'Mapeando el Voto',
			step3p1: 'Los resultados del referendum variaron dramaticamente a traves de los 78 municipios de Puerto Rico. La geografia, la historia y la lealtad partidista moldearon como votaron las comunidades.',
			step3p2: 'A diferencia de la carrera de gobernador, donde las lineas partidistas son claras, la cuestion del estatus cruza los limites politicos tradicionales. Algunos municipios tradicionalmente del PNP votaron No; algunos bastiones del PPD sorprendieron con mayorias de Si.',
			step3p3: 'El mapa muestra donde la estadidad encontro su mayor apoyo.',
			step4Title: 'La Division Geografica',
			step4p1pre: 'El mapa revela patrones claros.',
			step4p1a: 'Las areas verde azuladas',
			step4p1b: 'votaron Si por encima del 50%;',
			step4p1c: 'las areas rojas',
			step4p1d: 'votaron No. La intensidad muestra el margen de victoria.',
			step4p2pre: '',
			step4p2a: 'lidero la isla con 60.6% Si, mientras que',
			step4p2b: 'fue el mas opuesto con solo 41.3%. Las dos pequenas islas frente a la costa este votaron en direcciones opuestas, un microcosmos del debate mas amplio.',
			step4p3pre: 'Notablemente, San Juan, la capital y ciudad mas grande, voto estrechamente',
			step4p3a: 'en contra',
			step4p3b: 'de la estadidad con 49.8%, aceptando el statu quo aun cuando la mayoria a nivel de isla exigia cambio.',
			step5Title: 'Cada Distrito Dijo Si',
			step5p1: 'Puerto Rico esta dividido en ocho distritos senatoriales para representacion legislativa. En el referendum de 2020, los ocho votaron Si a la estadidad, aunque con margenes variados.',
			step5p2: 'Bayamon II lidero con 55.2% Si, reflejando la inclinacion pro-estadidad del anillo suburbano alrededor de San Juan. San Juan I y Guayama VI mostraron los margenes mas estrechos, apenas cruzando el umbral del 50%.',
			step5p3: 'La unanimidad entre distritos dio a los defensores de la estadidad un argumento poderoso: esto no era una preferencia regional, era un mandato a nivel de isla.',
			step6Title: 'La Brecha de Participacion',
			step6p1: 'Los criticos del referendum senalaron la participacion. Mientras el 54.7% de los votantes registrados emitieron votos en la carrera de gobernador, solo el 52.3% participo en el referendum de estatus, a pesar de aparecer en la misma papeleta.',
			step6p2: 'Esa brecha de 2.4 puntos porcentuales representa aproximadamente 50,000 votantes que eligieron al gobernador pero omitieron la pregunta del referendum. Algunos boicotearon por principio; otros simplemente no les importo.',
			step6p3: 'Los opositores a la estadidad argumentaron que esta brecha socavaba el mandato. Los partidarios respondieron que el 52% de participacion supera a la mayoria de las elecciones intermedias de EE.UU. y que la abstencion sigue siendo participacion, solo participacion pasiva.',
			step7Title: 'El Largo Arco del Estatus',
			step7p1: 'El resultado de 2020 se ubica dentro de una trayectoria de 53 anos. Del 39% en 1967 al 52.5% en 2020, el apoyo a la estadidad ha crecido de manera constante, con un valor atipico dramatico.',
			step7p2: 'El referendum de 2017, boicoteado por el PPD y el PIP, produjo un resultado sin sentido del 97% para la estadidad con solo 23% de participacion. Ese referendum enseno una leccion importante: la legitimidad del proceso importa tanto como el resultado.',
			step7p3: 'El referendum de 2020 fue disenado para evitar esos escollos. Papeleta simple. Alta participacion. Margen claro. Sin embargo, el resultado seguia siendo no vinculante, consultivo, ignorable.',
			step8Title: '52% en Contexto Global',
			step8p1: 'Como se compara el 52.5% de Puerto Rico con otros referendums consecuentes? Brexit paso con 51.9%, desencadenando la salida del Reino Unido de la Union Europea. Escocia permanecio en el Reino Unido despues de que el 55.3% votara contra la independencia.',
			step8p2: 'El margen de Puerto Rico fue mayor que el de Brexit. Fue mas decisivo que el voto de independencia de Quebec del 49.4% en 1995. Por los estandares que gobiernan la autodeterminacion en otros lugares, el 52.5% deberia tener consecuencias.',
			step8p3: 'Pero Puerto Rico no es una nacion soberana celebrando un referendum sobre su futuro. Es una colonia pidiendo permiso al Congreso. La comparacion ilumina el deficit democratico en el corazon del estatus del territorio.',
			step9Title: 'El Silencio de Washington',
			step9p1: 'Despues del 3 de noviembre de 2020, la atencion del mundo estaba en otro lugar: una eleccion presidencial disputada, una pandemia desatada, un capitolio que seria asaltado en enero. El referendum de Puerto Rico apenas registro en los medios continentales.',
			step9p2: 'El Congreso ha introducido proyectos de ley de estadidad en sesiones subsiguientes. Ninguno ha pasado. El Senado ha mostrado poco interes. El 52.52% que voto Si en 2020 no ha recibido ni admision ni rechazo, solo el silencio colonial familiar.',
			step9p3: 'El referendum respondio la pregunta de Puerto Rico. No respondio la pregunta de Estados Unidos: aceptara Estados Unidos un estado 51, con todo el realineamiento politico que eso implica?',
			// Conclusion
			conclusionTitle: 'La Paradoja Colonial',
			conclusionP1: 'El referendum de 2020 cristaliza la contradiccion democratica de Puerto Rico. Sus residentes pueden votar, pero sus votos no pueden obligar a la accion. Expresaron una preferencia, pero las preferencias no atan a los poderes coloniales. El 52.52% no cambio nada porque el referendum nunca fue disenado para cambiar nada. Fue disenado para expresar. Expresion sin consecuencia es la definicion de gobernanza colonial.',
			statVotedYes: 'Votaron Si por la estadidad',
			statVoteMargin: 'Margen de votos',
			statReferendum: 'Referendum de estatus desde 1967',
			statCongressVotes: 'Votos del Congreso sobre admision desde entonces',
			// Newspaper headline
			dateline: 'SAN JUAN, 4 de noviembre de 2020',
			headline: 'Puertorriquenos Votan por la Estadidad; Se Espera que el Congreso No Haga Nada',
			subhead: 'En el sexto referendum sobre estatus politico, una mayoria finalmente respalda la admision a la Union. Expertos dicen que el resultado es "consultivo" y "no vinculante", planteando preguntas sobre el proposito del ejercicio.',
			// Sources
			sources: 'Fuentes',
			sourceCEE: 'Resultados del referendum 2020 por municipio',
			sourceCensus: 'Datos de poblacion y demograficos de Puerto Rico',
			sourceBrexit: 'Datos del referendum del Brexit (2016)',
			sourceScotland: 'Datos del referendum de independencia de Escocia (2014)',
			// Navigation
			previous: 'Anterior',
			nextChapter: 'Proximo Capitulo',
			prevTitle: 'Una Pregunta, Dos Decadas',
			nextTitle: 'Divididos por Diseno'
		}
	};

	// Reactive content based on language
	let content = $derived(t[$language]);
	let chapterTitle = $derived(content.chapterTitle);

	let currentStep = $state(0);
	let loading = $state(true);
	let activeViz = $state<'countdown' | 'result' | 'map' | 'historical' | 'global' | 'turnout' | 'senatorial'>('countdown');

	// Data types
	interface IslandResults {
		si: number;
		no: number;
		total: number;
		siPercent: number;
		noPercent: number;
	}

	interface HistoricalPoint {
		year: number;
		statehood: number;
		label: string;
		turnout: number;
	}

	interface BarDataPoint {
		label: string;
		value: number;
		color: string;
	}

	interface ChapterData {
		islandResults: IslandResults;
		municipalityResults: Record<string, number>;
		historicalData: HistoricalPoint[];
		globalComparisons: BarDataPoint[];
		senatorialResults: BarDataPoint[];
		turnoutComparison: {
			governorRace: number;
			referendum: number;
		};
		summary: {
			margin: number;
			yesSIPercent: number;
			noPercent: number;
			totalVotes: number;
			referendumNumber: number;
			yearsSinceFirst: number;
			congressionalVotesSince: number;
		};
	}

	// State with defaults
	let islandResults = $state<IslandResults>({
		si: 655505,
		no: 592671,
		total: 1248176,
		siPercent: 52.52,
		noPercent: 47.48
	});

	let municipalityResults = $state<Record<string, number>>({});

	let historicalData = $state<HistoricalPoint[]>([]);

	let globalComparisons = $state<BarDataPoint[]>([]);

	let senatorialResults = $state<BarDataPoint[]>([]);

	let turnoutComparisonData = $state<{ governorRace: number; referendum: number }>({
		governorRace: 54.7,
		referendum: 52.3
	});

	// Load data from JSON
	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/chapters/referendum-2020.json`);
			const data: ChapterData = await response.json();

			islandResults = data.islandResults;
			municipalityResults = data.municipalityResults;
			historicalData = data.historicalData;
			globalComparisons = data.globalComparisons;
			senatorialResults = data.senatorialResults;
			turnoutComparisonData = data.turnoutComparison;
		} catch (err) {
			console.error('Failed to load referendum-2020 data:', err);
		} finally {
			loading = false;
		}
	});

	// Turnout comparison for display
	let turnoutComparison = $derived([
		{ label: content.governorRace, value: turnoutComparisonData.governorRace, color: CATEGORY_COLORS[0] },
		{ label: content.referendum, value: turnoutComparisonData.referendum, color: CATEGORY_COLORS[1] }
	]);

	// Animated countdown state
	let displayPercent = $state(0);
	let countdownComplete = $state(false);

	let mapData = $state(new Map<string, number>());
	const colorScale = createDivergingScale([40, 50, 60]);

	// Line chart data for historical trend
	let historicalSeriesLabel = $derived(content.statehoodSupportLabel);
	let historicalSeries = $derived([
		{
			id: 'statehood',
			label: historicalSeriesLabel,
			color: '#6b9080',
			data: historicalData
				.filter(d => d.year !== 2017) // Exclude boycotted referendum
				.map(d => ({ x: d.year, y: d.statehood }))
		}
	]);

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
	<title>{content.chapter} {chapterNum}: {chapterTitle} | Puerto Rico Elections</title>
</svelte:head>

<Progress {currentStep} {totalSteps} chapterTitle={chapterTitle} />

<article class="chapter">
	<header class="chapter-header">
		<div class="container content">
			<span class="label">{content.chapter} {chapterNum}</span>
			<div class="accent-line"></div>
			<h1>{chapterTitle}</h1>
			<p class="lead">{content.lead}</p>
		</div>
	</header>

	<ScrollySection offset={0.6} onStepEnter={handleStepEnter}>
		{#snippet graphic()}
			<div class="viz-container">
				{#if loading}
					<p class="loading">{content.loading}</p>
				{:else if activeViz === 'countdown'}
					<div class="countdown-display">
						<div class="ballot-question">
							<span class="question-label">{content.theQuestion}</span>
							<blockquote>
								"{content.ballotQuestion}"
							</blockquote>
						</div>
						{#if displayPercent > 0}
							<div class="countdown-number" class:complete={countdownComplete}>
								<span class="percent-value">{displayPercent.toFixed(1)}</span>
								<span class="percent-sign">%</span>
								<span class="percent-label">{content.votedYes}</span>
							</div>
						{/if}
					</div>
				{:else if activeViz === 'result'}
					<div class="result-display">
						<h3 class="viz-title">{content.finalResults}</h3>
						<div class="result-bars">
							<div class="result-bar yes">
								<div class="bar-fill" style="width: {islandResults.siPercent}%"></div>
								<div class="bar-label">
									<span class="option">{content.siYes}</span>
									<span class="votes">{formatNumber(islandResults.si)} {content.votes}</span>
									<span class="percent">{islandResults.siPercent}%</span>
								</div>
							</div>
							<div class="result-bar no">
								<div class="bar-fill" style="width: {islandResults.noPercent}%"></div>
								<div class="bar-label">
									<span class="option">{content.no}</span>
									<span class="votes">{formatNumber(islandResults.no)} {content.votes}</span>
									<span class="percent">{islandResults.noPercent}%</span>
								</div>
							</div>
						</div>
						<div class="result-total">
							{content.totalVotes}: {formatNumber(islandResults.total)}
						</div>
						<div class="margin-highlight">
							<span class="margin-value">62,834</span>
							<span class="margin-label">{content.voteMargin}</span>
						</div>
					</div>
				{:else if activeViz === 'map'}
					<h3 class="viz-title">{content.statehoodSupport}</h3>
					<ChoroplethMap
						data={mapData}
						colorScale={colorScale}
						tooltipFormat={(name, value) =>
							value !== undefined ? `${name}: ${value.toFixed(1)}% ${$language === 'en' ? 'Yes' : 'Si'}` : name
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
								<span>{content.legendNo}</span>
								<span>{content.legendMid}</span>
								<span>{content.legendYes}</span>
							</div>
						</div>
					{/if}
				{:else if activeViz === 'senatorial'}
					<h3 class="viz-title">{content.senatorialResults}</h3>
					<BarChart
						data={senatorialResults}
						width={500}
						height={350}
						horizontal={true}
						valueFormat={(v) => `${v.toFixed(1)}%`}
					/>
					<div class="viz-note">{content.senatorialNote}</div>
				{:else if activeViz === 'turnout'}
					<h3 class="viz-title">{content.turnoutComparison}</h3>
					<div class="turnout-comparison">
						<div class="turnout-item">
							<div class="turnout-bar governor" style="width: 54.7%"></div>
							<div class="turnout-label">
								<span class="turnout-name">{content.governorRace}</span>
								<span class="turnout-value">54.7%</span>
							</div>
						</div>
						<div class="turnout-item">
							<div class="turnout-bar referendum" style="width: 52.3%"></div>
							<div class="turnout-label">
								<span class="turnout-name">{content.referendum}</span>
								<span class="turnout-value">52.3%</span>
							</div>
						</div>
					</div>
					<div class="turnout-note">
						{content.turnoutNote}
					</div>
				{:else if activeViz === 'historical'}
					<h3 class="viz-title">{content.historicalTitle}</h3>
					<LineChart
						series={historicalSeries}
						width={550}
						height={380}
						xLabel={content.year}
						yLabel="{content.statehoodSupportLabel} (%)"
						xFormat={(v) => String(v)}
						yFormat={(v) => `${v}%`}
						showArea={true}
					/>
					<div class="viz-note">{content.historicalNote}</div>
				{:else if activeViz === 'global'}
					<h3 class="viz-title">{content.globalTitle}</h3>
					<BarChart
						data={globalComparisons}
						width={500}
						height={320}
						horizontal={true}
						valueFormat={(v) => `${v.toFixed(1)}%`}
					/>
					<div class="viz-note">
						{content.globalNote}
					</div>
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>{content.step0Title}</h3>
			<p>{content.step0p1}</p>
			<p>
				{content.step0p2}
				{content.step0p2b} <span class="highlight">{content.yes}</span> {content.step0p2c} <span class="highlight">{content.no}</span>.
			</p>
			<p>
				{content.step0p3}
				<em>{content.immediately}</em> {content.step0p3b}
			</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>{content.step1Title}</h3>
			<p>{content.step1p1}</p>
			<p>{content.step1p2}</p>
			<p>{content.step1p3}</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>{content.step2Title}</h3>
			<p>
				{content.step2p1pre}<span class="stat">52.52%</span> {content.step2p1mid} <span class="stat">47.48%</span>
				{content.step2p1b}
			</p>
			<p>
				{content.step2p2pre} <span class="stat">62,834</span> {content.step2p2mid}
			</p>
			<p>{content.step2p3}</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>{content.step3Title}</h3>
			<p>{content.step3p1}</p>
			<p>{content.step3p2}</p>
			<p>{content.step3p3}</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>{content.step4Title}</h3>
			<p>
				{content.step4p1pre} <span class="highlight">{content.step4p1a}</span>
				{content.step4p1b} <span class="highlight">{content.step4p1c}</span> {content.step4p1d}
			</p>
			<p>
				{content.step4p2pre}<span class="stat">Ceiba</span> {content.step4p2a}
				<span class="stat">Vieques</span> {content.step4p2b}
			</p>
			<p>
				{content.step4p3pre}
				<em>{content.step4p3a}</em> {content.step4p3b}
			</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>{content.step5Title}</h3>
			<p>{content.step5p1}</p>
			<p>{content.step5p2}</p>
			<p>{content.step5p3}</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>{content.step6Title}</h3>
			<p>{content.step6p1}</p>
			<p>{content.step6p2}</p>
			<p>{content.step6p3}</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>{content.step7Title}</h3>
			<p>{content.step7p1}</p>
			<p>{content.step7p2}</p>
			<p>{content.step7p3}</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>{content.step8Title}</h3>
			<p>{content.step8p1}</p>
			<p>{content.step8p2}</p>
			<p>{content.step8p3}</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>{content.step9Title}</h3>
			<p>{content.step9p1}</p>
			<p>{content.step9p2}</p>
			<p>{content.step9p3}</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>{content.conclusionTitle}</h2>
			<p>{content.conclusionP1}</p>

			<div class="stat-grid">
				<div class="stat-card">
					<span class="stat-value">52.52%</span>
					<span class="stat-label">{content.statVotedYes}</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">62,834</span>
					<span class="stat-label">{content.statVoteMargin}</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">6{$language === 'en' ? 'th' : 'to'}</span>
					<span class="stat-label">{content.statReferendum}</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">0</span>
					<span class="stat-label">{content.statCongressVotes}</span>
				</div>
			</div>

			<div class="headline-moment">
				<div class="newspaper-style">
					<span class="dateline">{content.dateline}</span>
					<h3>{content.headline}</h3>
					<p class="subhead">{content.subhead}</p>
				</div>
			</div>

			<div class="sources">
				<h3>{content.sources}</h3>
				<ul>
					<li><a href="https://ww2.ceepur.org/Home/EventosElectorales" target="_blank" rel="noopener">Comision Estatal de Elecciones de Puerto Rico (CEE)</a> - {content.sourceCEE}</li>
					<li><a href="https://data.census.gov/" target="_blank" rel="noopener">U.S. Census Bureau</a> - {content.sourceCensus}</li>
					<li><a href="https://www.electoralcommission.org.uk/" target="_blank" rel="noopener">UK Electoral Commission</a> - {content.sourceBrexit}</li>
					<li><a href="https://www.electoralmanagement.scot/" target="_blank" rel="noopener">Electoral Management Board for Scotland</a> - {content.sourceScotland}</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/plebiscites" class="nav-link prev">
					<span class="nav-direction">{content.previous}</span>
					<span class="nav-title">{content.prevTitle}</span>
				</a>
				<a href="{base}/chapters/geography" class="nav-link next">
					<span class="nav-direction">{content.nextChapter}</span>
					<span class="nav-title">{content.nextTitle}</span>
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
		border-left: 4px solid var(--color-accent);
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
		color: var(--color-accent);
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
		color: var(--color-accent);
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
		background: var(--color-accent);
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
		color: var(--color-accent);
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
</style>
