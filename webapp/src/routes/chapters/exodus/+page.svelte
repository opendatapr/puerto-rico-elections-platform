<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { ChoroplethMap } from '$lib/components/maps';
	import { LineChart } from '$lib/components/charts';
	import { BarChart } from '$lib/components/charts';
	import { ScatterPlot } from '$lib/components/charts';
	import { createLossScale, createPovertyScale, DIVERGING_COLORS, CATEGORY_COLORS, SEQUENTIAL_LOSS_COLORS, SEQUENTIAL_POVERTY_COLORS } from '$lib/utils/colors';
	import { formatPercent, formatCompact, formatNumber, formatPercentChange } from '$lib/utils/format';
	import { language } from '$lib/stores/language';

	// Chapter metadata
	const chapterNum = 1;
	const totalSteps = 12;

	// Bilingual content for key sections
	const t = {
		en: {
			chapterTitle: 'The Great Exodus',
			lead: "Since 2006, Puerto Rico has hemorrhaged more than half a million residents. Every week for almost two decades, planes have carried families away from the island they called home. This is the story of the greatest population collapse in modern American history.",
			peopleLost: 'People Left',
			decline: 'Population Decline',
			muniLost: 'Municipalities Lost Residents',
			loading: 'Loading data...',
			whatWeLearned: 'What We\'ve Learned',
			keyTakeaways: 'Key Takeaways',
			sources: 'Sources',
			backTo: 'Back to',
			home: 'Home',
			nextChapter: 'Next Chapter',
			nextTitle: 'Democracy Under Strain',
			peak: '2004 (Peak)',
			popTimeline: 'Puerto Rico Population 2000-2020',
			popChangeMap: 'Population Change by Municipality (2010-2020)',
			topLoss: 'Municipalities with Greatest Population Loss',
			metroSJ: 'Metro San Juan',
			mariaCliff: 'The Maria Cliff (2017-2018)',
			povertyVsLoss: 'Poverty Rate vs Population Loss',
			povertyMap: 'Poverty Rate by Municipality',
			agingIsland: 'An Aging Island',
			whereTheyWent: 'Where They Went',
			newElectoralMap: 'The New Electoral Map',
			hurricaneMaria: 'Hurricane Maria',
			mariaNote: 'Sept 2017: 130,000+ leave in following year',
			prPopStates: 'Puerto Rican population in US states (2020)',
			absLoss: 'Absolute population loss 2010-2020',
			scatterNote: 'Each point is a municipality. Size indicates population.',
			legendPoverty: 'Poverty rate',
			legendPopChange: 'Population change',
			prPopulation: 'Puerto Rico Population',
			conclusionP1: "Puerto Rico's population collapse is unprecedented in modern American history. Over half a million people left the island between 2006 and 2020, driven by economic crisis, natural disaster, and the accumulated weight of decades of disinvestment.",
			conclusionP2: "The exodus was not uniform. Mountain communities and southern coastal towns suffered the deepest losses. The poorest municipalities lost the most. Those who left were disproportionately young and working-age, leaving behind an older, more vulnerable population.",
			conclusionP3: "The political implications are profound. A smaller, older, poorer electorate will shape Puerto Rico's future. The next chapter examines how these demographic shifts have affected voter turnout and civic participation across the island.",
			// Step content
			step0Title: 'A Nation at Its Peak',
			step0P1: 'In 2004, Puerto Rico reached its population zenith: <stat>3,826,878</stat> people called the island home. Families had deep roots here, some stretching back generations. Towns bustled with activity. Schools were full. The future seemed bright.',
			step0P2: 'Then came the unraveling. What began as a trickle would become a flood, as economic crisis, natural disaster, and years of austerity combined to trigger the largest peacetime population exodus in American history.',
			step0P3: 'Every number you\'ll see represents a family that made the agonizing choice to leave home.',
			step1Quote: 'No other American jurisdiction has experienced anything comparable to Puerto Rico\'s population collapse.',
			step1Citation: 'U.S. Census Bureau analysis, 2020',
			step1P1: 'After decades of growth, Puerto Rico\'s population began falling in 2006, coinciding with the end of federal tax incentives. Between <stat>2006 and 2020</stat>, the island lost <stat>{totalLost}</stat> residents.',
			step1P2: 'To put this in perspective: if New York State lost population at the same rate, it would lose 2.7 million people in 14 years.',
			step2Title: 'The Countdown',
			step2P1: 'Watch the counter. Every digit represents lives uprooted, communities fractured, families separated. The decline from <stat>3.8 million</stat> to <stat>3.3 million</stat> played out across countless individual dramas.',
			step2P2: 'A teacher who couldn\'t find work after school consolidations. A nurse recruited by a Florida hospital offering double the salary. A family fleeing after Hurricane Maria destroyed their home. A young professional seeking opportunities that the stagnant economy couldn\'t provide.',
			step2P3: 'The numbers are staggering, but behind each decimal point is a human story.',
			step3Title: 'The Geography of Loss',
			step3P1: 'The exodus touched every corner of the island, but not equally. The map reveals profound geographic disparities. Of Puerto Rico\'s <stat>78 municipalities</stat>, <stat>77</stat> lost population between 2010 and 2020.',
			step3P2: 'The darkest reds mark communities that lost more than a quarter of their residents in just a decade. <highlight>Guanica</highlight> suffered the steepest decline: <stat>{guanicaLoss}%</stat>, or nearly one in three residents gone. Southern coastal towns and mountain communities were hit hardest.',
			step3P3: 'The average municipality lost <stat>{avgLoss}</stat> of its population. Only <highlight>Rincon</highlight>, a beach town popular with surfers and American expats, managed to grow.',
			step4Title: 'The Biggest Losses',
			step4P1: 'In absolute terms, the largest cities lost the most people, simply because they had more to lose. But these numbers represent urban cores hollowing out, neighborhoods becoming ghost towns, apartment buildings standing empty.',
			step4P2: '<highlight>San Juan</highlight>, the capital, lost <stat>{sjLost}</stat> people, a decline of <stat>{sjPct}%</stat>. The historic city that once pulsed with nearly 400,000 residents now has barely 340,000. Entire barrios have depopulated.',
			step4P3: '<highlight>Ponce</highlight>, Puerto Rico\'s second city, lost <stat>{ponceLost}</stat> residents, nearly one in five. Its ornate plazas and historic center now serve a fraction of their former population.',
			step5Title: 'The Metro Exodus',
			step5P1: 'The San Juan metropolitan area, home to nearly half the island\'s population, experienced a devastating outflow. The six municipalities that make up metro San Juan lost a combined <stat>{metroLost}</stat> residents between 2010 and 2020.',
			step5P2: '<highlight>Catano</highlight>, a working-class municipality across the bay from San Juan, lost <stat>19.1%</stat> of its population. <highlight>Carolina</highlight>, home to the international airport, lost <stat>13.3%</stat>. Even wealthy <highlight>Guaynabo</highlight> lost <stat>8.6%</stat>.',
			step5P3: 'These weren\'t just numbers on a census form. Schools closed. Businesses shuttered. Property values collapsed. The urban fabric itself began to fray.',
			step6Title: 'The Maria Cliff',
			step6P1: 'On September 20, 2017, Hurricane Maria made landfall as a Category 4 storm, devastating the island\'s infrastructure. The power grid collapsed completely. Thousands died. And then came the second wave of destruction: the exodus.',
			step6P2: 'In the year following Maria, an estimated <stat>{mariaExodus}</stat> people left Puerto Rico. Look at the chart: the population line takes its steepest plunge between 2017 and 2018. This wasn\'t ordinary migration. It was displacement on a scale more commonly associated with war zones.',
			step6P3: 'Flights to the mainland were packed. FEMA hotels in Florida filled with families who had lost everything. Many who left "temporarily" never returned.',
			step7Title: 'Poverty Drove the Exodus',
			step7P1: 'The scatter plot reveals a troubling correlation: municipalities with higher poverty rates experienced greater population losses. Economic desperation pushed people away.',
			step7P2: 'If you can\'t find work, if your children\'s schools are closing, if the hospital is understaffed, why stay? The <stat>poorest communities</stat> had the least capacity to hold onto their residents.',
			step7P3: 'Community ties and family land kept some rooted despite hardship, but the overall pattern is clear: poverty and exodus go hand in hand.',
			step8Title: 'The Poverty Map',
			step8P1: 'Puerto Rico\'s poverty rate of <stat>43%</stat> is more than triple that of Mississippi, the poorest US state. The map shows this burden is not evenly distributed. Mountain municipalities like <highlight>Guanica</highlight> (<stat>64.8%</stat> poverty), <highlight>Adjuntas</highlight> (<stat>62%</stat>), and <highlight>Vieques</highlight> (<stat>59.5%</stat>) face grinding, persistent deprivation.',
			step8P2: 'These are the communities most likely to lose young people seeking opportunity elsewhere. They\'re also the communities least able to provide services to the older, poorer population that remains behind.',
			step8P3: 'The exodus and poverty form a vicious cycle: people leave because of poverty, and their departure deepens the poverty of those who stay.',
			step9Title: 'Who Left Behind',
			step9P1: 'The exodus wasn\'t random. Working-age adults with education and skills were most likely to leave, seeking opportunities on the mainland. The island\'s median age jumped from <stat>{medianAge2010}</stat> years in 2010 to <stat>{medianAge2020}</stat> years in 2020.',
			step9P2: 'The working-age population (25-54) declined by <stat>{workingAgeDecline}</stat>, while the elderly population grew by <stat>22.3%</stat>. Puerto Rico is rapidly becoming one of the oldest jurisdictions in the United States.',
			step9P3: 'This demographic inversion creates its own problems: fewer workers to support more retirees, fewer tax dollars for public services, fewer young families to keep schools open and communities vibrant.',
			step10Title: 'New Puerto Rican Capitals',
			step10P1: 'Where did they go? Florida became the primary destination, its Puerto Rican population swelling to <stat>1.2 million</stat> by 2020. Central Florida in particular saw explosive growth, transforming the I-4 corridor into a major Puerto Rican population center.',
			step10P2: 'Traditional destinations like New York and Connecticut continued to draw migrants, while newer paths led to Pennsylvania and Texas. The Puerto Rican diaspora now outnumbers the island population, with over 5.8 million Puerto Ricans living on the mainland.',
			step10P3: 'These new communities maintain strong ties to the island. Remittances flow back. Family visits fill holiday flights. But the center of gravity of Puerto Rican life has shifted, perhaps permanently.',
			step11Title: 'Electoral Implications',
			step11P1: 'Population loss translates directly into political power loss. Between 2012 and 2020, voter registration in Puerto Rico dropped by over <stat>400,000</stat>. The electorate that remains is older, poorer, and more rural.',
			step11P2: 'This demographic shift has profound implications for Puerto Rico\'s political future. Which municipalities will retain enough population to hold political sway? How will the remaining voters reshape the island\'s politics?',
			step11P3: 'The exodus didn\'t just empty neighborhoods. It rewrote the political map of Puerto Rico, changing the balance of power in ways that will take years to fully understand.',
			takeaway1: '<stat>{totalLost}</stat> people left Puerto Rico since 2004',
			takeaway2: '77 of 78 municipalities lost population between 2010-2020',
			takeaway3: 'Hurricane Maria triggered <stat>{mariaExodus}</stat> departures in one year',
			takeaway4: 'Poverty and population loss are strongly correlated',
			takeaway5: 'The median age rose from 36.9 to {medianAge2020} years'
		},
		es: {
			chapterTitle: 'El Gran Exodo',
			lead: 'Desde 2006, Puerto Rico ha perdido mas de medio millon de residentes. Cada semana durante casi dos decadas, aviones han llevado familias lejos de la isla que llamaban hogar. Esta es la historia del mayor colapso poblacional en la historia moderna de Estados Unidos.',
			peopleLost: 'Personas se Fueron',
			decline: 'Declive Poblacional',
			muniLost: 'Municipios Perdieron Residentes',
			loading: 'Cargando datos...',
			whatWeLearned: 'Lo que Hemos Aprendido',
			keyTakeaways: 'Conclusiones Clave',
			sources: 'Fuentes',
			backTo: 'Volver a',
			home: 'Inicio',
			nextChapter: 'Proximo Capitulo',
			nextTitle: 'Democracia Bajo Presion',
			peak: '2004 (Pico)',
			popTimeline: 'Poblacion de Puerto Rico 2000-2020',
			popChangeMap: 'Cambio Poblacional por Municipio (2010-2020)',
			topLoss: 'Municipios con Mayor Perdida de Poblacion',
			metroSJ: 'Metro San Juan',
			mariaCliff: 'El Precipicio de Maria (2017-2018)',
			povertyVsLoss: 'Tasa de Pobreza vs Perdida de Poblacion',
			povertyMap: 'Tasa de Pobreza por Municipio',
			agingIsland: 'Una Isla que Envejece',
			whereTheyWent: 'A Donde Fueron',
			newElectoralMap: 'El Nuevo Mapa Electoral',
			hurricaneMaria: 'Huracan Maria',
			mariaNote: 'Sept 2017: 130,000+ se van en el ano siguiente',
			prPopStates: 'Poblacion puertorriquena en estados de EE.UU. (2020)',
			absLoss: 'Perdida de poblacion absoluta 2010-2020',
			scatterNote: 'Cada punto es un municipio. El tamano indica poblacion.',
			legendPoverty: 'Tasa de pobreza',
			legendPopChange: 'Cambio poblacional',
			prPopulation: 'Poblacion de Puerto Rico',
			conclusionP1: 'El colapso poblacional de Puerto Rico no tiene precedentes en la historia moderna estadounidense. Mas de medio millon de personas dejaron la isla entre 2006 y 2020, impulsados por la crisis economica, el desastre natural y el peso acumulado de decadas de desinversion.',
			conclusionP2: 'El exodo no fue uniforme. Las comunidades montanosas y los pueblos costeros del sur sufrieron las perdidas mas profundas. Los municipios mas pobres perdieron mas. Los que se fueron eran desproporcionadamente jovenes y en edad laboral, dejando atras una poblacion mas vieja y vulnerable.',
			conclusionP3: 'Las implicaciones politicas son profundas. Un electorado mas pequeno, mas viejo y mas pobre dara forma al futuro de Puerto Rico. El proximo capitulo examina como estos cambios demograficos han afectado la participacion electoral y civica en toda la isla.',
			// Step content
			step0Title: 'Una Nacion en su Apogeo',
			step0P1: 'En 2004, Puerto Rico alcanzo su cenit poblacional: <stat>3,826,878</stat> personas llamaban a la isla su hogar. Las familias tenian raices profundas aqui, algunas remontandose generaciones. Los pueblos bullian de actividad. Las escuelas estaban llenas. El futuro parecia brillante.',
			step0P2: 'Luego vino el desmoronamiento. Lo que comenzo como un goteo se convertiria en una inundacion, cuando la crisis economica, el desastre natural y anos de austeridad se combinaron para desencadenar el mayor exodo poblacional en tiempos de paz en la historia estadounidense.',
			step0P3: 'Cada numero que veras representa una familia que tomo la angustiosa decision de dejar su hogar.',
			step1Quote: 'Ninguna otra jurisdiccion estadounidense ha experimentado algo comparable al colapso poblacional de Puerto Rico.',
			step1Citation: 'Analisis de la Oficina del Censo de EE.UU., 2020',
			step1P1: 'Despues de decadas de crecimiento, la poblacion de Puerto Rico comenzo a caer en 2006, coincidiendo con el fin de los incentivos fiscales federales. Entre <stat>2006 y 2020</stat>, la isla perdio <stat>{totalLost}</stat> residentes.',
			step1P2: 'Para ponerlo en perspectiva: si el estado de Nueva York perdiera poblacion al mismo ritmo, perderia 2.7 millones de personas en 14 anos.',
			step2Title: 'La Cuenta Regresiva',
			step2P1: 'Observa el contador. Cada digito representa vidas desarraigadas, comunidades fracturadas, familias separadas. El declive de <stat>3.8 millones</stat> a <stat>3.3 millones</stat> se desarrollo a traves de incontables dramas individuales.',
			step2P2: 'Una maestra que no pudo encontrar trabajo despues de las consolidaciones escolares. Una enfermera reclutada por un hospital de Florida que ofrecia el doble del salario. Una familia huyendo despues de que el Huracan Maria destruyera su hogar. Un joven profesional buscando oportunidades que la economia estancada no podia proveer.',
			step2P3: 'Los numeros son asombrosos, pero detras de cada punto decimal hay una historia humana.',
			step3Title: 'La Geografia de la Perdida',
			step3P1: 'El exodo toco cada rincon de la isla, pero no por igual. El mapa revela profundas disparidades geograficas. De los <stat>78 municipios</stat> de Puerto Rico, <stat>77</stat> perdieron poblacion entre 2010 y 2020.',
			step3P2: 'Los rojos mas oscuros marcan comunidades que perdieron mas de una cuarta parte de sus residentes en solo una decada. <highlight>Guanica</highlight> sufrio el declive mas pronunciado: <stat>{guanicaLoss}%</stat>, o casi uno de cada tres residentes se fue. Los pueblos costeros del sur y las comunidades montanosas fueron los mas afectados.',
			step3P3: 'El municipio promedio perdio <stat>{avgLoss}</stat> de su poblacion. Solo <highlight>Rincon</highlight>, un pueblo playero popular entre surfistas y expatriados estadounidenses, logro crecer.',
			step4Title: 'Las Mayores Perdidas',
			step4P1: 'En terminos absolutos, las ciudades mas grandes perdieron mas personas, simplemente porque tenian mas que perder. Pero estos numeros representan nucleos urbanos vaciandose, barrios convirtiendose en pueblos fantasma, edificios de apartamentos quedando vacios.',
			step4P2: '<highlight>San Juan</highlight>, la capital, perdio <stat>{sjLost}</stat> personas, un declive de <stat>{sjPct}%</stat>. La ciudad historica que una vez pulsaba con casi 400,000 residentes ahora tiene apenas 340,000. Barrios enteros se han despoblado.',
			step4P3: '<highlight>Ponce</highlight>, la segunda ciudad de Puerto Rico, perdio <stat>{ponceLost}</stat> residentes, casi uno de cada cinco. Sus ornamentadas plazas y centro historico ahora sirven a una fraccion de su antigua poblacion.',
			step5Title: 'El Exodo Metropolitano',
			step5P1: 'El area metropolitana de San Juan, hogar de casi la mitad de la poblacion de la isla, experimento una devastadora salida. Los seis municipios que componen el metro de San Juan perdieron un combinado de <stat>{metroLost}</stat> residentes entre 2010 y 2020.',
			step5P2: '<highlight>Catano</highlight>, un municipio de clase trabajadora al otro lado de la bahia de San Juan, perdio <stat>19.1%</stat> de su poblacion. <highlight>Carolina</highlight>, sede del aeropuerto internacional, perdio <stat>13.3%</stat>. Incluso el acaudalado <highlight>Guaynabo</highlight> perdio <stat>8.6%</stat>.',
			step5P3: 'Estos no eran solo numeros en un formulario del censo. Escuelas cerraron. Negocios clausuraron. Los valores de las propiedades colapsaron. El tejido urbano mismo comenzo a deshilacharse.',
			step6Title: 'El Precipicio de Maria',
			step6P1: 'El 20 de septiembre de 2017, el Huracan Maria toco tierra como tormenta de Categoria 4, devastando la infraestructura de la isla. La red electrica colapso completamente. Miles murieron. Y luego vino la segunda ola de destruccion: el exodo.',
			step6P2: 'En el ano siguiente a Maria, se estima que <stat>{mariaExodus}</stat> personas dejaron Puerto Rico. Mira el grafico: la linea de poblacion toma su caida mas pronunciada entre 2017 y 2018. Esto no era migracion ordinaria. Era desplazamiento a una escala mas comunmente asociada con zonas de guerra.',
			step6P3: 'Los vuelos al continente estaban llenos. Los hoteles de FEMA en Florida se llenaron de familias que lo habian perdido todo. Muchos que se fueron "temporalmente" nunca regresaron.',
			step7Title: 'La Pobreza Impulso el Exodo',
			step7P1: 'El grafico de dispersion revela una correlacion preocupante: los municipios con mayores tasas de pobreza experimentaron mayores perdidas de poblacion. La desesperacion economica empujo a la gente a irse.',
			step7P2: 'Si no puedes encontrar trabajo, si las escuelas de tus hijos estan cerrando, si el hospital no tiene suficiente personal, ¿por que quedarse? Las <stat>comunidades mas pobres</stat> tenian la menor capacidad para retener a sus residentes.',
			step7P3: 'Los lazos comunitarios y las tierras familiares mantuvieron a algunos arraigados a pesar de las dificultades, pero el patron general es claro: pobreza y exodo van de la mano.',
			step8Title: 'El Mapa de la Pobreza',
			step8P1: 'La tasa de pobreza de Puerto Rico del <stat>43%</stat> es mas del triple que la de Mississippi, el estado mas pobre de EE.UU. El mapa muestra que esta carga no esta distribuida uniformemente. Municipios montanosos como <highlight>Guanica</highlight> (<stat>64.8%</stat> de pobreza), <highlight>Adjuntas</highlight> (<stat>62%</stat>) y <highlight>Vieques</highlight> (<stat>59.5%</stat>) enfrentan privacion persistente y agobiante.',
			step8P2: 'Estas son las comunidades con mayor probabilidad de perder jovenes que buscan oportunidades en otros lugares. Tambien son las comunidades menos capaces de proveer servicios a la poblacion mas vieja y pobre que se queda.',
			step8P3: 'El exodo y la pobreza forman un ciclo vicioso: la gente se va por la pobreza, y su partida profundiza la pobreza de los que se quedan.',
			step9Title: 'Quienes se Quedaron',
			step9P1: 'El exodo no fue aleatorio. Los adultos en edad laboral con educacion y habilidades tenian mas probabilidades de irse, buscando oportunidades en el continente. La edad mediana de la isla salto de <stat>{medianAge2010}</stat> anos en 2010 a <stat>{medianAge2020}</stat> anos en 2020.',
			step9P2: 'La poblacion en edad laboral (25-54) disminuyo en <stat>{workingAgeDecline}</stat>, mientras que la poblacion de adultos mayores crecio en <stat>22.3%</stat>. Puerto Rico se esta convirtiendo rapidamente en una de las jurisdicciones mas envejecidas de Estados Unidos.',
			step9P3: 'Esta inversion demografica crea sus propios problemas: menos trabajadores para mantener a mas jubilados, menos dolares de impuestos para servicios publicos, menos familias jovenes para mantener las escuelas abiertas y las comunidades vibrantes.',
			step10Title: 'Nuevas Capitales Puertorriquenas',
			step10P1: '¿A donde fueron? Florida se convirtio en el destino principal, su poblacion puertorriquena creciendo a <stat>1.2 millones</stat> para 2020. El centro de Florida en particular vio un crecimiento explosivo, transformando el corredor I-4 en un importante centro de poblacion puertorriquena.',
			step10P2: 'Destinos tradicionales como Nueva York y Connecticut continuaron atrayendo migrantes, mientras nuevos caminos llevaron a Pensilvania y Texas. La diaspora puertorriquena ahora supera en numero a la poblacion de la isla, con mas de 5.8 millones de puertorriquenos viviendo en el continente.',
			step10P3: 'Estas nuevas comunidades mantienen fuertes lazos con la isla. Las remesas fluyen de regreso. Las visitas familiares llenan los vuelos de vacaciones. Pero el centro de gravedad de la vida puertorriquena se ha desplazado, quizas permanentemente.',
			step11Title: 'Implicaciones Electorales',
			step11P1: 'La perdida de poblacion se traduce directamente en perdida de poder politico. Entre 2012 y 2020, el registro de votantes en Puerto Rico cayo en mas de <stat>400,000</stat>. El electorado que queda es mas viejo, mas pobre y mas rural.',
			step11P2: 'Este cambio demografico tiene profundas implicaciones para el futuro politico de Puerto Rico. ¿Cuales municipios retendran suficiente poblacion para mantener influencia politica? ¿Como reshapearan los votantes restantes la politica de la isla?',
			step11P3: 'El exodo no solo vacio vecindarios. Reescribio el mapa politico de Puerto Rico, cambiando el equilibrio de poder de maneras que tomaran anos en comprenderse completamente.',
			takeaway1: '<stat>{totalLost}</stat> personas dejaron Puerto Rico desde 2004',
			takeaway2: '77 de 78 municipios perdieron poblacion entre 2010-2020',
			takeaway3: 'El Huracan Maria provoco <stat>{mariaExodus}</stat> partidas en un ano',
			takeaway4: 'La pobreza y la perdida de poblacion estan fuertemente correlacionadas',
			takeaway5: 'La edad mediana subio de 36.9 a {medianAge2020} anos'
		}
	};

	// Reactive content based on language
	let content = $derived(t[$language]);
	let chapterTitle = $derived(content.chapterTitle);

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
			result[muni] = data.poverty_rate; // Positive values for poverty scale
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

	// Color scales - sequential for loss data (light = no loss, dark red = severe loss)
	const populationColorScale = createLossScale([-30, 0]);
	// Poverty scale: light = low poverty, dark orange-red = high poverty
	const povertyColorScale = createPovertyScale([20, 65]);

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
			<span class="label">{$language === 'en' ? 'Chapter' : 'Capitulo'} {chapterNum}</span>
			<div class="accent-line"></div>
			<h1>{chapterTitle}</h1>
			<p class="lead">{content.lead}</p>
			<div class="lead-stats">
				<div class="stat-block">
					<span class="stat-value">{formatNumber(541004)}</span>
					<span class="stat-label">{content.peopleLost}</span>
				</div>
				<div class="stat-block">
					<span class="stat-value">14.1%</span>
					<span class="stat-label">{content.decline}</span>
				</div>
				<div class="stat-block">
					<span class="stat-value">77 {$language === 'en' ? 'of' : 'de'} 78</span>
					<span class="stat-label">{content.muniLost}</span>
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
					<p class="loading">{content.loading}</p>
				{:else if currentViz === 'map'}
					{#if currentStep === 0 || currentStep === 2}
						<!-- Animated counter display -->
						<div class="counter-display">
							<div class="counter-label">{content.prPopulation}</div>
							<div class="counter-value">{formatNumber(displayedPopulation)}</div>
							<div class="counter-year">{currentStep === 0 ? content.peak : '2020'}</div>
						</div>
					{:else}
						<h3 class="viz-title">{mapTitle}</h3>
						<ChoroplethMap
							data={mapData}
							colorScale={currentStep === 8 ? povertyColorScale : populationColorScale}
							tooltipFormat={(name, value) => {
								if (currentStep === 8) {
									return value !== undefined
										? `${name}: ${value.toFixed(1)}% ${$language === 'en' ? 'poverty' : 'pobreza'}`
										: name;
								}
								return value !== undefined
									? `${name}: ${value > 0 ? '+' : ''}${value.toFixed(1)}%`
									: name;
							}}
						/>
						{#if mapData.size > 0}
							<div class="legend">
								<span class="legend-label">{currentStep === 8 ? content.legendPoverty : content.legendPopChange}</span>
								<div class="legend-scale">
									{#if currentStep === 8}
										<span style="background: {povertyColorScale(30)}"></span>
										<span style="background: {povertyColorScale(45)}"></span>
										<span style="background: {povertyColorScale(60)}"></span>
									{:else}
										<span style="background: {populationColorScale(-25)}"></span>
										<span style="background: {populationColorScale(-12)}"></span>
										<span style="background: {populationColorScale(-3)}"></span>
									{/if}
								</div>
								<div class="legend-labels">
									{#if currentStep === 8}
										<span>30%</span>
										<span>45%</span>
										<span>60%+</span>
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
							xLabel={$language === 'en' ? 'Year' : 'Ano'}
							yLabel={$language === 'en' ? 'Population' : 'Poblacion'}
							showArea={true}
							showDots={true}
							xFormat={(v) => String(v)}
							yFormat={(v) => formatCompact(v)}
						/>
					</div>
					{#if currentStep === 6}
						<div class="chart-annotation">
							<span class="annotation-marker">{content.hurricaneMaria}</span>
							<span class="annotation-text">{content.mariaNote}</span>
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
							<p class="chart-note">{content.prPopStates}</p>
						{:else}
							<BarChart
								data={topLossMunicipalities()}
								width={500}
								height={400}
								horizontal={true}
								valueFormat={(v) => formatNumber(v)}
							/>
							<p class="chart-note">{content.absLoss}</p>
						{/if}
					</div>
				{:else if currentViz === 'scatter'}
					<h3 class="viz-title">{mapTitle}</h3>
					<div class="chart-container">
						<ScatterPlot
							data={povertyVsLossData()}
							width={500}
							height={400}
							xLabel={$language === 'en' ? 'Poverty Rate (%)' : 'Tasa de Pobreza (%)'}
							yLabel={$language === 'en' ? 'Population Loss (%)' : 'Perdida de Poblacion (%)'}
							showRegression={true}
							xFormat={(v) => `${v.toFixed(0)}%`}
							yFormat={(v) => `${v.toFixed(0)}%`}
						/>
					</div>
					<p class="chart-note">{content.scatterNote}</p>
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>{content.step0Title}</h3>
			<p>
				{@html content.step0P1.replace(/<stat>/g, '<span class="stat">').replace(/<\/stat>/g, '</span>')}
			</p>
			<p>
				{@html content.step0P2}
			</p>
			<p class="emphasis">
				{@html content.step0P3}
			</p>
		</Step>

		<Step active={currentStep === 1} index={1} variant="quote">
			{#snippet quote()}
				<p>{content.step1Quote}</p>
			{/snippet}
			{#snippet citation()}
				{content.step1Citation}
			{/snippet}
			<p>
				{@html content.step1P1
					.replace(/<stat>/g, '<span class="stat">')
					.replace(/<\/stat>/g, '</span>')
					.replace('{totalLost}', formatNumber(541004))}
			</p>
			<p>{content.step1P2}</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>{content.step2Title}</h3>
			<p>
				{@html content.step2P1.replace(/<stat>/g, '<span class="stat">').replace(/<\/stat>/g, '</span>')}
			</p>
			<p>{content.step2P2}</p>
			<p>{content.step2P3}</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>{content.step3Title}</h3>
			<p>
				{@html content.step3P1.replace(/<stat>/g, '<span class="stat">').replace(/<\/stat>/g, '</span>')}
			</p>
			<p>
				{@html content.step3P2
					.replace(/<stat>/g, '<span class="stat">')
					.replace(/<\/stat>/g, '</span>')
					.replace(/<highlight>/g, '<span class="highlight">')
					.replace(/<\/highlight>/g, '</span>')
					.replace('{guanicaLoss}', String(guanicaLoss))}
			</p>
			<p>
				{@html content.step3P3
					.replace(/<stat>/g, '<span class="stat">')
					.replace(/<\/stat>/g, '</span>')
					.replace(/<highlight>/g, '<span class="highlight">')
					.replace(/<\/highlight>/g, '</span>')
					.replace('{avgLoss}', formatPercentChange(avgLoss))}
			</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>{content.step4Title}</h3>
			<p>{content.step4P1}</p>
			<p>
				{@html content.step4P2
					.replace(/<stat>/g, '<span class="stat">')
					.replace(/<\/stat>/g, '</span>')
					.replace(/<highlight>/g, '<span class="highlight">')
					.replace(/<\/highlight>/g, '</span>')
					.replace('{sjLost}', formatNumber(56665))
					.replace('{sjPct}', String(sanJuanLoss))}
			</p>
			<p>
				{@html content.step4P3
					.replace(/<stat>/g, '<span class="stat">')
					.replace(/<\/stat>/g, '</span>')
					.replace(/<highlight>/g, '<span class="highlight">')
					.replace(/<\/highlight>/g, '</span>')
					.replace('{ponceLost}', formatNumber(Math.abs(ponceLoss)))}
			</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>{content.step5Title}</h3>
			<p>
				{@html content.step5P1
					.replace(/<stat>/g, '<span class="stat">')
					.replace(/<\/stat>/g, '</span>')
					.replace('{metroLost}', formatNumber(Math.abs(metroLoss)))}
			</p>
			<p>
				{@html content.step5P2
					.replace(/<stat>/g, '<span class="stat">')
					.replace(/<\/stat>/g, '</span>')
					.replace(/<highlight>/g, '<span class="highlight">')
					.replace(/<\/highlight>/g, '</span>')}
			</p>
			<p>{content.step5P3}</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>{content.step6Title}</h3>
			<p>{content.step6P1}</p>
			<p>
				{@html content.step6P2
					.replace(/<stat>/g, '<span class="stat">')
					.replace(/<\/stat>/g, '</span>')
					.replace('{mariaExodus}', formatNumber(mariaExodus))}
			</p>
			<p>{content.step6P3}</p>
		</Step>

		<Step active={currentStep === 7} index={7} variant="callout">
			<h3>{content.step7Title}</h3>
			<p>{content.step7P1}</p>
			<p>
				{@html content.step7P2.replace(/<stat>/g, '<span class="stat">').replace(/<\/stat>/g, '</span>')}
			</p>
			<p>{content.step7P3}</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>{content.step8Title}</h3>
			<p>
				{@html content.step8P1
					.replace(/<stat>/g, '<span class="stat">')
					.replace(/<\/stat>/g, '</span>')
					.replace(/<highlight>/g, '<span class="highlight">')
					.replace(/<\/highlight>/g, '</span>')}
			</p>
			<p>{content.step8P2}</p>
			<p>{content.step8P3}</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>{content.step9Title}</h3>
			<p>
				{@html content.step9P1
					.replace(/<stat>/g, '<span class="stat">')
					.replace(/<\/stat>/g, '</span>')
					.replace('{medianAge2010}', String(exodusData?.demographic_shifts?.median_age_2010 ?? 36.9))
					.replace('{medianAge2020}', String(medianAge2020))}
			</p>
			<p>
				{@html content.step9P2
					.replace(/<stat>/g, '<span class="stat">')
					.replace(/<\/stat>/g, '</span>')
					.replace('{workingAgeDecline}', formatPercentChange(workingAgeDecline))}
			</p>
			<p>{content.step9P3}</p>
		</Step>

		<Step active={currentStep === 10} index={10}>
			<h3>{content.step10Title}</h3>
			<p>
				{@html content.step10P1.replace(/<stat>/g, '<span class="stat">').replace(/<\/stat>/g, '</span>')}
			</p>
			<p>{content.step10P2}</p>
			<p>{content.step10P3}</p>
		</Step>

		<Step active={currentStep === 11} index={11}>
			<h3>{content.step11Title}</h3>
			<p>
				{@html content.step11P1.replace(/<stat>/g, '<span class="stat">').replace(/<\/stat>/g, '</span>')}
			</p>
			<p>{content.step11P2}</p>
			<p>{content.step11P3}</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>{content.whatWeLearned}</h2>
			<p>{content.conclusionP1}</p>
			<p>{content.conclusionP2}</p>
			<p>{content.conclusionP3}</p>

			<div class="key-takeaways">
				<h3>{content.keyTakeaways}</h3>
				<ul>
					{#if $language === 'en'}
						<li><span class="stat">{formatNumber(541004)}</span> people left Puerto Rico since 2004</li>
						<li>77 of 78 municipalities lost population between 2010-2020</li>
						<li>Hurricane Maria triggered <span class="stat">{formatNumber(mariaExodus)}</span> departures in one year</li>
						<li>Poverty and population loss are strongly correlated</li>
						<li>The median age rose from 36.9 to {medianAge2020} years</li>
					{:else}
						<li><span class="stat">{formatNumber(541004)}</span> personas dejaron Puerto Rico desde 2004</li>
						<li>77 de 78 municipios perdieron poblacion entre 2010-2020</li>
						<li>El Huracan Maria provoco <span class="stat">{formatNumber(mariaExodus)}</span> partidas en un ano</li>
						<li>La pobreza y la perdida de poblacion estan fuertemente correlacionadas</li>
						<li>La edad mediana subio de 36.9 a {medianAge2020} anos</li>
					{/if}
				</ul>
			</div>

			<div class="sources">
				<h3>{content.sources}</h3>
				<ul>
					<li><a href="https://www.census.gov/programs-surveys/popest.html" target="_blank" rel="noopener">U.S. Census Bureau</a> - Decennial Census 2010, 2020; Population Estimates Program 2004-2020</li>
					<li><a href="https://data.census.gov/" target="_blank" rel="noopener">American Community Survey 5-Year Estimates</a> - {$language === 'en' ? 'Poverty rates, demographic characteristics by municipality' : 'Tasas de pobreza, caracteristicas demograficas por municipio'}</li>
					<li>{$language === 'en' ? 'Puerto Rico Institute of Statistics - Migration data and demographic trends' : 'Instituto de Estadisticas de Puerto Rico - Datos de migracion y tendencias demograficas'}</li>
					<li><a href="https://www.pewresearch.org/short-reads/2022/08/02/key-facts-about-puerto-rican-population/" target="_blank" rel="noopener">Pew Research Center</a> - "Puerto Rican Population Declines on Island, Grows on U.S. Mainland" (2022)</li>
					<li><a href="https://centropr.hunter.cuny.edu/" target="_blank" rel="noopener">Center for Puerto Rican Studies</a> - {$language === 'en' ? 'Post-Hurricane Maria migration analysis (2018)' : 'Analisis de migracion post-Huracan Maria (2018)'}</li>
					<li>Federal Reserve Bank of New York - {$language === 'en' ? 'Economic conditions in Puerto Rico (2014-2020)' : 'Condiciones economicas en Puerto Rico (2014-2020)'}</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/" class="nav-link prev">
					<span class="nav-direction">{content.backTo}</span>
					<span class="nav-title">{content.home}</span>
				</a>
				<a href="{base}/chapters/turnout" class="nav-link next">
					<span class="nav-direction">{content.nextChapter}</span>
					<span class="nav-title">{content.nextTitle}</span>
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
		animation: counterPulse 2s ease-in-out infinite;
	}

	@keyframes counterPulse {
		0%, 100% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.01);
		}
	}

	.counter-label {
		font-size: var(--text-xl);
		font-family: var(--font-display);
		color: var(--color-text-muted);
		margin-bottom: var(--space-md);
		letter-spacing: 0.05em;
		text-transform: uppercase;
	}

	.counter-value {
		font-family: var(--font-mono, monospace);
		font-size: 5rem;
		font-weight: var(--font-bold);
		color: var(--color-text);
		letter-spacing: -0.02em;
		transition: color 0.5s ease, text-shadow 0.5s ease;
		text-shadow: 0 0 40px rgba(212, 163, 115, 0.2);
	}

	.counter-year {
		font-size: var(--text-lg);
		color: var(--color-accent);
		margin-top: var(--space-md);
		font-weight: var(--font-semibold);
		padding: var(--space-xs) var(--space-md);
		background: var(--color-surface-elevated);
		border-radius: var(--radius-full);
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
		margin-top: var(--space-lg);
		padding: var(--space-md) var(--space-lg);
		background: linear-gradient(135deg, var(--color-surface-elevated) 0%, rgba(196, 30, 58, 0.1) 100%);
		border-radius: var(--radius-lg);
		border-left: 4px solid #c41e3a;
		animation: annotationSlideIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
	}

	@keyframes annotationSlideIn {
		from {
			opacity: 0;
			transform: translateX(-20px);
		}
		to {
			opacity: 1;
			transform: translateX(0);
		}
	}

	.annotation-marker {
		font-family: var(--font-display);
		font-size: var(--text-lg);
		font-weight: var(--font-bold);
		color: #c41e3a;
		margin-bottom: var(--space-xs);
	}

	.annotation-text {
		font-size: var(--text-base);
		color: var(--color-text-muted);
		line-height: 1.5;
	}

	.chart-note {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin-top: var(--space-md);
		text-align: center;
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

	.sources li a {
		color: var(--color-accent);
		text-decoration: underline;
		text-underline-offset: 2px;
	}

	.sources li a:hover {
		color: var(--color-accent-light, #e5c46d);
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
