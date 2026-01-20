<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { LineChart, ScatterPlot, BarChart } from '$lib/components/charts';
	import { ChoroplethMap } from '$lib/components/maps';
	import { Legend } from '$lib/components/ui';
	import { CATEGORY_COLORS, createSequentialBlueScale, SEQUENTIAL_BLUE_COLORS } from '$lib/utils/colors';
	import { formatPercent, formatNumber, formatCompact } from '$lib/utils/format';
	import { language } from '$lib/stores/language';
	import * as d3 from 'd3';

	const chapterNum = 2;
	const totalSteps = 12;

	// Bilingual content
	const t = {
		en: {
			chapterTitle: 'The Vanishing Voter',
			chapter: 'Chapter',
			lead: "Puerto Rico once had among the highest voter turnout rates in the Western Hemisphere. In the span of a single generation, that changed dramatically. This is the story of a democracy in crisis - who stopped voting, why they left, and what it means for the island's political future.",
			missingVoters: 'Missing Voters in 2020',
			registeredNote: "registered voters who didn't cast a ballot",
			loading: 'Loading data...',
			// Viz titles
			turnoutTimeline: 'Voter Turnout Over Time (1992-2020)',
			turnoutMap: 'Turnout by Municipality (2020)',
			incomeVsTurnout: 'Income vs. Turnout by Municipality',
			turnoutByQuintile: 'Turnout by Income Quintile',
			// Viz captions
			timelineCaption: 'The shaded area shows the magnitude of decline - from over 80% to around 55%.',
			scatterCaption: 'Each dot is a municipality. The trend line reveals a stark correlation.',
			quintileCaption: 'Municipalities grouped by median household income, from poorest to richest.',
			// Legend
			legendTurnout: 'Voter Turnout',
			// Step titles
			step0Title: 'A Tradition of Participation',
			step1Title: 'The Warning Signs (2000-2012)',
			step2Turnout2012: 'Turnout in 2012',
			step2Turnout2016: 'Turnout in 2016',
			step3Title: 'After the Storm',
			step4Title: 'The Geography of Disengagement',
			step5Title: 'Two Puerto Ricos',
			step6Title: 'The Wealth Factor',
			step7Title: 'The Wealthy Vote',
			step8Title: 'The Silenced Poor',
			step9Title: 'The Poverty Gap',
			step10Title: 'Why do the poor stop voting?',
			step11Title: 'Breaking the Cycle',
			// Step content
			step0p1: 'For decades, Puerto Rico was a model of democratic engagement. From 1992 through 2012, voter turnout consistently exceeded',
			step0p1b: '- numbers that would make any U.S. state envious. In 1992, turnout peaked at an extraordinary',
			step0p2: 'Voting was not just a civic duty on the island - it was a cultural ritual. Election day was a holiday. Families went to the polls together. Political rallies drew hundreds of thousands. The three-way competition between status options (statehood, commonwealth, independence) gave every election existential stakes.',
			step0p3: 'What happened to that tradition?',
			step1p1: 'The first cracks appeared in the early 2000s. While still high by mainland standards, turnout began a slow decline: from 82.4% in 2000 to 81.5% in 2004, then to 79.4% in 2008, and 78.2% in 2012. Each election, a few more voters stayed home.',
			step1p2: "Economic stagnation was setting in. Puerto Rico's economy had been shrinking since 2006, when the phase-out of federal tax incentives (Section 936) gutted the manufacturing sector. Jobs disappeared. Young professionals began leaving for Florida, Texas, and New York. The debt crisis was brewing.",
			step1p3: 'But the real collapse was still to come.',
			step2p1: 'The 2016 election marked a catastrophic turning point. Nearly',
			step2p1b: 'fewer people voted. Congress passed PROMESA, creating an unelected fiscal control board. For many Puerto Ricans:',
			step2p1c: "your vote doesn't matter anymore",
			step3p1: "Hurricane Maria struck in September 2017, killing nearly 3,000 people and triggering the largest exodus in Puerto Rico's modern history. In the months following the storm, an estimated 130,000 people left the island - many permanently.",
			step3p2: 'By the 2020 election, turnout had fallen even further to just',
			step3p2b: 'Only',
			step3p2c: 'people cast ballots. The total drop from the 1990s peak:',
			step3p3: "But the decline wasn't distributed equally across the island. The geography of disengagement reveals a troubling pattern.",
			step4p1: "The map reveals stark geographic disparities in voter turnout. The San Juan metropolitan area - home to the island's wealthiest suburbs like Guaynabo, Trujillo Alto, and Carolina - shows notably higher participation. Meanwhile, rural municipalities in the mountainous interior and coastal towns show significantly lower turnout.",
			step4p2: "This isn't coincidence. It reflects deep structural inequalities: access to transportation, economic security, trust in institutions, and the practical ability to take time off work to vote. The communities hit hardest by the debt crisis and Hurricane Maria are the same ones disappearing from the polls.",
			step4p3: "Hover over the map to see each municipality's turnout rate.",
			step5p1pre: 'The gap is striking.',
			step5p1a: 'had the highest turnout at',
			step5p1b: 'while',
			step5p1c: 'saw just',
			step5p1d: "That's a",
			step5p1e: 'difference between neighboring communities on the same island.',
			step5p2: 'The highest-turnout municipalities cluster in the metro San Juan area and a few outliers like Culebra. The lowest turnout concentrates in the central mountain municipalities and economically distressed coastal towns. These patterns mirror income and poverty rates with uncanny precision.',
			step6p1: "Across Puerto Rico's 78 municipalities, a clear pattern emerges when we plot income against turnout. The scatter plot reveals a strong positive correlation: wealthier communities vote at significantly higher rates than poorer ones.",
			step6p2: "The regression line (R-squared shown above) quantifies what's visible at a glance: for every $10,000 increase in median household income, turnout increases by roughly 5-6 percentage points. This isn't a small effect - it's a fundamental divide in democratic participation.",
			step6p3: 'This pattern holds across the entire island, from the rural highlands to the urban coast. The extremes tell the story.',
			step7p1pre: '',
			step7p1a: "is Puerto Rico's wealthiest municipality, with a median household income of",
			step7p1b: 'Its voter turnout? An impressive',
			step7p1c: '- among the highest on the island.',
			step7p2: "Guaynabo is a suburb of San Juan, home to gated communities, private schools, and corporate headquarters. Its residents have stable jobs, reliable transportation, and the economic security to engage in civic life. Voting is easy when you're not worried about your next paycheck.",
			step7p3: "The contrast with the island's poorest communities couldn't be starker.",
			step8p1pre: 'At the other extreme sits',
			step8p1a: 'with median income of just',
			step8p1b: 'Turnout there was only',
			step8p2: 'In municipalities like Las Marias, Guanica, and Comerio, more than half the population lives below the poverty line. Hurricane Maria devastated these communities. Many residents lack reliable transportation. Some polling places closed or were relocated after the storm.',
			step8p3: 'When daily survival is a struggle, voting becomes a luxury.',
			step9p1: 'Breaking municipalities into income quintiles makes the pattern undeniable. The richest fifth of municipalities averages roughly',
			step9p1b: 'turnout, while the poorest fifth averages around',
			step9p2pre: "Of Puerto Rico's 78 municipalities,",
			step9p2a: 'have poverty rates above 50%. These high-poverty communities averaged just',
			step9p2b: 'turnout - compared to',
			step9p2c: 'in lower-poverty areas.',
			step9p3: 'The voices of the poor are systematically underrepresented at the ballot box.',
			step10p1: "Low turnout among poor communities creates a dangerous feedback loop. When the wealthy vote and the poor don't, elected officials have less incentive to address poverty. Policies favor those who show up.",
			step10p2: 'The fiscal control board has imposed austerity measures that disproportionately affect low-income residents: school closures, pension cuts, healthcare reductions. The people most hurt are the least represented.',
			step10p3: 'Democracy requires participation. When participation becomes unequal, so does power.',
			step11p1: "The socioeconomic turnout gap isn't inevitable. Other democracies have implemented reforms that boost participation among marginalized communities: automatic voter registration, election day holidays, early voting, vote-by-mail, and investment in civic education.",
			step11p2: 'Puerto Rico has some of these tools but deploys them unevenly. After Hurricane Maria, some municipalities saw polling places closed or consolidated, creating new barriers. Trust in institutions - never high - has eroded further amid corruption scandals and the ongoing debt crisis.',
			step11p3: "Understanding these patterns is the first step toward addressing them. The data shows us who's being left behind. The question is whether we'll do something about it.",
			// Conclusion
			keyFindings: 'Key Findings',
			finding1pre: 'Turnout collapsed from',
			finding1mid: 'in the 1990s to',
			finding1post: 'in 2020 - a drop of',
			finding2: 'The 2016 PROMESA law and 2017 Hurricane Maria accelerated an already-existing decline in democratic participation',
			finding3pre: 'A',
			finding3post: 'gap exists between the highest and lowest turnout municipalities',
			finding4: 'Income strongly predicts turnout: wealthier municipalities vote at significantly higher rates than poorer ones',
			finding5pre: '',
			finding5post: 'have poverty rates above 50%, and these communities show systematically lower turnout',
			finding6: 'The turnout gap creates a feedback loop where the voices of the poor are underrepresented in the political process',
			pullquote: "When the wealthy vote and the poor don't, elected officials have less incentive to address poverty. Policies favor those who show up.",
			sources: 'Sources',
			source1: 'Official voter turnout data 2000-2024',
			source2: 'Voting and Registration data for Puerto Rico',
			source3: 'Household income by municipality',
			source4: 'Election Administration and Voting Survey',
			source5: 'Puerto Rico electoral data',
			// Navigation
			previous: 'Previous',
			nextChapter: 'Next Chapter',
			prevTitle: 'The Great Exodus',
			nextTitle: 'The Shrinking Electorate',
			// Bar chart labels
			lowPoverty: 'Low Poverty (<35%)',
			highPoverty: 'High Poverty (>50%)',
			quintilePoorest: 'Poorest',
			quintile2nd: '2nd',
			quintile3rd: '3rd',
			quintile4th: '4th',
			quintileRichest: 'Richest',
			percentagePoints: 'percentage points',
			percentagePoint: 'percentage point',
			municipalities: 'municipalities',
			// Chart axis labels
			electionYear: 'Election Year',
			turnoutPct: 'Turnout %',
			medianHouseholdIncome: 'Median Household Income ($)',
			turnout: 'turnout',
			// Meta description
			metaDescription: "Investigating the collapse of voter participation in Puerto Rico - from 80%+ turnout in the 1990s to under 55% today."
		},
		es: {
			chapterTitle: 'El Votante Desaparecido',
			chapter: 'Capitulo',
			lead: 'Puerto Rico alguna vez tuvo una de las tasas de participacion electoral mas altas del hemisferio occidental. En el transcurso de una sola generacion, eso cambio dramaticamente. Esta es la historia de una democracia en crisis: quienes dejaron de votar, por que se fueron y que significa para el futuro politico de la isla.',
			missingVoters: 'Votantes Ausentes en 2020',
			registeredNote: 'votantes registrados que no emitieron un voto',
			loading: 'Cargando datos...',
			// Viz titles
			turnoutTimeline: 'Participacion Electoral a Traves del Tiempo (1992-2020)',
			turnoutMap: 'Participacion por Municipio (2020)',
			incomeVsTurnout: 'Ingreso vs. Participacion por Municipio',
			turnoutByQuintile: 'Participacion por Quintil de Ingreso',
			// Viz captions
			timelineCaption: 'El area sombreada muestra la magnitud del declive - de mas del 80% a alrededor del 55%.',
			scatterCaption: 'Cada punto es un municipio. La linea de tendencia revela una correlacion marcada.',
			quintileCaption: 'Municipios agrupados por ingreso medio del hogar, del mas pobre al mas rico.',
			// Legend
			legendTurnout: 'Participacion Electoral',
			// Step titles
			step0Title: 'Una Tradicion de Participacion',
			step1Title: 'Las Senales de Alerta (2000-2012)',
			step2Turnout2012: 'Participacion en 2012',
			step2Turnout2016: 'Participacion en 2016',
			step3Title: 'Despues de la Tormenta',
			step4Title: 'La Geografia del Desapego',
			step5Title: 'Dos Puerto Ricos',
			step6Title: 'El Factor de la Riqueza',
			step7Title: 'Los Ricos Votan',
			step8Title: 'Los Pobres Silenciados',
			step9Title: 'La Brecha de Pobreza',
			step10Title: 'Por que los pobres dejan de votar?',
			step11Title: 'Rompiendo el Ciclo',
			// Step content
			step0p1: 'Durante decadas, Puerto Rico fue un modelo de participacion democratica. Desde 1992 hasta 2012, la participacion electoral consistentemente supero el',
			step0p1b: '- numeros que harian envidiosos a cualquier estado de EE.UU. En 1992, la participacion alcanzo un extraordinario',
			step0p2: 'Votar no era solo un deber civico en la isla, era un ritual cultural. El dia de elecciones era feriado. Las familias iban juntas a las urnas. Los mitines politicos atraian a cientos de miles. La competencia tripartita entre opciones de estatus (estadidad, estado libre asociado, independencia) le daba a cada eleccion una importancia existencial.',
			step0p3: 'Que paso con esa tradicion?',
			step1p1: 'Las primeras grietas aparecieron a principios de los 2000. Aunque todavia alta segun estandares continentales, la participacion comenzo un lento declive: de 82.4% en 2000 a 81.5% en 2004, luego a 79.4% en 2008 y 78.2% en 2012. En cada eleccion, unos pocos votantes mas se quedaron en casa.',
			step1p2: 'El estancamiento economico se estaba instalando. La economia de Puerto Rico se habia contraido desde 2006, cuando la eliminacion gradual de incentivos fiscales federales (Seccion 936) devasto el sector manufacturero. Los empleos desaparecieron. Los jovenes profesionales comenzaron a irse a Florida, Texas y Nueva York. La crisis de deuda se gestaba.',
			step1p3: 'Pero el verdadero colapso aun estaba por venir.',
			step2p1: 'La eleccion de 2016 marco un punto de inflexion catastrofico. Casi',
			step2p1b: 'personas menos votaron. El Congreso aprobo PROMESA, creando una junta de control fiscal no electa. Para muchos puertorriquenos:',
			step2p1c: 'tu voto ya no importa',
			step3p1: 'El Huracan Maria azoto en septiembre de 2017, matando a casi 3,000 personas y desencadenando el mayor exodo en la historia moderna de Puerto Rico. En los meses posteriores a la tormenta, se estima que 130,000 personas abandonaron la isla, muchas permanentemente.',
			step3p2: 'Para la eleccion de 2020, la participacion habia caido aun mas, a solo',
			step3p2b: 'Solo',
			step3p2c: 'personas emitieron votos. La caida total desde el pico de los 1990:',
			step3p3: 'Pero el declive no se distribuyo equitativamente en la isla. La geografia del desapego revela un patron preocupante.',
			step4p1: 'El mapa revela marcadas disparidades geograficas en la participacion electoral. El area metropolitana de San Juan, hogar de los suburbios mas ricos de la isla como Guaynabo, Trujillo Alto y Carolina, muestra una participacion notablemente mayor. Mientras tanto, los municipios rurales en el interior montanoso y los pueblos costeros muestran una participacion significativamente menor.',
			step4p2: 'Esto no es coincidencia. Refleja profundas desigualdades estructurales: acceso a transporte, seguridad economica, confianza en las instituciones y la capacidad practica de tomar tiempo libre del trabajo para votar. Las comunidades mas afectadas por la crisis de deuda y el Huracan Maria son las mismas que desaparecen de las urnas.',
			step4p3: 'Pasa el cursor sobre el mapa para ver la tasa de participacion de cada municipio.',
			step5p1pre: 'La brecha es sorprendente.',
			step5p1a: 'tuvo la mayor participacion con',
			step5p1b: 'mientras que',
			step5p1c: 'vio solo',
			step5p1d: 'Esa es una diferencia de',
			step5p1e: 'entre comunidades vecinas en la misma isla.',
			step5p2: 'Los municipios de mayor participacion se agrupan en el area metropolitana de San Juan y algunos valores atipicos como Culebra. La menor participacion se concentra en los municipios de las montanas centrales y pueblos costeros economicamente deprimidos. Estos patrones reflejan las tasas de ingreso y pobreza con una precision inquietante.',
			step6p1: 'En los 78 municipios de Puerto Rico, emerge un patron claro cuando graficamos ingreso contra participacion. El grafico de dispersion revela una fuerte correlacion positiva: las comunidades mas ricas votan a tasas significativamente mas altas que las mas pobres.',
			step6p2: 'La linea de regresion (R-cuadrado mostrado arriba) cuantifica lo visible a simple vista: por cada $10,000 de aumento en el ingreso medio del hogar, la participacion aumenta aproximadamente 5-6 puntos porcentuales. Este no es un efecto pequeno, es una division fundamental en la participacion democratica.',
			step6p3: 'Este patron se mantiene en toda la isla, desde las tierras altas rurales hasta la costa urbana. Los extremos cuentan la historia.',
			step7p1pre: '',
			step7p1a: 'es el municipio mas rico de Puerto Rico, con un ingreso medio del hogar de',
			step7p1b: 'Su participacion electoral? Un impresionante',
			step7p1c: '- entre los mas altos de la isla.',
			step7p2: 'Guaynabo es un suburbio de San Juan, hogar de comunidades cerradas, escuelas privadas y sedes corporativas. Sus residentes tienen empleos estables, transporte confiable y la seguridad economica para participar en la vida civica. Votar es facil cuando no te preocupa tu proximo cheque.',
			step7p3: 'El contraste con las comunidades mas pobres de la isla no podria ser mas marcado.',
			step8p1pre: 'En el otro extremo esta',
			step8p1a: 'con un ingreso medio de solo',
			step8p1b: 'La participacion alli fue de solo',
			step8p2: 'En municipios como Las Marias, Guanica y Comerio, mas de la mitad de la poblacion vive bajo la linea de pobreza. El Huracan Maria devasto estas comunidades. Muchos residentes carecen de transporte confiable. Algunos centros de votacion cerraron o fueron reubicados despues de la tormenta.',
			step8p3: 'Cuando la supervivencia diaria es una lucha, votar se convierte en un lujo.',
			step9p1: 'Dividir los municipios en quintiles de ingreso hace el patron innegable. El quinto mas rico de los municipios promedia aproximadamente',
			step9p1b: 'de participacion, mientras que el quinto mas pobre promedia alrededor de',
			step9p2pre: 'De los 78 municipios de Puerto Rico,',
			step9p2a: 'tienen tasas de pobreza superiores al 50%. Estas comunidades de alta pobreza promediaron solo',
			step9p2b: 'de participacion - comparado con',
			step9p2c: 'en areas de menor pobreza.',
			step9p3: 'Las voces de los pobres estan sistematicamente subrepresentadas en las urnas.',
			step10p1: 'La baja participacion entre las comunidades pobres crea un ciclo peligroso de retroalimentacion. Cuando los ricos votan y los pobres no, los funcionarios electos tienen menos incentivo para abordar la pobreza. Las politicas favorecen a quienes se presentan.',
			step10p2: 'La junta de control fiscal ha impuesto medidas de austeridad que afectan desproporcionadamente a los residentes de bajos ingresos: cierres de escuelas, recortes de pensiones, reducciones en salud. Las personas mas perjudicadas son las menos representadas.',
			step10p3: 'La democracia requiere participacion. Cuando la participacion se vuelve desigual, tambien lo hace el poder.',
			step11p1: 'La brecha socioeconomica en la participacion no es inevitable. Otras democracias han implementado reformas que aumentan la participacion entre comunidades marginadas: registro automatico de votantes, feriados electorales, voto anticipado, voto por correo e inversion en educacion civica.',
			step11p2: 'Puerto Rico tiene algunas de estas herramientas pero las despliega de manera desigual. Despues del Huracan Maria, algunos municipios vieron centros de votacion cerrados o consolidados, creando nuevas barreras. La confianza en las instituciones, nunca alta, se ha erosionado aun mas en medio de escandalos de corrupcion y la crisis de deuda en curso.',
			step11p3: 'Entender estos patrones es el primer paso para abordarlos. Los datos nos muestran quienes se estan quedando atras. La pregunta es si haremos algo al respecto.',
			// Conclusion
			keyFindings: 'Conclusiones Clave',
			finding1pre: 'La participacion colapso de',
			finding1mid: 'en los 1990 a',
			finding1post: 'en 2020 - una caida de',
			finding2: 'La ley PROMESA de 2016 y el Huracan Maria de 2017 aceleraron un declive ya existente en la participacion democratica',
			finding3pre: 'Existe una brecha de',
			finding3post: 'entre los municipios de mayor y menor participacion',
			finding4: 'El ingreso predice fuertemente la participacion: los municipios mas ricos votan a tasas significativamente mas altas que los mas pobres',
			finding5pre: '',
			finding5post: 'tienen tasas de pobreza superiores al 50%, y estas comunidades muestran sistematicamente menor participacion',
			finding6: 'La brecha de participacion crea un ciclo de retroalimentacion donde las voces de los pobres estan subrepresentadas en el proceso politico',
			pullquote: 'Cuando los ricos votan y los pobres no, los funcionarios electos tienen menos incentivo para abordar la pobreza. Las politicas favorecen a quienes se presentan.',
			sources: 'Fuentes',
			source1: 'Datos oficiales de participacion electoral 2000-2024',
			source2: 'Datos de votacion y registro para Puerto Rico',
			source3: 'Ingreso del hogar por municipio',
			source4: 'Encuesta de Administracion Electoral y Votacion',
			source5: 'Datos electorales de Puerto Rico',
			// Navigation
			previous: 'Anterior',
			nextChapter: 'Proximo Capitulo',
			prevTitle: 'El Gran Exodo',
			nextTitle: 'El Electorado Menguante',
			// Bar chart labels
			lowPoverty: 'Baja Pobreza (<35%)',
			highPoverty: 'Alta Pobreza (>50%)',
			quintilePoorest: 'Mas Pobre',
			quintile2nd: '2do',
			quintile3rd: '3ro',
			quintile4th: '4to',
			quintileRichest: 'Mas Rico',
			percentagePoints: 'puntos porcentuales',
			percentagePoint: 'punto porcentual',
			municipalities: 'municipios',
			// Chart axis labels
			electionYear: 'Ano Electoral',
			turnoutPct: 'Participacion %',
			medianHouseholdIncome: 'Ingreso Medio del Hogar ($)',
			turnout: 'participacion',
			// Meta description
			metaDescription: 'Investigando el colapso de la participacion electoral en Puerto Rico - de mas del 80% en los 1990 a menos del 55% hoy.'
		}
	};

	// Reactive content based on language
	let content = $derived(t[$language]);
	let chapterTitle = $derived(content.chapterTitle);

	let currentStep = $state(0);
	let activeViz = $state<'line' | 'scatter' | 'bar' | 'map'>('line');
	let loading = $state(true);

	// Data loaded from API
	let turnoutData = $state<Array<{ x: number; y: number }>>([]);
	let incomeVsTurnout = $state<Array<{ x: number; y: number; label: string; poverty_rate: number }>>([]);
	let rawTurnoutSeries = $state<Array<{ year: number; total_votes: number; turnout_pct: number }>>([]);

	// Computed statistics
	let peakTurnout = $derived(Math.max(...turnoutData.map(d => d.y), 0));
	let lowestTurnout = $derived(Math.min(...turnoutData.map(d => d.y), 100));
	let turnoutDrop = $derived(peakTurnout - lowestTurnout);
	let totalVotes2020 = $derived(rawTurnoutSeries.find(d => d.year === 2020)?.total_votes || 0);
	let avgTurnout = $derived(incomeVsTurnout.length > 0
		? d3.mean(incomeVsTurnout, d => d.y) || 0
		: 0);

	// Municipality extremes
	let richestMunicipality = $derived(
		incomeVsTurnout.length > 0
			? incomeVsTurnout.reduce((a, b) => a.x > b.x ? a : b)
			: null
	);
	let poorestMunicipality = $derived(
		incomeVsTurnout.length > 0
			? incomeVsTurnout.reduce((a, b) => a.x < b.x ? a : b)
			: null
	);
	let highestTurnoutMuni = $derived(
		incomeVsTurnout.length > 0
			? incomeVsTurnout.reduce((a, b) => a.y > b.y ? a : b)
			: null
	);
	let lowestTurnoutMuni = $derived(
		incomeVsTurnout.length > 0
			? incomeVsTurnout.reduce((a, b) => a.y < b.y ? a : b)
			: null
	);
	let turnoutGap = $derived(
		highestTurnoutMuni && lowestTurnoutMuni
			? highestTurnoutMuni.y - lowestTurnoutMuni.y
			: 0
	);

	// Poverty correlation
	let highPovertyMunicipalities = $derived(
		incomeVsTurnout.filter(d => d.poverty_rate > 50)
	);
	let lowPovertyMunicipalities = $derived(
		incomeVsTurnout.filter(d => d.poverty_rate < 35)
	);
	let highPovertyAvgTurnout = $derived(
		highPovertyMunicipalities.length > 0
			? d3.mean(highPovertyMunicipalities, d => d.y) || 0
			: 0
	);
	let lowPovertyAvgTurnout = $derived(
		lowPovertyMunicipalities.length > 0
			? d3.mean(lowPovertyMunicipalities, d => d.y) || 0
			: 0
	);
	let povertyTurnoutGap = $derived(lowPovertyAvgTurnout - highPovertyAvgTurnout);

	// Historical turnout for context (approximate data based on historical records)
	const historicalTurnout = [
		{ x: 1992, y: 84.0 },
		{ x: 1996, y: 82.0 },
		{ x: 2000, y: 82.4 },
		{ x: 2004, y: 81.5 },
		{ x: 2008, y: 79.4 },
		{ x: 2012, y: 78.2 },
	];

	// Bar chart data for poverty comparison
	let povertyComparisonData = $derived([
		{
			label: content.lowPoverty,
			value: lowPovertyAvgTurnout,
			color: CATEGORY_COLORS[0]
		},
		{
			label: content.highPoverty,
			value: highPovertyAvgTurnout,
			color: CATEGORY_COLORS[3]
		}
	]);

	// Quintile bar chart data
	let quintileData = $derived(() => {
		if (incomeVsTurnout.length === 0) return [];
		const sorted = [...incomeVsTurnout].sort((a, b) => a.x - b.x);
		const quintileSize = Math.ceil(sorted.length / 5);
		const quintiles = [];
		const quintileLabels = [content.quintilePoorest, content.quintile2nd, content.quintile3rd, content.quintile4th, content.quintileRichest];
		for (let i = 0; i < 5; i++) {
			const start = i * quintileSize;
			const end = Math.min(start + quintileSize, sorted.length);
			const slice = sorted.slice(start, end);
			const avgTurnout = d3.mean(slice, d => d.y) || 0;
			quintiles.push({
				label: quintileLabels[i],
				value: avgTurnout,
				color: CATEGORY_COLORS[i % CATEGORY_COLORS.length]
			});
		}
		return quintiles;
	});

	// Map data
	let turnoutMapData = $derived(() => {
		const map = new Map<string, number>();
		for (const item of incomeVsTurnout) {
			map.set(item.label, item.y);
		}
		return map;
	});

	// Color scale for map - sequential blue (higher turnout = darker blue = good)
	const turnoutColorScale = createSequentialBlueScale([50, 70]);

	// Load chapter data
	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/chapters/turnout.json`);
			const data = await response.json();

			// Store raw series for stats
			rawTurnoutSeries = data.turnout_series || [];

			// Combine historical + actual data for line chart
			const actualData = (data.turnout_series || []).map((item: { year: number; turnout_pct: number }) => ({
				x: item.year,
				y: item.turnout_pct
			}));

			// Merge historical with actual, using actual where years overlap
			const actualYears = new Set(actualData.map((d: { x: number }) => d.x));
			const combined = [
				...historicalTurnout.filter(d => !actualYears.has(d.x)),
				...actualData
			].sort((a, b) => a.x - b.x);

			turnoutData = combined;

			// Map income vs turnout data with poverty rate
			incomeVsTurnout = (data.income_turnout || []).map((item: {
				municipality: string;
				income: number;
				turnout: number;
				poverty_rate: number;
			}) => ({
				x: item.income,
				y: item.turnout,
				label: item.municipality,
				poverty_rate: item.poverty_rate || 0
			}));
		} catch (err) {
			console.error('Failed to load turnout data:', err);
		} finally {
			loading = false;
		}
	});

	// Derived turnout series for chart
	let turnoutSeriesLabel = $derived(content.legendTurnout);
	let turnoutSeries = $derived([{
		id: 'turnout',
		label: turnoutSeriesLabel,
		data: turnoutData,
		color: CATEGORY_COLORS[0]
	}]);

	// Highlighted point for scatter plot
	let highlightedMunicipality = $state<string | null>(null);

	function handleStepEnter(response: { index: number }) {
		currentStep = response.index;
		highlightedMunicipality = null;

		switch (response.index) {
			case 0:
			case 1:
			case 2:
			case 3:
				activeViz = 'line';
				break;
			case 4:
			case 5:
				activeViz = 'map';
				break;
			case 6:
			case 7:
			case 8:
				activeViz = 'scatter';
				break;
			case 9:
			case 10:
				activeViz = 'bar';
				break;
			case 11:
				activeViz = 'scatter';
				break;
		}

		// Set municipality highlights for scatter
		if (response.index === 7 && richestMunicipality) {
			highlightedMunicipality = richestMunicipality.label;
		} else if (response.index === 8 && poorestMunicipality) {
			highlightedMunicipality = poorestMunicipality.label;
		}
	}
</script>

<svelte:head>
	<title>{content.chapter} {chapterNum}: {chapterTitle} | Puerto Rico Elections</title>
	<meta name="description" content={content.metaDescription}>
</svelte:head>

<Progress {currentStep} {totalSteps} chapterTitle={chapterTitle} />

<article class="chapter">
	<header class="chapter-header">
		<div class="container content">
			<span class="label">{content.chapter} {chapterNum}</span>
			<div class="accent-line"></div>
			<h1>{chapterTitle}</h1>
			<p class="lead">{content.lead}</p>
			{#if !loading && rawTurnoutSeries.length > 0}
				<div class="missing-voters-banner">
					<span class="counter-label">{content.missingVoters}</span>
					<span class="counter-value">~{formatCompact(2350000 - totalVotes2020)}</span>
					<span class="counter-note">{content.registeredNote}</span>
				</div>
			{/if}
		</div>
	</header>

	<ScrollySection offset={0.6} onStepEnter={handleStepEnter}>
		{#snippet graphic()}
			<div class="viz-container">
				{#if loading}
					<p class="loading">{content.loading}</p>
				{:else if activeViz === 'line'}
					<h3 class="viz-title">{content.turnoutTimeline}</h3>
					<LineChart
						series={turnoutSeries}
						width={520}
						height={380}
						xLabel={content.electionYear}
						yLabel={content.turnoutPct}
						xFormat={(v) => String(v)}
						yFormat={(v) => `${v}%`}
						showArea={true}
					/>
					<p class="viz-caption">{content.timelineCaption}</p>
				{:else if activeViz === 'map'}
					<h3 class="viz-title">{content.turnoutMap}</h3>
					<ChoroplethMap
						data={turnoutMapData()}
						colorScale={turnoutColorScale}
						tooltipFormat={(name, value) =>
							value !== undefined
								? `${name}: ${value.toFixed(1)}% ${content.turnout}`
								: name
						}
					/>
					<div class="legend">
						<span class="legend-label">{content.legendTurnout}</span>
						<div class="legend-scale">
							<span style="background: {turnoutColorScale(52)}"></span>
							<span style="background: {turnoutColorScale(60)}"></span>
							<span style="background: {turnoutColorScale(68)}"></span>
						</div>
						<div class="legend-labels">
							<span>~52%</span>
							<span>~60%</span>
							<span>~70%</span>
						</div>
					</div>
				{:else if activeViz === 'scatter'}
					<h3 class="viz-title">{content.incomeVsTurnout}</h3>
					<ScatterPlot
						data={incomeVsTurnout}
						width={520}
						height={380}
						xLabel={content.medianHouseholdIncome}
						yLabel={content.turnoutPct}
						xFormat={(v) => `$${(v/1000).toFixed(0)}K`}
						yFormat={(v) => `${v.toFixed(1)}%`}
						showRegression={true}
						highlightLabel={highlightedMunicipality}
					/>
					<p class="viz-caption">{content.scatterCaption}</p>
				{:else}
					<h3 class="viz-title">{content.turnoutByQuintile}</h3>
					<BarChart
						data={quintileData()}
						width={480}
						height={350}
						showValues={true}
						valueFormat={(v) => `${v.toFixed(1)}%`}
					/>
					<p class="viz-caption">{content.quintileCaption}</p>
				{/if}
			</div>
		{/snippet}

		<!-- PART 1: THE GOLDEN ERA -->
		<Step active={currentStep === 0} index={0}>
			<h3>{content.step0Title}</h3>
			{#if $language === 'en'}
				<p>
					{content.step0p1} <span class="stat">78%</span> {content.step0p1b}
					<span class="stat">{peakTurnout.toFixed(1)}%</span>.
				</p>
				<p>{content.step0p2}</p>
				<p class="emphasis">{content.step0p3}</p>
			{:else}
				<p>
					{content.step0p1} <span class="stat">78%</span> {content.step0p1b}
					<span class="stat">{peakTurnout.toFixed(1)}%</span>.
				</p>
				<p>{content.step0p2}</p>
				<p class="emphasis">{content.step0p3}</p>
			{/if}
		</Step>

		<!-- PART 2: THE DECLINE BEGINS -->
		<Step active={currentStep === 1} index={1}>
			<h3>{content.step1Title}</h3>
			<p>{content.step1p1}</p>
			<p>{content.step1p2}</p>
			<p>{content.step1p3}</p>
		</Step>

		<!-- PART 3: THE COLLAPSE -->
		<Step active={currentStep === 2} index={2} variant="comparison">
			{#snippet before()}
				<span class="stat">78.2%</span>
				<p>{content.step2Turnout2012}</p>
			{/snippet}
			{#snippet after()}
				<span class="stat">67.2%</span>
				<p>{content.step2Turnout2016}</p>
			{/snippet}
			<p>
				{content.step2p1} <span class="stat">250,000</span> {content.step2p1b}
				<em>{content.step2p1c}</em>.
			</p>
		</Step>

		<!-- PART 4: MARIA AND AFTERMATH -->
		<Step active={currentStep === 3} index={3}>
			<h3>{content.step3Title}</h3>
			<p>{content.step3p1}</p>
			<p>
				{content.step3p2} <span class="stat">{lowestTurnout.toFixed(1)}%</span>.
				{content.step3p2b} <span class="stat">{formatNumber(totalVotes2020)}</span> {content.step3p2c}
				<span class="stat">{turnoutDrop.toFixed(1)} {content.percentagePoints}</span>.
			</p>
			<p>{content.step3p3}</p>
		</Step>

		<!-- PART 5: GEOGRAPHIC PATTERNS -->
		<Step active={currentStep === 4} index={4}>
			<h3>{content.step4Title}</h3>
			<p>{content.step4p1}</p>
			<p>{content.step4p2}</p>
			<p>{content.step4p3}</p>
		</Step>

		<!-- PART 6: HIGH VS LOW TURNOUT REGIONS -->
		<Step active={currentStep === 5} index={5}>
			<h3>{content.step5Title}</h3>
			<p>
				{#if highestTurnoutMuni && lowestTurnoutMuni}
					{content.step5p1pre} <span class="highlight">{highestTurnoutMuni.label}</span> {content.step5p1a}
					<span class="stat">{highestTurnoutMuni.y.toFixed(1)}%</span>,
					{content.step5p1b} <span class="highlight">{lowestTurnoutMuni.label}</span> {content.step5p1c}
					<span class="stat">{lowestTurnoutMuni.y.toFixed(1)}%</span>. {content.step5p1d}
					<span class="stat">{turnoutGap.toFixed(1)} {content.percentagePoint}</span> {content.step5p1e}
				{/if}
			</p>
			<p>{content.step5p2}</p>
		</Step>

		<!-- PART 7: THE INCOME CONNECTION -->
		<Step active={currentStep === 6} index={6}>
			<h3>{content.step6Title}</h3>
			<p>{content.step6p1}</p>
			<p>{content.step6p2}</p>
			<p>{content.step6p3}</p>
		</Step>

		<!-- PART 8: RICHEST MUNICIPALITY -->
		<Step active={currentStep === 7} index={7}>
			<h3>{content.step7Title}</h3>
			<p>
				{#if richestMunicipality}
					{content.step7p1pre}<span class="highlight">{richestMunicipality.label}</span> {content.step7p1a}
					<span class="stat">${formatNumber(richestMunicipality.x)}</span>. {content.step7p1b}
					<span class="stat">{richestMunicipality.y.toFixed(1)}%</span> {content.step7p1c}
				{/if}
			</p>
			<p>{content.step7p2}</p>
			<p>{content.step7p3}</p>
		</Step>

		<!-- PART 9: POOREST MUNICIPALITY -->
		<Step active={currentStep === 8} index={8}>
			<h3>{content.step8Title}</h3>
			<p>
				{#if poorestMunicipality}
					{content.step8p1pre} <span class="highlight">{poorestMunicipality.label}</span>,
					{content.step8p1a} <span class="stat">${formatNumber(poorestMunicipality.x)}</span>.
					{content.step8p1b} <span class="stat">{poorestMunicipality.y.toFixed(1)}%</span>.
				{/if}
			</p>
			<p>{content.step8p2}</p>
			<p>{content.step8p3}</p>
		</Step>

		<!-- PART 10: POVERTY COMPARISON -->
		<Step active={currentStep === 9} index={9}>
			<h3>{content.step9Title}</h3>
			<p>
				{content.step9p1} <span class="stat">{quintileData()[4]?.value.toFixed(1) || '65'}%</span>
				{content.step9p1b} <span class="stat">{quintileData()[0]?.value.toFixed(1) || '55'}%</span>.
			</p>
			<p>
				{#if highPovertyMunicipalities.length > 0}
					{content.step9p2pre} <span class="stat">{highPovertyMunicipalities.length}</span>
					{content.step9p2a} <span class="stat">{highPovertyAvgTurnout.toFixed(1)}%</span>
					{content.step9p2b} <span class="stat">{lowPovertyAvgTurnout.toFixed(1)}%</span> {content.step9p2c}
				{/if}
			</p>
			<p>{content.step9p3}</p>
		</Step>

		<!-- PART 11: THE FEEDBACK LOOP -->
		<Step active={currentStep === 10} index={10} variant="question">
			<h3>{content.step10Title}</h3>
			<p>{content.step10p1}</p>
			<p>{content.step10p2}</p>
			<p>{content.step10p3}</p>
		</Step>

		<!-- PART 12: WHAT NOW -->
		<Step active={currentStep === 11} index={11}>
			<h3>{content.step11Title}</h3>
			<p>{content.step11p1}</p>
			<p>{content.step11p2}</p>
			<p>{content.step11p3}</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>{content.keyFindings}</h2>
			<ul class="findings-list">
				<li>
					{content.finding1pre} <strong>{peakTurnout.toFixed(0)}%</strong> {content.finding1mid}
					<strong>{lowestTurnout.toFixed(0)}%</strong> {content.finding1post}
					<strong>{turnoutDrop.toFixed(0)} {content.percentagePoints}</strong>
				</li>
				<li>{content.finding2}</li>
				<li>
					{#if turnoutGap > 0}
						{content.finding3pre} <strong>{turnoutGap.toFixed(1)} {content.percentagePoint}</strong> {content.finding3post}
					{/if}
				</li>
				<li>{content.finding4}</li>
				<li>
					{#if highPovertyMunicipalities.length > 0}
						{content.finding5pre}<strong>{highPovertyMunicipalities.length} {content.municipalities}</strong> {content.finding5post}
					{/if}
				</li>
				<li>{content.finding6}</li>
			</ul>

			<div class="pullquote">
				<blockquote>"{content.pullquote}"</blockquote>
			</div>

			<div class="sources">
				<h3>{content.sources}</h3>
				<ul>
					<li><a href="https://ww2.ceepur.org/Home/EventosElectorales" target="_blank" rel="noopener">Comision Estatal de Elecciones de Puerto Rico (CEE)</a> - {content.source1}</li>
					<li><a href="https://data.census.gov/" target="_blank" rel="noopener">U.S. Census Bureau</a> - {content.source2}</li>
					<li><a href="https://data.census.gov/" target="_blank" rel="noopener">American Community Survey</a> - {content.source3}</li>
					<li><a href="https://www.eac.gov/research-and-data/datasets-codebooks-and-surveys" target="_blank" rel="noopener">U.S. Election Assistance Commission</a> - {content.source4}</li>
					<li><a href="https://www.icpsr.umich.edu/" target="_blank" rel="noopener">Inter-University Consortium for Political and Social Research</a> - {content.source5}</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/exodus" class="nav-link prev">
					<span class="nav-direction">{content.previous}</span>
					<span class="nav-title">{content.prevTitle}</span>
				</a>
				<a href="{base}/chapters/shrinking" class="nav-link next">
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
		background: radial-gradient(ellipse at 50% 100%, var(--color-surface) 0%, var(--color-bg) 70%);
	}

	.missing-voters-banner {
		margin-top: var(--space-xl);
		padding: var(--space-lg);
		background: var(--color-surface);
		border-left: 4px solid var(--color-accent);
		border-radius: var(--radius-md);
		display: flex;
		flex-direction: column;
		gap: var(--space-xs);
	}

	.counter-label {
		font-size: var(--text-sm);
		text-transform: uppercase;
		letter-spacing: var(--tracking-wide);
		color: var(--color-text-muted);
	}

	.counter-value {
		font-family: var(--font-display);
		font-size: var(--text-4xl);
		font-weight: var(--font-bold);
		color: var(--color-accent);
		line-height: 1;
	}

	.counter-note {
		font-size: var(--text-sm);
		color: var(--color-text-light);
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

	.viz-caption {
		font-size: var(--text-sm);
		color: var(--color-text-light);
		text-align: center;
		margin-top: var(--space-lg);
		max-width: 420px;
		line-height: 1.6;
		padding: var(--space-sm) var(--space-md);
		background: var(--color-surface-elevated);
		border-radius: var(--radius-md);
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

	.legend-label {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		text-transform: uppercase;
		letter-spacing: var(--tracking-wide);
		font-weight: var(--font-medium);
	}

	.legend-scale {
		display: flex;
		width: 220px;
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
		width: 220px;
		font-size: var(--text-sm);
		color: var(--color-text-light);
		font-weight: var(--font-medium);
	}

	.emphasis {
		font-style: italic;
		color: var(--color-text);
		font-weight: var(--font-medium);
	}

	.chapter-conclusion {
		padding: var(--space-3xl) 0;
		background: var(--color-surface);
	}

	.findings-list {
		list-style: none;
		padding: 0;
		margin: var(--space-lg) 0;
	}

	.findings-list li {
		padding: var(--space-md) 0;
		border-bottom: 1px solid var(--color-border);
		color: var(--color-text-muted);
		line-height: 1.6;
	}

	.findings-list li:last-child {
		border-bottom: none;
	}

	.findings-list strong {
		color: var(--color-accent);
	}

	.pullquote {
		margin: var(--space-2xl) 0;
		padding: var(--space-xl);
		background: var(--color-bg);
		border-radius: var(--radius-lg);
	}

	.pullquote blockquote {
		margin: 0;
		font-family: var(--font-display);
		font-size: var(--text-xl);
		font-weight: var(--font-medium);
		color: var(--color-text);
		line-height: 1.5;
		font-style: italic;
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

	/* Mobile adjustments */
	@media (max-width: 640px) {
		.chapter-header {
			min-height: 50vh;
			padding: var(--space-xl) 0;
		}

		.missing-voters-banner {
			padding: var(--space-md);
			margin-top: var(--space-lg);
		}

		.counter-value {
			font-size: var(--text-2xl);
		}

		.counter-label,
		.counter-note {
			font-size: var(--text-xs);
		}

		.viz-container {
			padding: var(--space-sm);
		}

		.viz-title {
			font-size: var(--text-base);
			margin-bottom: var(--space-sm);
		}

		.viz-caption {
			font-size: var(--text-xs);
			max-width: 100%;
		}

		.legend {
			margin-top: var(--space-md);
		}

		.legend-scale {
			width: 160px;
		}

		.legend-labels {
			width: 160px;
		}

		.findings-list li {
			padding: var(--space-sm) 0;
			font-size: var(--text-sm);
		}

		.pullquote {
			padding: var(--space-lg);
			margin: var(--space-xl) 0;
		}

		.pullquote blockquote {
			font-size: var(--text-lg);
		}

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
