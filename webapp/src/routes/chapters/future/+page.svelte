<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { LineChart, BarChart } from '$lib/components/charts';
	import { CATEGORY_COLORS, PARTY_COLORS } from '$lib/utils/colors';
	import { language } from '$lib/stores/language';

	const chapterNum = 12;
	const totalSteps = 8;

	// Bilingual content
	const t = {
		en: {
			chapterTitle: "Puerto Rico's Electoral Future",
			chapter: 'Chapter',
			lead: "Throughout this series, we've examined Puerto Rico's electoral transformation: a shrinking population, an aging electorate, fragmenting parties, and declining engagement. Now we must ask: where does this lead?",
			loading: 'Loading data...',
			// Chart axis labels
			axisYear: 'Year',
			axisPopulation: 'Population',
			axisVoters: 'Voters',
			axisAge: 'Age',
			axisVoteShare: 'Vote Share',
			labelHistorical: 'Historical',
			labelProjected: 'Projected',
			labelRegisteredVoters: 'Registered Voters',
			labelActualVotes: 'Actual Votes',
			labelThirdParties: 'Third Parties',
			unitYears: 'years',
			unitMillion: 'million',
			// Viz titles and notes
			vizPopulationTrajectory: 'Population Trajectory',
			vizShrinkingElectorate: 'The Shrinking Electorate',
			vizMedianVoterAge: 'Median Voter Age',
			vizPartyVoteShare: 'Party Vote Share Evolution',
			vizScenarioProbability: 'Scenario Probability Assessment',
			vizNoteProjections: 'Dashed line indicates Census Bureau projections',
			vizNoteVoterGap: 'Gap between registered and actual voters widens',
			vizNoteAging: 'The electorate ages as young people leave',
			vizNoteThirdParties: 'Third parties have grown from 5% to 28% in 12 years',
			vizNoteScenario: 'Based on historical trends and expert assessment',
			// Step titles
			step0Title: 'The Demographic Trajectory',
			step1Title: 'The Invisible Emigration',
			step2Title: 'The Shrinking Voter Pool',
			step3Title: 'An Aging Electorate',
			step4Title: 'The Fragmenting Party System',
			step5Title: 'The Status Question Persists',
			step6Title: 'Four Scenarios for 2040',
			step7Title: 'Why This Data Matters',
			// Step 6 scenario labels
			step6Continuation: 'Continuation',
			step6Statehood: 'Statehood',
			step6AcceleratedDecline: 'Accelerated Decline',
			step6Probability: 'probability',
			// Step content
			step0p1: "Puerto Rico's population has declined by",
			step0p1b: "people since 2010, a loss of 16% in just fourteen years. This isn't natural decline but exodus: hurricanes, economic collapse, and austerity have driven a generation to seek opportunity on the mainland.",
			step0p2a: "Census projections suggest the island could fall below",
			step0p2b: "by 2040. Each departure removes not just a resident but a voter, a taxpayer, a voice in the democratic process. The feedback loop is vicious: fewer people means less federal funding, worse services, and more reasons to leave.",
			step0p3: "Compare this to Florida, which gained 2.7 million residents in the same period. Many of those new Floridians are former Puerto Ricans who can now vote for President for the first time.",
			step1p1: "The people who leave aren't random. They're disproportionately young, educated, and working-age. A 28-year-old engineer who moves to Texas takes their productivity, their tax payments, and their potential 40 years of civic participation with them.",
			step1p2: "Those who stay tend to be older, with deeper roots or fewer options. Retirees on fixed incomes, older homeowners who can't sell, public employees with pensions tied to the island. This isn't just population decline; it's selective depletion of the workforce and electorate.",
			step1p3: "The result is an accelerating age imbalance. Puerto Rico is becoming a retirement community without the tax base to support it.",
			step2p1a: "Registered voters have declined from",
			step2p1b: "in 2004 to",
			step2p1c: "in 2024, a loss of nearly half a million eligible voters. But the damage runs deeper: actual votes cast fell from 1.99 million to 1.22 million over the same period.",
			step2p2a: "By 2028, projections suggest Puerto Rico may have fewer than",
			step2p2b: "registered voters. By 2040, perhaps",
			step2p2c: "Elections that once mobilized two million people may see barely 800,000 ballots cast.",
			step2p3: "This isn't voter suppression in the traditional sense. It's demographic attrition combined with civic disengagement, a slow-motion erosion of democratic participation that no single policy can reverse.",
			step3p1a: "The median voter in Puerto Rico was 42 years old in 2012. Today, they're",
			step3p1b: "By 2032, projections suggest the median voter could be 56. In a single generation, Puerto Rico's electorate has aged by nearly 15 years.",
			step3p2: "Older electorates tend to favor stability, incremental change, and preservation of existing benefits. They're less likely to support systemic reform or accept short-term pain for long-term gain. Traditional parties often benefit from this dynamic.",
			step3p3: "But this aging also concentrates political power among those with the strongest ties to the status quo, potentially blocking the very changes needed to reverse the island's decline. The young people most invested in Puerto Rico's future increasingly vote with their feet.",
			step4p1: "For decades, Puerto Rican politics was a two-party affair. PNP and PPD together captured 95%+ of gubernatorial votes as recently as 2012. The status question dominated: statehood versus commonwealth, with independence a distant third.",
			step4p2a: "That duopoly is shattered. Third parties grew from",
			step4p2b: "in 2012 to",
			step4p2c: "in 2020. Even after partial consolidation in 2024, they held nearly 28% of the vote. Movimiento Victoria Ciudadana emerged from protests; Proyecto Dignidad represents conservative voters alienated by corruption scandals.",
			step4p3: "If current trends continue, 2028 could see a truly three-way race. No party would hold a mandate. Coalition governance or minority rule would become the norm, fundamentally changing how Puerto Rico is governed.",
			step5p1: "Puerto Rico has held multiple status referendums. In 2012, 61% voted for statehood, but turnout was limited. In 2017, 97% chose statehood, but only 23% participated due to boycotts. In 2020, 52.5% voted Yes on a simple statehood question with broader turnout.",
			step5p2: "Congress has not acted. The Puerto Rico Status Act passed the House in 2022 but died in the Senate. Another attempt in 2024 failed to advance. Meanwhile, the island remains in limbo: citizens but not voters, taxed but not represented, American but not quite.",
			step5p3: "With a shrinking, aging electorate, the mandate question becomes complex. Does 52% of a smaller turnout carry more or less weight than 48% of a larger one? How many people must vote for statehood before Congress acts? The status debate will outlive all of us.",
			step6p1: "Current trends persist. Population falls to 2.6 million, the electorate to 1.46 million. Third parties stabilize around 30%. Status remains unresolved. Puerto Rico muddles through, neither thriving nor collapsing.",
			step6p2: "Congress acts. Federal investment flows. Migration stabilizes or reverses. Puerto Rico gains 5 electoral votes and 4 House seats, more representation than several existing states combined. Turnout rebounds as citizenship gains meaning.",
			step6p3: "Climate disasters or economic shocks accelerate exodus. Population falls below 2 million by 2040. The electorate becomes geriatric. Infrastructure collapses. The island becomes economically unviable as an autonomous unit.",
			step7p1: "This isn't just about statistics. Behind every number is a family deciding whether to stay or go, a young person weighing their future, an elder watching their community empty out. Elections are how democracies make collective decisions. When the electorate shrinks, so does democratic capacity.",
			step7p2: "The data we've explored across these twelve chapters tells a story of transformation without resolution. Puerto Rico's political system is adapting to forces largely beyond its control: federal policy, global economics, climate change, and the accumulated weight of colonial status.",
			step7p3: "Understanding these patterns is the first step to shaping them.",
			step7p3highlight: "The future is not yet written.",
			step7p3b: "But it will be written by those who show up to vote, stay on the island, and engage with the political process. That's where you come in.",
			// Dashboard section
			numbersAtGlance: 'The Numbers at a Glance',
			populationChange: 'Population Change',
			registeredVoters: 'Registered Voters',
			turnoutChange: 'Turnout Change',
			thirdPartyGrowth: 'Third Party Growth',
			period2010_2024: '2010-2024',
			period2004_2024: '2004-2024',
			period2012_2024: '2012-2024',
			// Scenarios section
			scenariosTitle: 'Scenarios for Puerto Rico\'s Future',
			scenariosIntro: 'Based on demographic trends, political dynamics, and external factors, we can model four potential futures for Puerto Rico by 2040.',
			population: 'Population',
			voters: 'Voters',
			turnout: 'Turnout',
			keyAssumptions: 'Key Assumptions',
			// Statehood section
			whatIfStatehood: 'What If: Statehood',
			statehoodIntro: 'If Puerto Rico became the 51st state, it would immediately become a significant player in American politics.',
			electoralVotes: 'Electoral Votes',
			houseSeats: 'House Seats',
			senators: 'Senators',
			statehoodComparison: 'More than Wyoming, Vermont, Alaska, and DC combined',
			// Conclusion section
			thankYouTitle: 'Thank You for Reading',
			thankYouP1: 'This data journalism series was created using open data from the Puerto Rico State Elections Commission and the U.S. Census Bureau. All code, data, and methodology are available on GitHub for verification, reproduction, and extension.',
			thankYouP2: "Democracy depends on informed citizens. We hope these visualizations have illuminated patterns that matter for Puerto Rico's future, and inspired you to engage with your community's political process, wherever you live.",
			exploreData: 'Explore the Data',
			backToStart: 'Back to Start',
			completeSeries: 'The Complete Series',
			seriesChapter1: 'The Shrinking Electorate',
			seriesChapter2: 'The Exodus',
			seriesChapter3: 'Turnout Collapse',
			seriesChapter4: 'Geography of Power',
			seriesChapter5: 'La Fortaleza',
			seriesChapter6: '78 Battlegrounds',
			seriesChapter7: 'The Senate',
			seriesChapter8: '40 House Races',
			seriesChapter9: 'The Future (You Are Here)',
			sources: 'Sources',
			sourceCEE: 'Historical election data 2000-2024',
			sourceCensus: 'Population projections for Puerto Rico 2020-2050',
			sourceInstitute: 'Puerto Rico Institute of Statistics - Demographic trend analysis and forecasts',
			sourceCentro: 'Future of Puerto Rican politics research',
			sourceBrookings: 'Puerto Rico economic and political outlook',
			// Navigation
			previous: 'Previous',
			prevTitle: '40 House Races',
			returnTo: 'Return to',
			home: 'Home'
		},
		es: {
			chapterTitle: 'El Futuro Electoral de Puerto Rico',
			chapter: 'Capitulo',
			lead: 'A lo largo de esta serie, hemos examinado la transformacion electoral de Puerto Rico: una poblacion menguante, un electorado envejecido, partidos fragmentados y una participacion en declive. Ahora debemos preguntar: a donde lleva esto?',
			loading: 'Cargando datos...',
			// Chart axis labels
			axisYear: 'Ano',
			axisPopulation: 'Poblacion',
			axisVoters: 'Votantes',
			axisAge: 'Edad',
			axisVoteShare: 'Porcentaje del Voto',
			labelHistorical: 'Historico',
			labelProjected: 'Proyectado',
			labelRegisteredVoters: 'Votantes Registrados',
			labelActualVotes: 'Votos Reales',
			labelThirdParties: 'Terceros Partidos',
			unitYears: 'anos',
			unitMillion: 'millones',
			// Viz titles and notes
			vizPopulationTrajectory: 'Trayectoria Poblacional',
			vizShrinkingElectorate: 'El Electorado Menguante',
			vizMedianVoterAge: 'Edad Mediana del Votante',
			vizPartyVoteShare: 'Evolucion del Voto por Partido',
			vizScenarioProbability: 'Evaluacion de Probabilidad de Escenarios',
			vizNoteProjections: 'La linea punteada indica proyecciones de la Oficina del Censo',
			vizNoteVoterGap: 'La brecha entre votantes registrados y votos reales se amplia',
			vizNoteAging: 'El electorado envejece mientras los jovenes se van',
			vizNoteThirdParties: 'Los terceros partidos han crecido del 5% al 28% en 12 anos',
			vizNoteScenario: 'Basado en tendencias historicas y evaluacion experta',
			// Step titles
			step0Title: 'La Trayectoria Demografica',
			step1Title: 'La Emigracion Invisible',
			step2Title: 'El Grupo de Votantes Menguante',
			step3Title: 'Un Electorado Envejecido',
			step4Title: 'El Sistema de Partidos se Fragmenta',
			step5Title: 'La Pregunta del Estatus Persiste',
			step6Title: 'Cuatro Escenarios para 2040',
			step7Title: 'Por Que Importan Estos Datos',
			// Step 6 scenario labels
			step6Continuation: 'Continuacion',
			step6Statehood: 'Estadidad',
			step6AcceleratedDecline: 'Declive Acelerado',
			step6Probability: 'probabilidad',
			// Step content
			step0p1: 'La poblacion de Puerto Rico ha declinado en',
			step0p1b: 'personas desde 2010, una perdida del 16% en solo catorce anos. Esto no es declive natural sino exodo: huracanes, colapso economico y austeridad han impulsado a una generacion a buscar oportunidades en el continente.',
			step0p2a: 'Las proyecciones del Censo sugieren que la isla podria caer por debajo de',
			step0p2b: 'para 2040. Cada partida remueve no solo un residente sino un votante, un contribuyente, una voz en el proceso democratico. El ciclo es vicioso: menos personas significa menos fondos federales, peores servicios y mas razones para irse.',
			step0p3: 'Compara esto con Florida, que gano 2.7 millones de residentes en el mismo periodo. Muchos de esos nuevos floridanos son ex puertorriquenos que ahora pueden votar por Presidente por primera vez.',
			step1p1: 'Las personas que se van no son aleatorias. Son desproporcionadamente jovenes, educadas y en edad laboral. Un ingeniero de 28 anos que se muda a Texas se lleva su productividad, sus pagos de impuestos y sus potenciales 40 anos de participacion civica.',
			step1p2: 'Los que se quedan tienden a ser mayores, con raices mas profundas o menos opciones. Jubilados con ingresos fijos, propietarios mayores que no pueden vender, empleados publicos con pensiones atadas a la isla. Esto no es solo declive poblacional; es agotamiento selectivo de la fuerza laboral y el electorado.',
			step1p3: 'El resultado es un desequilibrio de edad acelerado. Puerto Rico se esta convirtiendo en una comunidad de retiro sin la base tributaria para sostenerla.',
			step2p1a: 'Los votantes registrados han declinado de',
			step2p1b: 'en 2004 a',
			step2p1c: 'en 2024, una perdida de casi medio millon de votantes elegibles. Pero el dano es mas profundo: los votos reales emitidos cayeron de 1.99 millones a 1.22 millones en el mismo periodo.',
			step2p2a: 'Para 2028, las proyecciones sugieren que Puerto Rico podria tener menos de',
			step2p2b: 'votantes registrados. Para 2040, quizas',
			step2p2c: 'Elecciones que una vez movilizaron a dos millones de personas podrian ver apenas 800,000 papeletas emitidas.',
			step2p3: 'Esto no es supresion de votantes en el sentido tradicional. Es desgaste demografico combinado con desapego civico, una erosion en camara lenta de la participacion democratica que ninguna politica individual puede revertir.',
			step3p1a: 'El votante mediano en Puerto Rico tenia 42 anos en 2012. Hoy, tiene',
			step3p1b: 'Para 2032, las proyecciones sugieren que el votante mediano podria tener 56. En una sola generacion, el electorado de Puerto Rico ha envejecido casi 15 anos.',
			step3p2: 'Los electorados mayores tienden a favorecer la estabilidad, el cambio incremental y la preservacion de beneficios existentes. Es menos probable que apoyen reformas sistemicas o acepten dolor a corto plazo para ganancia a largo plazo. Los partidos tradicionales a menudo se benefician de esta dinamica.',
			step3p3: 'Pero este envejecimiento tambien concentra el poder politico entre aquellos con los lazos mas fuertes al status quo, potencialmente bloqueando los cambios necesarios para revertir el declive de la isla. Los jovenes mas invertidos en el futuro de Puerto Rico cada vez mas votan con los pies.',
			step4p1: 'Durante decadas, la politica puertorriquena fue un asunto bipartidista. PNP y PPD juntos capturaron mas del 95% de los votos para gobernador tan recientemente como 2012. La pregunta del estatus dominaba: estadidad versus estado libre asociado, con la independencia un distante tercero.',
			step4p2a: 'Ese duopolio se ha roto. Los terceros partidos crecieron del',
			step4p2b: 'en 2012 al',
			step4p2c: 'en 2020. Incluso despues de una consolidacion parcial en 2024, mantuvieron casi el 28% del voto. El Movimiento Victoria Ciudadana surgio de las protestas; Proyecto Dignidad representa a votantes conservadores alienados por escandalos de corrupcion.',
			step4p3: 'Si las tendencias actuales continuan, 2028 podria ver una verdadera carrera a tres bandas. Ningun partido tendria un mandato. La gobernanza de coalicion o el gobierno minoritario se convertirian en la norma, cambiando fundamentalmente como se gobierna Puerto Rico.',
			step5p1: 'Puerto Rico ha celebrado multiples referendums de estatus. En 2012, el 61% voto por la estadidad, pero la participacion fue limitada. En 2017, el 97% eligio estadidad, pero solo el 23% participo debido a boicots. En 2020, el 52.5% voto Si en una simple pregunta de estadidad con mayor participacion.',
			step5p2: 'El Congreso no ha actuado. La Ley de Estatus de Puerto Rico paso la Camara en 2022 pero murio en el Senado. Otro intento en 2024 no avanzo. Mientras tanto, la isla permanece en el limbo: ciudadanos pero no votantes, contribuyentes pero no representados, americanos pero no del todo.',
			step5p3: 'Con un electorado menguante y envejecido, la pregunta del mandato se vuelve compleja. El 52% de una participacion menor tiene mas o menos peso que el 48% de una mayor? Cuantas personas deben votar por la estadidad antes de que el Congreso actue? El debate del estatus nos sobrevivira a todos.',
			step6p1: 'Las tendencias actuales persisten. La poblacion cae a 2.6 millones, el electorado a 1.46 millones. Los terceros partidos se estabilizan alrededor del 30%. El estatus permanece sin resolver. Puerto Rico sigue adelante, sin prosperar ni colapsar.',
			step6p2: 'El Congreso actua. La inversion federal fluye. La migracion se estabiliza o se revierte. Puerto Rico gana 5 votos electorales y 4 escanos en la Camara, mas representacion que varios estados existentes combinados. La participacion rebota cuando la ciudadania gana significado.',
			step6p3: 'Desastres climaticos o choques economicos aceleran el exodo. La poblacion cae por debajo de 2 millones para 2040. El electorado se vuelve geriatrico. La infraestructura colapsa. La isla se vuelve economicamente inviable como unidad autonoma.',
			step7p1: 'Esto no se trata solo de estadisticas. Detras de cada numero hay una familia decidiendo si quedarse o irse, un joven sopesando su futuro, un mayor viendo su comunidad vaciarse. Las elecciones son como las democracias toman decisiones colectivas. Cuando el electorado se reduce, tambien lo hace la capacidad democratica.',
			step7p2: 'Los datos que hemos explorado a lo largo de estos doce capitulos cuentan una historia de transformacion sin resolucion. El sistema politico de Puerto Rico se esta adaptando a fuerzas en gran parte fuera de su control: politica federal, economia global, cambio climatico y el peso acumulado del estatus colonial.',
			step7p3: 'Entender estos patrones es el primer paso para darles forma.',
			step7p3highlight: 'El futuro aun no esta escrito.',
			step7p3b: 'Pero sera escrito por aquellos que se presenten a votar, se queden en la isla y participen en el proceso politico. Ahi es donde entras tu.',
			// Dashboard section
			numbersAtGlance: 'Los Numeros de un Vistazo',
			populationChange: 'Cambio Poblacional',
			registeredVoters: 'Votantes Registrados',
			turnoutChange: 'Cambio en Participacion',
			thirdPartyGrowth: 'Crecimiento de Terceros Partidos',
			period2010_2024: '2010-2024',
			period2004_2024: '2004-2024',
			period2012_2024: '2012-2024',
			// Scenarios section
			scenariosTitle: 'Escenarios para el Futuro de Puerto Rico',
			scenariosIntro: 'Basado en tendencias demograficas, dinamicas politicas y factores externos, podemos modelar cuatro futuros potenciales para Puerto Rico para 2040.',
			population: 'Poblacion',
			voters: 'Votantes',
			turnout: 'Participacion',
			keyAssumptions: 'Supuestos Clave',
			// Statehood section
			whatIfStatehood: 'Y Si: Estadidad',
			statehoodIntro: 'Si Puerto Rico se convirtiera en el estado 51, inmediatamente se convertiria en un jugador significativo en la politica estadounidense.',
			electoralVotes: 'Votos Electorales',
			houseSeats: 'Escanos en la Camara',
			senators: 'Senadores',
			statehoodComparison: 'Mas que Wyoming, Vermont, Alaska y DC combinados',
			// Conclusion section
			thankYouTitle: 'Gracias por Leer',
			thankYouP1: 'Esta serie de periodismo de datos fue creada usando datos abiertos de la Comision Estatal de Elecciones de Puerto Rico y la Oficina del Censo de EE.UU. Todo el codigo, datos y metodologia estan disponibles en GitHub para verificacion, reproduccion y extension.',
			thankYouP2: 'La democracia depende de ciudadanos informados. Esperamos que estas visualizaciones hayan iluminado patrones que importan para el futuro de Puerto Rico, y te hayan inspirado a participar en el proceso politico de tu comunidad, donde sea que vivas.',
			exploreData: 'Explora los Datos',
			backToStart: 'Volver al Inicio',
			completeSeries: 'La Serie Completa',
			seriesChapter1: 'El Electorado Menguante',
			seriesChapter2: 'El Exodo',
			seriesChapter3: 'Colapso de Participacion',
			seriesChapter4: 'Geografia del Poder',
			seriesChapter5: 'La Fortaleza',
			seriesChapter6: '78 Campos de Batalla',
			seriesChapter7: 'El Senado',
			seriesChapter8: '40 Carreras a la Camara',
			seriesChapter9: 'El Futuro (Estas Aqui)',
			sources: 'Fuentes',
			sourceCEE: 'Datos electorales historicos 2000-2024',
			sourceCensus: 'Proyecciones de poblacion para Puerto Rico 2020-2050',
			sourceInstitute: 'Instituto de Estadisticas de Puerto Rico - Analisis de tendencias demograficas y pronosticos',
			sourceCentro: 'Investigacion sobre el futuro de la politica puertorriquena',
			sourceBrookings: 'Perspectiva economica y politica de Puerto Rico',
			// Navigation
			previous: 'Anterior',
			prevTitle: '40 Carreras a la Camara',
			returnTo: 'Volver a',
			home: 'Inicio'
		}
	};

	// Reactive content based on language
	let content = $derived(t[$language]);
	let chapterTitle = $derived(content.chapterTitle);

	let currentStep = $state(0);
	let loading = $state(true);
	let activeViz = $state<'population' | 'electorate' | 'parties' | 'age' | 'scenarios'>('population');
	let selectedScenario = $state<string | null>(null);

	// Data structures
	interface PopulationPoint {
		year: number;
		population: number;
		low?: number;
		high?: number;
	}

	interface ElectoratePoint {
		year: number;
		registered_voters: number;
		turnout_pct: number;
		votes_cast: number;
	}

	interface PartySharePoint {
		year: number;
		pnp: number;
		ppd: number;
		third_parties: number;
	}

	interface Scenario {
		name: string;
		probability: number;
		description: string;
		population_2040: number;
		voters_2040: number;
		turnout_2040: number;
		third_party_share: number;
		key_assumptions: string[];
	}

	let populationHistorical = $state<PopulationPoint[]>([]);
	let populationProjected = $state<PopulationPoint[]>([]);
	let electorateHistorical = $state<ElectoratePoint[]>([]);
	let electorateProjected = $state<ElectoratePoint[]>([]);
	let partyShareHistorical = $state<PartySharePoint[]>([]);
	let scenarios = $state<Record<string, Scenario>>({});
	let keyMetrics = $state<Record<string, number>>({});
	let medianVoterAge = $state<Array<{year: number; age: number; projected?: boolean}>>([]);
	let whatIfStatehood = $state<Record<string, any>>({});

	// Load data
	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/chapters/future.json`);
			const data = await response.json();

			populationHistorical = data.population_projection.historical || [];
			populationProjected = data.population_projection.projected || [];
			electorateHistorical = data.electorate_projection.historical || [];
			electorateProjected = data.electorate_projection.projected || [];
			partyShareHistorical = data.party_vote_share_trend.historical || [];
			scenarios = data.scenarios || {};
			keyMetrics = data.key_metrics_summary || {};
			medianVoterAge = data.demographic_shift.median_voter_age || [];
			whatIfStatehood = data.what_if_statehood || {};
		} catch (err) {
			console.error('Failed to load future data:', err);
		} finally {
			loading = false;
		}
	});

	// Chart labels based on language (using content object)
	let historicalLabel = $derived(content.labelHistorical);
	let projectedLabel = $derived(content.labelProjected);
	let registeredLabel = $derived(content.labelRegisteredVoters);
	let actualVotesLabel = $derived(content.labelActualVotes);
	let thirdPartiesLabel = $derived(content.labelThirdParties);

	// Derived data for population chart with projection band
	let populationSeries = $derived(() => {
		const historicalData = populationHistorical.map(p => ({ x: p.year, y: p.population }));
		const projectedData = populationProjected.map(p => ({ x: p.year, y: p.population }));

		return [
			{ id: 'historical', label: historicalLabel, color: CATEGORY_COLORS[0], data: historicalData },
			{ id: 'projected', label: projectedLabel, color: CATEGORY_COLORS[1], data: projectedData },
		];
	});

	// Derived data for electorate chart
	let electorateSeries = $derived(() => {
		const historicalVoters = electorateHistorical.map(e => ({ x: e.year, y: e.registered_voters }));
		const projectedVoters = electorateProjected.map(e => ({ x: e.year, y: e.registered_voters }));
		const historicalVotes = electorateHistorical.map(e => ({ x: e.year, y: e.votes_cast }));
		const projectedVotes = electorateProjected.map(e => ({ x: e.year, y: e.votes_cast }));

		return [
			{ id: 'registered', label: registeredLabel, color: CATEGORY_COLORS[0], data: [...historicalVoters, ...projectedVoters] },
			{ id: 'actual', label: actualVotesLabel, color: CATEGORY_COLORS[3], data: [...historicalVotes, ...projectedVotes] },
		];
	});

	// Derived data for party share trends
	let partySeries = $derived(() => {
		const pnpData = partyShareHistorical.map(p => ({ x: p.year, y: p.pnp }));
		const ppdData = partyShareHistorical.map(p => ({ x: p.year, y: p.ppd }));
		const thirdData = partyShareHistorical.map(p => ({ x: p.year, y: p.third_parties }));

		return [
			{ id: 'pnp', label: 'PNP', color: PARTY_COLORS.PNP, data: pnpData },
			{ id: 'ppd', label: 'PPD', color: PARTY_COLORS.PPD, data: ppdData },
			{ id: 'third', label: thirdPartiesLabel, color: PARTY_COLORS.MVC, data: thirdData },
		];
	});

	// Derived data for median age trend
	let ageSeries = $derived(() => {
		const historical = medianVoterAge.filter(a => !a.projected).map(a => ({ x: a.year, y: a.age }));
		const projected = medianVoterAge.filter(a => a.projected).map(a => ({ x: a.year, y: a.age }));

		// Connect historical to projected
		if (historical.length > 0 && projected.length > 0) {
			projected.unshift(historical[historical.length - 1]);
		}

		return [
			{ id: 'historical', label: historicalLabel, color: CATEGORY_COLORS[0], data: historical },
			{ id: 'projected', label: projectedLabel, color: CATEGORY_COLORS[1], data: projected },
		];
	});

	// Scenario bar data
	let scenarioBarData = $derived(() => {
		return Object.entries(scenarios).map(([key, s]) => ({
			label: s.name,
			value: s.probability,
			color: key === 'status_quo' ? CATEGORY_COLORS[0] :
			       key === 'statehood' ? CATEGORY_COLORS[2] :
			       key === 'independence' ? CATEGORY_COLORS[4] : CATEGORY_COLORS[3]
		}));
	});

	function handleStepEnter(response: { index: number }) {
		currentStep = response.index;

		// Map steps to visualizations
		if (response.index <= 1) {
			activeViz = 'population';
		} else if (response.index === 2) {
			activeViz = 'electorate';
		} else if (response.index === 3) {
			activeViz = 'age';
		} else if (response.index === 4) {
			activeViz = 'parties';
		} else {
			activeViz = 'scenarios';
		}
	}

	function formatPopulation(v: number): string {
		return `${(v / 1000000).toFixed(2)}M`;
	}

	function formatVoters(v: number): string {
		return `${(v / 1000000).toFixed(2)}M`;
	}

	function formatPercent(v: number): string {
		return `${v.toFixed(0)}%`;
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
				{:else if activeViz === 'population'}
					<h3 class="viz-title">{content.vizPopulationTrajectory}</h3>
					<LineChart
						series={populationSeries()}
						width={500}
						height={340}
						xLabel={content.axisYear}
						yLabel={content.axisPopulation}
						xFormat={(v) => String(v)}
						yFormat={formatPopulation}
						showArea={true}
					/>
					<p class="viz-note">{content.vizNoteProjections}</p>
				{:else if activeViz === 'electorate'}
					<h3 class="viz-title">{content.vizShrinkingElectorate}</h3>
					<LineChart
						series={electorateSeries()}
						width={500}
						height={340}
						xLabel={content.axisYear}
						yLabel={content.axisVoters}
						xFormat={(v) => String(v)}
						yFormat={formatVoters}
						showArea={false}
					/>
					<p class="viz-note">{content.vizNoteVoterGap}</p>
				{:else if activeViz === 'age'}
					<h3 class="viz-title">{content.vizMedianVoterAge}</h3>
					<LineChart
						series={ageSeries()}
						width={500}
						height={340}
						xLabel={content.axisYear}
						yLabel={content.axisAge}
						xFormat={(v) => String(v)}
						yFormat={(v) => `${v} ${content.unitYears}`}
						showArea={false}
					/>
					<p class="viz-note">{content.vizNoteAging}</p>
				{:else if activeViz === 'parties'}
					<h3 class="viz-title">{content.vizPartyVoteShare}</h3>
					<LineChart
						series={partySeries()}
						width={500}
						height={340}
						xLabel={content.axisYear}
						yLabel={content.axisVoteShare}
						xFormat={(v) => String(v)}
						yFormat={formatPercent}
						showArea={false}
					/>
					<p class="viz-note">{content.vizNoteThirdParties}</p>
				{:else if activeViz === 'scenarios'}
					<h3 class="viz-title">{content.vizScenarioProbability}</h3>
					<BarChart
						data={scenarioBarData()}
						width={480}
						height={280}
						horizontal={true}
						valueFormat={(v) => `${v}%`}
					/>
					<p class="viz-note">{content.vizNoteScenario}</p>
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>{content.step0Title}</h3>
			<p>
				{content.step0p1} <span class="stat">600,000</span> {content.step0p1b}
			</p>
			<p>
				{content.step0p2a} <span class="stat">2.6 {content.unitMillion}</span>
				{content.step0p2b}
			</p>
			<p>{content.step0p3}</p>
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
				{content.step2p1a} <span class="stat">2.44 {content.unitMillion}</span>
				{content.step2p1b} <span class="stat">1.99 {content.unitMillion}</span>
				{content.step2p1c}
			</p>
			<p>
				{content.step2p2a} <span class="stat">1.85 {content.unitMillion}</span>
				{content.step2p2b} <span class="stat">1.46 {content.unitMillion}</span>.
				{content.step2p2c}
			</p>
			<p>{content.step2p3}</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>{content.step3Title}</h3>
			<p>
				{content.step3p1a} <span class="stat">51</span>. {content.step3p1b}
			</p>
			<p>{content.step3p2}</p>
			<p>{content.step3p3}</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>{content.step4Title}</h3>
			<p>{content.step4p1}</p>
			<p>
				{content.step4p2a} <span class="stat">4.7%</span>
				{content.step4p2b} <span class="stat">35%</span> {content.step4p2c}
			</p>
			<p>{content.step4p3}</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>{content.step5Title}</h3>
			<p>{content.step5p1}</p>
			<p>{content.step5p2}</p>
			<p>{content.step5p3}</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>{content.step6Title}</h3>
			<p><strong>{content.step6Continuation} (60% {content.step6Probability}):</strong> {content.step6p1}</p>
			<p><strong>{content.step6Statehood} (15%):</strong> {content.step6p2}</p>
			<p><strong>{content.step6AcceleratedDecline} (20%):</strong> {content.step6p3}</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>{content.step7Title}</h3>
			<p>{content.step7p1}</p>
			<p>{content.step7p2}</p>
			<p>
				{content.step7p3}
				<span class="highlight">{content.step7p3highlight}</span> {content.step7p3b}
			</p>
		</Step>
	</ScrollySection>

	<!-- Key Metrics Dashboard -->
	<section class="dashboard-section">
		<div class="container">
			<h2>{content.numbersAtGlance}</h2>
			<div class="metrics-dashboard">
				<div class="metric-card">
					<span class="metric-value">{keyMetrics.population_change_2010_2024?.toFixed(1) || '-14.0'}%</span>
					<span class="metric-label">{content.populationChange}<br/>{content.period2010_2024}</span>
				</div>
				<div class="metric-card">
					<span class="metric-value">{keyMetrics.voter_change_2004_2024?.toFixed(1) || '-18.6'}%</span>
					<span class="metric-label">{content.registeredVoters}<br/>{content.period2004_2024}</span>
				</div>
				<div class="metric-card">
					<span class="metric-value">{keyMetrics.turnout_change_2004_2024?.toFixed(1) || '-24.9'}%</span>
					<span class="metric-label">{content.turnoutChange}<br/>{content.period2004_2024}</span>
				</div>
				<div class="metric-card accent">
					<span class="metric-value">{keyMetrics.third_party_growth_2012_2024?.toFixed(0) || '492'}%</span>
					<span class="metric-label">{content.thirdPartyGrowth}<br/>{content.period2012_2024}</span>
				</div>
			</div>
		</div>
	</section>

	<!-- Scenario Cards -->
	<section class="scenarios-section">
		<div class="container">
			<h2>{content.scenariosTitle}</h2>
			<p class="section-intro">{content.scenariosIntro}</p>
			<div class="scenario-cards">
				{#each Object.entries(scenarios) as [key, scenario]}
					<button
						class="scenario-card {selectedScenario === key ? 'selected' : ''}"
						onclick={() => selectedScenario = selectedScenario === key ? null : key}
					>
						<div class="scenario-header">
							<span class="scenario-name">{scenario.name}</span>
							<span class="scenario-probability">{scenario.probability}%</span>
						</div>
						<p class="scenario-description">{scenario.description}</p>
						{#if selectedScenario === key}
							<div class="scenario-details">
								<div class="scenario-stat">
									<span class="stat-value">{(scenario.population_2040 / 1000000).toFixed(1)}M</span>
									<span class="stat-label">{content.population}</span>
								</div>
								<div class="scenario-stat">
									<span class="stat-value">{(scenario.voters_2040 / 1000000).toFixed(1)}M</span>
									<span class="stat-label">{content.voters}</span>
								</div>
								<div class="scenario-stat">
									<span class="stat-value">{scenario.turnout_2040}%</span>
									<span class="stat-label">{content.turnout}</span>
								</div>
								<div class="scenario-assumptions">
									<strong>{content.keyAssumptions}:</strong>
									<ul>
										{#each scenario.key_assumptions as assumption}
											<li>{assumption}</li>
										{/each}
									</ul>
								</div>
							</div>
						{/if}
					</button>
				{/each}
			</div>
		</div>
	</section>

	<!-- What If Statehood -->
	<section class="statehood-section">
		<div class="container content">
			<h2>{content.whatIfStatehood}</h2>
			<p>{content.statehoodIntro}</p>
			<div class="statehood-grid">
				<div class="statehood-stat">
					<span class="stat-number">{whatIfStatehood.electoral_votes || 5}</span>
					<span class="stat-desc">{content.electoralVotes}</span>
				</div>
				<div class="statehood-stat">
					<span class="stat-number">{whatIfStatehood.house_seats || 4}</span>
					<span class="stat-desc">{content.houseSeats}</span>
				</div>
				<div class="statehood-stat">
					<span class="stat-number">{whatIfStatehood.senators || 2}</span>
					<span class="stat-desc">{content.senators}</span>
				</div>
			</div>
			<p class="statehood-comparison">
				{whatIfStatehood.comparison || content.statehoodComparison}
			</p>
		</div>
	</section>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>{content.thankYouTitle}</h2>
			<p>{content.thankYouP1}</p>
			<p>{content.thankYouP2}</p>

			<div class="cta-section">
				<a href="https://github.com/opendatapr/puerto-rico-elections-platform" class="cta-button" target="_blank" rel="noopener">
					{content.exploreData}
				</a>
				<a href="{base}/" class="cta-button secondary">
					{content.backToStart}
				</a>
			</div>

			<div class="series-recap">
				<h3>{content.completeSeries}</h3>
				<ol class="chapter-list">
					<li>{content.seriesChapter1}</li>
					<li>{content.seriesChapter2}</li>
					<li>{content.seriesChapter3}</li>
					<li>{content.seriesChapter4}</li>
					<li>{content.seriesChapter5}</li>
					<li>{content.seriesChapter6}</li>
					<li>{content.seriesChapter7}</li>
					<li>{content.seriesChapter8}</li>
					<li>{content.seriesChapter9}</li>
				</ol>
			</div>

			<div class="sources">
				<h3>{content.sources}</h3>
				<ul>
					<li><a href="https://ww2.ceepur.org/Home/EventosElectorales" target="_blank" rel="noopener">Comision Estatal de Elecciones de Puerto Rico (CEE)</a> - {content.sourceCEE}</li>
					<li><a href="https://www.census.gov/programs-surveys/popest.html" target="_blank" rel="noopener">U.S. Census Bureau</a> - {content.sourceCensus}</li>
					<li>{content.sourceInstitute}</li>
					<li><a href="https://centropr.hunter.cuny.edu/" target="_blank" rel="noopener">Center for Puerto Rican Studies</a> - {content.sourceCentro}</li>
					<li><a href="https://www.brookings.edu/" target="_blank" rel="noopener">Brookings Institution</a> - {content.sourceBrookings}</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/house" class="nav-link prev">
					<span class="nav-direction">{content.previous}</span>
					<span class="nav-title">{content.prevTitle}</span>
				</a>
				<a href="{base}/" class="nav-link next">
					<span class="nav-direction">{content.returnTo}</span>
					<span class="nav-title">{content.home}</span>
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
	}

	.viz-note {
		font-size: var(--text-sm);
		color: var(--color-text-light);
		margin-top: var(--space-md);
		font-style: italic;
	}

	/* Dashboard Section */
	.dashboard-section {
		padding: var(--space-3xl) 0;
		background: var(--color-bg);
	}

	.dashboard-section h2 {
		text-align: center;
		margin-bottom: var(--space-xl);
	}

	.metrics-dashboard {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: var(--space-lg);
		max-width: 900px;
		margin: 0 auto;
	}

	.metric-card {
		background: var(--color-surface);
		border-radius: var(--radius-lg);
		padding: var(--space-xl);
		text-align: center;
		border: 1px solid var(--color-border);
		transition: transform var(--transition-base), box-shadow var(--transition-base);
	}

	.metric-card:hover {
		transform: translateY(-4px);
		box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
	}

	.metric-card.accent {
		background: var(--color-accent);
		border-color: var(--color-accent);
	}

	.metric-card.accent .metric-value,
	.metric-card.accent .metric-label {
		color: var(--color-bg);
	}

	.metric-value {
		display: block;
		font-family: var(--font-display);
		font-size: var(--text-3xl);
		font-weight: var(--font-bold);
		color: var(--color-text);
		margin-bottom: var(--space-sm);
	}

	.metric-label {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		line-height: 1.3;
	}

	/* Scenarios Section */
	.scenarios-section {
		padding: var(--space-3xl) 0;
		background: var(--color-surface);
	}

	.scenarios-section h2 {
		text-align: center;
		margin-bottom: var(--space-md);
	}

	.section-intro {
		text-align: center;
		max-width: 600px;
		margin: 0 auto var(--space-2xl);
		color: var(--color-text-muted);
	}

	.scenario-cards {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: var(--space-lg);
		max-width: 900px;
		margin: 0 auto;
	}

	.scenario-card {
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-lg);
		text-align: left;
		cursor: pointer;
		transition: all var(--transition-base);
	}

	.scenario-card:hover {
		border-color: var(--color-accent);
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
	}

	.scenario-card.selected {
		border-color: var(--color-accent);
		background: var(--color-surface-elevated);
	}

	.scenario-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--space-sm);
	}

	.scenario-name {
		font-family: var(--font-display);
		font-size: var(--text-lg);
		font-weight: var(--font-semibold);
		color: var(--color-text);
	}

	.scenario-probability {
		font-size: var(--text-xl);
		font-weight: var(--font-bold);
		color: var(--color-accent);
	}

	.scenario-description {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin: 0;
	}

	.scenario-details {
		margin-top: var(--space-lg);
		padding-top: var(--space-lg);
		border-top: 1px solid var(--color-border);
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: var(--space-md);
	}

	.scenario-stat {
		text-align: center;
	}

	.scenario-stat .stat-value {
		display: block;
		font-size: var(--text-xl);
		font-weight: var(--font-bold);
		color: var(--color-text);
	}

	.scenario-stat .stat-label {
		font-size: var(--text-xs);
		color: var(--color-text-muted);
	}

	.scenario-assumptions {
		grid-column: 1 / -1;
		margin-top: var(--space-md);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.scenario-assumptions ul {
		margin: var(--space-xs) 0 0;
		padding-left: var(--space-lg);
	}

	.scenario-assumptions li {
		margin: var(--space-xs) 0;
	}

	/* Statehood Section */
	.statehood-section {
		padding: var(--space-3xl) 0;
		background: linear-gradient(135deg, var(--color-surface) 0%, var(--color-bg) 100%);
	}

	.statehood-section h2 {
		margin-bottom: var(--space-lg);
	}

	.statehood-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: var(--space-xl);
		max-width: 500px;
		margin: var(--space-xl) 0;
	}

	.statehood-stat {
		text-align: center;
	}

	.stat-number {
		display: block;
		font-family: var(--font-display);
		font-size: var(--text-4xl);
		font-weight: var(--font-bold);
		color: var(--color-accent);
	}

	.stat-desc {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.statehood-comparison {
		font-style: italic;
		color: var(--color-text-muted);
		margin-top: var(--space-lg);
	}

	/* Conclusion Section */
	.chapter-conclusion {
		padding: var(--space-3xl) 0;
		background: var(--color-surface);
	}

	.cta-section {
		display: flex;
		gap: var(--space-md);
		margin: var(--space-xl) 0;
	}

	.cta-button {
		display: inline-flex;
		align-items: center;
		padding: var(--space-md) var(--space-xl);
		background: var(--color-accent);
		color: var(--color-bg);
		font-weight: var(--font-semibold);
		border-radius: var(--radius-md);
		text-decoration: none;
		transition: all var(--transition-base);
	}

	.cta-button:hover {
		background: var(--color-accent-light);
		transform: translateY(-2px);
	}

	.cta-button.secondary {
		background: var(--color-surface-elevated);
		color: var(--color-text);
	}

	.cta-button.secondary:hover {
		background: var(--color-border-light);
	}

	.series-recap {
		margin: var(--space-2xl) 0;
		padding: var(--space-xl);
		background: var(--color-bg);
		border-radius: var(--radius-lg);
	}

	.series-recap h3 {
		margin-bottom: var(--space-md);
	}

	.chapter-list {
		margin: 0;
		padding-left: var(--space-xl);
		columns: 2;
		column-gap: var(--space-2xl);
	}

	.chapter-list li {
		margin: var(--space-xs) 0;
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

	/* Responsive */
	@media (max-width: 768px) {
		.metrics-dashboard {
			grid-template-columns: repeat(2, 1fr);
		}

		.scenario-cards {
			grid-template-columns: 1fr;
		}

		.statehood-grid {
			max-width: 100%;
		}

		.chapter-list {
			columns: 1;
		}

		.cta-section {
			flex-direction: column;
		}
	}

	/* Sources Section */
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
