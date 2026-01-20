<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { BarChart, LineChart } from '$lib/components/charts';
	import { CATEGORY_COLORS, PARTY_COLORS } from '$lib/utils/colors';
	import { language } from '$lib/stores/language';

	const chapterNum = 4;
	const totalSteps = 12;

	// Bilingual content
	const t = {
		en: {
			chapterTitle: '50 Years of Asking the Same Question',
			chapter: 'Chapter',
			lead: "Since 1967, Puerto Rico has held six referendums on its political status. Statehood. Commonwealth. Independence. The question never changes. Neither does Congress's answer: silence.",
			referendums: 'Referendums',
			yearsOfDebate: 'Years of Debate',
			congressionalActions: 'Congressional Actions',
			loading: 'Loading data...',
			// Timeline viz
			timelineTitle: 'Six Referendums, Six Decades',
			normalTurnout: 'Normal Turnout',
			boycotted: 'Boycotted',
			// Results viz
			resultsTitle: 'Plebiscite Results',
			format: 'format',
			boycottedBy: 'Boycotted by',
			turnout: 'Turnout',
			totalVotes: 'Total Votes',
			// Ballot viz
			ballotTitle: 'Ballot',
			ballotOffice: 'PLEBISCITE',
			ballotQuestion2020: '"Should Puerto Rico be admitted immediately into the Union as a State?"',
			ballotQuestion2012Q1: 'Q1: "Do you agree that Puerto Rico should continue to have its present form of territorial political status?"',
			ballotQuestion2012Q2: 'Q2: "Which status would you prefer?"',
			ballotQuestionGeneral: '"Vote for your preferred political status option:"',
			// Step 0 stat
			six: 'six',
			// Turnout viz
			turnoutTitle: 'Turnout Across All Plebiscites',
			turnoutSubtitle: 'Gray bars indicate boycotted elections',
			// Status options
			statehood: 'Statehood',
			commonwealth: 'Commonwealth',
			independence: 'Independence',
			freeAssociation: 'Free Association',
			noneOfAbove: 'None of Above',
			sovereignFreeAssociated: 'Sovereign Free Associated State',
			// Step titles
			step0Title: 'The Endless Question',
			step1Title: '1967: The First Vote',
			step2Title: '1993: Statehood Rising',
			step3Title: '1998: The Boycott Strategy',
			step4Title: 'The Boycott Playbook',
			step4CalloutLabel: 'Key Finding',
			step5Title: '2012: The Two-Question Gambit',
			step6Title: 'The Blank Ballot Controversy',
			step7Title: '2017: The Ghost Plebiscite',
			step8Title: '97% of Almost Nobody',
			// Comparison step content
			step8ComparisonBefore: '2012',
			step8ComparisonAfter: '2017',
			step8Before1: '61.2%',
			step8Before2: 'for statehood',
			step8Before3: '78.2% turnout',
			step8After1: '97.2%',
			step8After2: 'for statehood',
			step8After3: '23% turnout',
			step9Title: '2020: The Simple Question',
			step10Title: 'The Narrow Yes',
			step11Title: 'What Will It Take?',
			step11QuestionTitle: 'Will Puerto Rico ever get an answer?',
			// Step content
			step0p1: "Puerto Rico's political status has been contested since 1898, when the island became a U.S. territory after the Spanish-American War. For over a century, three options have dominated the debate: statehood (becoming the 51st state), independence (full sovereignty), and commonwealth (the current territorial arrangement).",
			step0p2: "Since 1967, Puerto Rico has held",
			step0p2b: "official referendums on this question. The results vary wildly depending on how the question is asked, who boycotts, and what options appear on the ballot.",
			step0p3: "One constant: Congress has never acted on any result.",
			step1p1: "The inaugural plebiscite offered voters three clear choices: statehood, commonwealth, or independence. The political context was specific: the Cold War made independence seem radical, and the island's economy depended on federal programs.",
			step1p2: "Commonwealth won decisively with",
			step1p2b: "of the vote. Statehood received just 39%. Independence, associated with socialist movements, garnered less than 1%.",
			step1p3: "The PPD, which had governed Puerto Rico since 1949 under the commonwealth model, claimed vindication. But statehood supporters noted that turnout was just 65.8%, lower than typical elections. The question wasn't settled; it was merely deferred.",
			step2p1: "Twenty-six years later, the political landscape had shifted. The PNP (pro-statehood) had governed for much of the intervening period. Puerto Rico's economy had grown, but so had concerns about federal tax benefits that might disappear with statehood.",
			step2p2: "The result was the closest race yet: commonwealth squeaked by with",
			step2p2b: "while statehood surged to 46.3%. Independence remained marginal at 4.4%.",
			step2p3: "For the first time, the status quo felt precarious. The 2-point margin suggested that one more election cycle might tip the balance. Puerto Rico was changing.",
			step3p1: "The 1998 plebiscite introduced a new element: the boycott. The PPD, unhappy with how their preferred option was defined on the ballot, called on supporters to vote for \"None of the Above\" instead of the listed commonwealth option.",
			step3p2: "The ballot itself was unprecedented: five options including \"None of the Above.\" This made the vote more a protest than a mandate.",
			step3p3: "The PPD's strategy worked brilliantly. \"None of the Above\" won with",
			step3p3b: "while statehood received 46.5%. The result delegitimized the entire exercise. Congress could claim there was no clear mandate for any change.",
			step4p1: "The 1998 result established a template that would haunt future plebiscites: a boycott could invalidate even a strong showing by one side.",
			step4p2: "Statehood supporters pointed out that 46.5% voted for their option, while only 0.1% voted for the commonwealth option on the ballot. But the",
			step4p2b: "\"None of the Above\"",
			step4p2c: "vote absorbed most commonwealth supporters, making the result uninterpretable.",
			step4p3: "The lesson was clear: how the question is asked matters as much as the answer.",
			step5p1: "After a 14-year hiatus, Governor Luis Fortuno (PNP) called another plebiscite. This time, the ballot used a clever two-question format designed to separate satisfaction with the status quo from preference among alternatives.",
			step5p2: "Question 1: Do you want to maintain the current territorial status?",
			step5p3: "Question 2: Which non-territorial option do you prefer: statehood, sovereignty in free association, or independence?",
			step5p4: "The format meant that even those who voted \"No\" on Q1 could choose statehood on Q2. Critics called it a",
			step5p4b: "rigged ballot",
			step6p1: "The results looked like a statehood landslide:",
			step6p1b: "chose statehood on Question 2. But there was a catch.",
			step6p2: "Over",
			step6p2b: "500,000 voters",
			step6p2c: "left Question 2 blank. They voted on Question 1, but refused to choose among alternatives they found inadequate. When you counted blank ballots as votes against statehood, the majority evaporated.",
			step6p3: "Congress responded by... requesting funds for a future binding referendum. That referendum never happened. The pattern held: vote, then wait for nothing.",
			step7p1: "The 2017 plebiscite will be remembered for one number:",
			step7p1b: "That was the turnout, the lowest in Puerto Rico's electoral history.",
			step7p2: "Both the PPD (pro-commonwealth) and PIP (pro-independence) called for a boycott. They objected to ballot design, timing, and the lack of federal commitment to honor the results.",
			step7p3: "The boycott was devastatingly effective. In a normal election, Puerto Rico sees turnout of 70-80%. This time, barely one in four registered voters participated.",
			step8p1: "Among those who did vote, statehood won overwhelmingly:",
			step8p1b: "It was the highest percentage ever recorded for any status option.",
			step8p2: "It was also the most meaningless. When three-quarters of the electorate stays home, a \"win\" carries no democratic legitimacy. Congress dismissed the results immediately.",
			step8p3: "The 2017 plebiscite became a cautionary tale: you can't achieve political change through a vote your opponents refuse to recognize.",
			step9p1: "After the farce of 2017, Puerto Rico tried something different. The 2020 referendum posed the simplest possible question:",
			step9p2: "\"Should Puerto Rico be admitted immediately into the Union as a State?",
			step9p2b: "Yes",
			step9p2c: "or",
			step9p2d: "No",
			step9p3: "No complex ballot. No multiple options. No room for \"None of the Above.\" Just a direct question about statehood, run alongside the general election to ensure turnout.",
			step10p1: "For the first time, a simple majority voted",
			step10p1b: "Yes",
			step10p1c: "on a straightforward statehood question. The margin: 52.5% to 47.5%.",
			step10p2: "655,505 Puerto Ricans voted Yes. 592,671 voted No. The difference:",
			step10p2b: "62,834 votes",
			step10p2c: "about 2.5 percentage points.",
			step10p3: "There was no boycott. Turnout (54.7%) was lower than the concurrent gubernatorial election, but not dramatically so. For statehood supporters, this was the cleanest mandate yet.",
			step11p1: "Congress introduced HR 1522, a bill to admit Puerto Rico as a state based on the referendum result. It did not pass. The Senate took no action. The pattern held.",
			step11p2: "Since 1967, Puerto Rico has asked the same question six times. The answers have varied: 39% for statehood, 46%, 47%, 61%, 97%, 52.5%. What hasn't varied is the federal response.",
			step11p3: "After 53 years of asking, Puerto Rico is still waiting for an answer.",
			// Conclusion
			conclusionTitle: "The Numbers Don't Lie, But They Don't Decide",
			tableYear: 'Year',
			tableStatehood: 'Statehood',
			tableTurnout: 'Turnout',
			tableNote: 'Note',
			tableCongress: 'Congress',
			keyTakeaways: 'Key Takeaways',
			takeaway1Title: 'Format matters:',
			takeaway1: 'Results swing wildly based on ballot design. The 2012 two-question format yielded 61% for statehood; the 2020 Yes/No format yielded 52.5%.',
			takeaway2Title: 'Boycotts work:',
			takeaway2: 'When the PPD boycotted in 1998 and 2017, they effectively nullified the results. A referendum without broad participation has no legitimacy.',
			takeaway3Title: 'Trend is upward:',
			takeaway3: 'Statehood support has grown from 39% (1967) to 52.5% (2020). Generational change and economic crisis have shifted preferences.',
			takeaway4Title: 'Congress decides:',
			takeaway4: "Ultimately, no referendum is binding. Puerto Rico can vote however it wants; admission requires an act of Congress.",
			sources: 'Sources',
			source1: 'Official plebiscite results 1967-2020',
			source2: '"Puerto Rico: Information on How Statehood Would Potentially Affect Selected Federal Programs and Revenue Sources" (2014)',
			source3: '"Political Status of Puerto Rico: Options for Congress" (2017)',
			// Navigation
			previous: 'Previous',
			nextChapter: 'Next Chapter',
			prevTitle: 'The Shrinking Electorate',
			nextTitle: 'The 52.5% Threshold'
		},
		es: {
			chapterTitle: '50 Anos Haciendo la Misma Pregunta',
			chapter: 'Capitulo',
			lead: 'Desde 1967, Puerto Rico ha celebrado seis referendos sobre su estatus politico. Estadidad. Estado Libre Asociado. Independencia. La pregunta nunca cambia. Tampoco la respuesta del Congreso: silencio.',
			referendums: 'Referendos',
			yearsOfDebate: 'Anos de Debate',
			congressionalActions: 'Acciones del Congreso',
			loading: 'Cargando datos...',
			// Timeline viz
			timelineTitle: 'Seis Referendos, Seis Decadas',
			normalTurnout: 'Participacion Normal',
			boycotted: 'Boicoteado',
			// Results viz
			resultsTitle: 'Resultados del Plebiscito',
			format: 'formato',
			boycottedBy: 'Boicoteado por',
			turnout: 'Participacion',
			totalVotes: 'Votos Totales',
			// Ballot viz
			ballotTitle: 'Papeleta',
			ballotOffice: 'PLEBISCITO',
			ballotQuestion2020: '"Debe Puerto Rico ser admitido inmediatamente a la Union como un Estado?"',
			ballotQuestion2012Q1: 'P1: "Esta usted de acuerdo con que Puerto Rico continue teniendo su forma actual de estatus politico territorial?"',
			ballotQuestion2012Q2: 'P2: "Cual estatus preferiria?"',
			ballotQuestionGeneral: '"Vote por su opcion de estatus politico preferida:"',
			// Step 0 stat
			six: 'seis',
			// Turnout viz
			turnoutTitle: 'Participacion en Todos los Plebiscitos',
			turnoutSubtitle: 'Las barras grises indican elecciones boicoteadas',
			// Status options
			statehood: 'Estadidad',
			commonwealth: 'Estado Libre Asociado',
			independence: 'Independencia',
			freeAssociation: 'Libre Asociacion',
			noneOfAbove: 'Ninguna de las Anteriores',
			sovereignFreeAssociated: 'Estado Libre Asociado Soberano',
			// Step titles
			step0Title: 'La Pregunta Interminable',
			step1Title: '1967: El Primer Voto',
			step2Title: '1993: La Estadidad en Ascenso',
			step3Title: '1998: La Estrategia del Boicot',
			step5Title: '2012: La Estratagema de Dos Preguntas',
			step6Title: 'La Controversia de la Papeleta en Blanco',
			step7Title: '2017: El Plebiscito Fantasma',
			step8Title: '97% de Casi Nadie',
			// Comparison step content
			step8ComparisonBefore: '2012',
			step8ComparisonAfter: '2017',
			step8Before1: '61.2%',
			step8Before2: 'por estadidad',
			step8Before3: '78.2% participacion',
			step8After1: '97.2%',
			step8After2: 'por estadidad',
			step8After3: '23% participacion',
			step9Title: '2020: La Pregunta Simple',
			step10Title: 'El Si Estrecho',
			step11Title: 'Que Tomara?',
			step11QuestionTitle: 'Obtendra Puerto Rico alguna vez una respuesta?',
			// Step content
			step0p1: 'El estatus politico de Puerto Rico ha sido disputado desde 1898, cuando la isla se convirtio en territorio de EE.UU. tras la Guerra Hispano-Estadounidense. Durante mas de un siglo, tres opciones han dominado el debate: estadidad (convertirse en el estado 51), independencia (soberania total) y estado libre asociado (el arreglo territorial actual).',
			step0p2: 'Desde 1967, Puerto Rico ha celebrado',
			step0p2b: 'referendos oficiales sobre esta cuestion. Los resultados varian drasticamente dependiendo de como se formula la pregunta, quien boicotea y que opciones aparecen en la papeleta.',
			step0p3: 'Una constante: el Congreso nunca ha actuado sobre ningun resultado.',
			step1p1: 'El plebiscito inaugural ofrecio a los votantes tres opciones claras: estadidad, estado libre asociado o independencia. El contexto politico era especifico: la Guerra Fria hacia que la independencia pareciera radical, y la economia de la isla dependia de programas federales.',
			step1p2: 'El estado libre asociado gano decisivamente con',
			step1p2b: 'del voto. La estadidad recibio solo 39%. La independencia, asociada con movimientos socialistas, obtuvo menos del 1%.',
			step1p3: 'El PPD, que habia gobernado Puerto Rico desde 1949 bajo el modelo de estado libre asociado, reclamo vindicacion. Pero los defensores de la estadidad notaron que la participacion fue solo 65.8%, menor que en elecciones tipicas. La cuestion no se resolvio; simplemente se aplazaba.',
			step2p1: 'Veintiseis anos despues, el panorama politico habia cambiado. El PNP (pro-estadidad) habia gobernado durante gran parte del periodo intermedio. La economia de Puerto Rico habia crecido, pero tambien las preocupaciones sobre los beneficios fiscales federales que podrian desaparecer con la estadidad.',
			step2p2: 'El resultado fue la carrera mas cerrada hasta entonces: el estado libre asociado gano por poco con',
			step2p2b: 'mientras la estadidad subio a 46.3%. La independencia permanecio marginal con 4.4%.',
			step2p3: 'Por primera vez, el statu quo se sentia precario. El margen de 2 puntos sugeria que un ciclo electoral mas podria inclinar la balanza. Puerto Rico estaba cambiando.',
			step3p1: 'El plebiscito de 1998 introdujo un nuevo elemento: el boicot. El PPD, descontento con como se definia su opcion preferida en la papeleta, llamo a sus seguidores a votar por "Ninguna de las Anteriores" en lugar de la opcion de estado libre asociado listada.',
			step3p2: 'La papeleta misma fue sin precedentes: cinco opciones incluyendo "Ninguna de las Anteriores". Esto convirtio el voto mas en una protesta que en un mandato.',
			step3p3: 'La estrategia del PPD funciono brillantemente. "Ninguna de las Anteriores" gano con',
			step3p3b: 'mientras la estadidad recibio 46.5%. El resultado deslegitimo todo el ejercicio. El Congreso podia afirmar que no habia mandato claro para ningun cambio.',
			step4Title: 'El Manual del Boicot',
			step4CalloutLabel: 'Hallazgo Clave',
			step4p1: 'El resultado de 1998 establecio una plantilla que perseguiria futuros plebiscitos: un boicot podia invalidar incluso una fuerte muestra de un lado.',
			step4p2: 'Los defensores de la estadidad senalaron que 46.5% voto por su opcion, mientras que solo 0.1% voto por la opcion de estado libre asociado en la papeleta. Pero el voto de',
			step4p2b: '"Ninguna de las Anteriores"',
			step4p2c: 'absorbio a la mayoria de los simpatizantes del estado libre asociado, haciendo el resultado ininterpretable.',
			step4p3: 'La leccion era clara: como se hace la pregunta importa tanto como la respuesta.',
			step5p1: 'Despues de un hiato de 14 anos, el gobernador Luis Fortuno (PNP) convoco otro plebiscito. Esta vez, la papeleta uso un ingenioso formato de dos preguntas disenado para separar la satisfaccion con el statu quo de la preferencia entre alternativas.',
			step5p2: 'Pregunta 1: Desea mantener el estatus territorial actual?',
			step5p3: 'Pregunta 2: Cual opcion no territorial prefiere: estadidad, soberania en libre asociacion, o independencia?',
			step5p4: 'El formato significaba que incluso quienes votaron "No" en la P1 podian elegir estadidad en la P2. Los criticos lo llamaron una',
			step5p4b: 'papeleta manipulada',
			step6p1: 'Los resultados parecian un triunfo arrollador de la estadidad:',
			step6p1b: 'eligio estadidad en la Pregunta 2. Pero habia una trampa.',
			step6p2: 'Mas de',
			step6p2b: '500,000 votantes',
			step6p2c: 'dejaron la Pregunta 2 en blanco. Votaron en la Pregunta 1, pero se negaron a elegir entre alternativas que encontraban inadecuadas. Cuando contabas las papeletas en blanco como votos contra la estadidad, la mayoria se evaporaba.',
			step6p3: 'El Congreso respondio... solicitando fondos para un futuro referendum vinculante. Ese referendum nunca ocurrio. El patron se mantuvo: votar, luego esperar nada.',
			step7p1: 'El plebiscito de 2017 sera recordado por un numero:',
			step7p1b: 'Esa fue la participacion, la mas baja en la historia electoral de Puerto Rico.',
			step7p2: 'Tanto el PPD (pro-estado libre asociado) como el PIP (pro-independencia) llamaron al boicot. Se opusieron al diseno de la papeleta, el momento y la falta de compromiso federal para honrar los resultados.',
			step7p3: 'El boicot fue devastadoramente efectivo. En una eleccion normal, Puerto Rico ve participacion del 70-80%. Esta vez, apenas uno de cada cuatro votantes registrados participo.',
			step8p1: 'Entre quienes si votaron, la estadidad gano abrumadoramente:',
			step8p1b: 'Fue el porcentaje mas alto jamas registrado para cualquier opcion de estatus.',
			step8p2: 'Tambien fue el mas carente de significado. Cuando tres cuartos del electorado se queda en casa, una "victoria" no tiene legitimidad democratica. El Congreso desestimo los resultados inmediatamente.',
			step8p3: 'El plebiscito de 2017 se convirtio en una historia de advertencia: no puedes lograr cambio politico a traves de un voto que tus oponentes se niegan a reconocer.',
			step9p1: 'Despues de la farsa de 2017, Puerto Rico intento algo diferente. El referendum de 2020 planteo la pregunta mas simple posible:',
			step9p2: '"Debe Puerto Rico ser admitido inmediatamente a la Union como un Estado?',
			step9p2b: 'Si',
			step9p2c: 'o',
			step9p2d: 'No',
			step9p3: 'Sin papeleta compleja. Sin opciones multiples. Sin espacio para "Ninguna de las Anteriores". Solo una pregunta directa sobre la estadidad, realizada junto a la eleccion general para asegurar participacion.',
			step10p1: 'Por primera vez, una mayoria simple voto',
			step10p1b: 'Si',
			step10p1c: 'en una pregunta directa sobre estadidad. El margen: 52.5% a 47.5%.',
			step10p2: '655,505 puertorriquenos votaron Si. 592,671 votaron No. La diferencia:',
			step10p2b: '62,834 votos',
			step10p2c: 'aproximadamente 2.5 puntos porcentuales.',
			step10p3: 'No hubo boicot. La participacion (54.7%) fue menor que la eleccion gubernamental concurrente, pero no dramaticamente. Para los defensores de la estadidad, este fue el mandato mas limpio hasta ahora.',
			step11p1: 'El Congreso presento HR 1522, un proyecto de ley para admitir a Puerto Rico como estado basado en el resultado del referendum. No paso. El Senado no tomo accion. El patron se mantuvo.',
			step11p2: 'Desde 1967, Puerto Rico ha hecho la misma pregunta seis veces. Las respuestas han variado: 39% para estadidad, 46%, 47%, 61%, 97%, 52.5%. Lo que no ha variado es la respuesta federal.',
			step11p3: 'Despues de 53 anos de preguntar, Puerto Rico sigue esperando una respuesta.',
			// Conclusion
			conclusionTitle: 'Los Numeros No Mienten, Pero No Deciden',
			tableYear: 'Ano',
			tableStatehood: 'Estadidad',
			tableTurnout: 'Participacion',
			tableNote: 'Nota',
			tableCongress: 'Congreso',
			keyTakeaways: 'Conclusiones Clave',
			takeaway1Title: 'El formato importa:',
			takeaway1: 'Los resultados varian drasticamente segun el diseno de la papeleta. El formato de dos preguntas de 2012 produjo 61% para estadidad; el formato Si/No de 2020 produjo 52.5%.',
			takeaway2Title: 'Los boicots funcionan:',
			takeaway2: 'Cuando el PPD boicoteo en 1998 y 2017, efectivamente anulo los resultados. Un referendum sin amplia participacion no tiene legitimidad.',
			takeaway3Title: 'La tendencia es ascendente:',
			takeaway3: 'El apoyo a la estadidad ha crecido de 39% (1967) a 52.5% (2020). El cambio generacional y la crisis economica han cambiado las preferencias.',
			takeaway4Title: 'El Congreso decide:',
			takeaway4: 'En ultima instancia, ningun referendum es vinculante. Puerto Rico puede votar como quiera; la admision requiere un acto del Congreso.',
			sources: 'Fuentes',
			source1: 'Resultados oficiales de plebiscitos 1967-2020',
			source2: '"Puerto Rico: Informacion sobre Como la Estadidad Podria Afectar Programas Federales Seleccionados y Fuentes de Ingresos" (2014)',
			source3: '"Estatus Politico de Puerto Rico: Opciones para el Congreso" (2017)',
			// Navigation
			previous: 'Anterior',
			nextChapter: 'Proximo Capitulo',
			prevTitle: 'El Electorado Menguante',
			nextTitle: 'El Umbral del 52.5%'
		}
	};

	// Reactive content based on language
	let content = $derived(t[$language]);
	let chapterTitle = $derived(content.chapterTitle);

	let currentStep = $state(0);
	let loading = $state(true);

	// Plebiscite data types
	interface Plebiscite {
		year: number;
		statehood: number;
		commonwealth: number;
		independence: number;
		freeAssociation?: number;
		noneOfAbove?: number;
		turnout: number;
		totalVotes: number;
		statehoodVotes: number;
		question: string;
		boycott: boolean;
		boycottParty?: string;
		context: string;
		winner: string;
		congressResponse: string;
		ballotOptions: string[];
	}

	interface ChapterData {
		plebiscites: Plebiscite[];
		statusColors: Record<string, string>;
		summary: {
			totalReferendums: number;
			yearsOfDebate: number;
			congressionalActions: number;
		};
	}

	let plebiscites = $state<Plebiscite[]>([]);

	// Status options colors - consistent theming
	let STATUS_COLORS = $state<Record<string, string>>({
		statehood: '#1e4d8c',      // PNP blue
		commonwealth: '#c41e3a',   // PPD red
		independence: '#228b22',   // PIP green
		freeAssociation: '#9b59b6', // Purple
		noneOfAbove: '#6b7280',    // Gray
		blank: '#d4a373'          // Tan
	});

	// Load data from JSON
	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/chapters/plebiscites.json`);
			const data: ChapterData = await response.json();
			plebiscites = data.plebiscites;
			STATUS_COLORS = data.statusColors;
		} catch (err) {
			console.error('Failed to load plebiscites data:', err);
		} finally {
			loading = false;
		}
	});

	let activeYear = $state(1967);
	let activePlebiscite = $derived(plebiscites.find(p => p.year === activeYear) || plebiscites[0]);
	let activeViz = $state<'timeline' | 'results' | 'turnout' | 'ballot'>('timeline');

	// Translated status labels
	let statusLabels = $derived({
		statehood: content.statehood,
		commonwealth: content.commonwealth,
		independence: content.independence,
		freeAssociation: content.freeAssociation,
		noneOfAbove: content.noneOfAbove
	});

	// Ballot option translations (English -> localized)
	let ballotOptionTranslations = $derived<Record<string, string>>({
		// Common status options
		'Statehood': content.statehood,
		'Commonwealth (ELA)': content.commonwealth,
		'Independence': content.independence,
		'Free Association': content.freeAssociation,
		'None of the Above': content.noneOfAbove,
		'Territorial Commonwealth': content.commonwealth,
		'Free Association/Independence': $language === 'en' ? 'Free Association/Independence' : 'Libre Asociacion/Independencia',
		'Current Territory': $language === 'en' ? 'Current Territory' : 'Territorio Actual',
		// 2012 ballot
		'Q1: Keep status? (Yes/No)': $language === 'en' ? 'Q1: Keep status? (Yes/No)' : 'P1: Mantener estatus? (Si/No)',
		'Q2: Statehood / Free Association / Independence': $language === 'en' ? 'Q2: Statehood / Free Association / Independence' : 'P2: Estadidad / Libre Asociacion / Independencia',
		// 2020 ballot
		'Yes': $language === 'en' ? 'Yes' : 'Si',
		'No': 'No'
	});

	// Function to translate ballot option
	function translateBallotOption(option: string): string {
		return ballotOptionTranslations[option] || option;
	}

	// Context and congress response translations for summary table
	let contextTranslations = $derived<Record<string, string>>({
		'First status referendum': $language === 'en' ? 'First status referendum' : 'Primer referendum de estatus',
		'Post-Cold War vote': $language === 'en' ? 'Post-Cold War vote' : 'Voto post-Guerra Fria',
		'PPD boycotted, "None of the Above" won': $language === 'en' ? 'PPD boycotted, "None of the Above" won' : 'PPD boicoteo, "Ninguna de las Anteriores" gano',
		'500K+ left Q2 blank': $language === 'en' ? '500K+ left Q2 blank' : '500K+ dejaron P2 en blanco',
		'Lowest turnout in PR history': $language === 'en' ? 'Lowest turnout in PR history' : 'Participacion mas baja en historia de PR',
		'First simple majority Yes': $language === 'en' ? 'First simple majority Yes' : 'Primera mayoria simple Si'
	});

	let congressResponseTranslations = $derived<Record<string, string>>({
		'No action': $language === 'en' ? 'No action' : 'Sin accion',
		'Requested funds for binding vote': $language === 'en' ? 'Requested funds for binding vote' : 'Solicito fondos para voto vinculante',
		'Dismissed due to low turnout': $language === 'en' ? 'Dismissed due to low turnout' : 'Descartado por baja participacion',
		'HR 1522 introduced but not passed': $language === 'en' ? 'HR 1522 introduced but not passed' : 'HR 1522 presentado pero no aprobado'
	});

	function translateContext(context: string): string {
		return contextTranslations[context] || context;
	}

	function translateCongressResponse(response: string): string {
		return congressResponseTranslations[response] || response;
	}

	// Bar data for results visualization
	let resultsBarData = $derived(() => {
		const p = activePlebiscite;
		const data = [
			{ label: statusLabels.statehood, value: p.statehood, color: STATUS_COLORS.statehood }
		];

		if (p.commonwealth > 0) {
			data.push({ label: statusLabels.commonwealth, value: p.commonwealth, color: STATUS_COLORS.commonwealth });
		}
		if (p.independence > 0) {
			data.push({ label: statusLabels.independence, value: p.independence, color: STATUS_COLORS.independence });
		}
		if (p.freeAssociation && p.freeAssociation > 0) {
			data.push({ label: statusLabels.freeAssociation, value: p.freeAssociation, color: STATUS_COLORS.freeAssociation });
		}
		if (p.noneOfAbove && p.noneOfAbove > 0) {
			data.push({ label: statusLabels.noneOfAbove, value: p.noneOfAbove, color: STATUS_COLORS.noneOfAbove });
		}

		return data.sort((a, b) => b.value - a.value);
	});

	// Turnout comparison data
	let turnoutData = $derived(
		plebiscites.map(p => ({
			label: String(p.year),
			value: p.turnout,
			color: p.boycott ? STATUS_COLORS.noneOfAbove : CATEGORY_COLORS[0]
		}))
	);

	// Statehood trend line data
	let statehoodTrendData = $derived([{
		id: 'statehood',
		label: content.statehood,
		color: STATUS_COLORS.statehood,
		data: plebiscites.map(p => ({ x: p.year, y: p.statehood }))
	}]);

	function handleStepEnter(response: { index: number }) {
		currentStep = response.index;
		switch (response.index) {
			case 0:
				activeViz = 'timeline';
				activeYear = 1967;
				break;
			case 1:
				activeViz = 'ballot';
				activeYear = 1967;
				break;
			case 2:
				activeViz = 'results';
				activeYear = 1993;
				break;
			case 3:
				activeViz = 'ballot';
				activeYear = 1998;
				break;
			case 4:
				activeViz = 'results';
				activeYear = 1998;
				break;
			case 5:
				activeViz = 'ballot';
				activeYear = 2012;
				break;
			case 6:
				activeViz = 'results';
				activeYear = 2012;
				break;
			case 7:
				activeViz = 'turnout';
				activeYear = 2017;
				break;
			case 8:
				activeViz = 'results';
				activeYear = 2017;
				break;
			case 9:
				activeViz = 'ballot';
				activeYear = 2020;
				break;
			case 10:
				activeViz = 'results';
				activeYear = 2020;
				break;
			case 11:
				activeViz = 'timeline';
				activeYear = 2020;
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
			<div class="header-stats">
				<div class="stat-box">
					<span class="stat-number">6</span>
					<span class="stat-label">{content.referendums}</span>
				</div>
				<div class="stat-box">
					<span class="stat-number">53</span>
					<span class="stat-label">{content.yearsOfDebate}</span>
				</div>
				<div class="stat-box">
					<span class="stat-number">0</span>
					<span class="stat-label">{content.congressionalActions}</span>
				</div>
			</div>
		</div>
	</header>

	<ScrollySection offset={0.6} onStepEnter={handleStepEnter}>
		{#snippet graphic()}
			<div class="viz-container">
				{#if loading}
					<p class="loading">{content.loading}</p>
				{:else if activeViz === 'timeline'}
					<h3 class="viz-title">{content.timelineTitle}</h3>
					<div class="timeline-viz">
						{#each plebiscites as p}
							<button
								class="timeline-node"
								class:active={p.year === activeYear}
								class:boycott={p.boycott}
								onclick={() => activeYear = p.year}
							>
								<span class="node-year">{p.year}</span>
								<span class="node-dot"></span>
								<span class="node-result">{p.statehood.toFixed(0)}%</span>
								<span class="node-label">{p.winner}</span>
							</button>
						{/each}
						<div class="timeline-line"></div>
					</div>
					<div class="timeline-legend">
						<span class="legend-item"><span class="dot active"></span> {content.normalTurnout}</span>
						<span class="legend-item"><span class="dot boycott"></span> {content.boycotted}</span>
					</div>
				{:else if activeViz === 'results'}
					<h3 class="viz-title">{activePlebiscite.year} {content.resultsTitle}</h3>
					<div class="viz-subtitle">
						{activePlebiscite.question} {content.format}
						{#if activePlebiscite.boycott}
							<span class="boycott-badge">{content.boycottedBy} {activePlebiscite.boycottParty}</span>
						{/if}
					</div>
					<BarChart
						data={resultsBarData()}
						width={420}
						height={280}
						horizontal={true}
						valueFormat={(v) => `${v.toFixed(1)}%`}
					/>
					<div class="result-meta">
						<span class="meta-item">{content.turnout}: <strong>{activePlebiscite.turnout}%</strong></span>
						<span class="meta-item">{content.totalVotes}: <strong>{activePlebiscite.totalVotes.toLocaleString()}</strong></span>
					</div>
				{:else if activeViz === 'turnout'}
					<h3 class="viz-title">{content.turnoutTitle}</h3>
					<div class="viz-subtitle">{content.turnoutSubtitle}</div>
					<BarChart
						data={turnoutData}
						width={500}
						height={300}
						horizontal={false}
						valueFormat={(v) => `${v.toFixed(0)}%`}
						highlightLabel={String(activeYear)}
					/>
				{:else if activeViz === 'ballot'}
					<h3 class="viz-title">{activePlebiscite.year} {content.ballotTitle}</h3>
					<div class="ballot-recreation">
						<div class="ballot-header">
							<div class="ballot-seal">PR</div>
							<div class="ballot-title">
								<span class="ballot-office">{content.ballotOffice}</span>
								<span class="ballot-year">{activePlebiscite.year}</span>
							</div>
						</div>
						<div class="ballot-question">
							{#if activePlebiscite.year === 2020}
								{content.ballotQuestion2020}
							{:else if activePlebiscite.year === 2012}
								{content.ballotQuestion2012Q1}
							{:else}
								{content.ballotQuestionGeneral}
							{/if}
						</div>
						<div class="ballot-options">
							{#each activePlebiscite.ballotOptions as option, i}
								<div class="ballot-option">
									<div class="ballot-checkbox"></div>
									<span class="ballot-option-text">{translateBallotOption(option)}</span>
								</div>
							{/each}
						</div>
						{#if activePlebiscite.year === 2012}
							<div class="ballot-divider"></div>
							<div class="ballot-question">
								{content.ballotQuestion2012Q2}
							</div>
							<div class="ballot-options">
								<div class="ballot-option">
									<div class="ballot-checkbox"></div>
									<span class="ballot-option-text">{content.statehood}</span>
								</div>
								<div class="ballot-option">
									<div class="ballot-checkbox"></div>
									<span class="ballot-option-text">{content.sovereignFreeAssociated}</span>
								</div>
								<div class="ballot-option">
									<div class="ballot-checkbox"></div>
									<span class="ballot-option-text">{content.independence}</span>
								</div>
							</div>
						{/if}
					</div>
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>{content.step0Title}</h3>
			<p>{content.step0p1}</p>
			<p>
				{content.step0p2} <span class="stat">{content.six}</span>
				{content.step0p2b}
			</p>
			<p>{content.step0p3}</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>{content.step1Title}</h3>
			<p>{content.step1p1}</p>
			<p>
				{content.step1p2} <span class="stat">60.4%</span>
				{content.step1p2b}
			</p>
			<p>{content.step1p3}</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>{content.step2Title}</h3>
			<p>{content.step2p1}</p>
			<p>
				{content.step2p2} <span class="stat">48.6%</span>,
				{content.step2p2b}
			</p>
			<p>{content.step2p3}</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>{content.step3Title}</h3>
			<p>{content.step3p1}</p>
			<p>{content.step3p2}</p>
			<p>
				{content.step3p3} <span class="stat">50.3%</span>,
				{content.step3p3b}
			</p>
		</Step>

		<Step active={currentStep === 4} index={4} variant="callout">
			<h3>{content.step4Title}</h3>
			<p>{content.step4p1}</p>
			<p>
				{content.step4p2}
				<span class="highlight">{content.step4p2b}</span>
				{content.step4p2c}
			</p>
			<p>{content.step4p3}</p>
		</Step>

		<Step active={currentStep === 5} index={5}>
			<h3>{content.step5Title}</h3>
			<p>{content.step5p1}</p>
			<p>{content.step5p2}</p>
			<p>{content.step5p3}</p>
			<p>
				{content.step5p4} <span class="highlight">{content.step5p4b}</span>.
			</p>
		</Step>

		<Step active={currentStep === 6} index={6}>
			<h3>{content.step6Title}</h3>
			<p>
				{content.step6p1} <span class="stat">61.2%</span>
				{content.step6p1b}
			</p>
			<p>
				{content.step6p2} <span class="highlight">{content.step6p2b}</span>
				{content.step6p2c}
			</p>
			<p>{content.step6p3}</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>{content.step7Title}</h3>
			<p>
				{content.step7p1} <span class="stat">23%</span>.
				{content.step7p1b}
			</p>
			<p>{content.step7p2}</p>
			<p>{content.step7p3}</p>
		</Step>

		<Step active={currentStep === 8} index={8} variant="comparison">
			{#snippet before()}
				<span class="stat">{content.step8Before1}</span>
				<p><strong>{content.step8Before2}</strong></p>
				<p>{content.step8Before3}</p>
			{/snippet}
			{#snippet after()}
				<span class="stat">{content.step8After1}</span>
				<p><strong>{content.step8After2}</strong></p>
				<p>{content.step8After3}</p>
			{/snippet}
			<h3>{content.step8Title}</h3>
			<p>{content.step8p2}</p>
			<p>{content.step8p3}</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>{content.step9Title}</h3>
			<p>{content.step9p1}</p>
			<p class="quote">
				{content.step9p2}
				<strong>{content.step9p2b}</strong> {content.step9p2c} <strong>{content.step9p2d}</strong>."
			</p>
			<p>{content.step9p3}</p>
		</Step>

		<Step active={currentStep === 10} index={10}>
			<h3>{content.step10Title}</h3>
			<p>
				{content.step10p1} <span class="stat">{content.step10p1b}</span> {content.step10p1c}
			</p>
			<p>
				{content.step10p2}
				<span class="highlight">{content.step10p2b}</span>, {content.step10p2c}
			</p>
			<p>{content.step10p3}</p>
		</Step>

		<Step active={currentStep === 11} index={11} variant="question">
			<h3>{content.step11QuestionTitle}</h3>
			<p>{content.step11p1}</p>
			<p>{content.step11p2}</p>
			<p>{content.step11p3}</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>{content.conclusionTitle}</h2>

			<div class="summary-table">
				<div class="table-header">
					<span class="col-year">{content.tableYear}</span>
					<span class="col-result">{content.tableStatehood}</span>
					<span class="col-turnout">{content.tableTurnout}</span>
					<span class="col-note">{content.tableNote}</span>
					<span class="col-congress">{content.tableCongress}</span>
				</div>
				{#each plebiscites as p}
					<div class="table-row" class:boycott={p.boycott}>
						<span class="col-year">{p.year}</span>
						<span class="col-result">{p.statehood.toFixed(1)}%</span>
						<span class="col-turnout">{p.turnout}%</span>
						<span class="col-note">{translateContext(p.context)}</span>
						<span class="col-congress">{translateCongressResponse(p.congressResponse)}</span>
					</div>
				{/each}
			</div>

			<div class="key-takeaways">
				<h3>{content.keyTakeaways}</h3>
				<ul>
					<li>
						<strong>{content.takeaway1Title}</strong> {content.takeaway1}
					</li>
					<li>
						<strong>{content.takeaway2Title}</strong> {content.takeaway2}
					</li>
					<li>
						<strong>{content.takeaway3Title}</strong> {content.takeaway3}
					</li>
					<li>
						<strong>{content.takeaway4Title}</strong> {content.takeaway4}
					</li>
				</ul>
			</div>

			<div class="sources">
				<h3>{content.sources}</h3>
				<ul>
					<li><a href="https://ww2.ceepur.org/Home/EventosElectorales" target="_blank" rel="noopener">Comision Estatal de Elecciones de Puerto Rico (CEE)</a> - {content.source1}</li>
					<li><a href="https://www.gao.gov/" target="_blank" rel="noopener">U.S. Government Accountability Office</a> - {content.source2}</li>
					<li><a href="https://crsreports.congress.gov/" target="_blank" rel="noopener">Congressional Research Service</a> - {content.source3}</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/shrinking" class="nav-link prev">
					<span class="nav-direction">{content.previous}</span>
					<span class="nav-title">{content.prevTitle}</span>
				</a>
				<a href="{base}/chapters/referendum-2020" class="nav-link next">
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
		min-height: 70vh;
		display: flex;
		align-items: center;
		padding: var(--space-3xl) 0;
		background: radial-gradient(ellipse at 50% 100%, var(--color-surface) 0%, var(--color-bg) 70%);
	}

	.header-stats {
		display: flex;
		gap: var(--space-xl);
		margin-top: var(--space-2xl);
	}

	.stat-box {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: var(--space-lg);
		background: var(--color-surface-elevated);
		border-radius: var(--radius-lg);
		min-width: 100px;
	}

	.stat-number {
		font-family: var(--font-display);
		font-size: var(--text-4xl);
		font-weight: var(--font-bold);
		color: var(--color-accent);
		line-height: 1;
	}

	.stat-label {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin-top: var(--space-xs);
	}

	.viz-container {
		width: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: var(--space-lg);
	}

	.viz-title {
		font-size: var(--text-xl);
		font-weight: var(--font-semibold);
		color: var(--color-text);
		margin-bottom: var(--space-xs);
	}

	.viz-subtitle {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin-bottom: var(--space-lg);
		display: flex;
		align-items: center;
		gap: var(--space-sm);
	}

	.boycott-badge {
		background: #c41e3a;
		color: white;
		padding: var(--space-xs) var(--space-sm);
		border-radius: var(--radius-sm);
		font-size: var(--text-xs);
		font-weight: var(--font-medium);
	}

	/* Timeline Visualization */
	.timeline-viz {
		position: relative;
		display: flex;
		justify-content: space-between;
		align-items: center;
		width: 100%;
		max-width: 600px;
		padding: var(--space-xl) 0;
	}

	.timeline-line {
		position: absolute;
		top: 50%;
		left: 0;
		right: 0;
		height: 2px;
		background: var(--color-border);
		z-index: 0;
	}

	.timeline-node {
		position: relative;
		z-index: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-xs);
		background: none;
		border: none;
		cursor: pointer;
		padding: var(--space-sm);
		transition: transform var(--transition-fast);
	}

	.timeline-node:hover {
		transform: scale(1.1);
	}

	.timeline-node .node-year {
		font-family: var(--font-display);
		font-size: var(--text-sm);
		font-weight: var(--font-bold);
		color: var(--color-text-muted);
	}

	.timeline-node .node-dot {
		width: 16px;
		height: 16px;
		border-radius: 50%;
		background: var(--color-accent);
		border: 3px solid var(--color-bg);
		box-shadow: 0 0 0 2px var(--color-accent);
	}

	.timeline-node.boycott .node-dot {
		background: #6b7280;
		box-shadow: 0 0 0 2px #6b7280;
	}

	.timeline-node.active .node-dot {
		width: 20px;
		height: 20px;
		box-shadow: 0 0 0 3px var(--color-accent);
	}

	.timeline-node .node-result {
		font-size: var(--text-lg);
		font-weight: var(--font-bold);
		color: var(--color-text);
	}

	.timeline-node .node-label {
		font-size: var(--text-xs);
		color: var(--color-text-muted);
		white-space: nowrap;
	}

	.timeline-legend {
		display: flex;
		gap: var(--space-lg);
		margin-top: var(--space-lg);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
	}

	.legend-item .dot {
		width: 10px;
		height: 10px;
		border-radius: 50%;
	}

	.legend-item .dot.active {
		background: var(--color-accent);
	}

	.legend-item .dot.boycott {
		background: #6b7280;
	}

	/* Ballot Recreation */
	.ballot-recreation {
		background: #fffef8;
		border: 2px solid #1a1a1a;
		border-radius: var(--radius-md);
		padding: var(--space-xl);
		max-width: 400px;
		width: 100%;
		box-shadow: var(--shadow-lg);
	}

	.ballot-header {
		display: flex;
		align-items: center;
		gap: var(--space-md);
		margin-bottom: var(--space-lg);
		padding-bottom: var(--space-md);
		border-bottom: 2px solid #1a1a1a;
	}

	.ballot-seal {
		width: 48px;
		height: 48px;
		border: 2px solid #1a1a1a;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-family: var(--font-display);
		font-weight: var(--font-bold);
		font-size: var(--text-lg);
		color: #1a1a1a;
	}

	.ballot-title {
		display: flex;
		flex-direction: column;
	}

	.ballot-office {
		font-family: var(--font-display);
		font-size: var(--text-lg);
		font-weight: var(--font-bold);
		color: #1a1a1a;
		letter-spacing: 0.1em;
	}

	.ballot-year {
		font-size: var(--text-sm);
		color: #666;
	}

	.ballot-question {
		font-size: var(--text-sm);
		color: #1a1a1a;
		margin-bottom: var(--space-md);
		font-style: italic;
		line-height: 1.5;
	}

	.ballot-options {
		display: flex;
		flex-direction: column;
		gap: var(--space-sm);
	}

	.ballot-option {
		display: flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-sm);
		background: #f5f5f0;
		border-radius: var(--radius-sm);
	}

	.ballot-checkbox {
		width: 18px;
		height: 18px;
		border: 2px solid #1a1a1a;
		border-radius: 2px;
		flex-shrink: 0;
	}

	.ballot-option-text {
		font-size: var(--text-sm);
		color: #1a1a1a;
	}

	.ballot-divider {
		height: 1px;
		background: #ccc;
		margin: var(--space-lg) 0;
	}

	/* Result metadata */
	.result-meta {
		display: flex;
		gap: var(--space-xl);
		margin-top: var(--space-lg);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.meta-item strong {
		color: var(--color-text);
	}

	/* Quote styling */
	.quote {
		font-size: var(--text-lg);
		font-style: italic;
		color: var(--color-text);
		background: var(--color-surface-elevated);
		padding: var(--space-md) var(--space-lg);
		border-left: 4px solid var(--color-accent);
		border-radius: 0 var(--radius-md) var(--radius-md) 0;
		margin: var(--space-md) 0;
	}

	/* Chapter Conclusion */
	.chapter-conclusion {
		padding: var(--space-3xl) 0;
		background: var(--color-surface);
	}

	.summary-table {
		margin: var(--space-xl) 0;
		background: var(--color-surface-elevated);
		border-radius: var(--radius-lg);
		overflow: hidden;
	}

	.table-header {
		display: grid;
		grid-template-columns: 80px 100px 90px 1fr 120px;
		gap: var(--space-md);
		padding: var(--space-md);
		background: var(--color-bg);
		font-size: var(--text-sm);
		font-weight: var(--font-semibold);
		color: var(--color-text-muted);
	}

	.table-row {
		display: grid;
		grid-template-columns: 80px 100px 90px 1fr 120px;
		gap: var(--space-md);
		padding: var(--space-md);
		border-top: 1px solid var(--color-border);
		font-size: var(--text-sm);
	}

	.table-row.boycott {
		background: rgba(107, 114, 128, 0.1);
	}

	.col-year {
		font-family: var(--font-display);
		font-weight: var(--font-bold);
		color: var(--color-accent);
	}

	.col-result {
		font-weight: var(--font-semibold);
	}

	.col-turnout {
		color: var(--color-text-muted);
	}

	.col-note {
		color: var(--color-text);
	}

	.col-congress {
		color: var(--color-text-muted);
		font-size: var(--text-xs);
	}

	.key-takeaways {
		margin-top: var(--space-2xl);
	}

	.key-takeaways h3 {
		font-family: var(--font-display);
		font-size: var(--text-xl);
		margin-bottom: var(--space-md);
	}

	.key-takeaways ul {
		display: flex;
		flex-direction: column;
		gap: var(--space-md);
		list-style: none;
		padding: 0;
	}

	.key-takeaways li {
		padding: var(--space-md);
		background: var(--color-surface-elevated);
		border-radius: var(--radius-md);
		border-left: 4px solid var(--color-accent);
	}

	.key-takeaways li strong {
		color: var(--color-accent);
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

	/* Responsive */
	@media (max-width: 768px) {
		.header-stats {
			flex-direction: column;
			gap: var(--space-md);
		}

		.timeline-viz {
			flex-wrap: wrap;
			justify-content: center;
			gap: var(--space-lg);
		}

		.timeline-line {
			display: none;
		}

		.table-header,
		.table-row {
			grid-template-columns: 60px 70px 60px 1fr;
		}

		.col-congress {
			display: none;
		}
	}
</style>
