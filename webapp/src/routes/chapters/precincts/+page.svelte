<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { ChoroplethMap } from '$lib/components/maps';
	import { BarChart, ScatterPlot } from '$lib/components/charts';
	import { PARTY_COLORS, createDivergingScale, CATEGORY_COLORS } from '$lib/utils/colors';
	import { formatNumber, formatPercent, formatChange } from '$lib/utils/format';
	import { language } from '$lib/stores/language';

	// Chapter metadata
	const chapterNum = 9;
	const totalSteps = 10;

	// Bilingual content
	const t = {
		en: {
			chapterTitle: 'Down to the Precinct',
			chapter: 'Chapter',
			lead: "Municipality averages hide enormous variation. Within San Juan alone, precincts range from 29% to 37% PNP support. The same city. Completely different political worlds.",
			electoralPrecincts: 'Electoral Precincts',
			sanJuanSpread: 'San Juan Spread',
			maxInternalVariation: 'Max Internal Variation',
			loading: 'Loading precinct data...',
			// Viz titles
			zoomingIntoSanJuan: 'Zooming Into San Juan',
			fromOneNumberToFive: 'From one number to five distinct stories',
			sanJuanFivePrecincts: "San Juan's Five Precincts",
			pnpVoteShare: 'PNP Vote Share (2020 Governor)',
			spreadNote: 'percentage point spread within one municipality',
			withinMuniVariation: 'Within-Municipality Variation',
			howPrecinctsDiffer: 'How precincts differ from their neighbors',
			spread: 'spread',
			ppdLeaning: 'PPD-leaning',
			competitive: 'Competitive',
			pnpLeaning: 'PNP-leaning',
			fullPicture: 'The Full Picture',
			precinctSizeVsCompetitiveness: 'Precinct Size vs. Competitiveness',
			largeCompetitivePrize: 'Large competitive precincts are the prize',
			competitivenessNote: '100 = perfectly competitive (PNP vs PPD tied). Higher = more competitive.',
			battlegroundPrecincts: 'The Battleground Precincts',
			marginBetween: 'Margin between PNP and PPD (percentage points)',
			thinMarginsNote: 'These precincts are decided by thin margins. Every vote matters.',
			safeSeats: 'Safe Seats',
			predeterminedOutcomes: 'Precincts where outcomes are predetermined',
			safeSeatsNote: 'Margins over 15 points rarely flip. Campaigns rarely invest here.',
			highValueTargets: 'High-Value Targets',
			largeCompetitive: 'Large precincts that are still competitive',
			totalVotesCast: 'Total votes cast. Color indicates current lean.',
			precinctMapTitle: "Puerto Rico's Electoral Precincts",
			eachPrecinctUniverse: 'Each precinct is its own political universe',
			hoverForDetails: 'Colors show precinct boundaries. Hover for details.',
			microscopeView: 'The Microscope View',
			whatAggregateHides: 'What aggregate data hides, precinct data reveals',
			// Step titles
			step0Title: 'The Municipality Illusion',
			step1Title: 'Case Study: San Juan',
			step2Title: 'The Precinct Spectrum',
			step3Title: 'Not Just San Juan',
			step4Title: 'Size Meets Competitiveness',
			step5Title: 'The Battleground Precincts',
			step6Title: 'The Safe Seats',
			step7Title: 'The Campaign Target List',
			step8Title: 'What Aggregate Data Hides',
			step9Title: 'The Ground Game',
			// Step content
			step0p1: "When we analyze Puerto Rico's elections, we typically look at the 78 municipalities. San Juan voted",
			step0p1b: "PNP in the 2020 governor's race. Bayamon:",
			step0p1c: 'Ponce:',
			step0p2: "These numbers are useful, but they're averages. And averages can deceive. They smooth over the sharp edges of political geography, hiding the real story of who votes where and why.",
			step0p3: 'To see the truth, we need to zoom in. Below the municipality level, Puerto Rico is divided into',
			step0p3b: 'electoral precincts.',
			step1p1: "San Juan, the capital and most populous municipality, isn't one political community. It's five precincts, each encompassing different neighborhoods with distinct demographics, histories, and voting patterns.",
			step1p2a: 'includes much of Old San Juan and Condado, areas with higher incomes and tourism infrastructure.',
			step1p2b: 'covers Santurce and parts of Hato Rey, with more mixed-income housing and a younger population.',
			step1p3: 'The voting patterns tell the rest of the story.',
			step2p1: 'Within San Juan, PNP support ranges from',
			step2p1b: 'to',
			step2p1c: ". That's nearly an",
			step2p1d: 'spread, all within what the census calls a single municipality.',
			step2p2a: 'was the most PNP-friendly, with',
			step2p2b: 'support. This area tends to have higher homeownership rates and older residents.',
			step2p3a: 'covering the Santurce arts district and surrounding neighborhoods, gave PNP only',
			step2p3b: 'Same city. Very different politics.',
			step3p1: "San Juan's internal diversity isn't unique. Many municipalities show similar or even greater variation.",
			step3p1b: 'has the largest spread:',
			step3p1c: 'between its two precincts.',
			step3p2a: 'precincts differ by',
			step3p2b: 'shows',
			step3p2c: 'of variation. Even mid-sized municipalities contain multitudes.',
			step3p3: "The chart shows the top five municipalities by internal variation. Each dot is a precinct; the line shows the range. These aren't uniform political units. They're coalitions of neighborhoods with different interests and identities.",
			step4p1: "For campaigns, not all precincts matter equally. A tiny safe precinct can be ignored. A large competitive one is a treasure. This scatter plot reveals where the action is.",
			step4p2: "is the prize: large precincts that are still competitive. These are the places where voter outreach, advertising, and get-out-the-vote operations deliver the highest return on investment.",
			step4p3: "Notice the cluster of competitive precincts in the 20,000-30,000 vote range. These are the true battlegrounds of Puerto Rican elections.",
			step5p1: 'Some precincts are decided by razor-thin margins.',
			step5p1b: 'was essentially tied in 2020, with PNP and PPD within a tenth of a percentage point.',
			step5p2: "These ultra-competitive precincts are where elections can be won or lost. A few hundred votes in the right places can swing outcomes. Campaigns that understand this geography have a structural advantage.",
			step5p3: 'In these precincts,',
			step5p3b: 'Turnout operations become critical. A rainy election day could decide which party wins.',
			step6p1: "Not every precinct is competitive.",
			step6p1b: 'gave PNP a',
			step6p1c: 'margin.',
			step6p1d: 'was',
			step6p1e: 'toward PNP. These are safe seats where outcomes are virtually predetermined.',
			step6p2: "For campaigns, these precincts require a different calculus. Persuasion is largely pointless. The goal becomes turnout: making sure your reliable voters actually show up.",
			step6p3: 'Safe seats also matter for',
			step6p3b: 'In deeply partisan areas, the real election is often the primary, not the general.',
			step7p1: "Professional campaigns build target lists: which precincts to invest in, which to ignore. The ideal targets are",
			step7p1b: 'and have room for persuasion or turnout gains.',
			step7p2a: 'cast nearly 30,000 votes and was decided by just 1.4 percentage points.',
			step7p2b: 'had 29,000 votes and a 0.2-point margin. These are the precincts where campaigns spend money.',
			step7p3: "Knowing your precincts isn't just strategy. It's the difference between efficient resource allocation and wasted effort.",
			step8p1: 'Municipal averages hide important details:',
			step8p2a: 'Precinct-level data reveals whether district lines unnaturally split or combine neighborhoods. You can\'t spot manipulation in aggregate data.',
			step8p2b: 'Campaigns can identify exactly which neighborhoods need attention. Generic "get out the vote" messaging is replaced by block-by-block strategy.',
			step8p2c: 'A municipality might look safe while containing fiercely contested precincts and vice versa.',
			step9p1: "Puerto Rican elections are won on the ground, in neighborhoods, at community centers and front doors. The parties know this. Their precinct captains know every street, every family, every political lean.",
			step9p2: 'This granular knowledge is power. A campaign that understands that',
			step9p2b: 'can allocate resources intelligently. One-size-fits-all strategies fail.',
			step9p3: 'The data is available. The patterns are clear. The only question is whether anyone is paying attention.',
			// UI labels
			precinctLabel: 'Precinct',
			everyVoteMatters: 'every voter matters',
			candidateRecruitment: 'candidate recruitment',
			large: 'large',
			upperRightQuadrant: 'upper right quadrant',
			gerrymanderingDetection: 'Gerrymandering detection:',
			targetedMobilization: 'Targeted mobilization:',
			trueCompetitiveness: 'True competitiveness:',
			precinct001LeansPNP: 'Precinct 001 leans PNP while Precinct 002 is more competitive',
			// Conclusion
			conclusionTitle: 'The Micro-Geography of Politics',
			conclusionP1: "Precinct-level analysis reveals the true texture of Puerto Rico's political landscape. What looks like a uniform municipality is actually a patchwork of distinct communities with their own political cultures.",
			conclusionP2a: "Within San Juan's 5 precincts, we found a",
			conclusionP2b: "spread in PNP support. In Las Piedras, the spread was",
			conclusionP2c: "These differences aren't noise. They're signal.",
			conclusionP3: "Understanding precinct geography matters for anyone who cares about Puerto Rican democracy: campaigns trying to win elections, journalists trying to explain outcomes, and citizens trying to understand their neighbors.",
			keyTakeaways: 'Key Takeaways',
			takeaway1: 'Puerto Rico has',
			takeaway1b: 'across 78 municipalities',
			takeaway2: "San Juan's precincts range from 29% to 37% PNP support (",
			takeaway2b: 'spread)',
			takeaway3: 'Las Piedras has the largest internal variation:',
			takeaway4: 'was the most competitive precinct (0.0pp margin)',
			takeaway5: 'Large competitive precincts like Caguas 083 (30K votes, 1.4pp margin) are key targets',
			sources: 'Sources',
			source1: 'Precinct-level election results 2016-2024',
			source2: 'Precinct boundary definitions and voter registration by precinct',
			source3: 'Block group population data for precinct analysis',
			source4: 'Geographic information systems data',
			// Navigation
			previous: 'Previous',
			prevTitle: '78 Battlegrounds',
			nextChapter: 'Next Chapter',
			nextTitle: 'The Senate Districts'
		},
		es: {
			chapterTitle: 'Hasta el Recinto',
			chapter: 'Capitulo',
			lead: 'Los promedios municipales ocultan una enorme variacion. Solo en San Juan, los recintos van del 29% al 37% de apoyo al PNP. La misma ciudad. Mundos politicos completamente diferentes.',
			electoralPrecincts: 'Recintos Electorales',
			sanJuanSpread: 'Rango en San Juan',
			maxInternalVariation: 'Variacion Interna Maxima',
			loading: 'Cargando datos de recintos...',
			// Viz titles
			zoomingIntoSanJuan: 'Acercamiento a San Juan',
			fromOneNumberToFive: 'De un numero a cinco historias distintas',
			sanJuanFivePrecincts: 'Los Cinco Recintos de San Juan',
			pnpVoteShare: 'Porcentaje de Votos PNP (Gobernador 2020)',
			spreadNote: 'puntos porcentuales de diferencia dentro de un municipio',
			withinMuniVariation: 'Variacion Dentro del Municipio',
			howPrecinctsDiffer: 'Como difieren los recintos de sus vecinos',
			spread: 'rango',
			ppdLeaning: 'Inclinacion PPD',
			competitive: 'Competitivo',
			pnpLeaning: 'Inclinacion PNP',
			fullPicture: 'El Panorama Completo',
			precinctSizeVsCompetitiveness: 'Tamano del Recinto vs. Competitividad',
			largeCompetitivePrize: 'Los recintos grandes y competitivos son el premio',
			competitivenessNote: '100 = perfectamente competitivo (PNP vs PPD empatados). Mayor = mas competitivo.',
			battlegroundPrecincts: 'Los Recintos de Batalla',
			marginBetween: 'Margen entre PNP y PPD (puntos porcentuales)',
			thinMarginsNote: 'Estos recintos se deciden por margenes estrechos. Cada voto cuenta.',
			safeSeats: 'Escanos Seguros',
			predeterminedOutcomes: 'Recintos donde los resultados estan predeterminados',
			safeSeatsNote: 'Margenes de mas de 15 puntos rara vez cambian. Las campanas rara vez invierten aqui.',
			highValueTargets: 'Objetivos de Alto Valor',
			largeCompetitive: 'Recintos grandes que aun son competitivos',
			totalVotesCast: 'Total de votos emitidos. El color indica la inclinacion actual.',
			precinctMapTitle: 'Los Recintos Electorales de Puerto Rico',
			eachPrecinctUniverse: 'Cada recinto es su propio universo politico',
			hoverForDetails: 'Los colores muestran los limites de los recintos. Pase el cursor para detalles.',
			microscopeView: 'La Vista de Microscopio',
			whatAggregateHides: 'Lo que los datos agregados ocultan, los datos de recintos revelan',
			// Step titles
			step0Title: 'La Ilusion Municipal',
			step1Title: 'Caso de Estudio: San Juan',
			step2Title: 'El Espectro de Recintos',
			step3Title: 'No Solo San Juan',
			step4Title: 'Tamano y Competitividad',
			step5Title: 'Los Recintos de Batalla',
			step6Title: 'Los Escanos Seguros',
			step7Title: 'La Lista de Objetivos de Campana',
			step8Title: 'Lo que Ocultan los Datos Agregados',
			step9Title: 'El Juego Terrestre',
			// Step content
			step0p1: 'Cuando analizamos las elecciones de Puerto Rico, tipicamente miramos los 78 municipios. San Juan voto',
			step0p1b: 'PNP en la carrera de gobernador de 2020. Bayamon:',
			step0p1c: 'Ponce:',
			step0p2: 'Estos numeros son utiles, pero son promedios. Y los promedios pueden enganar. Suavizan los bordes afilados de la geografia politica, ocultando la historia real de quien vota donde y por que.',
			step0p3: 'Para ver la verdad, necesitamos acercarnos. Por debajo del nivel municipal, Puerto Rico esta dividido en',
			step0p3b: 'recintos electorales.',
			step1p1: 'San Juan, la capital y el municipio mas poblado, no es una sola comunidad politica. Son cinco recintos, cada uno abarcando diferentes barrios con demografias, historias y patrones de votacion distintos.',
			step1p2a: 'incluye gran parte del Viejo San Juan y Condado, areas con mayores ingresos e infraestructura turistica.',
			step1p2b: 'cubre Santurce y partes de Hato Rey, con viviendas de ingresos mixtos y una poblacion mas joven.',
			step1p3: 'Los patrones de votacion cuentan el resto de la historia.',
			step2p1: 'Dentro de San Juan, el apoyo al PNP va desde',
			step2p1b: 'hasta',
			step2p1c: '. Eso es casi',
			step2p1d: 'de diferencia, todo dentro de lo que el censo llama un solo municipio.',
			step2p2a: 'fue el mas favorable al PNP, con',
			step2p2b: 'de apoyo. Esta area tiende a tener mayores tasas de propiedad de vivienda y residentes mayores.',
			step2p3a: 'cubriendo el distrito artistico de Santurce y los barrios circundantes, le dio al PNP solo',
			step2p3b: 'La misma ciudad. Politica muy diferente.',
			step3p1: 'La diversidad interna de San Juan no es unica. Muchos municipios muestran variacion similar o incluso mayor.',
			step3p1b: 'tiene el mayor rango:',
			step3p1c: 'entre sus dos recintos.',
			step3p2a: 'los recintos difieren por',
			step3p2b: 'muestra',
			step3p2c: 'de variacion. Incluso los municipios medianos contienen multitudes.',
			step3p3: 'El grafico muestra los cinco municipios con mayor variacion interna. Cada punto es un recinto; la linea muestra el rango. No son unidades politicas uniformes. Son coaliciones de barrios con diferentes intereses e identidades.',
			step4p1: 'Para las campanas, no todos los recintos importan igual. Un recinto pequeno y seguro puede ignorarse. Uno grande y competitivo es un tesoro. Este grafico de dispersion revela donde esta la accion.',
			step4p2: 'es el premio: recintos grandes que aun son competitivos. Estos son los lugares donde el alcance a votantes, la publicidad y las operaciones de movilizacion del voto ofrecen el mayor retorno de inversion.',
			step4p3: 'Note el grupo de recintos competitivos en el rango de 20,000-30,000 votos. Estos son los verdaderos campos de batalla de las elecciones puertorriquenas.',
			step5p1: 'Algunos recintos se deciden por margenes minimos.',
			step5p1b: 'estuvo practicamente empatado en 2020, con PNP y PPD a una decima de punto porcentual.',
			step5p2: 'Estos recintos ultracompetitivos son donde las elecciones se pueden ganar o perder. Unos cientos de votos en los lugares correctos pueden cambiar resultados. Las campanas que entienden esta geografia tienen una ventaja estructural.',
			step5p3: 'En estos recintos,',
			step5p3b: 'Las operaciones de movilizacion se vuelven criticas. Un dia de elecciones lluvioso podria decidir que partido gana.',
			step6p1: 'No todos los recintos son competitivos.',
			step6p1b: 'le dio al PNP un margen de',
			step6p1c: '',
			step6p1d: 'estaba',
			step6p1e: 'hacia el PNP. Estos son escanos seguros donde los resultados estan virtualmente predeterminados.',
			step6p2: 'Para las campanas, estos recintos requieren un calculo diferente. La persuasion es mayormente inutil. El objetivo se convierte en participacion: asegurarse de que sus votantes confiables realmente se presenten.',
			step6p3: 'Los escanos seguros tambien importan para',
			step6p3b: 'En areas profundamente partidistas, la verdadera eleccion es a menudo la primaria, no la general.',
			step7p1: 'Las campanas profesionales construyen listas de objetivos: en que recintos invertir, cuales ignorar. Los objetivos ideales son',
			step7p1b: 'y tienen espacio para persuasion o ganancias de participacion.',
			step7p2a: 'emitio casi 30,000 votos y se decidio por solo 1.4 puntos porcentuales.',
			step7p2b: 'tuvo 29,000 votos y un margen de 0.2 puntos. Estos son los recintos donde las campanas gastan dinero.',
			step7p3: 'Conocer tus recintos no es solo estrategia. Es la diferencia entre asignacion eficiente de recursos y esfuerzo desperdiciado.',
			step8p1: 'Los promedios municipales ocultan detalles importantes:',
			step8p2a: 'Los datos a nivel de recinto revelan si las lineas distritales dividen o combinan barrios de manera antinatural. No puedes detectar manipulacion en datos agregados.',
			step8p2b: 'Las campanas pueden identificar exactamente que barrios necesitan atencion. Los mensajes genericos de "sal a votar" se reemplazan por estrategia cuadra por cuadra.',
			step8p2c: 'Un municipio podria parecer seguro mientras contiene recintos ferozmente disputados y viceversa.',
			step9p1: 'Las elecciones puertorriquenas se ganan en el terreno, en los barrios, en centros comunitarios y puertas de casas. Los partidos lo saben. Sus capitanes de recinto conocen cada calle, cada familia, cada inclinacion politica.',
			step9p2: 'Este conocimiento granular es poder. Una campana que entiende que',
			step9p2b: 'puede asignar recursos inteligentemente. Las estrategias de talla unica fracasan.',
			step9p3: 'Los datos estan disponibles. Los patrones son claros. La unica pregunta es si alguien esta prestando atencion.',
			// UI labels
			precinctLabel: 'Recinto',
			everyVoteMatters: 'cada votante importa',
			candidateRecruitment: 'reclutamiento de candidatos',
			large: 'grandes',
			upperRightQuadrant: 'cuadrante superior derecho',
			gerrymanderingDetection: 'Deteccion de gerrymandering:',
			targetedMobilization: 'Movilizacion dirigida:',
			trueCompetitiveness: 'Competitividad real:',
			precinct001LeansPNP: 'el Recinto 001 se inclina al PNP mientras que el Recinto 002 es mas competitivo',
			// Conclusion
			conclusionTitle: 'La Micro-Geografia de la Politica',
			conclusionP1: 'El analisis a nivel de recinto revela la verdadera textura del panorama politico de Puerto Rico. Lo que parece un municipio uniforme es en realidad un mosaico de comunidades distintas con sus propias culturas politicas.',
			conclusionP2a: 'Dentro de los 5 recintos de San Juan, encontramos una diferencia de',
			conclusionP2b: 'en el apoyo al PNP. En Las Piedras, el rango fue de',
			conclusionP2c: 'Estas diferencias no son ruido. Son senal.',
			conclusionP3: 'Entender la geografia de recintos importa para cualquiera que se preocupe por la democracia puertorriquena: campanas tratando de ganar elecciones, periodistas tratando de explicar resultados, y ciudadanos tratando de entender a sus vecinos.',
			keyTakeaways: 'Conclusiones Clave',
			takeaway1: 'Puerto Rico tiene',
			takeaway1b: 'a traves de 78 municipios',
			takeaway2: 'Los recintos de San Juan van del 29% al 37% de apoyo al PNP (',
			takeaway2b: 'de diferencia)',
			takeaway3: 'Las Piedras tiene la mayor variacion interna:',
			takeaway4: 'fue el recinto mas competitivo (margen de 0.0pp)',
			takeaway5: 'Recintos grandes y competitivos como Caguas 083 (30K votos, margen de 1.4pp) son objetivos clave',
			sources: 'Fuentes',
			source1: 'Resultados electorales a nivel de recinto 2016-2024',
			source2: 'Definiciones de limites de recintos y registro de votantes por recinto',
			source3: 'Datos de poblacion de grupos de bloques para analisis de recintos',
			source4: 'Datos de sistemas de informacion geografica',
			// Navigation
			previous: 'Anterior',
			prevTitle: '78 Campos de Batalla',
			nextChapter: 'Proximo Capitulo',
			nextTitle: 'Los Distritos Senatoriales'
		}
	};

	// Reactive content based on language
	let content = $derived(t[$language]);
	let chapterTitle = $derived(content.chapterTitle);

	// State
	let currentStep = $state(0);
	let loading = $state(true);
	let selectedMunicipality = $state<string | null>(null);

	// Data types
	interface PrecinctData {
		precinct: string;
		municipality: string;
		total_votes: number;
		pnp_pct: number;
		ppd_pct: number;
		margin: number;
		abs_margin: number;
		competitiveness: number;
	}

	interface MunicipalityVariation {
		municipality: string;
		num_precincts: number;
		min_pnp: number;
		max_pnp: number;
		spread: number;
		precincts: PrecinctData[];
	}

	interface ChapterData {
		year: number;
		total_precincts: number;
		total_municipalities: number;
		san_juan: {
			precincts: PrecinctData[];
			spread: number;
		};
		municipality_variation: MunicipalityVariation[];
		most_competitive: PrecinctData[];
		safe_seats: PrecinctData[];
		swing_targets: PrecinctData[];
		scatter_data: Array<{
			x: number;
			y: number;
			label: string;
			municipality: string;
			margin: number;
		}>;
		all_precincts: PrecinctData[];
	}

	// Loaded data
	let chapterData = $state<ChapterData | null>(null);

	// Current visualization type
	let currentViz = $state<'map' | 'bar' | 'scatter' | 'small-multiples' | 'boxplot'>('map');

	// Load chapter data
	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/chapters/precincts.json`);
			chapterData = await response.json();
		} catch (err) {
			console.error('Failed to load precincts data:', err);
		} finally {
			loading = false;
		}
	});

	// Derived data for visualizations

	// San Juan bar chart data
	let sanJuanBarData = $derived(() => {
		if (!chapterData?.san_juan?.precincts) return [];
		return chapterData.san_juan.precincts.map(p => ({
			label: p.precinct.replace('San Juan ', `${content.precinctLabel} `),
			value: p.pnp_pct,
			color: p.pnp_pct > 35 ? PARTY_COLORS.PNP : p.pnp_pct < 30 ? PARTY_COLORS.PPD : CATEGORY_COLORS[5]
		}));
	});

	// Top variation municipalities for small multiples
	let topVariationMunis = $derived(() => {
		if (!chapterData?.municipality_variation) return [];
		return chapterData.municipality_variation.slice(0, 5);
	});

	// Most competitive bar data
	let competitiveBarData = $derived(() => {
		if (!chapterData?.most_competitive) return [];
		return chapterData.most_competitive.slice(0, 8).map(p => ({
			label: p.precinct,
			value: p.abs_margin,
			color: CATEGORY_COLORS[4]
		}));
	});

	// Swing targets bar data
	let swingTargetsData = $derived(() => {
		if (!chapterData?.swing_targets) return [];
		return chapterData.swing_targets.slice(0, 8).map(p => ({
			label: p.precinct,
			value: p.total_votes,
			color: p.margin > 0 ? PARTY_COLORS.PNP : PARTY_COLORS.PPD
		}));
	});

	// Scatter plot data for size vs competitiveness
	let scatterData = $derived(() => {
		if (!chapterData?.scatter_data) return [];
		return chapterData.scatter_data.map(p => ({
			x: p.x,
			y: p.y,
			label: p.label,
			color: p.margin < 5 ? CATEGORY_COLORS[4] : p.margin < 10 ? CATEGORY_COLORS[1] : CATEGORY_COLORS[3],
			size: 5
		}));
	});

	// Map data for both levels
	let mapData = $state(new Map<string, number>());
	let precinctMapData = $state(new Map<string, number>());
	const colorScale = createDivergingScale([25, 35, 45]);

	// Color scale for variation viz
	const variationColorScale = createDivergingScale([0, 7, 14]);

	// Map level: switches between municipality and precinct view
	let mapLevel = $state<'municipality' | 'precinct'>('municipality');

	// Build precinct map data from all_precincts when available
	// Note: TopoJSON uses IDs like "d01_p00" but we need to map from precinct names
	// For now, the map will use built-in colors from TopoJSON when data isn't mapped
	$effect(() => {
		if (chapterData?.all_precincts) {
			// This would require a crosswalk to map precinct names to TopoJSON IDs
			// For now, we'll let the map use built-in colors
		}
	});

	function handleStepEnter(response: { index: number }) {
		currentStep = response.index;

		switch (response.index) {
			case 0:
				// Opening - municipality illusion
				currentViz = 'map';
				mapLevel = 'municipality';
				mapData = new Map();
				break;
			case 1:
				// San Juan as case study
				currentViz = 'bar';
				selectedMunicipality = 'San Juan';
				break;
			case 2:
				// The precinct spectrum within San Juan
				currentViz = 'bar';
				break;
			case 3:
				// Small multiples - top varying municipalities
				currentViz = 'small-multiples';
				selectedMunicipality = null;
				break;
			case 4:
				// Scatter: size vs competitiveness
				currentViz = 'scatter';
				break;
			case 5:
				// Most competitive precincts
				currentViz = 'bar';
				break;
			case 6:
				// Safe seats
				currentViz = 'bar';
				break;
			case 7:
				// Campaign targeting - swing targets
				currentViz = 'bar';
				break;
			case 8:
				// What this means - show precinct map
				currentViz = 'map';
				mapLevel = 'precinct';
				break;
			case 9:
				// Ground game conclusion - show precinct map
				currentViz = 'map';
				mapLevel = 'precinct';
				break;
		}
	}

	// Key stats from data
	let sanJuanSpread = $derived(chapterData?.san_juan?.spread ?? 7.7);
	let lasPiedrasSpread = $derived(chapterData?.municipality_variation?.[0]?.spread ?? 13.1);
	let mostCompetitivePrecinct = $derived(chapterData?.most_competitive?.[0]?.precinct ?? 'Anasco 040');
	let totalPrecincts = $derived(chapterData?.total_precincts ?? 110);
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
			<div class="lead-stats">
				<div class="stat-block">
					<span class="stat-value">{totalPrecincts}</span>
					<span class="stat-label">{content.electoralPrecincts}</span>
				</div>
				<div class="stat-block">
					<span class="stat-value">{formatChange(sanJuanSpread)}pp</span>
					<span class="stat-label">{content.sanJuanSpread}</span>
				</div>
				<div class="stat-block">
					<span class="stat-value">{formatChange(lasPiedrasSpread)}pp</span>
					<span class="stat-label">{content.maxInternalVariation}</span>
				</div>
			</div>
		</div>
	</header>

	<ScrollySection offset={0.6} onStepEnter={handleStepEnter}>
		{#snippet graphic()}
			<div class="viz-container">
				{#if loading}
					<p class="loading">{content.loading}</p>
				{:else if currentViz === 'bar' && currentStep === 1}
					<!-- San Juan precinct intro -->
					<div class="zoom-metaphor">
						<div class="zoom-icon">
							<svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="2">
								<circle cx="11" cy="11" r="8"/>
								<path d="M21 21l-4.35-4.35"/>
								<path d="M11 8v6M8 11h6"/>
							</svg>
						</div>
						<h3 class="viz-title">{content.zoomingIntoSanJuan}</h3>
						<p class="viz-subtitle">{content.fromOneNumberToFive}</p>
					</div>
				{:else if currentViz === 'bar' && currentStep === 2}
					<!-- San Juan precincts bar chart -->
					<h3 class="viz-title">{content.sanJuanFivePrecincts}</h3>
					<p class="viz-subtitle">{content.pnpVoteShare}</p>
					<div class="chart-container">
						<BarChart
							data={sanJuanBarData()}
							width={450}
							height={320}
							horizontal={true}
							valueFormat={(v) => `${v.toFixed(1)}%`}
						/>
					</div>
					<p class="chart-note">{formatChange(sanJuanSpread)} {content.spreadNote}</p>
				{:else if currentViz === 'small-multiples'}
					<!-- Small multiples showing variation in multiple municipalities -->
					<h3 class="viz-title">{content.withinMuniVariation}</h3>
					<p class="viz-subtitle">{content.howPrecinctsDiffer}</p>
					<div class="small-multiples-container">
						{#each topVariationMunis() as muni}
							<div class="small-multiple">
								<h4>{muni.municipality}</h4>
								<div class="variation-bar">
									{#each muni.precincts as p}
										<div
											class="precinct-dot"
											style="left: {((p.pnp_pct - 20) / 40) * 100}%; background: {p.pnp_pct > 35 ? PARTY_COLORS.PNP : p.pnp_pct < 30 ? PARTY_COLORS.PPD : CATEGORY_COLORS[5]}"
											title="{p.precinct}: {p.pnp_pct}% PNP"
										></div>
									{/each}
									<div class="range-line" style="left: {((muni.min_pnp - 20) / 40) * 100}%; width: {((muni.max_pnp - muni.min_pnp) / 40) * 100}%"></div>
								</div>
								<div class="variation-stats">
									<span class="stat-small">{muni.min_pnp.toFixed(0)}%</span>
									<span class="spread-label">{formatChange(muni.spread)}pp {content.spread}</span>
									<span class="stat-small">{muni.max_pnp.toFixed(0)}%</span>
								</div>
							</div>
						{/each}
					</div>
					<div class="variation-legend">
						<span style="color: {PARTY_COLORS.PPD}">{content.ppdLeaning}</span>
						<span style="color: {CATEGORY_COLORS[5]}">{content.competitive}</span>
						<span style="color: {PARTY_COLORS.PNP}">{content.pnpLeaning}</span>
					</div>
				{:else if currentViz === 'scatter'}
					<!-- Scatter: precinct size vs competitiveness -->
					<h3 class="viz-title">{currentStep === 8 ? content.fullPicture : content.precinctSizeVsCompetitiveness}</h3>
					<p class="viz-subtitle">{content.largeCompetitivePrize}</p>
					<div class="chart-container">
						<ScatterPlot
							data={scatterData()}
							width={500}
							height={400}
							xLabel={$language === 'en' ? 'Total Votes Cast' : 'Total de Votos Emitidos'}
							yLabel={$language === 'en' ? 'Competitiveness Score' : 'Puntuacion de Competitividad'}
							xFormat={(v) => formatNumber(Math.round(v))}
							yFormat={(v) => `${v.toFixed(0)}`}
							showRegression={false}
						/>
					</div>
					<p class="chart-note">{content.competitivenessNote}</p>
				{:else if currentViz === 'bar' && currentStep === 5}
					<!-- Most competitive precincts -->
					<h3 class="viz-title">{content.battlegroundPrecincts}</h3>
					<p class="viz-subtitle">{content.marginBetween}</p>
					<div class="chart-container">
						<BarChart
							data={competitiveBarData()}
							width={500}
							height={350}
							horizontal={true}
							valueFormat={(v) => `${v.toFixed(1)}pp`}
						/>
					</div>
					<p class="chart-note">{content.thinMarginsNote}</p>
				{:else if currentViz === 'bar' && currentStep === 6}
					<!-- Safe seats -->
					<h3 class="viz-title">{content.safeSeats}</h3>
					<p class="viz-subtitle">{content.predeterminedOutcomes}</p>
					<div class="chart-container">
						{#if chapterData?.safe_seats}
							<BarChart
								data={chapterData.safe_seats.slice(0, 8).map(p => ({
									label: p.precinct,
									value: p.abs_margin,
									color: p.margin > 0 ? PARTY_COLORS.PNP : PARTY_COLORS.PPD
								}))}
								width={500}
								height={350}
								horizontal={true}
								valueFormat={(v) => `${v.toFixed(1)}pp`}
							/>
						{/if}
					</div>
					<p class="chart-note">{content.safeSeatsNote}</p>
				{:else if currentViz === 'bar' && currentStep === 7}
					<!-- Swing targets -->
					<h3 class="viz-title">{content.highValueTargets}</h3>
					<p class="viz-subtitle">{content.largeCompetitive}</p>
					<div class="chart-container">
						<BarChart
							data={swingTargetsData()}
							width={500}
							height={350}
							horizontal={true}
							valueFormat={(v) => formatNumber(v)}
						/>
					</div>
					<p class="chart-note">{content.totalVotesCast}</p>
				{:else if currentViz === 'map'}
					<!-- Map view - switches between municipality and precinct level -->
					{#if mapLevel === 'precinct'}
						<h3 class="viz-title">{content.precinctMapTitle} ({totalPrecincts})</h3>
						<p class="viz-subtitle">{content.eachPrecinctUniverse}</p>
						<div class="chart-container map-full">
							<ChoroplethMap
								level="precinct"
								data={precinctMapData}
								{colorScale}
								width={550}
								height={380}
								tooltipFormat={(name, value) => value !== undefined ? `${name}: ${value.toFixed(1)}% PNP` : name}
							/>
						</div>
						<p class="chart-note">{content.hoverForDetails}</p>
					{:else}
						<div class="microscope-intro">
							<svg class="microscope-icon" viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="currentColor" stroke-width="1.5">
								<circle cx="11" cy="11" r="8"/>
								<path d="M21 21l-4.35-4.35"/>
								<path d="M11 8v6M8 11h6"/>
							</svg>
							<h3 class="viz-title">{content.microscopeView}</h3>
							<p class="viz-subtitle">{content.whatAggregateHides}</p>
						</div>
					{/if}
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>{content.step0Title}</h3>
			<p>
				{content.step0p1} <span class="stat">33% PNP</span> {content.step0p1b}
				<span class="stat">34%</span>. {content.step0p1c} <span class="stat">32%</span>.
			</p>
			<p>{content.step0p2}</p>
			<p class="emphasis">
				{content.step0p3} {totalPrecincts} {content.step0p3b}
			</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>{content.step1Title}</h3>
			<p>{content.step1p1}</p>
			<p>
				<span class="highlight">{content.precinctLabel} 001</span> {content.step1p2a}
				<span class="highlight">{content.precinctLabel} 002</span> {content.step1p2b}
			</p>
			<p>{content.step1p3}</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>{content.step2Title}</h3>
			<p>
				{content.step2p1} <span class="stat">29%</span> {content.step2p1b}
				<span class="stat">37%</span>{content.step2p1c} <span class="stat">8 {$language === 'en' ? 'percentage point' : 'puntos porcentuales'}</span> {content.step2p1d}
			</p>
			<p>
				<span class="highlight">{content.precinctLabel} 001</span> {content.step2p2a}
				<span class="stat">36.9%</span> {content.step2p2b}
			</p>
			<p>
				<span class="highlight">{content.precinctLabel} 002</span>, {content.step2p3a}
				<span class="stat">29.2%</span>. {content.step2p3b}
			</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>{content.step3Title}</h3>
			<p>
				{content.step3p1} <span class="highlight">Las Piedras</span> {content.step3p1b}
				<span class="stat">{formatChange(lasPiedrasSpread)} {$language === 'en' ? 'percentage points' : 'puntos porcentuales'}</span> {content.step3p1c}
			</p>
			<p>
				<span class="highlight">Coamo</span> {content.step3p2a} <span class="stat">8.9 {$language === 'en' ? 'points' : 'puntos'}</span>.
				<span class="highlight">Barranquitas</span> {content.step3p2b} <span class="stat">8.1 {$language === 'en' ? 'points' : 'puntos'}</span> {content.step3p2c}
			</p>
			<p>{content.step3p3}</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>{content.step4Title}</h3>
			<p>{content.step4p1}</p>
			<p>
				{$language === 'en' ? 'The' : 'El'} <span class="highlight">{content.upperRightQuadrant}</span> {content.step4p2}
			</p>
			<p>{content.step4p3}</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>{content.step5Title}</h3>
			<p>
				{content.step5p1} <span class="highlight">{mostCompetitivePrecinct}</span> {content.step5p1b}
			</p>
			<p>{content.step5p2}</p>
			<p>
				{content.step5p3} <span class="highlight">{content.everyVoteMatters}</span>. {content.step5p3b}
			</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>{content.step6Title}</h3>
			<p>
				{content.step6p1} <span class="highlight">Barranquitas 071</span> {content.step6p1b}
				<span class="stat">21 {$language === 'en' ? 'points' : 'puntos'}</span>{content.step6p1c}
				<span class="highlight">Guaynabo 007</span> {content.step6p1d}
				<span class="stat">19 {$language === 'en' ? 'points' : 'puntos'}</span> {content.step6p1e}
			</p>
			<p>{content.step6p2}</p>
			<p>
				{content.step6p3} <span class="highlight">{content.candidateRecruitment}</span>. {content.step6p3b}
			</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>{content.step7Title}</h3>
			<p>
				{content.step7p1} <span class="highlight">{content.large}</span>,
				<span class="highlight">{content.competitive}</span>, {content.step7p1b}
			</p>
			<p>
				<span class="highlight">Caguas 083</span> {content.step7p2a}
				<span class="highlight">San Juan 002</span> {content.step7p2b}
			</p>
			<p>{content.step7p3}</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>{content.step8Title}</h3>
			<p>{content.step8p1}</p>
			<p>
				<span class="highlight">{content.gerrymanderingDetection}</span> {content.step8p2a}
			</p>
			<p>
				<span class="highlight">{content.targetedMobilization}</span> {content.step8p2b}
			</p>
			<p>
				<span class="highlight">{content.trueCompetitiveness}</span> {content.step8p2c}
			</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>{content.step9Title}</h3>
			<p>{content.step9p1}</p>
			<p>
				{content.step9p2}
				<span class="highlight">{content.precinct001LeansPNP}</span> {content.step9p2b}
			</p>
			<p class="emphasis">{content.step9p3}</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>{content.conclusionTitle}</h2>
			<p>{content.conclusionP1}</p>
			<p>
				{content.conclusionP2a} {formatChange(sanJuanSpread)} {$language === 'en' ? 'percentage point' : 'puntos porcentuales'}
				{content.conclusionP2b} {formatChange(lasPiedrasSpread)} {$language === 'en' ? 'points' : 'puntos'}.
				{content.conclusionP2c}
			</p>
			<p>{content.conclusionP3}</p>

			<div class="key-takeaways">
				<h3>{content.keyTakeaways}</h3>
				<ul>
					<li>{content.takeaway1} <span class="stat">{totalPrecincts} {$language === 'en' ? 'electoral precincts' : 'recintos electorales'}</span> {content.takeaway1b}</li>
					<li>{content.takeaway2}{formatChange(sanJuanSpread)}pp {content.takeaway2b}</li>
					<li>{content.takeaway3} <span class="stat">{formatChange(lasPiedrasSpread)}pp</span></li>
					<li><span class="stat">{mostCompetitivePrecinct}</span> {content.takeaway4}</li>
					<li>{content.takeaway5}</li>
				</ul>
			</div>

			<div class="sources">
				<h3>{content.sources}</h3>
				<ul>
					<li><a href="https://ww2.ceepur.org/Home/EventosElectorales" target="_blank" rel="noopener">Comision Estatal de Elecciones de Puerto Rico (CEE)</a> - {content.source1}</li>
					<li><a href="https://ww2.ceepur.org/" target="_blank" rel="noopener">CEE</a> - {content.source2}</li>
					<li><a href="https://data.census.gov/" target="_blank" rel="noopener">U.S. Census Bureau</a> - {content.source3}</li>
					<li>{$language === 'en' ? 'Puerto Rico Planning Board' : 'Junta de Planificacion de Puerto Rico'} - {content.source4}</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/battlegrounds" class="nav-link prev">
					<span class="nav-direction">{content.previous}</span>
					<span class="nav-title">{content.prevTitle}</span>
				</a>
				<a href="{base}/chapters/senate" class="nav-link next">
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
		color: var(--color-text);
		margin-bottom: var(--space-xs);
		text-align: center;
	}

	.viz-subtitle {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
		text-align: center;
	}

	/* Zoom/microscope metaphor */
	.zoom-metaphor, .microscope-intro {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 300px;
		text-align: center;
	}

	.zoom-icon, .microscope-icon {
		color: var(--color-accent);
		margin-bottom: var(--space-lg);
		opacity: 0.8;
	}

	/* Chart container */
	.chart-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		width: 100%;
		max-width: 550px;
	}

	.chart-container.map-full {
		max-width: 600px;
		min-height: 400px;
	}

	.chart-note {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin-top: var(--space-md);
		text-align: center;
		font-style: italic;
	}

	/* Small multiples visualization */
	.small-multiples-container {
		display: flex;
		flex-direction: column;
		gap: var(--space-lg);
		width: 100%;
		max-width: 500px;
	}

	.small-multiple {
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
	}

	.small-multiple h4 {
		font-size: var(--text-sm);
		font-weight: var(--font-medium);
		color: var(--color-text);
		margin: 0;
	}

	.variation-bar {
		position: relative;
		height: 24px;
		background: var(--color-surface);
		border-radius: var(--radius-sm);
		border: 1px solid var(--color-border);
	}

	.precinct-dot {
		position: absolute;
		width: 12px;
		height: 12px;
		border-radius: 50%;
		top: 5px;
		transform: translateX(-50%);
		border: 2px solid var(--color-bg);
		z-index: 2;
		cursor: pointer;
	}

	.range-line {
		position: absolute;
		height: 4px;
		background: var(--color-border);
		top: 10px;
		border-radius: 2px;
		z-index: 1;
	}

	.variation-stats {
		display: flex;
		justify-content: space-between;
		font-size: var(--text-xs);
		color: var(--color-text-muted);
	}

	.stat-small {
		font-weight: var(--font-medium);
	}

	.spread-label {
		color: var(--color-accent);
		font-weight: var(--font-medium);
	}

	.variation-legend {
		display: flex;
		gap: var(--space-lg);
		margin-top: var(--space-lg);
		font-size: var(--text-sm);
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

	/* Chapter conclusion */
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

	@media (max-width: 768px) {
		.lead-stats {
			flex-direction: column;
			gap: var(--space-lg);
		}

		.stat-value {
			font-size: var(--text-2xl);
		}

		.chart-container {
			max-width: 100%;
		}

		.small-multiples-container {
			max-width: 100%;
		}
	}
</style>
