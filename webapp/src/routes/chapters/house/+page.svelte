<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { LineChart, BarChart } from '$lib/components/charts';
	import { Legend } from '$lib/components/ui';
	import { PARTY_COLORS, CATEGORY_COLORS } from '$lib/utils/colors';
	import { formatPercent, formatPercentChange } from '$lib/utils/format';
	import { language } from '$lib/stores/language';

	const chapterNum = 11;
	const totalSteps = 10;

	// Bilingual content
	const t = {
		en: {
			chapterTitle: '40 Districts, 40 Stories',
			chapter: 'Chapter',
			lead: "Puerto Rico's House of Representatives has 40 district seats, each representing a distinct slice of the island. Unlike the Senate's regional districts or the governor's island-wide race, House elections are intensely local affairs where a few hundred votes can decide who represents your community.",
			loading: 'Loading data...',
			// Viz titles and notes
			vizCompetitiveness: 'District Competitiveness (2020)',
			vizSeatComposition: 'House Seat Composition',
			vizVictoryMargins: 'Victory Margins (2020)',
			vizClosestRaces: 'Closest Races (2020)',
			vizFlipped: 'Districts That Flipped (2016-2020)',
			vizThirdParty: 'Third-Party Vote Share (2020)',
			noteSeatLost: 'PNP lost {count} seats from 2016 to 2020',
			noteRacesDecided: '{count} races decided by less than 2%',
			noteMarginVictory: 'Margin of victory by district',
			noteMarginShift: 'PNP margin shift (negative = PPD gain)',
			noteTopDistricts: 'Top districts by MVC/PIP/PD combined vote',
			labelDistricts: 'districts',
			labelRaces: 'races',
			// Legend
			legendPNP: 'PNP advantage',
			legendTossup: 'Tossup',
			legendPPD: 'PPD advantage',
			// Chart axis labels
			electionYear: 'Election Year',
			seatsWon: 'Seats Won',
			// Inline text
			theResultIs: 'The result is',
			districtsLike: 'Districts like',
			and: 'and',
			seats: 'seats',
			// Step titles
			step0Title: 'The Most Local Level',
			step1Title: 'House vs. Senate: A Different Game',
			step2Title: 'The Competitiveness Landscape',
			step3Title: 'How Close Are These Races?',
			step4Title: 'The Closest Calls',
			step5Title: 'The 2020 Earthquake',
			step6Title: 'The Districts That Flipped',
			step7Title: 'The Third-Party Factor',
			step8Title: 'Local Issues, Local Politics',
			step9Title: 'The Path to Majority',
			// Step content
			step0p1: "The House of Representatives is where Puerto Rico politics gets personal. Each of the 40 districts has roughly",
			step0p1b: "residents, small enough that a representative might know their constituents by name in the smaller precincts. This is the chamber where neighborhood issues--potholes, school funding, water service--dominate the agenda.",
			step0p2: "Unlike the Senate (which uses 8 larger senatorial districts) or the governor's race (island-wide), House districts reflect the hyper-local political landscape. A district might encompass a single large municipality or stitch together parts of several smaller ones.",
			step0p3: "40 distinct political stories",
			step0p3b: ", each shaped by local demographics, economic conditions, and community ties that don't always align with island-wide party trends.",
			step1p1: "The Senate's 8 senatorial districts elect 2 senators each (16 total), plus 11 at-large senators--27 members total. The House's 40 single-member districts create a fundamentally different dynamic:",
			step1p1b: "winner-take-all in each district",
			step1p2: "In the Senate, proportional representation ensures minority parties get some seats. But in House districts, coming in second means nothing. A party can win 49% of the vote and still get zero seats from that district.",
			step1p3: "This makes the House more susceptible to",
			step1p3b: "wave elections",
			step1p3c: ": when one party has a good year, they can sweep competitive districts and build large majorities. When the tide turns, those gains can evaporate just as quickly--as PNP learned in 2020.",
			step2p1: "Of Puerto Rico's 40 House districts, the 2020 election revealed a surprisingly competitive landscape.",
			step2p1b: "districts--more than half--were decided by margins under 5 percentage points.",
			step2p2pre: "Only",
			step2p2: "districts were truly 'safe' with margins over 10%. The rest are battlegrounds where turnout, candidate quality, and local issues can swing the outcome.",
			step2p3: "This volatility reflects Puerto Rico's fragmenting party system. When voters are willing to consider third parties, even historically safe districts become competitive. The old certainties of the PNP-PPD duopoly no longer hold.",
			step3p1: "The margin distribution tells a stark story: House races in Puerto Rico are knife-edge affairs. In 2020,",
			step3p1b: "races were decided by less than 2%--often just a few hundred votes out of thousands cast.",
			step3p2pre: "Another",
			step3p2a: "races fell in the 2-5% range. Combined, that's",
			step3p2b: "races--nearly half the chamber--where the outcome was genuinely uncertain.",
			step3p3: "For campaign strategists, this means",
			step3p3b: "turnout operations matter enormously",
			step3p3c: ". In a district with 20,000 voters, a 2% margin is just 400 votes. A good get-out-the-vote effort can easily swing that many.",
			step4p1pre: "The tightest race in 2020 was decided by just",
			step4p1: "--a margin so slim that a recount could theoretically change the outcome. These razor-thin contests represent the ultimate test of democratic participation: every vote, literally, could be the deciding one.",
			step4p2: "exemplify the volatility of House races. These aren't ideological battlegrounds fought over big issues; they're communities where both parties have roughly equal support and elections become tests of mobilization.",
			step4p3: "For the representatives who win these races, governing is a constant campaign. A few hundred unhappy constituents could cost them their seat in the next election.",
			step5p1pre: "The 2020 election fundamentally reshaped the House. PNP went from controlling",
			step5p1mid: "seats in 2016 to just",
			step5p1mid2: "in 2020--a loss of",
			step5p1post: "seats. PPD correspondingly surged from",
			step5p1post2: "to",
			step5p2pre: "This wasn't a gradual shift; it was a",
			step5p2: "wave election",
			step5p2b: ". Frustration with the PNP government after Hurricane Maria, the Rossello protests, and the pandemic combined to create a perfect storm of anti-incumbent sentiment. Competitive districts that had leaned PNP broke decisively for PPD.",
			step5p3: "The question for 2024: was this a permanent realignment, or will the pendulum swing back? History suggests Puerto Rican voters are willing to punish both parties when they feel let down.",
			step6p1pre: "",
			step6p1: "districts changed party control between 2016 and 2020. These flips weren't random--they followed a geographic pattern, with western and rural districts leading the shift away from PNP.",
			step6p2: "The magnitude of some shifts was remarkable. Districts that PNP had won by comfortable margins in 2016 swung 15-20 percentage points to hand PPD decisive victories. This kind of volatility is unusual even in Puerto Rico's historically competitive elections.",
			step6p3pre: "What drove these flips? The data suggests a combination of factors:",
			step6p3: "incumbent fatigue",
			step6p3b: ", economic conditions, post-Maria recovery disparities, and the rise of younger voters more willing to abandon traditional party loyalties.",
			step7p1pre: "While no third party won a House district seat in 2020, their presence reshaped the competitive landscape. In the top districts, MVC, PIP, and Proyecto Dignidad combined for",
			step7p1: "of the vote or more.",
			step7p2: "This third-party vote doesn't distribute evenly. Urban, educated districts showed the strongest third-party presence, particularly for MVC. These are the districts where traditional PNP-PPD loyalty has weakened most dramatically.",
			step7p3: "For the major parties, this creates a strategic dilemma. Do they move toward the center to capture third-party-curious voters? Or do they double down on their base, hoping third parties split the opposition? The answer may determine who controls the House in 2024.",
			step8p1: "House races are won and lost on local issues that rarely make the news. Infrastructure--roads, water, electricity--dominates constituent concerns in many districts. Post-Maria, these concerns became even more acute: which representative can actually deliver recovery funds?",
			step8p2: "In rural districts, agricultural policy and land use matter. In urban districts, housing costs and public safety take precedence. Representatives who can credibly address these",
			step8p2b: "kitchen-table concerns",
			step8p2c: "build personal brands that can survive island-wide party swings.",
			step8p3: "This is why some representatives hold their seats for decades while others are one-and-done. The best House members understand that their job is part legislator, part social worker, part constituent services office. Those who treat it as just a stepping stone rarely last.",
			step9p1pre: "Control of the House requires",
			step9p1: "seats--a simple majority of the 40 districts (plus at-large seats bring the total chamber to 51). With 23 tossup districts in 2020, the battleground is vast.",
			step9p2: "For PNP, recovering their 2016 majority means winning back flipped districts while defending their remaining strongholds. For PPD, it means consolidating 2020 gains and proving they can govern effectively. For third parties, the goal is breaking through to win actual seats, not just influence margins.",
			step9p3: "The math is unforgiving: there are only so many truly competitive districts. Winning them all--or losing them all--is the difference between governing and opposition. In Puerto Rico's House, the battlefield is small, but the stakes are enormous.",
			// Conclusion
			conclusionTitle: '40 Stories, One Chamber',
			conclusionP1: "Each of Puerto Rico's 40 House districts tells a unique political story. Some are PNP strongholds rooted in statehood sentiment and urban professional voters. Others are PPD bastions where autonomy politics and rural traditions hold sway. And increasingly, many are genuinely competitive spaces where either party--or emerging third parties--could win.",
			conclusionP2: "Understanding the House requires zooming in: not just to districts, but to precincts, neighborhoods, and communities. It's the most granular level of Puerto Rican democracy, where every vote truly counts and local issues shape island-wide outcomes.",
			// Stats
			statsTitle: 'House Elections: 2020 Snapshot',
			statTossupDistricts: 'Tossup Districts',
			statDistrictsFlipped: 'Districts Flipped',
			statPNPSeatsLost: 'PNP Seats Lost',
			statClosestMargin: 'Closest Margin',
			// Sources
			sources: 'Sources',
			sourceCEE: 'House of Representatives results 2000-2024',
			sourceCamara: 'Historical composition data',
			sourceConstitution: 'Puerto Rico Constitution - Representative district boundaries and requirements',
			sourceICPSR: 'Legislative electoral data',
			// Navigation
			previous: 'Previous',
			nextChapter: 'Next Chapter',
			prevTitle: 'The Senate Districts',
			nextTitle: "Puerto Rico's Electoral Future"
		},
		es: {
			chapterTitle: '40 Distritos, 40 Historias',
			chapter: 'Capitulo',
			lead: 'La Camara de Representantes de Puerto Rico tiene 40 escanos distritales, cada uno representando una porcion distinta de la isla. A diferencia de los distritos regionales del Senado o la carrera del gobernador a nivel isla, las elecciones de la Camara son asuntos intensamente locales donde unos pocos cientos de votos pueden decidir quien representa a tu comunidad.',
			loading: 'Cargando datos...',
			// Viz titles and notes
			vizCompetitiveness: 'Competitividad de Distritos (2020)',
			vizSeatComposition: 'Composicion de Escanos en la Camara',
			vizVictoryMargins: 'Margenes de Victoria (2020)',
			vizClosestRaces: 'Carreras Mas Renidas (2020)',
			vizFlipped: 'Distritos que Cambiaron (2016-2020)',
			vizThirdParty: 'Voto de Terceros Partidos (2020)',
			noteSeatLost: 'PNP perdio {count} escanos de 2016 a 2020',
			noteRacesDecided: '{count} carreras decididas por menos del 2%',
			noteMarginVictory: 'Margen de victoria por distrito',
			noteMarginShift: 'Cambio de margen PNP (negativo = ganancia PPD)',
			noteTopDistricts: 'Principales distritos por voto combinado MVC/PIP/PD',
			labelDistricts: 'distritos',
			labelRaces: 'carreras',
			// Legend
			legendPNP: 'Ventaja PNP',
			legendTossup: 'Competitivo',
			legendPPD: 'Ventaja PPD',
			// Chart axis labels
			electionYear: 'Ano Electoral',
			seatsWon: 'Escanos Ganados',
			// Inline text
			theResultIs: 'El resultado es',
			districtsLike: 'Distritos como',
			and: 'y',
			seats: 'escanos',
			// Step titles
			step0Title: 'El Nivel Mas Local',
			step1Title: 'Camara vs. Senado: Un Juego Diferente',
			step2Title: 'El Panorama de Competitividad',
			step3Title: 'Que Tan Renidas Son Estas Carreras?',
			step4Title: 'Las Contiendas Mas Cerradas',
			step5Title: 'El Terremoto de 2020',
			step6Title: 'Los Distritos que Cambiaron',
			step7Title: 'El Factor de Terceros Partidos',
			step8Title: 'Asuntos Locales, Politica Local',
			step9Title: 'El Camino a la Mayoria',
			// Step content
			step0p1: 'La Camara de Representantes es donde la politica de Puerto Rico se vuelve personal. Cada uno de los 40 distritos tiene aproximadamente',
			step0p1b: 'residentes, lo suficientemente pequeno para que un representante pueda conocer a sus constituyentes por nombre en los precintos mas pequenos. Esta es la camara donde los asuntos del vecindario--baches, fondos escolares, servicio de agua--dominan la agenda.',
			step0p2: 'A diferencia del Senado (que usa 8 distritos senatoriales mas grandes) o la carrera del gobernador (a nivel isla), los distritos de la Camara reflejan el panorama politico hiperlocal. Un distrito puede abarcar un solo municipio grande o unir partes de varios mas pequenos.',
			step0p3: '40 historias politicas distintas',
			step0p3b: ', cada una moldeada por demografia local, condiciones economicas y lazos comunitarios que no siempre se alinean con las tendencias partidistas a nivel isla.',
			step1p1: 'Los 8 distritos senatoriales del Senado eligen 2 senadores cada uno (16 en total), mas 11 senadores por acumulacion--27 miembros en total. Los 40 distritos uninominales de la Camara crean una dinamica fundamentalmente diferente:',
			step1p1b: 'el ganador se lo lleva todo en cada distrito',
			step1p2: 'En el Senado, la representacion proporcional asegura que los partidos minoritarios obtengan algunos escanos. Pero en los distritos de la Camara, quedar segundo no significa nada. Un partido puede ganar el 49% de los votos y aun asi obtener cero escanos de ese distrito.',
			step1p3: 'Esto hace que la Camara sea mas susceptible a',
			step1p3b: 'elecciones de ola',
			step1p3c: ': cuando un partido tiene un buen ano, puede barrer los distritos competitivos y construir grandes mayorias. Cuando cambia la marea, esas ganancias pueden evaporarse igual de rapido--como aprendio el PNP en 2020.',
			step2p1: 'De los 40 distritos de la Camara de Puerto Rico, la eleccion de 2020 revelo un panorama sorprendentemente competitivo.',
			step2p1b: 'distritos--mas de la mitad--fueron decididos por margenes menores a 5 puntos porcentuales.',
			step2p2pre: 'Solo',
			step2p2: "distritos eran verdaderamente 'seguros' con margenes mayores al 10%. El resto son campos de batalla donde la participacion, la calidad del candidato y los asuntos locales pueden cambiar el resultado.",
			step2p3: 'Esta volatilidad refleja la fragmentacion del sistema de partidos de Puerto Rico. Cuando los votantes estan dispuestos a considerar terceros partidos, incluso los distritos historicamente seguros se vuelven competitivos. Las viejas certezas del duopolio PNP-PPD ya no se sostienen.',
			step3p1: 'La distribucion de margenes cuenta una historia contundente: las carreras de la Camara en Puerto Rico son asuntos al filo de la navaja. En 2020,',
			step3p1b: 'carreras fueron decididas por menos del 2%--a menudo solo unos pocos cientos de votos de miles emitidos.',
			step3p2pre: 'Otras',
			step3p2a: 'carreras cayeron en el rango del 2-5%. Combinadas, son',
			step3p2b: 'carreras--casi la mitad de la camara--donde el resultado era genuinamente incierto.',
			step3p3: 'Para los estrategas de campana, esto significa que',
			step3p3b: 'las operaciones de participacion importan enormemente',
			step3p3c: '. En un distrito con 20,000 votantes, un margen del 2% son solo 400 votos. Un buen esfuerzo de movilizacion puede facilmente mover esa cantidad.',
			step4p1pre: 'La carrera mas cerrada en 2020 fue decidida por solo',
			step4p1: '--un margen tan estrecho que un recuento teoricamente podria cambiar el resultado. Estas contiendas al filo de la navaja representan la prueba maxima de participacion democratica: cada voto, literalmente, podria ser el decisivo.',
			step4p2: 'ejemplifican la volatilidad de las carreras de la Camara. Estas no son campos de batalla ideologicos peleados por grandes temas; son comunidades donde ambos partidos tienen apoyo aproximadamente igual y las elecciones se convierten en pruebas de movilizacion.',
			step4p3: 'Para los representantes que ganan estas carreras, gobernar es una campana constante. Unos pocos cientos de constituyentes descontentos podrian costarles su escano en la proxima eleccion.',
			step5p1pre: 'La eleccion de 2020 remodelo fundamentalmente la Camara. El PNP paso de controlar',
			step5p1mid: 'escanos en 2016 a solo',
			step5p1mid2: 'en 2020--una perdida de',
			step5p1post: 'escanos. El PPD correspondio con un aumento de',
			step5p1post2: 'a',
			step5p2pre: 'Este no fue un cambio gradual; fue una',
			step5p2: 'eleccion de ola',
			step5p2b: '. La frustracion con el gobierno del PNP despues del Huracan Maria, las protestas de Rossello y la pandemia se combinaron para crear una tormenta perfecta de sentimiento anti-incumbente. Los distritos competitivos que se inclinaban hacia el PNP se volcaron decisivamente hacia el PPD.',
			step5p3: 'La pregunta para 2024: fue esto un realineamiento permanente, o el pendulo volvera a oscilar? La historia sugiere que los votantes puertorriquenos estan dispuestos a castigar a ambos partidos cuando se sienten decepcionados.',
			step6p1pre: '',
			step6p1: 'distritos cambiaron de control partidista entre 2016 y 2020. Estos cambios no fueron aleatorios--siguieron un patron geografico, con los distritos del oeste y rurales liderando el alejamiento del PNP.',
			step6p2: 'La magnitud de algunos cambios fue notable. Distritos que el PNP habia ganado por margenes comodos en 2016 oscilaron 15-20 puntos porcentuales para dar al PPD victorias decisivas. Este tipo de volatilidad es inusual incluso en las elecciones historicamente competitivas de Puerto Rico.',
			step6p3pre: 'Que impulso estos cambios? Los datos sugieren una combinacion de factores:',
			step6p3: 'fatiga del incumbente',
			step6p3b: ', condiciones economicas, disparidades en la recuperacion post-Maria, y el surgimiento de votantes mas jovenes mas dispuestos a abandonar las lealtades partidistas tradicionales.',
			step7p1pre: 'Aunque ningun tercer partido gano un escano distrital de la Camara en 2020, su presencia remodelo el panorama competitivo. En los principales distritos, MVC, PIP y Proyecto Dignidad combinaron',
			step7p1: 'del voto o mas.',
			step7p2: 'Este voto de terceros partidos no se distribuye uniformemente. Los distritos urbanos y educados mostraron la mayor presencia de terceros partidos, particularmente para MVC. Estos son los distritos donde la lealtad tradicional PNP-PPD se ha debilitado mas dramaticamente.',
			step7p3: 'Para los partidos principales, esto crea un dilema estrategico. Se mueven hacia el centro para captar votantes curiosos por terceros partidos? O duplican su apuesta en su base, esperando que los terceros partidos dividan la oposicion? La respuesta puede determinar quien controla la Camara en 2024.',
			step8p1: 'Las carreras de la Camara se ganan y se pierden con asuntos locales que rara vez salen en las noticias. La infraestructura--carreteras, agua, electricidad--domina las preocupaciones de los constituyentes en muchos distritos. Despues de Maria, estas preocupaciones se volvieron aun mas agudas: que representante puede realmente conseguir fondos de recuperacion?',
			step8p2: 'En distritos rurales, la politica agricola y el uso del suelo importan. En distritos urbanos, los costos de vivienda y la seguridad publica tienen prioridad. Los representantes que pueden abordar crediblemente estas',
			step8p2b: 'preocupaciones del dia a dia',
			step8p2c: 'construyen marcas personales que pueden sobrevivir a los cambios partidistas a nivel isla.',
			step8p3: 'Por eso algunos representantes mantienen sus escanos por decadas mientras otros duran un solo termino. Los mejores miembros de la Camara entienden que su trabajo es parte legislador, parte trabajador social, parte oficina de servicios al constituyente. Los que lo tratan solo como un escalon rara vez duran.',
			step9p1pre: 'Controlar la Camara requiere',
			step9p1: 'escanos--una mayoria simple de los 40 distritos (mas los escanos por acumulacion que llevan el total de la camara a 51). Con 23 distritos competitivos en 2020, el campo de batalla es vasto.',
			step9p2: 'Para el PNP, recuperar su mayoria de 2016 significa ganar de vuelta los distritos que cambiaron mientras defienden sus bastiones restantes. Para el PPD, significa consolidar las ganancias de 2020 y demostrar que pueden gobernar efectivamente. Para los terceros partidos, la meta es romper la barrera para ganar escanos reales, no solo influir en margenes.',
			step9p3: 'Las matematicas son implacables: solo hay tantos distritos verdaderamente competitivos. Ganarlos todos--o perderlos todos--es la diferencia entre gobernar y oposicion. En la Camara de Puerto Rico, el campo de batalla es pequeno, pero las apuestas son enormes.',
			// Conclusion
			conclusionTitle: '40 Historias, Una Camara',
			conclusionP1: 'Cada uno de los 40 distritos de la Camara de Puerto Rico cuenta una historia politica unica. Algunos son bastiones del PNP arraigados en el sentimiento estadista y votantes profesionales urbanos. Otros son bastiones del PPD donde la politica de autonomia y las tradiciones rurales prevalecen. Y cada vez mas, muchos son espacios genuinamente competitivos donde cualquier partido--o terceros partidos emergentes--podria ganar.',
			conclusionP2: 'Entender la Camara requiere hacer zoom: no solo a distritos, sino a precintos, vecindarios y comunidades. Es el nivel mas granular de la democracia puertorriquena, donde cada voto realmente cuenta y los asuntos locales dan forma a los resultados a nivel isla.',
			// Stats
			statsTitle: 'Elecciones de la Camara: Instantanea 2020',
			statTossupDistricts: 'Distritos Competitivos',
			statDistrictsFlipped: 'Distritos que Cambiaron',
			statPNPSeatsLost: 'Escanos Perdidos por PNP',
			statClosestMargin: 'Margen Mas Cerrado',
			// Sources
			sources: 'Fuentes',
			sourceCEE: 'Resultados de la Camara de Representantes 2000-2024',
			sourceCamara: 'Datos historicos de composicion',
			sourceConstitution: 'Constitucion de Puerto Rico - Limites y requisitos de distritos representativos',
			sourceICPSR: 'Datos electorales legislativos',
			// Navigation
			previous: 'Anterior',
			nextChapter: 'Proximo Capitulo',
			prevTitle: 'Los Distritos Senatoriales',
			nextTitle: 'El Futuro Electoral de Puerto Rico'
		}
	};

	// Reactive content based on language
	let content = $derived(t[$language]);
	let chapterTitle = $derived(content.chapterTitle);

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

	// District competitiveness bar data (2020) - bilingual labels
	let competitivenessBarData = $derived(() => {
		const comp = competitivenessData['2020'];
		if (!comp) return [];
		const safePNPLabel = $language === 'en' ? 'Safe PNP (>10%)' : 'PNP Seguro (>10%)';
		const leanPNPLabel = $language === 'en' ? 'Lean PNP (5-10%)' : 'Inclina PNP (5-10%)';
		const tossupLabel = $language === 'en' ? 'Tossup (<5%)' : 'Competitivo (<5%)';
		const leanPPDLabel = $language === 'en' ? 'Lean PPD (5-10%)' : 'Inclina PPD (5-10%)';
		const safePPDLabel = $language === 'en' ? 'Safe PPD (>10%)' : 'PPD Seguro (>10%)';
		return [
			{ label: safePNPLabel, value: comp.safe_pnp, color: PARTY_COLORS.PNP },
			{ label: leanPNPLabel, value: comp.lean_pnp, color: '#4a7ab8' },
			{ label: tossupLabel, value: comp.competitive, color: CATEGORY_COLORS[5] },
			{ label: leanPPDLabel, value: comp.lean_ppd, color: '#d86060' },
			{ label: safePPDLabel, value: comp.safe_ppd, color: PARTY_COLORS.PPD },
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
				{:else if activeViz === 'competitiveness'}
					<h3 class="viz-title">{content.vizCompetitiveness}</h3>
					<BarChart
						data={competitivenessBarData()}
						width={420}
						height={300}
						horizontal={true}
						valueFormat={(v) => `${v} ${content.labelDistricts}`}
						showValues={true}
					/>
					<Legend
						items={[
							{ label: content.legendPNP, color: PARTY_COLORS.PNP },
							{ label: content.legendTossup, color: CATEGORY_COLORS[5] },
							{ label: content.legendPPD, color: PARTY_COLORS.PPD }
						]}
					/>
				{:else if activeViz === 'seatTrend'}
					<h3 class="viz-title">{content.vizSeatComposition}</h3>
					<LineChart
						series={seatTrendData()}
						width={420}
						height={300}
						xLabel={content.electionYear}
						yLabel={content.seatsWon}
						xFormat={(v) => String(v)}
						yFormat={(v) => String(Math.round(v))}
						showArea={true}
					/>
					<p class="viz-note">
						{content.noteSeatLost.replace('{count}', String(stats().seatSwing > 0 ? stats().seatSwing : -stats().seatSwing))}
					</p>
				{:else if activeViz === 'marginDist'}
					<h3 class="viz-title">{content.vizVictoryMargins}</h3>
					<BarChart
						data={marginDistBarData()}
						width={420}
						height={280}
						horizontal={false}
						valueFormat={(v) => `${v} ${content.labelRaces}`}
						showValues={true}
					/>
					<p class="viz-note">
						{content.noteRacesDecided.replace('{count}', String(marginDistribution['2020']?.['0-2'] || 0))}
					</p>
				{:else if activeViz === 'closestRaces'}
					<h3 class="viz-title">{content.vizClosestRaces}</h3>
					<BarChart
						data={closestRacesBarData()}
						width={420}
						height={320}
						horizontal={true}
						valueFormat={(v) => `${v.toFixed(1)}%`}
						showValues={true}
					/>
					<p class="viz-note">{content.noteMarginVictory}</p>
				{:else if activeViz === 'flipped'}
					<h3 class="viz-title">{content.vizFlipped}</h3>
					<BarChart
						data={flippedBarData()}
						width={420}
						height={380}
						horizontal={true}
						valueFormat={(v) => `${v > 0 ? '+' : ''}${v.toFixed(1)}pp`}
						showValues={true}
					/>
					<p class="viz-note">{content.noteMarginShift}</p>
				{:else if activeViz === 'thirdParty'}
					<h3 class="viz-title">{content.vizThirdParty}</h3>
					<BarChart
						data={thirdPartyBarData()}
						width={420}
						height={320}
						horizontal={true}
						valueFormat={(v) => `${v.toFixed(1)}%`}
						showValues={true}
					/>
					<p class="viz-note">{content.noteTopDistricts}</p>
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>{content.step0Title}</h3>
			<p>
				{content.step0p1} <span class="stat">45,000</span> {content.step0p1b}
			</p>
			<p>{content.step0p2}</p>
			<p>
				{content.theResultIs} <span class="highlight">{content.step0p3}</span>{content.step0p3b}
			</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>{content.step1Title}</h3>
			<p>
				{content.step1p1} <span class="highlight">{content.step1p1b}</span>.
			</p>
			<p>{content.step1p2}</p>
			<p>
				{content.step1p3} <span class="highlight">{content.step1p3b}</span>{content.step1p3c}
			</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>{content.step2Title}</h3>
			<p>
				{content.step2p1} <span class="stat">{stats().totalTossups}</span> {content.step2p1b}
			</p>
			<p>
				{content.step2p2pre} <span class="stat">{(competitivenessData['2020']?.safe_pnp || 0) +
				(competitivenessData['2020']?.safe_ppd || 0)}</span> {content.step2p2}
			</p>
			<p>{content.step2p3}</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>{content.step3Title}</h3>
			<p>
				{content.step3p1} <span class="stat">{marginDistribution['2020']?.['0-2'] || 0}</span> {content.step3p1b}
			</p>
			<p>
				{content.step3p2pre} <span class="stat">{marginDistribution['2020']?.['2-5'] || 0}</span> {content.step3p2a}
				{(marginDistribution['2020']?.['0-2'] || 0) + (marginDistribution['2020']?.['2-5'] || 0)} {content.step3p2b}
			</p>
			<p>
				{content.step3p3} <span class="highlight">{content.step3p3b}</span>{content.step3p3c}
			</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>{content.step4Title}</h3>
			<p>
				{content.step4p1pre} <span class="stat">{formatPercent(stats().closestMargin, 1)}</span>{content.step4p1}
			</p>
			<p>
				{content.districtsLike} {closestRaces[0]?.district || 'District 31'} {content.and}
				{closestRaces[1]?.district || 'District 18'} {content.step4p2}
			</p>
			<p>{content.step4p3}</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>{content.step5Title}</h3>
			<p>
				{content.step5p1pre} <span class="stat">{stats().pnpSeats2016}</span> {content.step5p1mid}
				<span class="stat">{stats().pnpSeats2020}</span> {content.step5p1mid2}
				<span class="stat">{stats().pnpSeats2016 - stats().pnpSeats2020}</span> {content.step5p1post}
				{stats().ppdSeats2016} {content.step5p1post2} {stats().ppdSeats2020}.
			</p>
			<p>
				{content.step5p2pre} <span class="highlight">{content.step5p2}</span>{content.step5p2b}
			</p>
			<p>{content.step5p3}</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>{content.step6Title}</h3>
			<p>
				{content.step6p1pre}<span class="stat">{stats().flippedCount}</span> {content.step6p1}
			</p>
			<p>{content.step6p2}</p>
			<p>
				{content.step6p3pre} <span class="highlight">{content.step6p3}</span>{content.step6p3b}
			</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>{content.step7Title}</h3>
			<p>
				{content.step7p1pre} <span class="stat">{formatPercent(stats().avgThirdParty, 1)}</span> {content.step7p1}
			</p>
			<p>{content.step7p2}</p>
			<p>{content.step7p3}</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>{content.step8Title}</h3>
			<p>{content.step8p1}</p>
			<p>
				{content.step8p2} <span class="highlight">{content.step8p2b}</span> {content.step8p2c}
			</p>
			<p>{content.step8p3}</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>{content.step9Title}</h3>
			<p>
				{content.step9p1pre} <span class="stat">21</span> {content.step9p1}
			</p>
			<p>{content.step9p2}</p>
			<p>{content.step9p3}</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>{content.conclusionTitle}</h2>
			<p>{content.conclusionP1}</p>
			<p>{content.conclusionP2}</p>

			<!-- Summary Stats Box -->
			{#if !loading && stats()}
				<div class="stats-summary">
					<h3>{content.statsTitle}</h3>
					<div class="stats-grid">
						<div class="stat-item">
							<span class="stat-value">{stats().totalTossups}</span>
							<span class="stat-label">{content.statTossupDistricts}</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{stats().flippedCount}</span>
							<span class="stat-label">{content.statDistrictsFlipped}</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{stats().pnpSeats2016 - stats().pnpSeats2020}</span>
							<span class="stat-label">{content.statPNPSeatsLost}</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{formatPercent(stats().closestMargin, 1)}</span>
							<span class="stat-label">{content.statClosestMargin}</span>
						</div>
					</div>
				</div>
			{/if}

			<!-- Party Legend -->
			<div class="party-legend">
				<div class="party-item">
					<span class="party-dot" style="background: {PARTY_COLORS.PNP}"></span>
					PNP: {stats().pnpSeats2020} {content.seats} (2020)
				</div>
				<div class="party-item">
					<span class="party-dot" style="background: {PARTY_COLORS.PPD}"></span>
					PPD: {stats().ppdSeats2020} {content.seats} (2020)
				</div>
			</div>

			<div class="sources">
				<h3>{content.sources}</h3>
				<ul>
					<li><a href="https://ww2.ceepur.org/Home/EventosElectorales" target="_blank" rel="noopener">Comision Estatal de Elecciones de Puerto Rico (CEE)</a> - {content.sourceCEE}</li>
					<li><a href="https://www.camaraderepresentantes.pr.gov/" target="_blank" rel="noopener">Camara de Representantes de Puerto Rico</a> - {content.sourceCamara}</li>
					<li>{content.sourceConstitution}</li>
					<li><a href="https://www.icpsr.umich.edu/" target="_blank" rel="noopener">Inter-University Consortium for Political and Social Research</a> - {content.sourceICPSR}</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/senate" class="nav-link prev">
					<span class="nav-direction">{content.previous}</span>
					<span class="nav-title">{content.prevTitle}</span>
				</a>
				<a href="{base}/chapters/future" class="nav-link next">
					<span class="nav-direction">{content.nextChapter}</span>
					<span class="nav-title">{content.nextTitle}</span>
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
