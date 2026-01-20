<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { ChoroplethMap } from '$lib/components/maps';
	import { BarChart, ScatterPlot } from '$lib/components/charts';
	import { Legend } from '$lib/components/ui';
	import { PARTY_COLORS, createDivergingScale, createSequentialScale } from '$lib/utils/colors';
	import { formatPercent, formatNumber, formatPercentChange } from '$lib/utils/format';
	import { language } from '$lib/stores/language';

	const chapterNum = 8;
	const totalSteps = 11;

	// Bilingual content
	const t = {
		en: {
			chapterTitle: '78 Battlegrounds',
			chapter: 'Chapter',
			lead: "Puerto Rico has 78 municipalities, each with its own political character. Some are strongholds where campaigns barely bother; others are swing towns where elections are won and lost. Think like a campaign strategist: where would you spend your final weekend before Election Day?",
			loading: 'Loading data...',
			and: 'and',
			// Viz titles
			understandingSwing: 'Understanding Swing',
			pnpSwing: 'PNP Swing',
			westernShift: 'The Western Shift',
			competitiveness2020: 'Competitiveness: 2020 Margins',
			decidersSizeCompetitiveness: 'The Deciders: Size vs. Competitiveness',
			electoralWeightAnalysis: 'Electoral Weight Analysis',
			biggestSwings: 'Biggest Swings 2016-2020',
			whoFlipped: 'Who Flipped? PPD vs PNP Gains',
			threeWayRace: 'The Three-Way Race',
			battlefield2024: 'The 2024 Battlefield',
			// Tooltip formats
			swingTooltip: 'swing',
			marginTooltip: 'margin',
			tossup: 'Tossup',
			lean: 'Lean',
			safe: 'Safe',
			// Legend labels
			ppdPlus12: 'PPD +12',
			noChange: 'No change',
			pnpPlus12: 'PNP +12',
			competitiveness: 'Competitiveness',
			tossupLegend: 'Tossup (<5%)',
			leanLegend: 'Lean (5-10%)',
			safeLegend: 'Safe (>10%)',
			// Scatter plot
			bubbleNote: 'Bubble size = swing magnitude | Color = winner',
			populationThousands: 'Population (thousands)',
			marginOfVictory: 'Margin of Victory (%)',
			// Step titles and content
			step0Title: "The Campaign Strategist's View",
			step0p1: "Every election cycle, campaign managers face the same question:",
			step0p1Highlight: "where do we invest our limited resources?",
			step0p1End: "The answer lies in understanding which municipalities truly decide elections.",
			step0p2: "Not all municipalities are created equal. Some have voted the same way for decades-they're \"banked\" votes that won't change. Others swing wildly between elections, shifting by 10 or even 15 percentage points in a single cycle.",
			step0p3: "This chapter maps Puerto Rico's electoral battlefield: the strongholds, the swing towns, and the \"deciders\" that determine who governs from La Fortaleza.",
			step1Title: 'What Makes a Municipality "Swing"?',
			step1p1: "A swing municipality isn't just one where the margin is close-it's one where",
			step1p1Highlight: "voter preferences change significantly between elections",
			step1p1End: ". A town with a 2% margin that stays at 2% isn't swing; it's a stable tossup.",
			step1p2: "True swing municipalities show volatility: perhaps they went PNP +8 in one election, then PPD +4 in the next. This 12-point swing signals that voters there are persuadable-or that mobilization can make the difference.",
			step1p3: "Campaign strategists separate municipalities into three categories: safe (margin > 10%), lean (5-10%), and tossup (< 5%). But within tossups, some are stable while others are genuinely volatile.",
			step2Title: 'The Swing Map',
			step2p1Start: "This map shows how each municipality's PNP margin changed between",
			step2p1And: "and",
			step2p1Blue: "Blue",
			step2p1Indicates: "indicates the PNP gained ground;",
			step2p1Red: "red",
			step2p1Shows: "shows PPD gains.",
			step2p2Start: "The data reveals a striking pattern:",
			step2p2Mid: "municipalities swung by more than 10 percentage points-unprecedented volatility that suggests a realigning electorate. The average swing was",
			step2p2End: "toward PPD.",
			step2p3Start: "Most dramatically,",
			step2p3Mid: "municipalities actually flipped parties-switching from PNP-leaning to PPD-leaning or vice versa. These flips aren't random; they tell us where the political winds are blowing.",
			step3Title: 'The Western Shift',
			step3p1: "The most dramatic swings occurred in Puerto Rico's western municipalities. Towns like",
			step3p1Lares: "Lares (-16pp)",
			step3p1Isabela: "Isabela (-16pp)",
			step3p1Aguadilla: "Aguadilla (-14pp)",
			step3p1End: "showed massive movement toward PPD-or more accurately, away from the incumbent PNP.",
			step3p2: "This western shift wasn't just partisan realignment. These municipalities also showed the strongest growth for third parties like Movimiento Victoria Ciudadana and Proyecto Dignidad. In a traditional two-party system, a 16-point swing means PNP lost and PPD gained. But in 2020, much of that \"swing\" went to emerging parties.",
			step3p3: "The geographic clustering suggests common factors at play: economic conditions, post-Maria recovery, and the rise of a new political generation that rejects the traditional PNP/PPD binary.",
			step4Title: 'Classifying the Battlefield',
			step4p1Start: "Beyond swing, strategists need to know current competitiveness. This map classifies each municipality by its 2020 margin of victory:",
			step4Tossup: "Tossup",
			step4TossupRange: "(< 5%),",
			step4Lean: "Lean",
			step4LeanRange: "(5-10%),",
			step4Safe: "Safe",
			step4SafeRange: "(> 10%).",
			step4p2Start: "In 2020,",
			step4p2Tossups: "municipalities were true tossups,",
			step4p2Lean: "leaned one way, and",
			step4p2Safe: "were safely in one camp. PNP won",
			step4p2Outright: "municipalities outright; PPD took",
			step4p3Start: "The tossup municipalities-places like",
			step4p3Juncos: "Juncos",
			step4p3Coamo: "Coamo",
			step4p3VegaAlta: "Vega Alta",
			step4p3End: "-are where 2024 will be decided. A candidate who sweeps the tossups while holding their base wins the governorship.",
			step5Title: 'The Deciders',
			step5p1: "Some municipalities matter more than others-not because of margins, but because of size. The \"deciders\" are municipalities that are both",
			step5p1Large: "large enough to matter",
			step5p1And: "and",
			step5p1Competitive: "competitive enough to swing",
			step5p2Start: "decider municipalities identified:",
			step5p2End: "Populations over 30,000, margins under 8%.",
			step5p3: "If you're running for governor with one week left before Election Day, this is your target list.",
			step6Title: 'Electoral Weight Analysis',
			step6p1: "This scatter plot visualizes the strategic landscape. The X-axis shows population (how many voters a municipality has), and the Y-axis shows margin (how competitive it is). Each dot is sized by how much it swung in 2016-2020.",
			step6p2Start: "The",
			step6p2Quadrant: "bottom-right quadrant",
			step6p2Mid: "is campaign gold: large populations with tight margins. Points in this zone-San Juan, Carolina, Caguas-are where elections are won. The top-right quadrant (large but safe) can be taken for granted; the left side (small populations) won't move the needle regardless of competitiveness.",
			step6p3: "Notice how the biggest bubbles (largest swings) cluster in the middle-left: smaller municipalities with moderate margins. These towns are volatile but don't have enough votes to be decisive on their own.",
			step7Title: 'The Biggest Swings',
			step7p1Start: "Here are the ten municipalities with the largest swings from 2016 to 2020. The direction tells the story:",
			step7p1RedBars: "red bars",
			step7p1ShowPPD: "show PPD gains,",
			step7p1BlueBars: "blue bars",
			step7p1ShowPNP: "show PNP gains.",
			step7p2Start: "The asymmetry is striking. Nine of the top ten swings favored PPD-a wave election that swept across traditionally PNP-leaning towns. Only",
			step7p2Patillas: "Patillas",
			step7p2End: "(+13pp) bucked the trend with a massive PNP swing, flipping from PPD to PNP.",
			step7p3: "What drove these swings? Post-Maria frustration, economic decline, corruption scandals, and the rise of third-party alternatives all played roles. The question for 2024: will these shifts stick, or will the pendulum swing back?",
			step8Title: 'Who Actually Flipped?',
			step8p1Start: "Swing is one thing; actually flipping from one party to another is more dramatic.",
			step8p1Mid: "municipalities changed hands between 2016 and 2020, shifting from PNP-leaning to PPD-leaning or vice versa.",
			step8p2Start: "Notable flips include",
			step8p2Isabela: "Isabela",
			step8p2IsabelaSwing: "(PNP +2 to PPD +14),",
			step8p2Barceloneta: "Barceloneta",
			step8p2BarcelonetaSwing: "(PNP +0.3 to PPD +8), and",
			step8p2Aguadilla: "Aguadilla",
			step8p2AguadillaSwing: "(PNP +14 to dead even). These weren't marginal shifts-they represent complete reversals of political identity.",
			step8p3: "Flipped municipalities are the canaries in the coal mine. They signal where realignment is happening and often predict broader trends. Watch these towns closely in 2024.",
			step9Title: 'Beyond the Binary: Three-Way Races',
			step9p1Start: "Traditional swing analysis assumes a two-party system: votes move between PNP and PPD. But 2020 broke that model. Third parties-particularly",
			step9p1MVC: "MVC",
			step9p1And: "and",
			step9p1PD: "Proyecto Dignidad",
			step9p1End: "-captured significant vote shares, especially among younger voters.",
			step9p2: "This creates a new dimension of \"swing.\" A municipality can now shift in multiple directions: PNP<->PPD (traditional swing), major party<->third party (protest swing), or even between third parties (ideological sorting). The old maps don't capture this complexity.",
			step9p3: "In 2024, strategists must ask not just \"will this municipality swing?\" but \"swing to whom?\" A frustrated PNP voter might go PPD, MVC, PD, or stay home. Understanding these flows is the new frontier of Puerto Rican electoral analysis.",
			step10Title: 'The 2024 Battlefield',
			step10p1: "Looking ahead to 2024, the battleground map has shifted. The western municipalities that swung hard toward PPD in 2020 may now be PPD strongholds-or they may swing back if conditions change. The metropolitan San Juan area, with its mix of competitive suburbs, remains the decisive theater.",
			step10p2Start: "Key municipalities to watch:",
			step10p2Carolina: "Carolina",
			step10p2CarolinaNote: "(the largest tossup),",
			step10p2Caguas: "Caguas",
			step10p2CaguasNote: "(central mountain bellwether),",
			step10p2Bayamon: "Bayamon",
			step10p2BayamonNote: "(suburban swing), and",
			step10p2Ponce: "Ponce",
			step10p2PonceNote: "(southern anchor). Whoever wins three of these four likely wins the governorship.",
			step10p3: "The fundamental question: was 2020 a realigning election that reshaped Puerto Rico's political geography, or a wave election that will recede? The battleground municipalities will give us the answer.",
			// Conclusion
			conclusionTitle: 'The Strategic Map',
			conclusionP1: "Puerto Rico's 78 municipalities each tell a political story. Some are reliable strongholds, delivering predictable margins election after election. Others are volatile swing towns where campaigns are won and lost in the final days. This geography matters to anyone who wants to predict-or influence-Puerto Rican elections.",
			conclusionP2: "But municipality-level analysis only goes so far. Within large municipalities, individual precincts can vary by 30 or more percentage points. The next chapter goes deeper, exploring the precinct-level patterns that reveal Puerto Rico's true electoral fabric.",
			keyStatsTitle: 'Key Statistics',
			municipalitiesFlipped: 'Municipalities Flipped',
			swungOver10: 'Swung >10pp',
			tossupsIn2020: 'Tossups in 2020',
			averageSwing: 'Average Swing (toward PPD)',
			// Sources
			sources: 'Sources',
			source1: 'Municipality-level gubernatorial results 2016, 2020, 2024',
			source2: 'Population estimates by municipality',
			source3: 'Demographic and economic indicators by region',
			source4: 'Analysis methodology: Swing calculated as change in winning margin between elections',
			// Navigation
			previous: 'Previous',
			nextChapter: 'Next Chapter',
			prevTitle: 'La Fortaleza',
			nextTitle: 'Down to the Precinct'
		},
		es: {
			chapterTitle: '78 Campos de Batalla',
			chapter: 'Capitulo',
			lead: 'Puerto Rico tiene 78 municipios, cada uno con su propio caracter politico. Algunos son bastiones donde las campanas apenas se molestan; otros son pueblos competitivos donde las elecciones se ganan y se pierden. Piensa como un estratega de campana: donde pasarias tu ultimo fin de semana antes del Dia de Elecciones?',
			loading: 'Cargando datos...',
			and: 'y',
			// Viz titles
			understandingSwing: 'Entendiendo el Cambio',
			pnpSwing: 'Cambio PNP',
			westernShift: 'El Cambio del Oeste',
			competitiveness2020: 'Competitividad: Margenes 2020',
			decidersSizeCompetitiveness: 'Los Decisivos: Tamano vs. Competitividad',
			electoralWeightAnalysis: 'Analisis de Peso Electoral',
			biggestSwings: 'Mayores Cambios 2016-2020',
			whoFlipped: 'Quien Cambio? Ganancias PPD vs PNP',
			threeWayRace: 'La Carrera a Tres Bandas',
			battlefield2024: 'El Campo de Batalla 2024',
			// Tooltip formats
			swingTooltip: 'cambio',
			marginTooltip: 'margen',
			tossup: 'Renido',
			lean: 'Inclinado',
			safe: 'Seguro',
			// Legend labels
			ppdPlus12: 'PPD +12',
			noChange: 'Sin cambio',
			pnpPlus12: 'PNP +12',
			competitiveness: 'Competitividad',
			tossupLegend: 'Renido (<5%)',
			leanLegend: 'Inclinado (5-10%)',
			safeLegend: 'Seguro (>10%)',
			// Scatter plot
			bubbleNote: 'Tamano de burbuja = magnitud del cambio | Color = ganador',
			populationThousands: 'Poblacion (miles)',
			marginOfVictory: 'Margen de Victoria (%)',
			// Step titles and content
			step0Title: 'La Vision del Estratega de Campana',
			step0p1: 'En cada ciclo electoral, los gerentes de campana enfrentan la misma pregunta:',
			step0p1Highlight: 'donde invertimos nuestros recursos limitados?',
			step0p1End: 'La respuesta esta en entender cuales municipios realmente deciden las elecciones.',
			step0p2: 'No todos los municipios son iguales. Algunos han votado igual durante decadas-son votos \"asegurados\" que no cambiaran. Otros oscilan dramaticamente entre elecciones, cambiando 10 o hasta 15 puntos porcentuales en un solo ciclo.',
			step0p3: 'Este capitulo mapea el campo de batalla electoral de Puerto Rico: los bastiones, los pueblos competitivos y los \"decisivos\" que determinan quien gobierna desde La Fortaleza.',
			step1Title: 'Que Hace a un Municipio "Competitivo"?',
			step1p1: 'Un municipio competitivo no es solo uno donde el margen es cerrado-es uno donde',
			step1p1Highlight: 'las preferencias de los votantes cambian significativamente entre elecciones',
			step1p1End: '. Un pueblo con margen de 2% que se mantiene en 2% no es competitivo; es un empate estable.',
			step1p2: 'Los municipios verdaderamente competitivos muestran volatilidad: quizas fueron PNP +8 en una eleccion, luego PPD +4 en la siguiente. Este cambio de 12 puntos indica que los votantes alli son persuadibles-o que la movilizacion puede marcar la diferencia.',
			step1p3: 'Los estrategas de campana separan los municipios en tres categorias: seguro (margen > 10%), inclinado (5-10%) y reñido (< 5%). Pero dentro de los reñidos, algunos son estables mientras otros son genuinamente volatiles.',
			step2Title: 'El Mapa de Cambios',
			step2p1Start: 'Este mapa muestra como cambio el margen del PNP en cada municipio entre',
			step2p1And: 'y',
			step2p1Blue: 'Azul',
			step2p1Indicates: 'indica que el PNP gano terreno;',
			step2p1Red: 'rojo',
			step2p1Shows: 'muestra ganancias del PPD.',
			step2p2Start: 'Los datos revelan un patron sorprendente:',
			step2p2Mid: 'municipios oscilaron mas de 10 puntos porcentuales-volatilidad sin precedentes que sugiere un electorado en realineamiento. El cambio promedio fue de',
			step2p2End: 'hacia el PPD.',
			step2p3Start: 'Lo mas dramatico,',
			step2p3Mid: 'municipios realmente cambiaron de partido-pasando de inclinarse al PNP a inclinarse al PPD o viceversa. Estos cambios no son aleatorios; nos dicen hacia donde soplan los vientos politicos.',
			step3Title: 'El Cambio del Oeste',
			step3p1: 'Los cambios mas dramaticos ocurrieron en los municipios del oeste de Puerto Rico. Pueblos como',
			step3p1Lares: 'Lares (-16pp)',
			step3p1Isabela: 'Isabela (-16pp)',
			step3p1Aguadilla: 'Aguadilla (-14pp)',
			step3p1End: 'mostraron movimiento masivo hacia el PPD-o mas precisamente, lejos del PNP incumbente.',
			step3p2: 'Este cambio del oeste no fue solo realineamiento partidista. Estos municipios tambien mostraron el mayor crecimiento para terceros partidos como Movimiento Victoria Ciudadana y Proyecto Dignidad. En un sistema bipartidista tradicional, un cambio de 16 puntos significa que el PNP perdio y el PPD gano. Pero en 2020, mucho de ese \"cambio\" fue a partidos emergentes.',
			step3p3: 'El agrupamiento geografico sugiere factores comunes en juego: condiciones economicas, recuperacion post-Maria y el surgimiento de una nueva generacion politica que rechaza el binomio tradicional PNP/PPD.',
			step4Title: 'Clasificando el Campo de Batalla',
			step4p1Start: 'Mas alla del cambio, los estrategas necesitan conocer la competitividad actual. Este mapa clasifica cada municipio por su margen de victoria en 2020:',
			step4Tossup: 'Reñido',
			step4TossupRange: '(< 5%),',
			step4Lean: 'Inclinado',
			step4LeanRange: '(5-10%),',
			step4Safe: 'Seguro',
			step4SafeRange: '(> 10%).',
			step4p2Start: 'En 2020,',
			step4p2Tossups: 'municipios eran verdaderamente reñidos,',
			step4p2Lean: 'se inclinaban hacia un lado, y',
			step4p2Safe: 'estaban seguros en un bando. El PNP gano',
			step4p2Outright: 'municipios directamente; el PPD tomo',
			step4p3Start: 'Los municipios reñidos-lugares como',
			step4p3Juncos: 'Juncos',
			step4p3Coamo: 'Coamo',
			step4p3VegaAlta: 'Vega Alta',
			step4p3End: '-son donde se decidira 2024. Un candidato que gane los reñidos mientras mantiene su base gana la gobernacion.',
			step5Title: 'Los Decisivos',
			step5p1: 'Algunos municipios importan mas que otros-no por sus margenes, sino por su tamano. Los \"decisivos\" son municipios que son',
			step5p1Large: 'lo suficientemente grandes para importar',
			step5p1And: 'y',
			step5p1Competitive: 'lo suficientemente competitivos para oscilar',
			step5p2Start: 'municipios decisivos identificados:',
			step5p2End: 'Poblaciones sobre 30,000, margenes bajo 8%.',
			step5p3: 'Si estas corriendo para gobernador con una semana antes del Dia de Elecciones, esta es tu lista objetivo.',
			step6Title: 'Analisis de Peso Electoral',
			step6p1: 'Este grafico de dispersion visualiza el panorama estrategico. El eje X muestra la poblacion (cuantos votantes tiene un municipio), y el eje Y muestra el margen (cuan competitivo es). Cada punto esta dimensionado por cuanto oscilo en 2016-2020.',
			step6p2Start: 'El',
			step6p2Quadrant: 'cuadrante inferior derecho',
			step6p2Mid: 'es oro para las campanas: grandes poblaciones con margenes ajustados. Los puntos en esta zona-San Juan, Carolina, Caguas-son donde se ganan las elecciones. El cuadrante superior derecho (grande pero seguro) se puede dar por sentado; el lado izquierdo (poblaciones pequeñas) no movera la aguja sin importar la competitividad.',
			step6p3: 'Nota como las burbujas mas grandes (mayores cambios) se agrupan en el centro-izquierda: municipios mas pequeños con margenes moderados. Estos pueblos son volatiles pero no tienen suficientes votos para ser decisivos por si solos.',
			step7Title: 'Los Mayores Cambios',
			step7p1Start: 'Aqui estan los diez municipios con los mayores cambios de 2016 a 2020. La direccion cuenta la historia:',
			step7p1RedBars: 'barras rojas',
			step7p1ShowPPD: 'muestran ganancias del PPD,',
			step7p1BlueBars: 'barras azules',
			step7p1ShowPNP: 'muestran ganancias del PNP.',
			step7p2Start: 'La asimetria es sorprendente. Nueve de los diez mayores cambios favorecieron al PPD-una eleccion de ola que barrio pueblos tradicionalmente inclinados al PNP. Solo',
			step7p2Patillas: 'Patillas',
			step7p2End: '(+13pp) rompio la tendencia con un cambio masivo hacia el PNP, pasando del PPD al PNP.',
			step7p3: 'Que impulso estos cambios? Frustracion post-Maria, declive economico, escandalos de corrupcion y el surgimiento de alternativas de terceros partidos jugaron roles. La pregunta para 2024: se mantendran estos cambios, o el pendulo oscilara de vuelta?',
			step8Title: 'Quienes Realmente Cambiaron?',
			step8p1Start: 'El cambio es una cosa; realmente cambiar de un partido a otro es mas dramatico.',
			step8p1Mid: 'municipios cambiaron de manos entre 2016 y 2020, pasando de inclinarse al PNP a inclinarse al PPD o viceversa.',
			step8p2Start: 'Cambios notables incluyen',
			step8p2Isabela: 'Isabela',
			step8p2IsabelaSwing: '(PNP +2 a PPD +14),',
			step8p2Barceloneta: 'Barceloneta',
			step8p2BarcelonetaSwing: '(PNP +0.3 a PPD +8), y',
			step8p2Aguadilla: 'Aguadilla',
			step8p2AguadillaSwing: '(PNP +14 a empate). Estos no fueron cambios marginales-representan reversiones completas de identidad politica.',
			step8p3: 'Los municipios que cambiaron son los canarios en la mina de carbon. Señalan donde esta ocurriendo el realineamiento y frecuentemente predicen tendencias mas amplias. Observa estos pueblos de cerca en 2024.',
			step9Title: 'Mas Alla del Binomio: Carreras a Tres Bandas',
			step9p1Start: 'El analisis tradicional de cambio asume un sistema bipartidista: los votos se mueven entre PNP y PPD. Pero 2020 rompio ese modelo. Los terceros partidos-particularmente',
			step9p1MVC: 'MVC',
			step9p1And: 'y',
			step9p1PD: 'Proyecto Dignidad',
			step9p1End: '-capturaron porciones significativas de votos, especialmente entre votantes jovenes.',
			step9p2: 'Esto crea una nueva dimension de \"cambio\". Un municipio ahora puede cambiar en multiples direcciones: PNP<->PPD (cambio tradicional), partido mayor<->tercer partido (cambio de protesta), o incluso entre terceros partidos (clasificacion ideologica). Los mapas viejos no capturan esta complejidad.',
			step9p3: 'En 2024, los estrategas deben preguntar no solo \"este municipio cambiara?\" sino \"hacia quien?\" Un votante frustrado del PNP podria ir al PPD, MVC, PD o quedarse en casa. Entender estos flujos es la nueva frontera del analisis electoral puertorriqueño.',
			step10Title: 'El Campo de Batalla 2024',
			step10p1: 'Mirando hacia 2024, el mapa de batalla ha cambiado. Los municipios del oeste que oscilaron fuertemente hacia el PPD en 2020 ahora pueden ser bastiones del PPD-o pueden oscilar de vuelta si las condiciones cambian. El area metropolitana de San Juan, con su mezcla de suburbios competitivos, sigue siendo el teatro decisivo.',
			step10p2Start: 'Municipios clave a observar:',
			step10p2Carolina: 'Carolina',
			step10p2CarolinaNote: '(el reñido mas grande),',
			step10p2Caguas: 'Caguas',
			step10p2CaguasNote: '(indicador de la montaña central),',
			step10p2Bayamon: 'Bayamon',
			step10p2BayamonNote: '(suburbio competitivo), y',
			step10p2Ponce: 'Ponce',
			step10p2PonceNote: '(ancla sureña). Quien gane tres de estos cuatro probablemente gana la gobernacion.',
			step10p3: 'La pregunta fundamental: fue 2020 una eleccion de realineamiento que remodelo la geografia politica de Puerto Rico, o una eleccion de ola que retrocedera? Los municipios campo de batalla nos daran la respuesta.',
			// Conclusion
			conclusionTitle: 'El Mapa Estrategico',
			conclusionP1: 'Los 78 municipios de Puerto Rico cada uno cuenta una historia politica. Algunos son bastiones confiables, entregando margenes predecibles eleccion tras eleccion. Otros son pueblos volatiles donde las campanas se ganan y pierden en los dias finales. Esta geografia importa a cualquiera que quiera predecir-o influenciar-las elecciones puertorriqueñas.',
			conclusionP2: 'Pero el analisis a nivel municipal solo llega hasta cierto punto. Dentro de municipios grandes, los precintos individuales pueden variar por 30 o mas puntos porcentuales. El proximo capitulo va mas profundo, explorando los patrones a nivel de precinto que revelan el verdadero tejido electoral de Puerto Rico.',
			keyStatsTitle: 'Estadisticas Clave',
			municipalitiesFlipped: 'Municipios que Cambiaron',
			swungOver10: 'Oscilaron >10pp',
			tossupsIn2020: 'Reñidos en 2020',
			averageSwing: 'Cambio Promedio (hacia PPD)',
			// Sources
			sources: 'Fuentes',
			source1: 'Resultados de gobernador a nivel municipal 2016, 2020, 2024',
			source2: 'Estimaciones de poblacion por municipio',
			source3: 'Indicadores demograficos y economicos por region',
			source4: 'Metodologia de analisis: Cambio calculado como diferencia en margen de victoria entre elecciones',
			// Navigation
			previous: 'Anterior',
			nextChapter: 'Proximo Capitulo',
			prevTitle: 'La Fortaleza',
			nextTitle: 'Hasta el Precinto'
		}
	};

	// Reactive content based on language
	let content = $derived(t[$language]);
	let chapterTitle = $derived(content.chapterTitle);

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
		'San Juan': 342259, 'Bayamon': 169269, 'Carolina': 146984, 'Ponce': 132502,
		'Caguas': 124606, 'Guaynabo': 83728, 'Arecibo': 82880, 'Mayaguez': 71083,
		'Toa Baja': 68767, 'Trujillo Alto': 62852, 'Aguadilla': 53298, 'Vega Baja': 51876,
		'Humacao': 51675, 'Toa Alta': 50142, 'Fajardo': 48892, 'Canovanas': 47304,
		'Yauco': 45105, 'Guayama': 41706, 'Cayey': 44530, 'Rio Grande': 46274,
		'Isabela': 40423, 'Manati': 38570, 'Dorado': 36141, 'Hatillo': 37610,
		'Cabo Rojo': 46538, 'Juncos': 39128, 'Vega Alta': 37005, 'Coamo': 37597,
		'San Sebastian': 36853, 'Salinas': 26510, 'Las Piedras': 36113, 'Cidra': 39675,
		'Gurabo': 38477, 'Camuy': 31463, 'Yabucoa': 30426, 'Aguada': 37516,
		'San Lorenzo': 35961, 'Aibonito': 23457, 'Naguabo': 26584, 'Guanica': 14740,
		'Corozal': 33894, 'Naranjito': 28557, 'Patillas': 16962, 'Loiza': 24553,
		'Barranquitas': 27725, 'Maunabo': 10699, 'Anasco': 24853, 'Juana Diaz': 43982,
		'Villalba': 21651, 'Ciales': 15828, 'Quebradillas': 22643, 'Moca': 35343,
		'Arroyo': 16888, 'Santa Isabel': 21245, 'Hormigueros': 14858, 'Orocovis': 19696,
		'San German': 30227, 'Utuado': 26778, 'Florida': 11317, 'Barceloneta': 21809,
		'Morovis': 29509, 'Penuelas': 19178, 'Aguas Buenas': 25648, 'Jayuya': 14043,
		'Ceiba': 11307, 'Lajas': 22659, 'Lares': 24927, 'Rincon': 13897,
		'Luquillo': 17665, 'Adjuntas': 17269, 'Vieques': 8249, 'Guayanilla': 17623,
		'Las Marias': 8347, 'Catano': 22066, 'Culebra': 1818, 'Maricao': 5361,
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
				mapTitle = content.understandingSwing;
				break;
			case 2: // Show full swing map
				activeViz = 'swingMap';
				mapData = new Map(Object.entries(swingData));
				mapTitle = `${content.pnpSwing}: ${yearsCompared[0]} -> ${yearsCompared[1]}`;
				break;
			case 3: // Western shift
				activeViz = 'swingMap';
				mapData = new Map(Object.entries(swingData));
				mapTitle = content.westernShift;
				break;
			case 4: // Competitiveness classification
				activeViz = 'competitivenessMap';
				mapData = new Map(Object.entries(getCompetitivenessData()));
				mapTitle = content.competitiveness2020;
				break;
			case 5: // The deciders
				activeViz = 'scatter';
				mapTitle = content.decidersSizeCompetitiveness;
				break;
			case 6: // Scatter intro
				activeViz = 'scatter';
				mapTitle = content.electoralWeightAnalysis;
				break;
			case 7: // Top swing bar
				activeViz = 'bar';
				mapTitle = content.biggestSwings;
				break;
			case 8: // Flipped municipalities
				activeViz = 'historicalBar';
				mapTitle = content.whoFlipped;
				break;
			case 9: // Third party dimension
				activeViz = 'competitivenessMap';
				mapData = new Map(Object.entries(getCompetitivenessData()));
				mapTitle = content.threeWayRace;
				break;
			case 10: // Conclusion
				activeViz = 'swingMap';
				mapData = new Map(Object.entries(swingData));
				mapTitle = content.battlefield2024;
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
				{:else if activeViz === 'swingMap'}
					<h3 class="viz-title">{mapTitle}</h3>
					<ChoroplethMap
						data={mapData}
						colorScale={swingColorScale}
						tooltipFormat={(name, value) =>
							value !== undefined
								? `${name}: ${value > 0 ? '+' : ''}${value.toFixed(1)}pp ${content.swingTooltip}`
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
								<span>{content.ppdPlus12}</span>
								<span>{content.noChange}</span>
								<span>{content.pnpPlus12}</span>
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
								? `${name}: ${value.toFixed(1)}% ${content.marginTooltip} (${value < 5 ? content.tossup : value < 10 ? content.lean : content.safe})`
								: name
						}
					/>
					<div class="legend">
						<Legend
							items={[
								{ label: content.tossupLegend, color: '#c41e3a' },
								{ label: content.leanLegend, color: '#e8a87c' },
								{ label: content.safeLegend, color: '#f7f7f7' }
							]}
							title={content.competitiveness}
						/>
					</div>
				{:else if activeViz === 'scatter'}
					<h3 class="viz-title">{mapTitle}</h3>
					<ScatterPlot
						data={scatterData()}
						width={450}
						height={350}
						xLabel={content.populationThousands}
						yLabel={content.marginOfVictory}
						xFormat={(v) => v.toFixed(0) + 'K'}
						yFormat={(v) => v.toFixed(1) + '%'}
						showRegression={true}
					/>
					<p class="viz-note">{content.bubbleNote}</p>
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
			<h3>{content.step0Title}</h3>
			<p>
				{content.step0p1}
				<span class="highlight">{content.step0p1Highlight}</span>
				{content.step0p1End}
			</p>
			<p>{content.step0p2}</p>
			<p>{content.step0p3}</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>{content.step1Title}</h3>
			<p>
				{content.step1p1}
				<span class="highlight">{content.step1p1Highlight}</span>{content.step1p1End}
			</p>
			<p>{content.step1p2}</p>
			<p>{content.step1p3}</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>{content.step2Title} {yearsCompared[0]}-{yearsCompared[1]}</h3>
			<p>
				{content.step2p1Start} {yearsCompared[0]}
				{content.step2p1And} {yearsCompared[1]}. <span style="color: {PARTY_COLORS.PNP}">{content.step2p1Blue}</span> {content.step2p1Indicates}
				<span style="color: {PARTY_COLORS.PPD}">{content.step2p1Red}</span> {content.step2p1Shows}
			</p>
			<p>
				{#if stats()}
					{content.step2p2Start} <span class="stat">{stats().bigSwings}</span>
					{content.step2p2Mid} <span class="stat">{formatPercentChange(stats().avgSwing)}</span>
					{content.step2p2End}
				{/if}
			</p>
			<p>
				{content.step2p3Start} <span class="stat">{stats()?.flipped || 0}</span>
				{content.step2p3Mid}
			</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>{content.step3Title}</h3>
			<p>
				{content.step3p1}
				<span class="highlight">{content.step3p1Lares}</span>, <span class="highlight">{content.step3p1Isabela}</span>,
				{content.and} <span class="highlight">{content.step3p1Aguadilla}</span>
				{content.step3p1End}
			</p>
			<p>{content.step3p2}</p>
			<p>{content.step3p3}</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>{content.step4Title}</h3>
			<p>
				{content.step4p1Start}
				<span style="color: #c41e3a">{content.step4Tossup}</span> {content.step4TossupRange}
				<span style="color: #e8a87c">{content.step4Lean}</span> {content.step4LeanRange}
				{content.and} <span style="color: #f7f7f7">{content.step4Safe}</span> {content.step4SafeRange}
			</p>
			<p>
				{#if stats()}
					{content.step4p2Start} <span class="stat">{stats().tossups}</span> {content.step4p2Tossups}
					<span class="stat">{stats().lean}</span> {content.step4p2Lean} <span class="stat">{stats().safe}</span>
					{content.step4p2Safe} <span class="stat">{stats().pnpWins}</span>
					{content.step4p2Outright} <span class="stat">{stats().ppdWins}</span>.
				{/if}
			</p>
			<p>
				{content.step4p3Start} <span class="highlight">{content.step4p3Juncos}</span>,
				<span class="highlight">{content.step4p3Coamo}</span>, {content.and} <span class="highlight">{content.step4p3VegaAlta}</span>{content.step4p3End}
			</p>
		</Step>

		<Step active={currentStep === 5} index={5} variant="callout">
			<h3>{content.step5Title}</h3>
			<p>
				{content.step5p1}
				<span class="highlight">{content.step5p1Large}</span>
				{content.step5p1And}
				<span class="highlight">{content.step5p1Competitive}</span>.
			</p>
			<p>
				{#if deciderMunis.length > 0}
					<span class="stat">{deciderMunis.length}</span> {content.step5p2Start}
					{deciderMunis.slice(0, 5).join(', ')}{deciderMunis.length > 5 ? '...' : ''}.
					{content.step5p2End}
				{/if}
			</p>
			<p>{content.step5p3}</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>{content.step6Title}</h3>
			<p>{content.step6p1}</p>
			<p>
				{content.step6p2Start} <span class="highlight">{content.step6p2Quadrant}</span> {content.step6p2Mid}
			</p>
			<p>{content.step6p3}</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>{content.step7Title}</h3>
			<p>
				{content.step7p1Start} <span style="color: {PARTY_COLORS.PPD}">{content.step7p1RedBars}</span>
				{content.step7p1ShowPPD} <span style="color: {PARTY_COLORS.PNP}">{content.step7p1BlueBars}</span> {content.step7p1ShowPNP}
			</p>
			<p>
				{content.step7p2Start} <span class="highlight">{content.step7p2Patillas}</span>
				{content.step7p2End}
			</p>
			<p>{content.step7p3}</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>{content.step8Title}</h3>
			<p>
				{content.step8p1Start}
				{#if flippedMunis.length > 0}
					<span class="stat">{flippedMunis.length}</span> {content.step8p1Mid}
				{/if}
			</p>
			<p>
				{content.step8p2Start} <span class="highlight">{content.step8p2Isabela}</span> {content.step8p2IsabelaSwing}
				<span class="highlight">{content.step8p2Barceloneta}</span> {content.step8p2BarcelonetaSwing}
				<span class="highlight">{content.step8p2Aguadilla}</span> {content.step8p2AguadillaSwing}
			</p>
			<p>{content.step8p3}</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>{content.step9Title}</h3>
			<p>
				{content.step9p1Start}
				<span style="color: {PARTY_COLORS.MVC}">{content.step9p1MVC}</span> {content.step9p1And}
				<span style="color: {PARTY_COLORS.PD}">{content.step9p1PD}</span>{content.step9p1End}
			</p>
			<p>{content.step9p2}</p>
			<p>{content.step9p3}</p>
		</Step>

		<Step active={currentStep === 10} index={10}>
			<h3>{content.step10Title}</h3>
			<p>{content.step10p1}</p>
			<p>
				{content.step10p2Start} <span class="highlight">{content.step10p2Carolina}</span> {content.step10p2CarolinaNote}
				<span class="highlight">{content.step10p2Caguas}</span> {content.step10p2CaguasNote}
				<span class="highlight">{content.step10p2Bayamon}</span> {content.step10p2BayamonNote}
				<span class="highlight">{content.step10p2Ponce}</span> {content.step10p2PonceNote}
			</p>
			<p>{content.step10p3}</p>
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
					<h3>{content.keyStatsTitle}: {yearsCompared[0]}-{yearsCompared[1]}</h3>
					<div class="stats-grid">
						<div class="stat-item">
							<span class="stat-value">{stats().flipped}</span>
							<span class="stat-label">{content.municipalitiesFlipped}</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{stats().bigSwings}</span>
							<span class="stat-label">{content.swungOver10}</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{stats().tossups}</span>
							<span class="stat-label">{content.tossupsIn2020}</span>
						</div>
						<div class="stat-item">
							<span class="stat-value">{formatPercentChange(stats().avgSwing)}</span>
							<span class="stat-label">{content.averageSwing}</span>
						</div>
					</div>
				</div>
			{/if}

			<div class="sources">
			<h3>{content.sources}</h3>
			<ul>
				<li><a href="https://ww2.ceepur.org/Home/EventosElectorales" target="_blank" rel="noopener">Comision Estatal de Elecciones de Puerto Rico (CEE)</a> - {content.source1}</li>
				<li><a href="https://www.census.gov/programs-surveys/popest.html" target="_blank" rel="noopener">U.S. Census Bureau</a> - {content.source2}</li>
				<li>Puerto Rico Planning Board - {content.source3}</li>
				<li>{content.source4}</li>
			</ul>
		</div>

		<nav class="chapter-nav">
				<a href="{base}/chapters/fortaleza" class="nav-link prev">
					<span class="nav-direction">{content.previous}</span>
					<span class="nav-title">{content.prevTitle}</span>
				</a>
				<a href="{base}/chapters/precincts" class="nav-link next">
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
