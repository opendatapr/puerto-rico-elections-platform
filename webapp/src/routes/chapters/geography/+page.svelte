<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ScrollySection, Step, Progress } from '$lib/components/scrollytelling';
	import { ChoroplethMap } from '$lib/components/maps';
	import { BarChart, ScatterPlot } from '$lib/components/charts';
	import { createDivergingScale, createSequentialScale, CATEGORY_COLORS, PARTY_COLORS } from '$lib/utils/colors';
	import { language } from '$lib/stores/language';

	const chapterNum = 6;
	const totalSteps = 12;

	// Bilingual content
	const t = {
		en: {
			chapterTitle: 'Divided by Design',
			chapter: 'Chapter',
			lead: "Puerto Rico's electoral geography is not an accident. Carved from colonial legacies and shaped by decades of migration, these 78 municipalities are the building blocks of political power. Where you live shapes how you vote, and the map itself becomes a battleground.",
			loading: 'Loading geographic data...',
			// Map titles
			map78Municipalities: '78 Municipalities of Puerto Rico',
			mapPartisanLean: 'Partisan Lean (2016 Governor)',
			mapPopulationDistribution: 'Population Distribution',
			mapUrbanRuralClassification: 'Urban-Rural Classification',
			mapIncomeVsPnp: 'Income vs. PNP Vote Share',
			mapRegionalBalance: 'Regional Partisan Balance',
			mapSenateDistricts: 'Senate Districts',
			mapTop10Population: 'Top 10 Municipalities by Population',
			mapElectoralMap: 'The Electoral Map',
			// Viz notes
			vizNoteDeviation: 'Deviation from 50-50 (positive = PNP lean)',
			// Legend labels
			legendUrban: 'Urban',
			legendSuburban: 'Suburban',
			legendTown: 'Town',
			legendRural: 'Rural',
			legendPpdLean: 'PPD Lean',
			legendEven: 'Even',
			legendPnpLean: 'PNP Lean',
			// Scatter plot
			scatterXLabel: 'Median Household Income ($)',
			scatterYLabel: 'PNP Vote Share (%)',
			// Step titles
			step0Title: 'The Map is Not the Territory',
			step1Title: '78 Pieces of a Colonial Puzzle',
			step2Title: 'The Partisan Divide',
			step3Title: 'Where the People Are',
			step4Title: 'The Population Paradox',
			step5Title: 'Urban vs. Rural',
			step6Title: 'The Class Dimension',
			step7Title: 'Regional Coalitions',
			step8Title: 'At-Large vs. District: The Senate',
			step9Title: 'The House: 40 Districts',
			step10Title: 'The Population Giants',
			step11Title: 'The Stakes of the Map',
			// Step 0
			step0p1: 'Every election night, the map of Puerto Rico lights up in red and blue. Municipalities flip, margins shift, and pundits draw sweeping conclusions from the colored shapes on screen.',
			step0p2: 'But what are these shapes? Where did they come from? And why do they matter so much to Puerto Rican politics? The answers reveal how',
			step0p2Highlight: 'geography itself becomes a political actor',
			step0p3: "This chapter examines how Puerto Rico's electoral geography was designed, how it divides the island, and what it means for representation.",
			// Step 1
			step1p1: "trace their origins to the Spanish colonial era. Unlike American counties, which were often drawn on gridlines across empty land, Puerto Rico's boundaries followed rivers, mountain ridges, and the practical limits of 18th-century governance.",
			step1p2: 'When the United States took control in 1898, these Spanish administrative units remained intact. The island\'s rugged terrain and dispersed population made them practical for governance. A municipality centered on each town plaza, radiating outward to the next mountain range.',
			step1p3: "This colonial inheritance means Puerto Rico's political geography predates modern transportation, communication, and demographic patterns. The map was designed for a different island.",
			// Step 2
			step2p1a: 'When we color each municipality by its partisan lean, a pattern emerges.',
			step2p1b: 'lean toward the pro-statehood PNP, while',
			step2p1c: 'favor the pro-commonwealth PPD.',
			step2p2a: 'In 2016,',
			step2p2b: 'was the most pro-PNP municipality, while',
			step2p2c: "leaned most heavily toward PPD. These aren't random variations; they reflect deep structural differences in demographics, economics, and political culture.",
			step2p3: 'The clustering is striking: neighboring municipalities tend to vote alike, creating',
			step2p3Highlight: 'regional blocs',
			step2p3b: 'that persist across multiple elections.',
			// Step 3
			step3p1: "But the map lies. A municipality's size on the map has nothing to do with its political importance.",
			step3p1Highlight: 'Population',
			step3p1b: "determines votes, and Puerto Rico's population is concentrated in a few urban centers.",
			step3p2a: 'alone holds',
			step3p2b: "of the island's population. The San Juan metro area, a ring of municipalities around the capital, contains over a third of all Puerto Ricans.",
			step3p3: 'This means the sprawling rural municipalities of the interior, which dominate the map visually, are politically marginalized by their small populations.',
			// Step 4
			step4p1: 'Consider this:',
			step4p1b: 'has',
			step4p1c: 'residents, while',
			step4p1d: 'has just',
			step4p2: "That's a ratio of over",
			step4p2Highlight: '200 to 1',
			step4p2b: '. Yet on most maps, these municipalities appear roughly similar in size. Equal-area maps distort political reality, making rural regions seem more important than they are electorally.',
			step4p3: "When journalists and analysts use standard maps, they inadvertently reinforce the illusion that Puerto Rico's politics is evenly distributed across space.",
			// Step 5
			step5p1: "Puerto Rico's municipalities fall into distinct categories that shape their political character. Only",
			step5p1b: 'qualify as fully urban with populations over 100,000.',
			step5p2: 'includes San Juan, Bayamon, Carolina, Ponce, and Caguas. These municipalities have diverse economies, higher incomes, and professional workforces that vote differently from the rest of the island.',
			step5p3: 'in the central mountains and western coast maintain agricultural traditions, face higher poverty rates, and often support different candidates than the metro areas.',
			step5p4: 'This urban-rural divide cuts across the statehood-commonwealth debate, creating cross-cutting cleavages that complicate Puerto Rico\'s political coalitions.',
			labelUrbanCore: 'The urban core',
			labelRuralMunicipalities: 'Rural municipalities',
			// Comparison variant labels
			comparisonUrbanLabel: 'Urban Core',
			comparisonRuralLabel: 'Rural Interior',
			comparisonUrbanStat: '5 municipalities',
			comparisonRuralStat: '40+ municipalities',
			comparisonUrbanDesc: 'Higher incomes, diverse economies, professional workforce',
			comparisonRuralDesc: 'Agricultural traditions, higher poverty, scattered populations',
			// Step 6
			step6p1: "Plotting each municipality's median household income against its PNP vote share reveals a striking pattern:",
			step6p1Highlight: 'wealthier municipalities tend to vote more for PNP',
			step6p2: 'The trendline shows a positive correlation (R-squared indicates the strength of this relationship). While not deterministic, income is one of the strongest predictors of partisan lean at the municipal level.',
			step6p3: 'This class dimension helps explain why the pro-statehood movement, despite advocating for full U.S. citizenship rights, draws more support from economically advantaged areas where residents may benefit from federal programs and economic integration.',
			// Callout variant content
			calloutStat: 'R-squared correlation',
			calloutStatValue: '0.35',
			calloutInsight: 'Income is one of the strongest predictors of municipal voting patterns, more powerful than age or education level alone.',
			// Step 7
			step7p1: "Puerto Rico's eight Senate districts roughly correspond to historical regions with distinct political cultures. Each bar shows how far that region deviates from a 50-50 partisan split.",
			step7p2a: 'The',
			step7p2SanJuan: 'San Juan Metro',
			step7p2and: 'and',
			step7p2Bayamon: 'Bayamon/North',
			step7p2b: 'regions tilt toward PNP, while the',
			step7p2Mayaguez: 'Mayaguez/West',
			step7p2c: 'and',
			step7p2Ponce: 'Ponce/South',
			step7p2d: 'regions lean PPD.',
			step7p3: "These regional patterns have proven durable across elections. A municipality's geographic location predicts its partisan lean better than most demographic variables. Your neighbors shape your politics, and regional identity reinforces party loyalty across generations.",
			// Step 8
			step8p1: "Puerto Rico elects its legislature through a mixed system. The",
			step8p1Senate: '8 Senate districts',
			step8p1b: ', shown here, each elect 2 senators by district. An additional 11 senators are elected at-large, island-wide.',
			step8p2: 'This hybrid system creates interesting dynamics. District senators must represent specific geographic areas with particular concerns, while at-large senators can appeal to the entire island.',
			step8p3: 'The district boundaries matter enormously. Each colored region on this map sends 2 senators to San Juan, regardless of whether it contains 300,000 or 500,000 people. Malapportionment gives some regions more representation per capita than others.',
			// Step 9
			step9p1: 'The House of Representatives has',
			step9p1House: '40 districts',
			step9p1b: ', each electing a single representative, plus 11 at-large seats. These districts are smaller than Senate districts, sometimes splitting municipalities.',
			step9p2a: 'Large municipalities like San Juan span',
			step9p2Highlight: '5 House districts',
			step9p2b: ", meaning the capital's residents are represented by multiple district representatives with potentially different agendas. Smaller municipalities share a representative with their neighbors.",
			step9p3: 'This arrangement means campaigns must be intensely local. A candidate in House District 3 (part of San Juan) faces entirely different voters than someone in District 4, even though both are technically in the same city.',
			// Step 10
			step10p1: 'The top 10 municipalities by population illustrate the concentration of political power. Together, they hold over',
			step10p1Highlight: '50%',
			step10p1b: "of Puerto Rico's total population.",
			step10p2: 'Winning elections means winning these urban centers, or at least limiting losses there. A candidate who sweeps the San Juan metro but loses the rural interior can still win island-wide, while the reverse is nearly impossible.',
			step10p3: "This population concentration explains why Puerto Rico's political debates often center on urban issues: traffic, public services, economic development, and professional employment. Rural concerns, from agricultural policy to infrastructure investment, take a back seat.",
			// Step 11
			step11p1: "Puerto Rico's electoral geography matters because",
			step11p1Highlight: 'the map itself is contested terrain',
			step11p1b: '. Proposals to consolidate municipalities, redraw district lines, or change the at-large vs. district balance would reshape political power.',
			step11p2: 'The current system favors parties that can build broad geographic coalitions while maintaining strong urban cores. It disadvantages parties concentrated in a few regions, and it gives smaller municipalities outsized influence in some legislative races.',
			step11p3: 'As Puerto Rico debates its future, from statehood to independence, the question of how to draw the map, and who decides, remains as politically charged as the debates over the island\'s ultimate status.',
			// Question variant content
			questionTitle: 'Who Will Redraw the Map?',
			questionP1: 'As population continues to shift and municipalities lose residents to the mainland, will Puerto Rico consolidate its 78 municipalities? Will district lines be redrawn to reflect new realities?',
			questionP2: 'The answers will shape political power for a generation, and both parties know it.',
			// Conclusion
			conclusionTitle: 'The Geography of Power',
			conclusionP1: "Puerto Rico's electoral map tells a story of colonial inheritance, urban concentration, and regional identity. The 78 municipalities, 8 Senate districts, and 40 House districts create a complex terrain where geography shapes political outcomes.",
			keyTakeaways: 'Key Takeaways',
			takeaway1Title: 'Colonial Legacy:',
			takeaway1: 'Municipality boundaries date to Spanish rule and no longer reflect modern population patterns',
			takeaway2Title: 'Population Concentration:',
			takeaway2: 'Over half the population lives in just 10 municipalities, making urban areas decisive',
			takeaway3Title: 'Regional Blocs:',
			takeaway3: 'Neighboring municipalities vote alike, creating persistent geographic coalitions',
			takeaway4Title: 'Class Geography:',
			takeaway4: 'Wealthier areas lean PNP; poorer areas lean PPD, with exceptions',
			takeaway5Title: 'Mixed Representation:',
			takeaway5: 'The combination of district and at-large seats creates complex campaign incentives',
			// Sources
			sources: 'Sources',
			sourceCee: 'Municipality-level election results 2016-2024',
			sourceCensus: 'Puerto Rico geographic definitions and TIGER/Line shapefiles',
			sourcePlanningBoard: 'Puerto Rico Planning Board - Regional classifications and urban/rural definitions',
			sourceAcs: 'Population and demographic data by municipality',
			// Navigation
			previous: 'Previous',
			nextChapter: 'Next Chapter',
			prevTitle: 'The 52.5% Threshold',
			nextTitle: 'La Fortaleza',
			// Tooltips
			tooltipResidents: 'residents',
			tooltipPop: 'pop.',
			tooltipDistrict: 'District',
			tooltipPoverty: 'poverty',
			blueMunicipalities: 'Blue municipalities',
			redMunicipalities: 'red municipalities',
			municipalities78: "Puerto Rico's 78 municipalities"
		},
		es: {
			chapterTitle: 'Dividido por Diseno',
			chapter: 'Capitulo',
			lead: 'La geografia electoral de Puerto Rico no es un accidente. Tallada de legados coloniales y moldeada por decadas de migracion, estos 78 municipios son los bloques de construccion del poder politico. Donde vives moldea como votas, y el mapa mismo se convierte en un campo de batalla.',
			loading: 'Cargando datos geograficos...',
			// Map titles
			map78Municipalities: '78 Municipios de Puerto Rico',
			mapPartisanLean: 'Inclinacion Partidista (Gobernador 2016)',
			mapPopulationDistribution: 'Distribucion Poblacional',
			mapUrbanRuralClassification: 'Clasificacion Urbano-Rural',
			mapIncomeVsPnp: 'Ingreso vs. Voto PNP',
			mapRegionalBalance: 'Balance Partidista Regional',
			mapSenateDistricts: 'Distritos Senatoriales',
			mapTop10Population: 'Los 10 Municipios Mas Poblados',
			mapElectoralMap: 'El Mapa Electoral',
			// Viz notes
			vizNoteDeviation: 'Desviacion del 50-50 (positivo = tendencia PNP)',
			// Legend labels
			legendUrban: 'Urbano',
			legendSuburban: 'Suburbano',
			legendTown: 'Pueblo',
			legendRural: 'Rural',
			legendPpdLean: 'Tendencia PPD',
			legendEven: 'Parejo',
			legendPnpLean: 'Tendencia PNP',
			// Scatter plot
			scatterXLabel: 'Ingreso Medio del Hogar ($)',
			scatterYLabel: 'Porcentaje de Voto PNP (%)',
			// Step titles
			step0Title: 'El Mapa No Es el Territorio',
			step1Title: '78 Piezas de un Rompecabezas Colonial',
			step2Title: 'La Division Partidista',
			step3Title: 'Donde Esta la Gente',
			step4Title: 'La Paradoja de Poblacion',
			step5Title: 'Urbano vs. Rural',
			step6Title: 'La Dimension de Clase',
			step7Title: 'Coaliciones Regionales',
			step8Title: 'Por Acumulacion vs. Por Distrito: El Senado',
			step9Title: 'La Camara: 40 Distritos',
			step10Title: 'Los Gigantes Poblacionales',
			step11Title: 'Lo Que Esta en Juego en el Mapa',
			// Step 0
			step0p1: 'Cada noche de elecciones, el mapa de Puerto Rico se ilumina en rojo y azul. Los municipios cambian de color, los margenes se mueven, y los analistas sacan conclusiones amplias de las formas coloreadas en pantalla.',
			step0p2: 'Pero, que son estas formas? De donde vienen? Y por que importan tanto para la politica puertorriquena? Las respuestas revelan como',
			step0p2Highlight: 'la geografia misma se convierte en actor politico',
			step0p3: 'Este capitulo examina como se diseno la geografia electoral de Puerto Rico, como divide la isla, y que significa para la representacion.',
			// Step 1
			step1p1: 'trazan sus origenes a la era colonial espanola. A diferencia de los condados estadounidenses, que frecuentemente se trazaron en cuadriculas sobre tierras vacias, las fronteras de Puerto Rico siguieron rios, cordilleras montanosas y los limites practicos de la gobernanza del siglo XVIII.',
			step1p2: 'Cuando Estados Unidos tomo control en 1898, estas unidades administrativas espanolas permanecieron intactas. El terreno accidentado de la isla y la poblacion dispersa las hacian practicas para gobernar. Un municipio centrado en cada plaza del pueblo, irradiandose hacia la proxima cordillera.',
			step1p3: 'Esta herencia colonial significa que la geografia politica de Puerto Rico es anterior al transporte moderno, las comunicaciones y los patrones demograficos. El mapa fue disenado para una isla diferente.',
			// Step 2
			step2p1a: 'Cuando coloreamos cada municipio segun su inclinacion partidista, emerge un patron.',
			step2p1b: 'se inclinan hacia el PNP pro-estadidad, mientras que',
			step2p1c: 'favorecen al PPD pro-estado libre asociado.',
			step2p2a: 'En 2016,',
			step2p2b: 'fue el municipio mas pro-PNP, mientras que',
			step2p2c: 'se inclino mas fuertemente hacia el PPD. Estas no son variaciones aleatorias; reflejan profundas diferencias estructurales en demografia, economia y cultura politica.',
			step2p3: 'La agrupacion es sorprendente: los municipios vecinos tienden a votar igual, creando',
			step2p3Highlight: 'bloques regionales',
			step2p3b: 'que persisten a traves de multiples elecciones.',
			// Step 3
			step3p1: 'Pero el mapa miente. El tamano de un municipio en el mapa no tiene nada que ver con su importancia politica.',
			step3p1Highlight: 'La poblacion',
			step3p1b: 'determina los votos, y la poblacion de Puerto Rico esta concentrada en unos pocos centros urbanos.',
			step3p2a: 'solo tiene',
			step3p2b: 'de la poblacion de la isla. El area metropolitana de San Juan, un anillo de municipios alrededor de la capital, contiene mas de un tercio de todos los puertorriquenos.',
			step3p3: 'Esto significa que los extensos municipios rurales del interior, que dominan el mapa visualmente, estan politicamente marginados por sus pequenas poblaciones.',
			// Step 4
			step4p1: 'Considera esto:',
			step4p1b: 'tiene',
			step4p1c: 'residentes, mientras que',
			step4p1d: 'tiene solo',
			step4p2: 'Eso es una proporcion de mas de',
			step4p2Highlight: '200 a 1',
			step4p2b: '. Sin embargo, en la mayoria de los mapas, estos municipios parecen tener un tamano similar. Los mapas de igual area distorsionan la realidad politica, haciendo que las regiones rurales parezcan mas importantes de lo que son electoralmente.',
			step4p3: 'Cuando los periodistas y analistas usan mapas estandar, inadvertidamente refuerzan la ilusion de que la politica de Puerto Rico esta distribuida equitativamente en el espacio.',
			// Step 5
			step5p1: 'Los municipios de Puerto Rico caen en categorias distintas que moldean su caracter politico. Solo',
			step5p1b: 'califican como completamente urbanos con poblaciones de mas de 100,000.',
			step5p2: 'incluye San Juan, Bayamon, Carolina, Ponce y Caguas. Estos municipios tienen economias diversas, ingresos mas altos y fuerzas laborales profesionales que votan diferente al resto de la isla.',
			step5p3: 'en las montanas centrales y la costa oeste mantienen tradiciones agricolas, enfrentan tasas de pobreza mas altas, y frecuentemente apoyan candidatos diferentes que las areas metropolitanas.',
			step5p4: 'Esta division urbano-rural atraviesa el debate estadidad-estado libre asociado, creando divisiones cruzadas que complican las coaliciones politicas de Puerto Rico.',
			labelUrbanCore: 'El nucleo urbano',
			labelRuralMunicipalities: 'Los municipios rurales',
			// Comparison variant labels
			comparisonUrbanLabel: 'Nucleo Urbano',
			comparisonRuralLabel: 'Interior Rural',
			comparisonUrbanStat: '5 municipios',
			comparisonRuralStat: '40+ municipios',
			comparisonUrbanDesc: 'Mayores ingresos, economias diversas, fuerza laboral profesional',
			comparisonRuralDesc: 'Tradiciones agricolas, mayor pobreza, poblaciones dispersas',
			// Step 6
			step6p1: 'Graficando el ingreso medio del hogar de cada municipio contra su porcentaje de voto PNP revela un patron sorprendente:',
			step6p1Highlight: 'los municipios mas ricos tienden a votar mas por el PNP',
			step6p2: 'La linea de tendencia muestra una correlacion positiva (R-cuadrado indica la fuerza de esta relacion). Aunque no es determinista, el ingreso es uno de los predictores mas fuertes de la inclinacion partidista a nivel municipal.',
			step6p3: 'Esta dimension de clase ayuda a explicar por que el movimiento pro-estadidad, a pesar de abogar por plenos derechos de ciudadania estadounidense, atrae mas apoyo de areas economicamente aventajadas donde los residentes pueden beneficiarse de programas federales e integracion economica.',
			// Callout variant content
			calloutStat: 'Correlacion R-cuadrado',
			calloutStatValue: '0.35',
			calloutInsight: 'El ingreso es uno de los predictores mas fuertes de los patrones de votacion municipal, mas poderoso que la edad o el nivel educativo por si solos.',
			// Step 7
			step7p1: 'Los ocho distritos senatoriales de Puerto Rico corresponden aproximadamente a regiones historicas con culturas politicas distintas. Cada barra muestra cuanto se desvia esa region de una division partidista 50-50.',
			step7p2a: 'Las regiones de',
			step7p2SanJuan: 'San Juan Metro',
			step7p2and: 'y',
			step7p2Bayamon: 'Bayamon/Norte',
			step7p2b: 'se inclinan hacia el PNP, mientras que las regiones de',
			step7p2Mayaguez: 'Mayaguez/Oeste',
			step7p2c: 'y',
			step7p2Ponce: 'Ponce/Sur',
			step7p2d: 'se inclinan hacia el PPD.',
			step7p3: 'Estos patrones regionales han demostrado ser duraderos a traves de las elecciones. La ubicacion geografica de un municipio predice su inclinacion partidista mejor que la mayoria de las variables demograficas. Tus vecinos moldean tu politica, y la identidad regional refuerza la lealtad partidista a traves de generaciones.',
			// Step 8
			step8p1: 'Puerto Rico elige su legislatura a traves de un sistema mixto. Los',
			step8p1Senate: '8 distritos senatoriales',
			step8p1b: ', mostrados aqui, cada uno elige 2 senadores por distrito. Otros 11 senadores adicionales son elegidos por acumulacion, a nivel de toda la isla.',
			step8p2: 'Este sistema hibrido crea dinamicas interesantes. Los senadores por distrito deben representar areas geograficas especificas con preocupaciones particulares, mientras que los senadores por acumulacion pueden apelar a toda la isla.',
			step8p3: 'Los limites de los distritos importan enormemente. Cada region coloreada en este mapa envia 2 senadores a San Juan, independientemente de si contiene 300,000 o 500,000 personas. La mala distribucion da a algunas regiones mas representacion per capita que a otras.',
			// Step 9
			step9p1: 'La Camara de Representantes tiene',
			step9p1House: '40 distritos',
			step9p1b: ', cada uno eligiendo un solo representante, mas 11 escanos por acumulacion. Estos distritos son mas pequenos que los distritos senatoriales, a veces dividiendo municipios.',
			step9p2a: 'Municipios grandes como San Juan abarcan',
			step9p2Highlight: '5 distritos de la Camara',
			step9p2b: ', lo que significa que los residentes de la capital estan representados por multiples representantes de distrito con agendas potencialmente diferentes. Los municipios mas pequenos comparten un representante con sus vecinos.',
			step9p3: 'Este arreglo significa que las campanas deben ser intensamente locales. Un candidato en el Distrito 3 de la Camara (parte de San Juan) enfrenta votantes completamente diferentes que alguien en el Distrito 4, aunque ambos tecnicamente estan en la misma ciudad.',
			// Step 10
			step10p1: 'Los 10 municipios mas poblados ilustran la concentracion del poder politico. Juntos, tienen mas del',
			step10p1Highlight: '50%',
			step10p1b: 'de la poblacion total de Puerto Rico.',
			step10p2: 'Ganar elecciones significa ganar estos centros urbanos, o al menos limitar las perdidas alli. Un candidato que arrasa en el metro de San Juan pero pierde el interior rural puede aun ganar a nivel de toda la isla, mientras que lo contrario es casi imposible.',
			step10p3: 'Esta concentracion poblacional explica por que los debates politicos de Puerto Rico frecuentemente se centran en asuntos urbanos: trafico, servicios publicos, desarrollo economico y empleo profesional. Las preocupaciones rurales, desde politica agricola hasta inversion en infraestructura, quedan en segundo plano.',
			// Step 11
			step11p1: 'La geografia electoral de Puerto Rico importa porque',
			step11p1Highlight: 'el mapa mismo es terreno en disputa',
			step11p1b: '. Las propuestas para consolidar municipios, redibujar lineas de distrito, o cambiar el balance entre acumulacion y distrito reconfigurarían el poder politico.',
			step11p2: 'El sistema actual favorece a partidos que pueden construir coaliciones geograficas amplias mientras mantienen nucleos urbanos fuertes. Desfavorece a partidos concentrados en unas pocas regiones, y da a municipios mas pequenos una influencia desproporcionada en algunas contiendas legislativas.',
			step11p3: 'Mientras Puerto Rico debate su futuro, desde la estadidad hasta la independencia, la cuestion de como trazar el mapa, y quien decide, permanece tan politicamente cargada como los debates sobre el estatus final de la isla.',
			// Question variant content
			questionTitle: 'Quien Redibujara el Mapa?',
			questionP1: 'A medida que la poblacion continua cambiando y los municipios pierden residentes hacia el continente, consolidara Puerto Rico sus 78 municipios? Se redibujaran las lineas de distrito para reflejar nuevas realidades?',
			questionP2: 'Las respuestas moldearan el poder politico por una generacion, y ambos partidos lo saben.',
			// Conclusion
			conclusionTitle: 'La Geografia del Poder',
			conclusionP1: 'El mapa electoral de Puerto Rico cuenta una historia de herencia colonial, concentracion urbana e identidad regional. Los 78 municipios, 8 distritos senatoriales y 40 distritos de la Camara crean un terreno complejo donde la geografia moldea los resultados politicos.',
			keyTakeaways: 'Conclusiones Clave',
			takeaway1Title: 'Legado Colonial:',
			takeaway1: 'Los limites de los municipios datan del dominio espanol y ya no reflejan los patrones de poblacion modernos',
			takeaway2Title: 'Concentracion Poblacional:',
			takeaway2: 'Mas de la mitad de la poblacion vive en solo 10 municipios, haciendo que las areas urbanas sean decisivas',
			takeaway3Title: 'Bloques Regionales:',
			takeaway3: 'Los municipios vecinos votan igual, creando coaliciones geograficas persistentes',
			takeaway4Title: 'Geografia de Clase:',
			takeaway4: 'Las areas mas ricas se inclinan hacia el PNP; las mas pobres hacia el PPD, con excepciones',
			takeaway5Title: 'Representacion Mixta:',
			takeaway5: 'La combinacion de escanos por distrito y por acumulacion crea incentivos de campana complejos',
			// Sources
			sources: 'Fuentes',
			sourceCee: 'Resultados electorales a nivel municipal 2016-2024',
			sourceCensus: 'Definiciones geograficas de Puerto Rico y archivos de formas TIGER/Line',
			sourcePlanningBoard: 'Junta de Planificacion de Puerto Rico - Clasificaciones regionales y definiciones urbano/rural',
			sourceAcs: 'Datos poblacionales y demograficos por municipio',
			// Navigation
			previous: 'Anterior',
			nextChapter: 'Proximo Capitulo',
			prevTitle: 'El Umbral del 52.5%',
			nextTitle: 'La Fortaleza',
			// Tooltips
			tooltipResidents: 'residentes',
			tooltipPop: 'pob.',
			tooltipDistrict: 'Distrito',
			tooltipPoverty: 'pobreza',
			blueMunicipalities: 'Los municipios azules',
			redMunicipalities: 'los municipios rojos',
			municipalities78: 'Los 78 municipios de Puerto Rico'
		}
	};

	// Reactive content based on language
	let content = $derived(t[$language]);
	let chapterTitle = $derived(content.chapterTitle);

	let currentStep = $state(0);
	let mapTitle = $state('');
	let loading = $state(true);

	// Data from chapter JSON
	interface Municipality {
		name: string;
		population: number;
		vap: number;
		precincts: number;
		pnp_share_2016: number;
		ppd_share_2016: number;
		margin_2016: number;
		house_districts: number[];
		senate_district: number;
		senate_name: string;
		region: string;
		classification: string;
		median_income: number | null;
		poverty_rate: number | null;
		bachelors_or_higher: number | null;
		pop_share: number;
	}

	interface Region {
		name: string;
		municipalities: number;
		population: number;
		pnp_share: number;
		ppd_share: number;
	}

	interface SenateDistrict {
		district: number;
		name: string;
		municipalities: number;
		population: number;
		pnp_share: number;
	}

	interface ChapterData {
		municipalities: Municipality[];
		regions: Region[];
		senate_districts: SenateDistrict[];
		stats: {
			total_municipalities: number;
			total_population: number;
			total_precincts: number;
			total_house_districts: number;
			total_senate_districts: number;
			urban_count: number;
			rural_count: number;
			largest_municipality: string;
			smallest_municipality: string;
			most_pro_pnp: string;
			most_pro_ppd: string;
		};
		classification_breakdown: {
			urban: string[];
			suburban: string[];
			town: string[];
			rural: string[];
		};
	}

	let chapterData = $state<ChapterData | null>(null);

	onMount(async () => {
		try {
			const response = await fetch(`${base}/data/chapters/geography.json`);
			chapterData = await response.json();
		} catch (err) {
			console.error('Failed to load geography data:', err);
		} finally {
			loading = false;
		}
	});

	// Different color scales for different visualizations
	const marginScale = createDivergingScale([-20, 0, 20]);
	const populationScale = createSequentialScale([0, 400000]);
	const povertyScale = createSequentialScale([30, 60]);

	// Classification colors
	const classificationColors: Record<string, string> = {
		'urban': CATEGORY_COLORS[0],      // Blue
		'suburban': CATEGORY_COLORS[4],   // Teal
		'town': CATEGORY_COLORS[1],       // Gold
		'rural': CATEGORY_COLORS[2]       // Green
	};

	// Active visualization type
	type VizType = 'blank' | 'partisan' | 'population' | 'classification' | 'senate' | 'scatter' | 'regions' | 'size';
	let activeViz = $state<VizType>('blank');

	// Map data computed from chapterData
	let mapData = $derived(() => {
		if (!chapterData) return new Map<string, number>();
		const map = new Map<string, number>();

		switch (activeViz) {
			case 'partisan':
				for (const m of chapterData.municipalities) {
					map.set(m.name, m.margin_2016);
				}
				break;
			case 'population':
				for (const m of chapterData.municipalities) {
					map.set(m.name, m.population);
				}
				break;
			case 'classification':
				for (const m of chapterData.municipalities) {
					// Map classification to numeric for color scale
					const classVal = m.classification === 'urban' ? 3 :
									 m.classification === 'suburban' ? 2 :
									 m.classification === 'town' ? 1 : 0;
					map.set(m.name, classVal);
				}
				break;
			case 'senate':
				for (const m of chapterData.municipalities) {
					map.set(m.name, m.senate_district);
				}
				break;
		}
		return map;
	});

	// Current color scale based on viz type
	let currentColorScale = $derived(() => {
		switch (activeViz) {
			case 'partisan':
				return marginScale;
			case 'population':
				return populationScale;
			case 'classification':
				return (v: number) => {
					const classes = ['rural', 'town', 'suburban', 'urban'];
					return classificationColors[classes[v]] || 'var(--color-surface-elevated)';
				};
			case 'senate':
				return (v: number) => CATEGORY_COLORS[(v - 1) % CATEGORY_COLORS.length];
			default:
				return () => 'var(--color-surface-elevated)';
		}
	});

	// Scatter plot data: Income vs PNP share
	let scatterData = $derived(() => {
		if (!chapterData) return [];
		return chapterData.municipalities
			.filter(m => m.median_income !== null)
			.map(m => ({
				x: m.median_income!,
				y: m.pnp_share_2016,
				label: m.name,
				color: m.margin_2016 > 0 ? PARTY_COLORS.PNP : PARTY_COLORS.PPD,
				size: Math.sqrt(m.population) / 80
			}));
	});

	// Region bar chart data
	let regionBarData = $derived(() => {
		if (!chapterData) return [];
		return chapterData.regions.map(r => ({
			label: r.name.split('/')[0],
			value: r.pnp_share - 50,
			color: r.pnp_share > 50 ? PARTY_COLORS.PNP : PARTY_COLORS.PPD
		}));
	});

	// Population size comparison
	let sizeComparisonData = $derived(() => {
		if (!chapterData) return [];
		return chapterData.municipalities.slice(0, 10).map(m => ({
			label: m.name,
			value: m.population,
			color: m.margin_2016 > 0 ? PARTY_COLORS.PNP : PARTY_COLORS.PPD
		}));
	});

	// Urban/rural breakdown bars
	let classificationData = $derived(() => {
		if (!chapterData) return [];
		const cb = chapterData.classification_breakdown;
		return [
			{ label: 'Urban', value: cb.urban.length, color: classificationColors.urban },
			{ label: 'Suburban', value: cb.suburban.length, color: classificationColors.suburban },
			{ label: 'Town', value: cb.town.length, color: classificationColors.town },
			{ label: 'Rural', value: cb.rural.length, color: classificationColors.rural }
		];
	});

	function handleStepEnter(response: { index: number }) {
		currentStep = response.index;

		switch (response.index) {
			case 0:
				activeViz = 'blank';
				mapTitle = '';
				break;
			case 1:
				activeViz = 'blank';
				mapTitle = content.map78Municipalities;
				break;
			case 2:
				activeViz = 'partisan';
				mapTitle = content.mapPartisanLean;
				break;
			case 3:
			case 4:
				activeViz = 'population';
				mapTitle = content.mapPopulationDistribution;
				break;
			case 5:
				activeViz = 'classification';
				mapTitle = content.mapUrbanRuralClassification;
				break;
			case 6:
				activeViz = 'scatter';
				mapTitle = content.mapIncomeVsPnp;
				break;
			case 7:
				activeViz = 'regions';
				mapTitle = content.mapRegionalBalance;
				break;
			case 8:
				activeViz = 'senate';
				mapTitle = content.mapSenateDistricts;
				break;
			case 9:
				activeViz = 'senate';
				mapTitle = content.mapSenateDistricts;
				break;
			case 10:
				activeViz = 'size';
				mapTitle = content.mapTop10Population;
				break;
			case 11:
				activeViz = 'partisan';
				mapTitle = content.mapElectoralMap;
				break;
		}
	}

	function getTooltip(name: string, value: number | undefined): string {
		if (!chapterData || value === undefined) return name;
		const muni = chapterData.municipalities.find(m => m.name === name);
		if (!muni) return name;

		switch (activeViz) {
			case 'partisan':
				return `${name}: ${muni.margin_2016 > 0 ? 'PNP' : 'PPD'} +${Math.abs(muni.margin_2016).toFixed(1)}%`;
			case 'population':
				return `${name}: ${muni.population.toLocaleString()} ${content.tooltipResidents}`;
			case 'classification':
				return `${name}: ${muni.classification} (${content.tooltipPop} ${muni.population.toLocaleString()})`;
			case 'senate':
				return `${name}: ${content.tooltipDistrict} ${muni.senate_district} (${muni.senate_name})`;
			default:
				return name;
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
				{:else if mapTitle}
					<h3 class="viz-title">{mapTitle}</h3>
				{/if}

				{#if activeViz === 'scatter' && chapterData}
					<ScatterPlot
						data={scatterData()}
						width={520}
						height={360}
						xLabel={content.scatterXLabel}
						yLabel={content.scatterYLabel}
						xFormat={(v) => `$${(v/1000).toFixed(0)}k`}
						yFormat={(v) => `${v.toFixed(0)}%`}
						showRegression={true}
					/>
				{:else if activeViz === 'regions' && chapterData}
					<div class="bar-container">
						<BarChart
							data={regionBarData()}
							width={440}
							height={300}
							horizontal={true}
							valueFormat={(v) => `${v > 0 ? '+' : ''}${v.toFixed(1)}%`}
						/>
						<p class="viz-note">{content.vizNoteDeviation}</p>
					</div>
				{:else if activeViz === 'size' && chapterData}
					<BarChart
						data={sizeComparisonData()}
						width={480}
						height={320}
						horizontal={true}
						valueFormat={(v) => `${(v/1000).toFixed(0)}k`}
					/>
				{:else if !loading}
					<ChoroplethMap
						data={mapData()}
						colorScale={currentColorScale()}
						width={600}
						height={400}
						tooltipFormat={getTooltip}
					/>

					{#if activeViz === 'classification'}
						<div class="legend-row">
							<div class="legend-item">
								<span class="legend-swatch" style="background: {classificationColors.urban}"></span>
								<span>{content.legendUrban} ({chapterData?.classification_breakdown.urban.length})</span>
							</div>
							<div class="legend-item">
								<span class="legend-swatch" style="background: {classificationColors.suburban}"></span>
								<span>{content.legendSuburban} ({chapterData?.classification_breakdown.suburban.length})</span>
							</div>
							<div class="legend-item">
								<span class="legend-swatch" style="background: {classificationColors.town}"></span>
								<span>{content.legendTown} ({chapterData?.classification_breakdown.town.length})</span>
							</div>
							<div class="legend-item">
								<span class="legend-swatch" style="background: {classificationColors.rural}"></span>
								<span>{content.legendRural} ({chapterData?.classification_breakdown.rural.length})</span>
							</div>
						</div>
					{/if}

					{#if activeViz === 'partisan'}
						<div class="legend-row">
							<div class="legend-item">
								<span class="legend-swatch" style="background: {PARTY_COLORS.PPD}"></span>
								<span>{content.legendPpdLean}</span>
							</div>
							<div class="legend-item">
								<span class="legend-swatch" style="background: #f7f7f7; border: 1px solid var(--color-border)"></span>
								<span>{content.legendEven}</span>
							</div>
							<div class="legend-item">
								<span class="legend-swatch" style="background: {PARTY_COLORS.PNP}"></span>
								<span>{content.legendPnpLean}</span>
							</div>
						</div>
					{/if}

					{#if activeViz === 'senate'}
						<div class="legend-row legend-wrap">
							{#each chapterData?.senate_districts || [] as sd}
								<div class="legend-item">
									<span class="legend-swatch" style="background: {CATEGORY_COLORS[(sd.district - 1) % CATEGORY_COLORS.length]}"></span>
									<span>D{sd.district}: {sd.name}</span>
								</div>
							{/each}
						</div>
					{/if}
				{/if}
			</div>
		{/snippet}

		<Step active={currentStep === 0} index={0}>
			<h3>{content.step0Title}</h3>
			<p>{content.step0p1}</p>
			<p>
				{content.step0p2} <span class="highlight">{content.step0p2Highlight}</span>.
			</p>
			<p>{content.step0p3}</p>
		</Step>

		<Step active={currentStep === 1} index={1}>
			<h3>{content.step1Title}</h3>
			<p>
				{content.municipalities78} <span class="stat">78 {$language === 'en' ? 'municipalities' : 'municipios'}</span>
				{content.step1p1}
			</p>
			<p>{content.step1p2}</p>
			<p>{content.step1p3}</p>
		</Step>

		<Step active={currentStep === 2} index={2}>
			<h3>{content.step2Title}</h3>
			<p>
				{content.step2p1a}
				<span style="color: {PARTY_COLORS.PNP}">{content.blueMunicipalities}</span> {content.step2p1b}
				<span style="color: {PARTY_COLORS.PPD}">{content.redMunicipalities}</span>
				{content.step2p1c}
			</p>
			<p>
				{content.step2p2a} {chapterData?.stats.most_pro_pnp || 'Loiza'}
				{content.step2p2b} {chapterData?.stats.most_pro_ppd || 'Cayey'}
				{content.step2p2c}
			</p>
			<p>
				{content.step2p3} <span class="highlight">{content.step2p3Highlight}</span>
				{content.step2p3b}
			</p>
		</Step>

		<Step active={currentStep === 3} index={3}>
			<h3>{content.step3Title}</h3>
			<p>
				{content.step3p1} <span class="highlight">{content.step3p1Highlight}</span>
				{content.step3p1b}
			</p>
			<p>
				<span class="stat">{chapterData?.municipalities[0]?.name || 'San Juan'}</span>
				{content.step3p2a} {((chapterData?.municipalities[0]?.pop_share || 10) ).toFixed(1)}%
				{content.step3p2b}
			</p>
			<p>{content.step3p3}</p>
		</Step>

		<Step active={currentStep === 4} index={4}>
			<h3>{content.step4Title}</h3>
			<p>
				{content.step4p1} <span class="stat">{chapterData?.stats.largest_municipality || 'San Juan'}</span>
				{content.step4p1b} {chapterData?.municipalities[0]?.population.toLocaleString() || '395,000'}
				{content.step4p1c} <span class="stat">{chapterData?.stats.smallest_municipality || 'Culebra'}</span>
				{content.step4p1d} {chapterData?.municipalities[chapterData.municipalities.length - 1]?.population.toLocaleString() || '1,800'}.
			</p>
			<p>
				{content.step4p2} <span class="highlight">{content.step4p2Highlight}</span>{content.step4p2b}
			</p>
			<p>{content.step4p3}</p>
		</Step>

		<Step active={currentStep === 5} index={5} variant="comparison">
			{#snippet before()}
				<span class="stat" style="color: {classificationColors.urban}">{content.comparisonUrbanStat}</span>
				<p><strong>{content.comparisonUrbanLabel}</strong></p>
				<p>{content.comparisonUrbanDesc}</p>
			{/snippet}
			{#snippet after()}
				<span class="stat" style="color: {classificationColors.rural}">{content.comparisonRuralStat}</span>
				<p><strong>{content.comparisonRuralLabel}</strong></p>
				<p>{content.comparisonRuralDesc}</p>
			{/snippet}
			<h3>{content.step5Title}</h3>
			<p>{content.step5p4}</p>
		</Step>

		<Step active={currentStep === 6} index={6} variant="callout">
			<h3>{content.step6Title}</h3>
			<p>
				{content.step6p1} <span class="highlight">{content.step6p1Highlight}</span>.
			</p>
			<p><span class="stat">{content.calloutStatValue}</span> {content.calloutStat}</p>
			<p>{content.calloutInsight}</p>
		</Step>

		<Step active={currentStep === 7} index={7}>
			<h3>{content.step7Title}</h3>
			<p>{content.step7p1}</p>
			<p>
				{content.step7p2a} <span class="highlight">{content.step7p2SanJuan}</span>
				{content.step7p2and} <span class="highlight">{content.step7p2Bayamon}</span>
				{content.step7p2b} <span class="highlight">{content.step7p2Mayaguez}</span>
				{content.step7p2c} <span class="highlight">{content.step7p2Ponce}</span>
				{content.step7p2d}
			</p>
			<p>{content.step7p3}</p>
		</Step>

		<Step active={currentStep === 8} index={8}>
			<h3>{content.step8Title}</h3>
			<p>
				{content.step8p1} <span class="stat">{content.step8p1Senate}</span>{content.step8p1b}
			</p>
			<p>{content.step8p2}</p>
			<p>{content.step8p3}</p>
		</Step>

		<Step active={currentStep === 9} index={9}>
			<h3>{content.step9Title}</h3>
			<p>
				{content.step9p1} <span class="stat">{content.step9p1House}</span>{content.step9p1b}
			</p>
			<p>
				{content.step9p2a} <span class="highlight">{content.step9p2Highlight}</span>{content.step9p2b}
			</p>
			<p>{content.step9p3}</p>
		</Step>

		<Step active={currentStep === 10} index={10}>
			<h3>{content.step10Title}</h3>
			<p>
				{content.step10p1} <span class="stat">{content.step10p1Highlight}</span>
				{content.step10p1b}
			</p>
			<p>{content.step10p2}</p>
			<p>{content.step10p3}</p>
		</Step>

		<Step active={currentStep === 11} index={11} variant="question">
			<h3>{content.questionTitle}</h3>
			<p>{content.questionP1}</p>
			<p>{content.questionP2}</p>
		</Step>
	</ScrollySection>

	<section class="chapter-conclusion">
		<div class="container content">
			<h2>{content.conclusionTitle}</h2>
			<p>{content.conclusionP1}</p>

			<div class="key-takeaways">
				<h3>{content.keyTakeaways}</h3>
				<ul>
					<li><strong>{content.takeaway1Title}</strong> {content.takeaway1}</li>
					<li><strong>{content.takeaway2Title}</strong> {content.takeaway2}</li>
					<li><strong>{content.takeaway3Title}</strong> {content.takeaway3}</li>
					<li><strong>{content.takeaway4Title}</strong> {content.takeaway4}</li>
					<li><strong>{content.takeaway5Title}</strong> {content.takeaway5}</li>
				</ul>
			</div>

			<div class="sources">
				<h3>{content.sources}</h3>
				<ul>
					<li><a href="https://ww2.ceepur.org/Home/EventosElectorales" target="_blank" rel="noopener">Comision Estatal de Elecciones de Puerto Rico (CEE)</a> - {content.sourceCee}</li>
					<li><a href="https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html" target="_blank" rel="noopener">U.S. Census Bureau</a> - {content.sourceCensus}</li>
					<li>{content.sourcePlanningBoard}</li>
					<li><a href="https://data.census.gov/" target="_blank" rel="noopener">American Community Survey</a> - {content.sourceAcs}</li>
				</ul>
			</div>

			<nav class="chapter-nav">
				<a href="{base}/chapters/referendum-2020" class="nav-link prev">
					<span class="nav-direction">{content.previous}</span>
					<span class="nav-title">{content.prevTitle}</span>
				</a>
				<a href="{base}/chapters/fortaleza" class="nav-link next">
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
		color: var(--color-text-light);
		margin-top: var(--space-md);
		font-style: italic;
	}

	.bar-container {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.legend-row {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-md);
		margin-top: var(--space-lg);
		justify-content: center;
	}

	.legend-wrap {
		max-width: 500px;
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: var(--space-xs);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.legend-swatch {
		width: 16px;
		height: 16px;
		border-radius: var(--radius-sm);
	}

	.chapter-conclusion {
		padding: var(--space-3xl) 0;
		background: var(--color-surface);
	}

	.key-takeaways {
		margin: var(--space-xl) 0;
		padding: var(--space-lg);
		background: var(--color-bg);
		border-radius: var(--radius-lg);
		border-left: 4px solid var(--color-accent);
	}

	.key-takeaways h3 {
		font-size: var(--text-md);
		font-weight: var(--font-semibold);
		margin-bottom: var(--space-md);
		color: var(--color-text);
	}

	.key-takeaways ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.key-takeaways li {
		padding: var(--space-sm) 0;
		border-bottom: 1px solid var(--color-border);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.key-takeaways li:last-child {
		border-bottom: none;
	}

	.key-takeaways strong {
		color: var(--color-text);
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

	.nav-link:hover { background: var(--color-bg); }
	.nav-link.next { text-align: right; }
	.nav-direction { font-size: var(--text-sm); color: var(--color-text-muted); }
	.nav-title { font-family: var(--font-display); font-size: var(--text-lg); font-weight: var(--font-semibold); color: var(--color-text); }

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

		.viz-container {
			padding: var(--space-sm);
		}

		.viz-title {
			font-size: var(--text-base);
			margin-bottom: var(--space-sm);
		}

		.legend-row {
			gap: var(--space-sm);
			margin-top: var(--space-md);
		}

		.legend-wrap {
			max-width: 100%;
		}

		.legend-item {
			font-size: var(--text-xs);
		}

		.legend-swatch {
			width: 12px;
			height: 12px;
		}

		.key-takeaways {
			padding: var(--space-md);
		}

		.key-takeaways h3 {
			font-size: var(--text-sm);
		}

		.key-takeaways li {
			font-size: var(--text-xs);
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
