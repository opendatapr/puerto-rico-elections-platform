<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { BarChart, LineChart } from '$lib/components/charts';
	import { PARTY_COLORS, CATEGORY_COLORS } from '$lib/utils/colors';
	import { formatPercent, formatNumber, formatPercentChange } from '$lib/utils/format';
	import { language } from '$lib/stores/language';

	const chapterNum = 10;
	const totalSteps = 10;

	// Bilingual content
	const t = {
		en: {
			chapterTitle: 'The At-Large Experiment',
			chapter: 'Chapter',
			lead: "Puerto Rico's Senate operates under a unique system: all 11 at-large senators are elected island-wide, making it one of the few legislatures where every voter votes for every seat. This design produces distinctive dynamics around representation, minority protections, and the rise of third parties.",
			loading: 'Loading data...',
			seats: 'Seats',
			// Viz titles
			senateComposition: 'Senate Composition',
			topVoteGetters: 'Top 11 At-Large Vote-Getters',
			partyVoteShare: 'Party Vote Share: At-Large Senate',
			compositionOverTime: 'Senate Composition Over Time',
			twoPartyVsThird: 'Two-Party vs Third-Party Seats',
			// Viz notes
			voteNote: 'Vote totals in thousands',
			thirdPartyNote: 'The rise of MVC, PIP, and independents since 2016',
			// Chart labels
			electionYear: 'Election Year',
			seatsWon: 'Seats Won',
			totalSeats: 'Total Seats',
			twoPartyLabel: 'PNP + PPD',
			thirdPartyLabel: 'Third Parties + Ind',
			// Step titles
			step0Title: 'A Unique Electoral Experiment',
			step1Title: 'How At-Large Voting Works',
			step2Title: 'The Top Vote-Getters',
			step3Title: 'Party Vote Share',
			step4Title: 'A Generation of Change',
			step5Title: 'The 2016 Supermajority',
			step6Title: 'The 2020 Fragmentation',
			step7Title: 'Third-Party Breakthrough',
			step8Title: 'The Minority Protection Clause',
			step9Title: 'The New Senate Politics',
			// Step content
			step0p1: "Puerto Rico's 27-member Senate is divided into two components: 16 district senators (two from each of 8 senatorial districts) and",
			step0p1b: '11 at-large senators',
			step0p1c: 'elected island-wide. This at-large system is virtually unique in American politics.',
			step0p2: 'The at-large design was intentional: framers wanted senators who would represent all of Puerto Rico, not just their district. In theory, this creates legislators with broader perspectives and reduces parochialism. In practice, it rewards name recognition, tests party loyalty, and makes vote accumulation an art form.',
			step0p3: 'The 2020 Senate shows the system in action:',
			step0p3b: '6 parties',
			step0p3c: 'won representation, the most fragmented Senate in Puerto Rican history.',
			step1p1: 'Each voter casts',
			step1p1b: 'up to 11 votes',
			step1p1c: 'for at-large senator, one for each seat. You can vote for candidates from different parties, split your ticket, or vote a straight party line. The 11 candidates with the most votes win.',
			step1p2: "This creates unique incentives. Unlike single-member districts where one candidate wins, at-large races reward broad appeal. A candidate who is everyone's second choice might accumulate more votes than someone who is polarizing. Personal popularity matters enormously.",
			step1p3: 'The result: at-large senate races often produce',
			step1p3b: 'surprising individual winners',
			step1p3c: 'who outperform their party. Independent candidates like Dr. Jose Vargas Vidot have won seats by building personal coalitions that transcend party lines.',
			step2p1: 'In 2020, the top vote-getter was',
			step2p1b: 'Maria de Lourdes Santiago',
			step2p1c: '(PIP) with nearly',
			step2p1d: 'votes, outpacing candidates from both major parties. Her success shows how the at-large system can elevate candidates with strong personal brands.',
			step2p2a: 'The bar chart shows the top 11 elected senators by total votes. Notice the color diversity: candidates from',
			step2p2b: 'Proyecto Dignidad',
			step2p2c: ', and independents all made the cut alongside traditional major-party candidates.',
			step2p3a: 'The gap between 11th and 12th place was only',
			step2p3b: 'votes, showing how competitive these races are. A few thousand votes in either direction would have changed the Senate\'s composition.',
			step3p1a: 'Looking at aggregate party vote share tells a different story than individual candidate success. In 2020,',
			step3p1b: 'still led with about 33% of at-large senate votes, followed closely by',
			step3p1c: 'at 31%.',
			step3p2a: 'But the real story is fragmentation. Third parties combined captured over',
			step3p2b: '35%',
			step3p2c: 'of the vote.',
			step3p2d: 'surged to 11%,',
			step3p2e: 'won 11%, and',
			step3p2f: 'emerged with 7%.',
			step3p3: "This fragmentation doesn't translate directly to seats because of winner-take-all dynamics. But the at-large system is more proportional than district elections, allowing smaller parties to win representation they might not get in single-member districts.",
			step4p1: 'The line chart tracks Senate composition across five election cycles. The pattern is dramatic: from near-total',
			step4p1b: 'dominance in 2008 (22 seats) to a fragmented chamber in 2020 where no party controls a majority.',
			step4p2a: 'The 2016 election was the peak of PNP power: they won',
			step4p2b: '21 of 27',
			step4p2c: 'seats, enough to override any veto. But by 2020, that supermajority collapsed to just 9 seats.',
			step4p2d: 'recovered somewhat, but the real winners were the emerging parties.',
			step4p3a: '2024 saw',
			step4p3b: 'take the lead with 13 seats, while',
			step4p3c: 'and',
			step4p3d: "maintained their foothold. The two-party system hasn't returned, and may never fully recover.",
			step5p1: 'The 2016 hemicycle shows PNP at the height of its power. With 21 seats, they held a',
			step5p1b: 'constitutional supermajority',
			step5p1c: ', able to override gubernatorial vetoes and control every committee.',
			step5p2: "This dominance came during the PROMESA fiscal crisis. Voters, exhausted by PPD's handling of the debt crisis, swung decisively toward PNP. The opposition was reduced to just 5 PPD senators and 1 PIP senator: Maria de Lourdes Santiago, who would later become the top vote-getter in 2020.",
			step5p3: 'But supermajorities breed complacency. The Rossello administration\'s scandals and the 2019 protests set the stage for a dramatic reversal.',
			step6p1a: 'By 2020, the Senate looked completely different. PNP collapsed from 21 to',
			step6p1b: '9 seats',
			step6p1c: '. PPD recovered to 8. But the real story was the emergence of four new players:',
			step6p1d: '(2 seats),',
			step6p1e: '(2 seats),',
			step6p1f: '(1), and an independent (1).',
			step6p2: "For the first time in memory, neither major party controlled a majority. Governing required coalition-building. The Senate president's election became a negotiation rather than a formality. Every vote mattered.",
			step6p3: 'This is what multi-party democracy looks like in a legislature designed for two parties. The at-large system, by allowing more proportional representation, accelerated the transition.',
			step7p1a: 'This chart shows the structural shift in stark terms. Before 2016, third parties and independents held at most',
			step7p1b: '1-2 seats',
			step7p1c: '. The two-party system captured 95%+ of Senate representation.',
			step7p2a: 'The breakthrough came suddenly. In 2020, non-traditional parties and independents won',
			step7p2b: '6 of 27 seats',
			step7p2c: ': 22% of the chamber. MVC\'s Ana Irma Rivera Lassen and Rafael Bernabe became the party\'s first-ever senators. Proyecto Dignidad\'s Joanne Rodriguez Veve won her seat in her first election.',
			step7p3: 'The at-large system enabled this breakthrough. In district-only elections, these candidates might have won nothing. But island-wide voting allowed them to accumulate support from pockets across Puerto Rico, reaching the threshold for victory.',
			step8p1a: 'Puerto Rico\'s constitution contains a remarkable provision: if any party wins more than two-thirds of legislative seats,',
			step8p1b: 'additional seats are created',
			step8p1c: 'for the minority. This "minority representation" clause ensures opposition voices are always heard.',
			step8p2: "The clause was triggered in 2008, when PNP's dominance required expanding the Senate to preserve PPD representation. It's a structural check against one-party rule that few other jurisdictions have.",
			step8p3: "In the current multi-party environment, the clause is less relevant, no single party comes close to two-thirds. But it remains a safeguard against future supermajorities, ensuring Puerto Rico's democracy always includes opposition voices.",
			step9p1a: 'Looking at the 2024 composition, the transformation is complete.',
			step9p1b: 'now leads with 13 seats, but still lacks a majority.',
			step9p1c: 'holds 9. The remaining 5 seats are split among third parties and independents.',
			step9p2: "This creates a new kind of legislative politics. The Senate president needs cross-party support. Major legislation requires coalition-building. Individual senators, especially independents, wield outsized influence as potential swing votes.",
			step9p3: "The at-large experiment has produced exactly what its designers feared and hoped for: a legislature that reflects Puerto Rico's political diversity, including voices that the two-party system had marginalized for decades.",
			// Conclusion
			conclusionTitle: 'The Island-Wide Chamber',
			conclusionP1: "Puerto Rico's at-large Senate system is an experiment in representation. By requiring candidates to seek island-wide support, it produces senators with broader constituencies than district-based elections. By allowing proportional outcomes, it gives voice to parties that might otherwise be shut out.",
			conclusionP2: "The 2020 election marked a watershed: the definitive end of two-party dominance in the Senate. Whether this fragmentation leads to gridlock or innovation depends on how legislators adapt to coalition politics. But one thing is clear: Puerto Rico's Senate will never look like it did in 2016 again.",
			// Stats
			keyStats: 'Key Statistics: 2020 At-Large Senate',
			partiesRepresented: 'Parties Represented',
			topVoteGetter: 'Top Vote-Getter',
			candidatesRunning: 'Candidates Running',
			gapLabel: '11th-12th Place Gap',
			// Table
			compositionByYear: 'Senate Composition by Year',
			year: 'Year',
			other: 'Other',
			// Sources
			sources: 'Sources',
			sourceCEE: 'Senate election results 2000-2024',
			sourceSenate: 'Historical composition and party affiliation data',
			sourceConstitution: 'Puerto Rico Constitution - Senate structure and at-large seat requirements',
			sourceUPR: 'University of Puerto Rico - Political Science Department electoral analysis',
			// Navigation
			previous: 'Previous',
			prevTitle: 'Down to the Precinct',
			nextChapter: 'Next Chapter',
			nextTitle: '40 House Races'
		},
		es: {
			chapterTitle: 'El Experimento Por Acumulacion',
			chapter: 'Capitulo',
			lead: 'El Senado de Puerto Rico opera bajo un sistema unico: los 11 senadores por acumulacion son elegidos a nivel de toda la isla, convirtiendolo en una de las pocas legislaturas donde cada votante vota por cada escano. Este diseno produce dinamicas distintivas en torno a la representacion, protecciones de minoria y el auge de terceros partidos.',
			loading: 'Cargando datos...',
			seats: 'Escanos',
			// Viz titles
			senateComposition: 'Composicion del Senado',
			topVoteGetters: 'Los 11 Senadores Por Acumulacion con Mas Votos',
			partyVoteShare: 'Participacion de Votos por Partido: Senado Por Acumulacion',
			compositionOverTime: 'Composicion del Senado a Traves del Tiempo',
			twoPartyVsThird: 'Escanos Bipartidistas vs Terceros Partidos',
			// Viz notes
			voteNote: 'Totales de votos en miles',
			thirdPartyNote: 'El auge del MVC, PIP e independientes desde 2016',
			// Chart labels
			electionYear: 'Ano Electoral',
			seatsWon: 'Escanos Ganados',
			totalSeats: 'Total de Escanos',
			twoPartyLabel: 'PNP + PPD',
			thirdPartyLabel: 'Terceros Partidos + Ind',
			// Step titles
			step0Title: 'Un Experimento Electoral Unico',
			step1Title: 'Como Funciona el Voto Por Acumulacion',
			step2Title: 'Los Mayores Receptores de Votos',
			step3Title: 'Participacion de Votos por Partido',
			step4Title: 'Una Generacion de Cambio',
			step5Title: 'La Supermayoria de 2016',
			step6Title: 'La Fragmentacion de 2020',
			step7Title: 'El Avance de Terceros Partidos',
			step8Title: 'La Clausula de Proteccion de Minoria',
			step9Title: 'La Nueva Politica del Senado',
			// Step content
			step0p1: 'El Senado de Puerto Rico de 27 miembros se divide en dos componentes: 16 senadores de distrito (dos de cada uno de los 8 distritos senatoriales) y',
			step0p1b: '11 senadores por acumulacion',
			step0p1c: 'elegidos a nivel de toda la isla. Este sistema por acumulacion es practicamente unico en la politica estadounidense.',
			step0p2: 'El diseno por acumulacion fue intencional: los redactores querian senadores que representaran a todo Puerto Rico, no solo a su distrito. En teoria, esto crea legisladores con perspectivas mas amplias y reduce el parroquialismo. En la practica, recompensa el reconocimiento de nombre, pone a prueba la lealtad partidista y convierte la acumulacion de votos en un arte.',
			step0p3: 'El Senado de 2020 muestra el sistema en accion:',
			step0p3b: '6 partidos',
			step0p3c: 'obtuvieron representacion, el Senado mas fragmentado en la historia de Puerto Rico.',
			step1p1: 'Cada votante emite',
			step1p1b: 'hasta 11 votos',
			step1p1c: 'para senador por acumulacion, uno por cada escano. Puedes votar por candidatos de diferentes partidos, dividir tu papeleta o votar en linea recta por un partido. Los 11 candidatos con mas votos ganan.',
			step1p2: 'Esto crea incentivos unicos. A diferencia de los distritos uninominales donde gana un solo candidato, las contiendas por acumulacion recompensan el atractivo amplio. Un candidato que sea la segunda opcion de todos podria acumular mas votos que alguien polarizador. La popularidad personal importa enormemente.',
			step1p3: 'El resultado: las contiendas por acumulacion del senado a menudo producen',
			step1p3b: 'ganadores individuales sorprendentes',
			step1p3c: 'que superan a su partido. Candidatos independientes como el Dr. Jose Vargas Vidot han ganado escanos construyendo coaliciones personales que trascienden las lineas partidistas.',
			step2p1: 'En 2020, quien obtuvo mas votos fue',
			step2p1b: 'Maria de Lourdes Santiago',
			step2p1c: '(PIP) con casi',
			step2p1d: 'votos, superando a candidatos de ambos partidos principales. Su exito muestra como el sistema por acumulacion puede elevar a candidatos con marcas personales fuertes.',
			step2p2a: 'El grafico de barras muestra los 11 senadores electos con mas votos. Note la diversidad de colores: candidatos del',
			step2p2b: 'Proyecto Dignidad',
			step2p2c: ', e independientes lograron entrar junto a candidatos tradicionales de partidos principales.',
			step2p3a: 'La brecha entre el lugar 11 y 12 fue de solo',
			step2p3b: 'votos, mostrando cuan competitivas son estas contiendas. Unos miles de votos en cualquier direccion habrian cambiado la composicion del Senado.',
			step3p1a: 'Mirar la participacion agregada de votos por partido cuenta una historia diferente al exito individual de candidatos. En 2020,',
			step3p1b: 'todavia lideraba con alrededor del 33% de los votos por acumulacion del senado, seguido de cerca por',
			step3p1c: 'con 31%.',
			step3p2a: 'Pero la verdadera historia es la fragmentacion. Los terceros partidos combinados capturaron mas del',
			step3p2b: '35%',
			step3p2c: 'del voto.',
			step3p2d: 'aumento al 11%,',
			step3p2e: 'obtuvo 11%, y',
			step3p2f: 'emergio con 7%.',
			step3p3: 'Esta fragmentacion no se traduce directamente en escanos debido a las dinamicas de ganador-toma-todo. Pero el sistema por acumulacion es mas proporcional que las elecciones de distrito, permitiendo a partidos pequenos ganar representacion que no obtendrian en distritos uninominales.',
			step4p1: 'El grafico de lineas rastrea la composicion del Senado a traves de cinco ciclos electorales. El patron es dramatico: de un dominio casi total del',
			step4p1b: 'en 2008 (22 escanos) a una camara fragmentada en 2020 donde ningun partido controla la mayoria.',
			step4p2a: 'La eleccion de 2016 fue el pico del poder del PNP: ganaron',
			step4p2b: '21 de 27',
			step4p2c: 'escanos, suficientes para anular cualquier veto. Pero para 2020, esa supermayoria colapso a solo 9 escanos.',
			step4p2d: 'se recupero algo, pero los verdaderos ganadores fueron los partidos emergentes.',
			step4p3a: '2024 vio al',
			step4p3b: 'tomar el liderazgo con 13 escanos, mientras que',
			step4p3c: 'y',
			step4p3d: 'mantuvieron su posicion. El sistema bipartidista no ha regresado, y puede que nunca se recupere completamente.',
			step5p1: 'El hemiciclo de 2016 muestra al PNP en la cima de su poder. Con 21 escanos, tenian una',
			step5p1b: 'supermayoria constitucional',
			step5p1c: ', capaz de anular vetos del gobernador y controlar cada comite.',
			step5p2: 'Este dominio llego durante la crisis fiscal de PROMESA. Los votantes, agotados por el manejo del PPD de la crisis de deuda, se inclinaron decisivamente hacia el PNP. La oposicion se redujo a solo 5 senadores del PPD y 1 senador del PIP: Maria de Lourdes Santiago, quien mas tarde se convertiria en la mayor receptora de votos en 2020.',
			step5p3: 'Pero las supermayorias engendran complacencia. Los escandalos de la administracion Rossello y las protestas de 2019 prepararon el escenario para un giro dramatico.',
			step6p1a: 'Para 2020, el Senado lucia completamente diferente. El PNP colapso de 21 a',
			step6p1b: '9 escanos',
			step6p1c: '. El PPD se recupero a 8. Pero la verdadera historia fue la emergencia de cuatro nuevos actores:',
			step6p1d: '(2 escanos),',
			step6p1e: '(2 escanos),',
			step6p1f: '(1), y un independiente (1).',
			step6p2: 'Por primera vez en la memoria, ningun partido principal controlaba la mayoria. Gobernar requeria construir coaliciones. La eleccion del presidente del Senado se convirtio en una negociacion en lugar de una formalidad. Cada voto importaba.',
			step6p3: 'Esto es lo que parece la democracia multipartidista en una legislatura disenada para dos partidos. El sistema por acumulacion, al permitir una representacion mas proporcional, acelero la transicion.',
			step7p1a: 'Este grafico muestra el cambio estructural en terminos crudos. Antes de 2016, los terceros partidos e independientes tenian como maximo',
			step7p1b: '1-2 escanos',
			step7p1c: '. El sistema bipartidista capturaba mas del 95% de la representacion del Senado.',
			step7p2a: 'El avance llego repentinamente. En 2020, los partidos no tradicionales e independientes ganaron',
			step7p2b: '6 de 27 escanos',
			step7p2c: ': 22% de la camara. Ana Irma Rivera Lassen y Rafael Bernabe del MVC se convirtieron en los primeros senadores del partido. Joanne Rodriguez Veve de Proyecto Dignidad gano su escano en su primera eleccion.',
			step7p3: 'El sistema por acumulacion habilito este avance. En elecciones solo de distrito, estos candidatos podrian no haber ganado nada. Pero el voto a nivel de toda la isla les permitio acumular apoyo de bolsillos a traves de Puerto Rico, alcanzando el umbral para la victoria.',
			step8p1a: 'La constitucion de Puerto Rico contiene una disposicion notable: si algun partido gana mas de dos tercios de los escanos legislativos,',
			step8p1b: 'se crean escanos adicionales',
			step8p1c: 'para la minoria. Esta clausula de "representacion de minoria" asegura que las voces de oposicion siempre sean escuchadas.',
			step8p2: 'La clausula se activo en 2008, cuando el dominio del PNP requirio expandir el Senado para preservar la representacion del PPD. Es un control estructural contra el gobierno de un solo partido que pocas otras jurisdicciones tienen.',
			step8p3: 'En el entorno multipartidista actual, la clausula es menos relevante, ningun partido se acerca a dos tercios. Pero sigue siendo una salvaguarda contra futuras supermayorias, asegurando que la democracia de Puerto Rico siempre incluya voces de oposicion.',
			step9p1a: 'Mirando la composicion de 2024, la transformacion esta completa.',
			step9p1b: 'ahora lidera con 13 escanos, pero todavia carece de mayoria.',
			step9p1c: 'tiene 9. Los 5 escanos restantes se dividen entre terceros partidos e independientes.',
			step9p2: 'Esto crea un nuevo tipo de politica legislativa. El presidente del Senado necesita apoyo interpartidista. La legislacion importante requiere construccion de coaliciones. Los senadores individuales, especialmente los independientes, ejercen una influencia desproporcionada como posibles votos decisivos.',
			step9p3: 'El experimento por acumulacion ha producido exactamente lo que sus disenadores temian y esperaban: una legislatura que refleja la diversidad politica de Puerto Rico, incluyendo voces que el sistema bipartidista habia marginado durante decadas.',
			// Conclusion
			conclusionTitle: 'La Camara a Nivel de Isla',
			conclusionP1: 'El sistema de Senado por acumulacion de Puerto Rico es un experimento en representacion. Al requerir que los candidatos busquen apoyo a nivel de toda la isla, produce senadores con electorados mas amplios que las elecciones basadas en distritos. Al permitir resultados proporcionales, da voz a partidos que de otro modo quedarian excluidos.',
			conclusionP2: 'La eleccion de 2020 marco un hito: el fin definitivo del dominio bipartidista en el Senado. Si esta fragmentacion lleva al estancamiento o la innovacion depende de como los legisladores se adapten a la politica de coaliciones. Pero una cosa esta clara: el Senado de Puerto Rico nunca volvera a lucir como en 2016.',
			// Stats
			keyStats: 'Estadisticas Clave: Senado Por Acumulacion 2020',
			partiesRepresented: 'Partidos Representados',
			topVoteGetter: 'Mayor Receptor de Votos',
			candidatesRunning: 'Candidatos Compitiendo',
			gapLabel: 'Brecha Lugar 11-12',
			// Table
			compositionByYear: 'Composicion del Senado por Ano',
			year: 'Ano',
			other: 'Otro',
			// Sources
			sources: 'Fuentes',
			sourceCEE: 'Resultados electorales del Senado 2000-2024',
			sourceSenate: 'Composicion historica y datos de afiliacion partidista',
			sourceConstitution: 'Constitucion de Puerto Rico - Estructura del Senado y requisitos de escanos por acumulacion',
			sourceUPR: 'Universidad de Puerto Rico - Analisis electoral del Departamento de Ciencias Politicas',
			// Navigation
			previous: 'Anterior',
			prevTitle: 'Hasta el Precinto',
			nextChapter: 'Proximo Capitulo',
			nextTitle: '40 Contiendas de la Camara'
		}
	};

	// Reactive content based on language
	let content = $derived(t[$language]);
	let chapterTitle = $derived(content.chapterTitle);

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
			{ id: 'twoparty', label: content.twoPartyLabel, color: '#666666', data: twoPartyData },
			{ id: 'third', label: content.thirdPartyLabel, color: PARTY_COLORS.MVC, data: thirdPartyData }
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
				{:else if activeViz === 'hemicycle'}
					<h3 class="viz-title">{content.senateComposition}: {selectedYear}</h3>
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
							27 {content.seats}
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
					<h3 class="viz-title">{content.topVoteGetters} ({selectedYear})</h3>
					<BarChart
						data={topVotesBarData()}
						width={450}
						height={380}
						horizontal={true}
						valueFormat={(v) => `${formatNumber(Math.round(v * 1000))}`}
					/>
					<p class="viz-note">{content.voteNote}</p>
				{:else if activeViz === 'partyShare'}
					<h3 class="viz-title">{content.partyVoteShare} ({selectedYear})</h3>
					<BarChart
						data={partyShareBarData()}
						width={400}
						height={280}
						horizontal={false}
						valueFormat={(v) => formatPercent(v)}
					/>
				{:else if activeViz === 'composition'}
					<h3 class="viz-title">{content.compositionOverTime}</h3>
					<LineChart
						series={compositionLineData()}
						width={480}
						height={320}
						xLabel={content.electionYear}
						yLabel={content.seatsWon}
						xFormat={(v) => String(v)}
						yFormat={(v) => String(Math.round(v))}
						showDots={true}
						showArea={false}
					/>
				{:else if activeViz === 'thirdParty'}
					<h3 class="viz-title">{content.twoPartyVsThird}</h3>
					<LineChart
						series={thirdPartyLineData()}
						width={480}
						height={320}
						xLabel={content.electionYear}
						yLabel={content.totalSeats}
						xFormat={(v) => String(v)}
						yFormat={(v) => String(Math.round(v))}
						showDots={true}
						showArea={true}
					/>
					<p class="viz-note">{content.thirdPartyNote}</p>
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>{content.step0Title}</h3>
			<p>
				{content.step0p1} <span class="highlight">{content.step0p1b}</span>
				{content.step0p1c}
			</p>
			<p>{content.step0p2}</p>
			<p>
				{content.step0p3} <span class="stat">{content.step0p3b}</span>
				{content.step0p3c}
			</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>{content.step1Title}</h3>
			<p>
				{content.step1p1} <span class="highlight">{content.step1p1b}</span>
				{content.step1p1c}
			</p>
			<p>{content.step1p2}</p>
			<p>
				{content.step1p3} <span class="highlight">{content.step1p3b}</span>
				{content.step1p3c}
			</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>{content.step2Title}</h3>
			<p>
				{content.step2p1} <span class="highlight">{content.step2p1b}</span>
				{content.step2p1c} <span class="stat">269,000</span>
				{content.step2p1d}
			</p>
			<p>
				{content.step2p2a}
				<span style="color: {PARTY_COLORS.PIP}">PIP</span>,
				<span style="color: {PARTY_COLORS.MVC}">MVC</span>,
				<span style="color: {PARTY_COLORS.PD}">{content.step2p2b}</span>
				{content.step2p2c}
			</p>
			<p>
				{content.step2p3a} <span class="stat">{formatNumber(stats()?.cutoffMargin || 0)}</span>
				{content.step2p3b}
			</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>{content.step3Title}</h3>
			<p>
				{content.step3p1a}
				<span style="color: {PARTY_COLORS.PNP}">PNP</span>
				{content.step3p1b}
				<span style="color: {PARTY_COLORS.PPD}">PPD</span>
				{content.step3p1c}
			</p>
			<p>
				{content.step3p2a}
				<span class="stat">{content.step3p2b}</span>
				{content.step3p2c}
				<span style="color: {PARTY_COLORS.PIP}">PIP</span>
				{content.step3p2d}
				<span style="color: {PARTY_COLORS.MVC}">MVC</span>
				{content.step3p2e}
				<span style="color: {PARTY_COLORS.PD}">{content.step2p2b}</span>
				{content.step3p2f}
			</p>
			<p>{content.step3p3}</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>{content.step4Title}</h3>
			<p>
				{content.step4p1}
				<span style="color: {PARTY_COLORS.PNP}">PNP</span>
				{content.step4p1b}
			</p>
			<p>
				{content.step4p2a}
				<span class="stat">{content.step4p2b}</span>
				{content.step4p2c}
				<span style="color: {PARTY_COLORS.PPD}">PPD</span>
				{content.step4p2d}
			</p>
			<p>
				{content.step4p3a}
				<span style="color: {PARTY_COLORS.PPD}">PPD</span>
				{content.step4p3b}
				<span style="color: {PARTY_COLORS.MVC}">MVC</span>
				{content.step4p3c}
				<span style="color: {PARTY_COLORS.PIP}">PIP</span>
				{content.step4p3d}
			</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>{content.step5Title}</h3>
			<p>
				{content.step5p1}
				<span class="highlight">{content.step5p1b}</span>
				{content.step5p1c}
			</p>
			<p>{content.step5p2}</p>
			<p>{content.step5p3}</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>{content.step6Title}</h3>
			<p>
				{content.step6p1a}
				<span class="stat">{content.step6p1b}</span>
				{content.step6p1c}
				<span style="color: {PARTY_COLORS.MVC}">MVC</span>
				{content.step6p1d}
				<span style="color: {PARTY_COLORS.PIP}">PIP</span>
				{content.step6p1e}
				<span style="color: {PARTY_COLORS.PD}">{content.step2p2b}</span>
				{content.step6p1f}
			</p>
			<p>{content.step6p2}</p>
			<p>{content.step6p3}</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>{content.step7Title}</h3>
			<p>
				{content.step7p1a}
				<span class="stat">{content.step7p1b}</span>
				{content.step7p1c}
			</p>
			<p>
				{content.step7p2a}
				<span class="stat">{content.step7p2b}</span>
				{content.step7p2c}
			</p>
			<p>{content.step7p3}</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>{content.step8Title}</h3>
			<p>
				{content.step8p1a}
				<span class="highlight">{content.step8p1b}</span>
				{content.step8p1c}
			</p>
			<p>{content.step8p2}</p>
			<p>{content.step8p3}</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>{content.step9Title}</h3>
			<p>
				{content.step9p1a}
				<span style="color: {PARTY_COLORS.PPD}">PPD</span>
				{content.step9p1b}
				<span style="color: {PARTY_COLORS.PNP}">PNP</span>
				{content.step9p1c}
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
			{#if stats()}
				<div class="stats-summary">
					<h3>{content.keyStats}</h3>
					<div class="stats-grid">
						<div class="stat-item">
							<span class="stat-value">6</span>
							<span class="stat-label">{content.partiesRepresented}</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{formatNumber(stats().topCandidate?.votes || 0)}</span>
							<span class="stat-label">{content.topVoteGetter}</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{stats().totalCandidates2020}</span>
							<span class="stat-label">{content.candidatesRunning}</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{formatNumber(stats().cutoffMargin)}</span>
							<span class="stat-label">{content.gapLabel}</span>
						</div>
					</div>
				</div>
			{/if}

			<!-- Historical Composition Table -->
			<div class="composition-table-container">
				<h3>{content.compositionByYear}</h3>
				<table class="composition-table">
					<thead>
						<tr>
							<th>{content.year}</th>
							<th><span class="party-label" style="background: {PARTY_COLORS.PNP}">PNP</span></th>
							<th><span class="party-label" style="background: {PARTY_COLORS.PPD}">PPD</span></th>
							<th><span class="party-label" style="background: {PARTY_COLORS.PIP}">PIP</span></th>
							<th><span class="party-label" style="background: {PARTY_COLORS.MVC}">MVC</span></th>
							<th>{content.other}</th>
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
				<h3>{content.sources}</h3>
				<ul>
					<li><a href="https://ww2.ceepur.org/Home/EventosElectorales" target="_blank" rel="noopener">Comision Estatal de Elecciones de Puerto Rico (CEE)</a> - {content.sourceCEE}</li>
					<li><a href="https://senado.pr.gov/" target="_blank" rel="noopener">Senado de Puerto Rico</a> - {content.sourceSenate}</li>
					<li>{content.sourceConstitution}</li>
					<li>{content.sourceUPR}</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/precincts" class="nav-link prev">
					<span class="nav-direction">{content.previous}</span>
					<span class="nav-title">{content.prevTitle}</span>
				</a>
				<a href="{base}/chapters/house" class="nav-link next">
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
