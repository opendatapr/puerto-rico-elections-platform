<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { LineChart, BarChart } from '$lib/components/charts';
	import { Legend } from '$lib/components/ui';
	import { PARTY_COLORS, CATEGORY_COLORS } from '$lib/utils/colors';
	import { formatNumber, formatPercent, formatCompact } from '$lib/utils/format';
	import { language } from '$lib/stores/language';

	const chapterNum = 7;
	const totalSteps = 10;

	// Bilingual content
	const t = {
		en: {
			chapterTitle: 'La Fortaleza',
			chapter: 'Chapter',
			subtitle: 'The Crumbling Duopoly',
			lead: "La Fortaleza--the 16th-century fortress that serves as the Governor's mansion--has witnessed a political earthquake. For fifty years, two parties took turns governing. Now governors win with barely a third of the vote. This is the story of how Puerto Rico's political establishment came undone.",
			loading: 'Loading data...',
			// Viz titles
			vizDuopolyDecline: "The Duopoly's Decline: Party Vote Share",
			vizGovernors: 'The Governors',
			vizShrinkingMandates: "Shrinking Mandates: Winner's Margin",
			vizCandidatesByYear: 'All Candidates by Year',
			vizThirdParty: '2020: The Third Party Breakthrough',
			// Viz labels
			marginNote: "Margin = Winner's % minus runner-up's %",
			xLabelElectionYear: 'Election Year',
			yLabelVoteShare: 'Vote Share %',
			thirdPartyTotal: 'Combined third party vote:',
			thirdParties: 'Third Parties',
			// Candidate cards
			resignedDisgrace: 'Resigned in disgrace',
			minorityMandate: 'Minority mandate',
			// Step titles
			step0Title: 'The Golden Age of Bipartisanship',
			step1Title: 'The 2016 Fracture Begins',
			step2Title: 'The Fall of Rossello',
			step3Title: 'Summer 2019: The Streets Rise',
			step4Title: 'The Shrinking Mandate',
			step5Title: 'The 2020 Four-Way Race',
			step6Title: 'The New Political Arithmetic',
			step7Title: 'The Third Party Surge',
			step8Title: 'Governing Without Majorities',
			step9Title: 'The Question Ahead',
			// Step 0 content
			step0p1: 'For half a century, Puerto Rico\'s politics operated like clockwork. The',
			step0p1party1: 'Partido Nuevo Progresista (PNP)',
			step0p1mid: ', advocating for U.S. statehood, and the',
			step0p1party2: 'Partido Popular Democratico (PPD)',
			step0p1end: ', defending the commonwealth status quo, traded control of La Fortaleza with metronomic regularity.',
			step0p2: 'Together, they commanded overwhelming majorities--routinely capturing',
			step0p2stat: '95% or more',
			step0p2end: 'of the vote. The independence movement was marginalized. Independents were novelties. The system seemed unshakeable.',
			step0p3: 'Governors won with clear mandates, often exceeding 48% in closely contested races. Electoral legitimacy was rarely questioned.',
			// Step 1 content
			step1p1: 'The cracks appeared suddenly. Puerto Rico was drowning in $72 billion of debt. PROMESA--the federal oversight board--had stripped the island of fiscal sovereignty. Austerity cuts slashed schools, hospitals, and pensions. The old parties offered no answers, only blame.',
			step1p2pre: 'Into this void stepped',
			step1p2name: 'Alexandra Lugaro',
			step1p2mid: ', an attorney and entrepreneur running as an independent. Young, charismatic, and unapologetically critical of both parties, she captured',
			step1p2stat: '11.1%',
			step1p2end: '--more than 175,000 votes. No independent had come close to such numbers in generations.',
			step1p3pre: '',
			step1p3name: 'Ricardo Rossello',
			step1p3mid: 'of the PNP won with just',
			step1p3stat: '41.8%',
			step1p3end: '--the lowest winning percentage in modern history. The duopoly still held, but its foundations had cracked.',
			// Step 2 content
			step2p1: 'Governor Ricardo Rossello promised a "new generation" of leadership. What Puerto Rico got was scandal. In July 2019, nearly 900 pages of private chat messages leaked to the public. The "Telegramgate" revelations were devastating.',
			step2p2: 'In the chats, Rossello and his inner circle mocked Hurricane Maria victims, made homophobic jokes about singer Ricky Martin, and called a former New York City councilwoman a "whore." The messages revealed casual corruption and breathtaking contempt for the people they governed.',
			step2p3pre: 'What followed was unprecedented:',
			step2p3highlight: 'twelve consecutive days of massive street protests',
			step2p3mid: '. Hundreds of thousands marched through Old San Juan. Ricky Martin led crowds chanting "Ricky Renuncia!" On August 2, 2019, Rossello resigned--the first governor in Puerto Rico history forced out by popular uprising.',
			// Step 3 content
			step3p1: 'The protests that toppled Rossello weren\'t just about a governor. They were about decades of accumulated grievances: the debt crisis, Hurricane Maria\'s botched response, corruption at every level, and a political class that seemed indifferent to suffering.',
			step3p2: 'Artists, students, labor unions, and ordinary citizens found common cause. Bad Bunny, Residente, and iLe released "Afilando Los Cuchillos" as an anthem of resistance. The protests crossed generational and ideological lines.',
			step3p3pre: 'From this uprising emerged',
			step3p3party: 'Movimiento Victoria Ciudadana (MVC)',
			step3p3end: '--a new progressive party built on the energy of the streets. The two-party system would never be the same.',
			// Step 4 content
			step4p1pre: 'Compare the margins. In 2016, Rossello beat his PPD rival by',
			step4p1stat: '2.9 percentage points',
			step4p1mid: '--a narrow but workable margin. In 2020, Pedro Pierluisi\'s margin over Charlie Delgado collapsed to just',
			step4p1stat2: '1.5 points',
			step4p1end: '.',
			step4p2: 'But the real story isn\'t the head-to-head margin--it\'s the overall fragmentation. When a governor wins with 33% of the vote, two-thirds of the electorate voted against them. What does democratic legitimacy mean in such conditions?',
			step4p3: 'The implications ripple through governance: weakened mandates, fragile coalitions, and a permanent legitimacy deficit that shadows every major decision.',
			// Step 5 content
			step5p1pre: 'The 2020 election shattered all precedents.',
			step5p1name: 'Pedro Pierluisi',
			step5p1mid: ', a PNP stalwart who briefly served as governor after Rossello\'s resignation, claimed victory with just',
			step5p1end: '--the lowest winning share in Puerto Rico\'s electoral history.',
			step5p2pre: '',
			step5p2name1: 'Charlie Delgado',
			step5p2mid1: 'of the PPD came agonizingly close at',
			step5p2stat1: '31.8%',
			step5p2mid2: '. But the story was the insurgents: Alexandra Lugaro, now running under the MVC banner, took',
			step5p2stat2: '14.0%',
			step5p2mid3: '. Juan Dalmau of the PIP captured',
			step5p2stat3: '13.6%',
			step5p2end: '--the independence party\'s best showing in decades.',
			step5p3pre: 'Even more striking:',
			step5p3name: 'Proyecto Dignidad',
			step5p3mid: ', a socially conservative evangelical party that didn\'t exist until 2019, debuted at',
			step5p3stat: '6.8%',
			step5p3end: '.',
			// Step 6 content
			step6p1pre: 'Look at these numbers and understand: the old rules no longer apply. In 2016, PNP and PPD together claimed',
			step6p1stat1: '80.7%',
			step6p1mid: '. By 2020, that combined share had fallen to',
			step6p1stat2: '65.0%',
			step6p1end: '--a collapse of nearly 16 percentage points in a single cycle.',
			step6p2: 'The erosion isn\'t limited to governor\'s races. Legislative elections show similar fragmentation. The two-party system that seemed eternal in 2012 now looks like a historical artifact.',
			step6p3: 'Puerto Rico has become, almost overnight, a genuinely competitive multi-party democracy--with all the opportunities and chaos that entails.',
			// Step 7 content
			step7p1pre: 'The 2020 third-party vote tells a story of ideological diversity.',
			step7p1party1: 'MVC',
			step7p1mid1: 'represents the progressive wing--young, urban, focused on corruption and social justice.',
			step7p1party2: 'PIP',
			step7p1end1: 'carries the independence torch, finding new relevance as status debates intensify.',
			step7p2pre: '',
			step7p2party: 'Proyecto Dignidad',
			step7p2mid: 'emerged from evangelical churches, mobilizing socially conservative voters who felt abandoned by both traditional parties. Together, these movements captured over',
			step7p2stat: 'one-third',
			step7p2end: 'of the 2020 gubernatorial vote.',
			step7p3: 'This isn\'t protest voting. These are durable political movements with distinct constituencies, clear ideologies, and growing organizational capacity.',
			// Step 8 content
			step8p1: 'What happens when governors rule with minority mandates? The calculus of governance transforms entirely. Traditional party discipline erodes. Coalition building becomes essential--and coalitions in a four-party system are fragile.',
			step8p2: 'Legislative gridlock increases. Major reforms require cross-party deals that satisfy conflicting ideologies. The old pattern of single-party dominance--where one side controlled La Fortaleza and the Legislature for four years--may be gone forever.',
			step8p3: 'Some see opportunity: multi-party systems can force compromise and represent diverse views. Others see paralysis: how do you govern an island in crisis when no one has a mandate?',
			// Step 9 content
			step9p1: 'Puerto Rico\'s political earthquake raises profound questions. Is the two-party system\'s collapse a one-time reaction to crisis, or a permanent realignment? Will MVC and PIP consolidate, or will their voters return to major parties? Can Proyecto Dignidad maintain momentum without the novelty factor?',
			step9p2: 'Most critically: can Puerto Rico\'s institutions adapt to multi-party governance? The island\'s winner-take-all electoral system was designed for two parties. It may need fundamental reform to accommodate its new political reality.',
			step9p3: 'La Fortaleza has stood for 500 years. The political system that governed from within it may not survive another decade.',
			// Conclusion section
			numbersTitle: 'The Numbers Tell the Story',
			statLowestEver: '2020 winning percentage--lowest ever',
			statDuopolyDecline: 'PNP+PPD share decline (2016-2020)',
			statThirdParty: 'Third party vote in 2020',
			statProtests: 'Of protests that ousted Rossello',
			// Party legend
			newLandscape: 'The New Political Landscape',
			partyPNP: 'PNP',
			partyPNPDesc: 'Pro-statehood, center-right',
			partyPPD: 'PPD',
			partyPPDDesc: 'Commonwealth status quo, center',
			partyMVC: 'MVC',
			partyMVCDesc: 'Progressive, anti-corruption',
			partyPIP: 'PIP',
			partyPIPDesc: 'Independence, democratic socialist',
			partyPD: 'PD',
			partyPDDesc: 'Socially conservative, evangelical',
			// Sources
			sources: 'Sources',
			sourceCEE: 'Official gubernatorial election results 1948-2024',
			sourceElNuevoDia: 'Archives - Historical election coverage and analysis',
			sourceUPR: 'University of Puerto Rico - Electoral Studies Program historical data',
			sourceCentro: 'Political party evolution in Puerto Rico',
			// Navigation
			previous: 'Previous',
			nextChapter: 'Next Chapter',
			prevTitle: 'Divided by Design',
			nextTitle: '78 Battlegrounds',
			// Legend items
			legendPNP: 'PNP (Statehood)',
			legendPPD: 'PPD (Commonwealth)',
			legendMVC: 'MVC (Progressive)',
			legendPIP: 'PIP (Independence)',
			legendPD: 'PD (Conservative)',
			// Stats
			days: 'days'
		},
		es: {
			chapterTitle: 'La Fortaleza',
			chapter: 'Capitulo',
			subtitle: 'El Duopolio Desmoronandose',
			lead: 'La Fortaleza--la fortaleza del siglo XVI que sirve como mansion del Gobernador--ha presenciado un terremoto politico. Durante cincuenta anos, dos partidos se turnaron para gobernar. Ahora los gobernadores ganan con apenas un tercio de los votos. Esta es la historia de como el establishment politico de Puerto Rico se deshizo.',
			loading: 'Cargando datos...',
			// Viz titles
			vizDuopolyDecline: 'El Declive del Duopolio: Porcentaje de Votos por Partido',
			vizGovernors: 'Los Gobernadores',
			vizShrinkingMandates: 'Mandatos Menguantes: Margen del Ganador',
			vizCandidatesByYear: 'Todos los Candidatos por Ano',
			vizThirdParty: '2020: El Avance de los Terceros Partidos',
			// Viz labels
			marginNote: 'Margen = % del ganador menos % del segundo lugar',
			xLabelElectionYear: 'Ano Electoral',
			yLabelVoteShare: 'Porcentaje de Votos',
			thirdPartyTotal: 'Voto combinado de terceros partidos:',
			thirdParties: 'Terceros Partidos',
			// Candidate cards
			resignedDisgrace: 'Renuncio en desgracia',
			minorityMandate: 'Mandato minoritario',
			// Step titles
			step0Title: 'La Era Dorada del Bipartidismo',
			step1Title: 'La Fractura de 2016 Comienza',
			step2Title: 'La Caida de Rossello',
			step3Title: 'Verano 2019: Las Calles se Levantan',
			step4Title: 'El Mandato Menguante',
			step5Title: 'La Carrera a Cuatro Bandas de 2020',
			step6Title: 'La Nueva Aritmetica Politica',
			step7Title: 'El Auge de los Terceros Partidos',
			step8Title: 'Gobernar Sin Mayorias',
			step9Title: 'La Pregunta por Delante',
			// Step 0 content
			step0p1: 'Durante medio siglo, la politica de Puerto Rico funciono como un reloj. El',
			step0p1party1: 'Partido Nuevo Progresista (PNP)',
			step0p1mid: ', que aboga por la estadidad estadounidense, y el',
			step0p1party2: 'Partido Popular Democratico (PPD)',
			step0p1end: ', que defiende el status quo del estado libre asociado, intercambiaron el control de La Fortaleza con regularidad metronomica.',
			step0p2: 'Juntos, comandaban mayorias abrumadoras--capturando rutinariamente',
			step0p2stat: '95% o mas',
			step0p2end: 'de los votos. El movimiento independentista estaba marginado. Los independientes eran novedades. El sistema parecia inquebrantable.',
			step0p3: 'Los gobernadores ganaban con mandatos claros, frecuentemente superando el 48% en carreras renidas. La legitimidad electoral raramente se cuestionaba.',
			// Step 1 content
			step1p1: 'Las grietas aparecieron subitamente. Puerto Rico se ahogaba en $72 mil millones de deuda. PROMESA--la junta de control fiscal federal--habia despojado a la isla de su soberania fiscal. Los recortes de austeridad devastaron escuelas, hospitales y pensiones. Los viejos partidos no ofrecian respuestas, solo culpas.',
			step1p2pre: 'En este vacio entro',
			step1p2name: 'Alexandra Lugaro',
			step1p2mid: ', una abogada y empresaria que se postulaba como independiente. Joven, carismatica y sin disculpas critica de ambos partidos, capturo',
			step1p2stat: '11.1%',
			step1p2end: '--mas de 175,000 votos. Ningun independiente se habia acercado a tales numeros en generaciones.',
			step1p3pre: '',
			step1p3name: 'Ricardo Rossello',
			step1p3mid: 'del PNP gano con solo',
			step1p3stat: '41.8%',
			step1p3end: '--el porcentaje ganador mas bajo en la historia moderna. El duopolio todavia se mantenia, pero sus cimientos se habian agrietado.',
			// Step 2 content
			step2p1: 'El Gobernador Ricardo Rossello prometio una "nueva generacion" de liderazgo. Lo que Puerto Rico recibio fue escandalo. En julio de 2019, casi 900 paginas de mensajes de chat privados se filtraron al publico. Las revelaciones del "Telegramgate" fueron devastadoras.',
			step2p2: 'En los chats, Rossello y su circulo intimo se burlaron de las victimas del Huracan Maria, hicieron chistes homofobicos sobre el cantante Ricky Martin, y llamaron "puta" a una ex concejala de la ciudad de Nueva York. Los mensajes revelaron corrupcion casual y un desprecio asombroso hacia el pueblo que gobernaban.',
			step2p3pre: 'Lo que siguio fue sin precedentes:',
			step2p3highlight: 'doce dias consecutivos de protestas masivas en las calles',
			step2p3mid: '. Cientos de miles marcharon por el Viejo San Juan. Ricky Martin lideraba multitudes que coreaban "Ricky Renuncia!" El 2 de agosto de 2019, Rossello renuncio--el primer gobernador en la historia de Puerto Rico forzado a salir por un levantamiento popular.',
			// Step 3 content
			step3p1: 'Las protestas que derrocaron a Rossello no eran solo sobre un gobernador. Eran sobre decadas de agravios acumulados: la crisis de deuda, la respuesta fallida al Huracan Maria, la corrupcion en todos los niveles, y una clase politica que parecia indiferente al sufrimiento.',
			step3p2: 'Artistas, estudiantes, sindicatos y ciudadanos comunes encontraron causa comun. Bad Bunny, Residente e iLe lanzaron "Afilando Los Cuchillos" como un himno de resistencia. Las protestas cruzaron lineas generacionales e ideologicas.',
			step3p3pre: 'De este levantamiento emergio el',
			step3p3party: 'Movimiento Victoria Ciudadana (MVC)',
			step3p3end: '--un nuevo partido progresista construido sobre la energia de las calles. El sistema bipartidista nunca seria el mismo.',
			// Step 4 content
			step4p1pre: 'Compara los margenes. En 2016, Rossello vencio a su rival del PPD por',
			step4p1stat: '2.9 puntos porcentuales',
			step4p1mid: '--un margen estrecho pero manejable. En 2020, el margen de Pedro Pierluisi sobre Charlie Delgado se desplomo a solo',
			step4p1stat2: '1.5 puntos',
			step4p1end: '.',
			step4p2: 'Pero la verdadera historia no es el margen cabeza a cabeza--es la fragmentacion general. Cuando un gobernador gana con el 33% de los votos, dos tercios del electorado votaron en su contra. Que significa la legitimidad democratica en tales condiciones?',
			step4p3: 'Las implicaciones se propagan a traves de la gobernanza: mandatos debilitados, coaliciones fragiles, y un deficit de legitimidad permanente que ensombrece cada decision importante.',
			// Step 5 content
			step5p1pre: 'La eleccion de 2020 rompio todos los precedentes.',
			step5p1name: 'Pedro Pierluisi',
			step5p1mid: ', un baluarte del PNP que sirvio brevemente como gobernador tras la renuncia de Rossello, reclamo la victoria con solo',
			step5p1end: '--la menor porcion ganadora en la historia electoral de Puerto Rico.',
			step5p2pre: '',
			step5p2name1: 'Charlie Delgado',
			step5p2mid1: 'del PPD estuvo agonizantemente cerca con',
			step5p2stat1: '31.8%',
			step5p2mid2: '. Pero la historia fueron los insurgentes: Alexandra Lugaro, ahora bajo la bandera del MVC, obtuvo',
			step5p2stat2: '14.0%',
			step5p2mid3: '. Juan Dalmau del PIP capturo',
			step5p2stat3: '13.6%',
			step5p2end: '--el mejor resultado del partido independentista en decadas.',
			step5p3pre: 'Aun mas sorprendente:',
			step5p3name: 'Proyecto Dignidad',
			step5p3mid: ', un partido evangelico socialmente conservador que no existia hasta 2019, debuto con',
			step5p3stat: '6.8%',
			step5p3end: '.',
			// Step 6 content
			step6p1pre: 'Mira estos numeros y entiende: las viejas reglas ya no aplican. En 2016, PNP y PPD juntos reclamaron',
			step6p1stat1: '80.7%',
			step6p1mid: '. Para 2020, esa porcion combinada habia caido a',
			step6p1stat2: '65.0%',
			step6p1end: '--un colapso de casi 16 puntos porcentuales en un solo ciclo.',
			step6p2: 'La erosion no se limita a las carreras de gobernador. Las elecciones legislativas muestran una fragmentacion similar. El sistema bipartidista que parecia eterno en 2012 ahora luce como un artefacto historico.',
			step6p3: 'Puerto Rico se ha convertido, casi de la noche a la manana, en una democracia multipartidista genuinamente competitiva--con todas las oportunidades y el caos que eso conlleva.',
			// Step 7 content
			step7p1pre: 'El voto de terceros partidos en 2020 cuenta una historia de diversidad ideologica.',
			step7p1party1: 'MVC',
			step7p1mid1: 'representa el ala progresista--joven, urbano, enfocado en la corrupcion y la justicia social.',
			step7p1party2: 'PIP',
			step7p1end1: 'porta la antorcha de la independencia, encontrando nueva relevancia a medida que los debates de estatus se intensifican.',
			step7p2pre: '',
			step7p2party: 'Proyecto Dignidad',
			step7p2mid: 'emergio de las iglesias evangelicas, movilizando votantes socialmente conservadores que se sentian abandonados por ambos partidos tradicionales. Juntos, estos movimientos capturaron mas de',
			step7p2stat: 'un tercio',
			step7p2end: 'del voto gubernatorial de 2020.',
			step7p3: 'Esto no es voto de protesta. Estos son movimientos politicos duraderos con bases distintas, ideologias claras y capacidad organizativa creciente.',
			// Step 8 content
			step8p1: 'Que pasa cuando los gobernadores gobiernan con mandatos minoritarios? El calculo de la gobernanza se transforma completamente. La disciplina partidista tradicional se erosiona. La construccion de coaliciones se vuelve esencial--y las coaliciones en un sistema de cuatro partidos son fragiles.',
			step8p2: 'El estancamiento legislativo aumenta. Las reformas importantes requieren acuerdos entre partidos que satisfagan ideologias conflictivas. El viejo patron de dominio de un solo partido--donde un lado controlaba La Fortaleza y la Legislatura por cuatro anos--puede haber desaparecido para siempre.',
			step8p3: 'Algunos ven oportunidad: los sistemas multipartidistas pueden forzar el compromiso y representar visiones diversas. Otros ven paralisis: como gobiernas una isla en crisis cuando nadie tiene mandato?',
			// Step 9 content
			step9p1: 'El terremoto politico de Puerto Rico plantea preguntas profundas. Es el colapso del sistema bipartidista una reaccion unica a la crisis, o un realineamiento permanente? Se consolidaran MVC y PIP, o sus votantes regresaran a los partidos principales? Puede Proyecto Dignidad mantener impulso sin el factor de novedad?',
			step9p2: 'Lo mas critico: pueden las instituciones de Puerto Rico adaptarse a la gobernanza multipartidista? El sistema electoral de ganador se lleva todo de la isla fue disenado para dos partidos. Puede necesitar una reforma fundamental para acomodar su nueva realidad politica.',
			step9p3: 'La Fortaleza ha permanecido por 500 anos. El sistema politico que goberno desde su interior puede no sobrevivir otra decada.',
			// Conclusion section
			numbersTitle: 'Los Numeros Cuentan la Historia',
			statLowestEver: 'Porcentaje ganador de 2020--el mas bajo',
			statDuopolyDecline: 'Declive de porcentaje PNP+PPD (2016-2020)',
			statThirdParty: 'Voto de terceros partidos en 2020',
			statProtests: 'De protestas que derrocaron a Rossello',
			// Party legend
			newLandscape: 'El Nuevo Paisaje Politico',
			partyPNP: 'PNP',
			partyPNPDesc: 'Pro-estadidad, centro-derecha',
			partyPPD: 'PPD',
			partyPPDDesc: 'Status quo del estado libre asociado, centro',
			partyMVC: 'MVC',
			partyMVCDesc: 'Progresista, anti-corrupcion',
			partyPIP: 'PIP',
			partyPIPDesc: 'Independencia, socialista democratico',
			partyPD: 'PD',
			partyPDDesc: 'Socialmente conservador, evangelico',
			// Sources
			sources: 'Fuentes',
			sourceCEE: 'Resultados oficiales de elecciones gubernamentales 1948-2024',
			sourceElNuevoDia: 'Archivos - Cobertura historica y analisis electoral',
			sourceUPR: 'Universidad de Puerto Rico - Datos historicos del Programa de Estudios Electorales',
			sourceCentro: 'Evolucion de los partidos politicos en Puerto Rico',
			// Navigation
			previous: 'Anterior',
			nextChapter: 'Proximo Capitulo',
			prevTitle: 'Divididos por Diseno',
			nextTitle: '78 Campos de Batalla',
			// Legend items
			legendPNP: 'PNP (Estadidad)',
			legendPPD: 'PPD (ELA)',
			legendMVC: 'MVC (Progresista)',
			legendPIP: 'PIP (Independencia)',
			legendPD: 'PD (Conservador)',
			// Stats
			days: 'dias'
		}
	};

	// Reactive content based on language
	let content = $derived(t[$language]);
	let chapterTitle = $derived(content.chapterTitle);

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
			{ id: 'other', label: content.thirdParties, color: PARTY_COLORS.MVC, data: otherData },
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
	let partyLegendItems = $derived([
		{ label: content.legendPNP, color: PARTY_COLORS.PNP },
		{ label: content.legendPPD, color: PARTY_COLORS.PPD },
		{ label: content.legendMVC, color: PARTY_COLORS.MVC },
		{ label: content.legendPIP, color: PARTY_COLORS.PIP },
		{ label: content.legendPD, color: PARTY_COLORS.PD },
	]);
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
			<p class="subtitle">{content.subtitle}</p>
			<p class="lead">{content.lead}</p>
		</div>
	</header>

	<ScrollySection offset={0.6} onStepEnter={handleStepEnter}>
		{#snippet graphic()}
			<div class="viz-container">
				{#if loading}
					<p class="loading">{content.loading}</p>
				{:else if activeViz === 'line'}
					<h3 class="viz-title">{content.vizDuopolyDecline}</h3>
					<LineChart
						series={partyTrends()}
						width={500}
						height={340}
						xLabel={content.xLabelElectionYear}
						yLabel={content.yLabelVoteShare}
						xFormat={(v) => String(v)}
						yFormat={(v) => `${v.toFixed(0)}%`}
						showArea={true}
					/>
					<div class="viz-legend">
						<Legend items={partyLegendItems.slice(0, 3)} orientation="horizontal" />
					</div>
				{:else if activeViz === 'candidates'}
					<h3 class="viz-title">{content.vizGovernors}</h3>
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
								<div class="candidate-fate">{content.resignedDisgrace}</div>
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
								<div class="candidate-fate">{content.minorityMandate}</div>
							</div>
						{/if}
					</div>
				{:else if activeViz === 'margin'}
					<h3 class="viz-title">{content.vizShrinkingMandates}</h3>
					<BarChart
						data={marginData()}
						width={420}
						height={280}
						horizontal={false}
						valueFormat={(v) => `+${v.toFixed(1)}pp`}
					/>
					<p class="viz-note">{content.marginNote}</p>
				{:else if activeViz === 'stacked'}
					<h3 class="viz-title">{content.vizCandidatesByYear}</h3>
					<BarChart
						data={stackedBarData()}
						width={480}
						height={420}
						horizontal={true}
						valueFormat={(v) => `${v.toFixed(1)}%`}
					/>
				{:else if activeViz === 'third-party'}
					<h3 class="viz-title">{content.vizThirdParty}</h3>
					<BarChart
						data={thirdPartyData()}
						width={420}
						height={280}
						horizontal={true}
						valueFormat={(v) => `${v.toFixed(1)}%`}
					/>
					<div class="third-party-total">
						<span class="stat-label">{content.thirdPartyTotal}</span>
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
			<h3>{content.step0Title}</h3>
			<p>
				{content.step0p1}
				<span class="party-name pnp">{content.step0p1party1}</span>{content.step0p1mid}
				<span class="party-name ppd">{content.step0p1party2}</span>{content.step0p1end}
			</p>
			<p>
				{content.step0p2}
				<span class="stat">{content.step0p2stat}</span> {content.step0p2end}
			</p>
			<p>{content.step0p3}</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>{content.step1Title}</h3>
			<p>{content.step1p1}</p>
			<p>
				{content.step1p2pre} <strong>{content.step1p2name}</strong>{content.step1p2mid}
				<span class="stat">{content.step1p2stat}</span>{content.step1p2end}
			</p>
			<p>
				{content.step1p3pre}<strong>{content.step1p3name}</strong> {content.step1p3mid}
				<span class="stat">{content.step1p3stat}</span>{content.step1p3end}
			</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>{content.step2Title}</h3>
			<p>{content.step2p1}</p>
			<p>{content.step2p2}</p>
			<p>
				{content.step2p3pre} <span class="highlight">{content.step2p3highlight}</span>{content.step2p3mid}
			</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>{content.step3Title}</h3>
			<p>{content.step3p1}</p>
			<p>{content.step3p2}</p>
			<p>
				{content.step3p3pre} <span class="party-name mvc">{content.step3p3party}</span>{content.step3p3end}
			</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>{content.step4Title}</h3>
			<p>
				{content.step4p1pre}
				<span class="stat">{content.step4p1stat}</span>{content.step4p1mid}
				<span class="stat">{content.step4p1stat2}</span>{content.step4p1end}
			</p>
			<p>{content.step4p2}</p>
			<p>{content.step4p3}</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>{content.step5Title}</h3>
			<p>
				{content.step5p1pre} <strong>{content.step5p1name}</strong>{content.step5p1mid}
				<span class="stat">{winner2020() ? formatPercent(winner2020().percentage) : '33.2%'}</span>{content.step5p1end}
			</p>
			<p>
				{content.step5p2pre}<strong>{content.step5p2name1}</strong> {content.step5p2mid1}
				<span class="stat">{content.step5p2stat1}</span>{content.step5p2mid2}
				<span class="stat">{content.step5p2stat2}</span>{content.step5p2mid3}
				<span class="stat">{content.step5p2stat3}</span>{content.step5p2end}
			</p>
			<p>
				{content.step5p3pre} <strong>{content.step5p3name}</strong>{content.step5p3mid}
				<span class="stat">{content.step5p3stat}</span>{content.step5p3end}
			</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>{content.step6Title}</h3>
			<p>
				{content.step6p1pre}
				<span class="stat">{content.step6p1stat1}</span>{content.step6p1mid}
				<span class="stat">{content.step6p1stat2}</span>{content.step6p1end}
			</p>
			<p>{content.step6p2}</p>
			<p>{content.step6p3}</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>{content.step7Title}</h3>
			<p>
				{content.step7p1pre}
				<span class="party-name mvc">{content.step7p1party1}</span> {content.step7p1mid1}
				<span class="party-name pip">{content.step7p1party2}</span> {content.step7p1end1}
			</p>
			<p>
				{content.step7p2pre}<span class="party-name pd">{content.step7p2party}</span> {content.step7p2mid}
				<span class="stat">{content.step7p2stat}</span> {content.step7p2end}
			</p>
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
			<h2>{content.numbersTitle}</h2>

			<div class="stat-grid">
				<div class="stat-card highlight-card">
					<span class="stat-value" style="color: {PARTY_COLORS.PNP}">
						{winner2020() ? formatPercent(winner2020().percentage) : '33.2%'}
					</span>
					<span class="stat-label">{content.statLowestEver}</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">-15.7pp</span>
					<span class="stat-label">{content.statDuopolyDecline}</span>
				</div>
				<div class="stat-card">
					<span class="stat-value" style="color: {PARTY_COLORS.MVC}">35.0%</span>
					<span class="stat-label">{content.statThirdParty}</span>
				</div>
				<div class="stat-card">
					<span class="stat-value">12 {content.days}</span>
					<span class="stat-label">{content.statProtests}</span>
				</div>
			</div>

			<div class="party-legend-section">
				<h3>{content.newLandscape}</h3>
				<div class="party-grid">
					<div class="party-item">
						<span class="party-dot" style="background: {PARTY_COLORS.PNP}"></span>
						<div class="party-info">
							<strong>{content.partyPNP}</strong>
							<span>{content.partyPNPDesc}</span>
						</div>
					</div>
					<div class="party-item">
						<span class="party-dot" style="background: {PARTY_COLORS.PPD}"></span>
						<div class="party-info">
							<strong>{content.partyPPD}</strong>
							<span>{content.partyPPDDesc}</span>
						</div>
					</div>
					<div class="party-item">
						<span class="party-dot" style="background: {PARTY_COLORS.MVC}"></span>
						<div class="party-info">
							<strong>{content.partyMVC}</strong>
							<span>{content.partyMVCDesc}</span>
						</div>
					</div>
					<div class="party-item">
						<span class="party-dot" style="background: {PARTY_COLORS.PIP}"></span>
						<div class="party-info">
							<strong>{content.partyPIP}</strong>
							<span>{content.partyPIPDesc}</span>
						</div>
					</div>
					<div class="party-item">
						<span class="party-dot" style="background: {PARTY_COLORS.PD}"></span>
						<div class="party-info">
							<strong>{content.partyPD}</strong>
							<span>{content.partyPDDesc}</span>
						</div>
					</div>
				</div>
			</div>

			<div class="sources">
				<h3>{content.sources}</h3>
				<ul>
					<li><a href="https://ww2.ceepur.org/Home/EventosElectorales" target="_blank" rel="noopener">Comision Estatal de Elecciones de Puerto Rico (CEE)</a> - {content.sourceCEE}</li>
					<li><a href="https://www.elnuevodia.com/" target="_blank" rel="noopener">El Nuevo Dia</a> {content.sourceElNuevoDia}</li>
					<li>{content.sourceUPR}</li>
					<li><a href="https://centropr.hunter.cuny.edu/" target="_blank" rel="noopener">Centro de Estudios Puertorriquenos</a> - {content.sourceCentro}</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/geography" class="nav-link prev">
					<span class="nav-direction">{content.previous}</span>
					<span class="nav-title">{content.prevTitle}</span>
				</a>
				<a href="{base}/chapters/battlegrounds" class="nav-link next">
					<span class="nav-direction">{content.nextChapter}</span>
					<span class="nav-title">{content.nextTitle}</span>
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
		border-top: 4px solid var(--party-color, var(--color-accent));
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
		color: var(--color-accent);
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

	/* Sources */
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

	/* Mobile adjustments */
	@media (max-width: 640px) {
		.chapter-header {
			min-height: 50vh;
			padding: var(--space-xl) 0;
		}

		.subtitle {
			font-size: var(--text-base);
		}

		.viz-container {
			padding: var(--space-sm);
		}

		.viz-title {
			font-size: var(--text-base);
			margin-bottom: var(--space-sm);
		}

		/* Candidate cards - stack on mobile */
		.candidate-cards {
			flex-direction: column;
			gap: var(--space-md);
			align-items: stretch;
		}

		.candidate-card {
			width: 100%;
			max-width: 280px;
			margin: 0 auto;
			padding: var(--space-lg);
		}

		.candidate-year {
			font-size: var(--text-2xl);
		}

		.candidate-name {
			font-size: var(--text-sm);
		}

		.candidate-result .percentage {
			font-size: var(--text-xl);
		}

		/* Third party total */
		.third-party-total {
			flex-direction: column;
			text-align: center;
			gap: var(--space-sm);
		}

		/* Stats grid */
		.stat-grid {
			grid-template-columns: repeat(2, 1fr);
			gap: var(--space-md);
		}

		.stat-card {
			padding: var(--space-md);
		}

		.stat-card .stat-value {
			font-size: var(--text-xl);
		}

		.stat-card .stat-label {
			font-size: var(--text-xs);
		}

		/* Party grid */
		.party-grid {
			grid-template-columns: 1fr;
		}

		/* Navigation */
		.chapter-nav {
			flex-direction: column;
			gap: var(--space-md);
		}

		.nav-link {
			text-align: center;
		}

		.nav-link.next {
			text-align: center;
		}

		.nav-title {
			font-size: var(--text-base);
		}
	}
</style>
