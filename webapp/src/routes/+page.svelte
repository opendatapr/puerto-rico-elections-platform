<script lang="ts">
	import { base } from '$app/paths';
	import { language } from '$lib/stores/language';

	// Bilingual content
	const content = {
		en: {
			label: 'Data Journalism Series',
			title: 'Puerto Rico Elections',
			lead: "An interactive exploration of Puerto Rico's electoral dynamics from 2012 to 2024. How migration, demographics, and geography shape political outcomes on the island.",
			cta: 'Start Reading',
			chaptersTitle: 'Chapters',
			stats: {
				chapters: 'Chapters',
				municipalities: 'Municipalities',
				years: 'Years of Data'
			},
			about: {
				title: 'About This Project',
				p1: "This data journalism series analyzes Puerto Rico's electoral landscape through the lens of demographic change, migration patterns, and geographic voting behavior. Using data from the Puerto Rico State Elections Commission (CEE) and the U.S. Census Bureau, we explore how the island's political dynamics have evolved over the past decade.",
				p2: 'All data and code are open source. The analysis uses statistical methods including regression modeling, spatial autocorrelation tests, and time series analysis to uncover patterns in voter behavior.'
			},
			parts: {
				part1: 'Part I: The Transformation',
				part2: 'Part II: The Status Question',
				part3: 'Part III: The Gubernatorial Battle',
				part4: 'Part IV: The Legislature',
				part5: 'Part V: Synthesis'
			}
		},
		es: {
			label: 'Serie de Periodismo de Datos',
			title: 'Elecciones de Puerto Rico',
			lead: 'Una exploracion interactiva de la dinamica electoral de Puerto Rico desde 2012 hasta 2024. Como la migracion, la demografia y la geografia determinan los resultados politicos en la isla.',
			cta: 'Comenzar a Leer',
			chaptersTitle: 'Capitulos',
			stats: {
				chapters: 'Capitulos',
				municipalities: 'Municipios',
				years: 'Anos de Datos'
			},
			about: {
				title: 'Sobre Este Proyecto',
				p1: 'Esta serie de periodismo de datos analiza el panorama electoral de Puerto Rico a traves del lente del cambio demografico, los patrones de migracion y el comportamiento geografico del voto. Utilizando datos de la Comision Estatal de Elecciones (CEE) y la Oficina del Censo de EE.UU., exploramos como ha evolucionado la dinamica politica de la isla durante la ultima decada.',
				p2: 'Todos los datos y el codigo son de fuente abierta. El analisis utiliza metodos estadisticos que incluyen modelos de regresion, pruebas de autocorrelacion espacial y analisis de series temporales para descubrir patrones en el comportamiento electoral.'
			},
			parts: {
				part1: 'Parte I: La Transformacion',
				part2: 'Parte II: La Cuestion del Estatus',
				part3: 'Parte III: La Batalla por La Fortaleza',
				part4: 'Parte IV: La Legislatura',
				part5: 'Parte V: Sintesis'
			}
		}
	};

	// Bilingual chapter data
	const chaptersData = {
		en: [
			{
				part: 'Part I: The Transformation',
				items: [
					{ num: 1, slug: 'exodus', title: 'The Great Exodus', desc: 'Migration impact, population collapse, Maria\'s effect' },
					{ num: 2, slug: 'turnout', title: 'Democracy Under Strain', desc: 'Turnout patterns and socioeconomic predictors' },
					{ num: 3, slug: 'shrinking', title: 'The Shrinking Electorate', desc: 'Vote loss geography by municipality and precinct' },
				]
			},
			{
				part: 'Part II: The Status Question',
				items: [
					{ num: 4, slug: 'plebiscites', title: 'One Question, Two Decades', desc: 'All plebiscites 2012-2024, question formats' },
					{ num: 5, slug: 'referendum-2020', title: 'The 52.5% Threshold', desc: '2020 referendum deep dive, precinct analysis' },
					{ num: 6, slug: 'geography', title: 'Divided by Design', desc: 'Geographic patterns, spatial autocorrelation' },
				]
			},
			{
				part: 'Part III: The Gubernatorial Battle',
				items: [
					{ num: 7, slug: 'fortaleza', title: 'La Fortaleza', desc: 'Governor races 2012-2024, party dynamics' },
					{ num: 8, slug: 'battlegrounds', title: '78 Battlegrounds', desc: 'Municipality-level results, swing municipalities' },
					{ num: 9, slug: 'precincts', title: 'Down to the Precinct', desc: 'Intra-municipal variation in major cities' },
				]
			},
			{
				part: 'Part IV: The Legislature',
				items: [
					{ num: 10, slug: 'senate', title: 'The Senate Districts', desc: '8 district analysis, cross-municipal composition' },
					{ num: 11, slug: 'house', title: '40 House Races', desc: 'Representative districts, competitive vs safe seats' },
				]
			},
			{
				part: 'Part V: Synthesis',
				items: [
					{ num: 12, slug: 'future', title: 'Puerto Rico\'s Electoral Future', desc: 'Projections and demographic trajectory' },
				]
			}
		],
		es: [
			{
				part: 'Parte I: La Transformacion',
				items: [
					{ num: 1, slug: 'exodus', title: 'El Gran Exodo', desc: 'Impacto migratorio, colapso poblacional, el efecto de Maria' },
					{ num: 2, slug: 'turnout', title: 'Democracia Bajo Presion', desc: 'Patrones de participacion y predictores socioeconomicos' },
					{ num: 3, slug: 'shrinking', title: 'El Electorado Menguante', desc: 'Geografia de perdida de votos por municipio y precinto' },
				]
			},
			{
				part: 'Parte II: La Cuestion del Estatus',
				items: [
					{ num: 4, slug: 'plebiscites', title: 'Una Pregunta, Dos Decadas', desc: 'Todos los plebiscitos 2012-2024, formatos de pregunta' },
					{ num: 5, slug: 'referendum-2020', title: 'El Umbral del 52.5%', desc: 'Analisis profundo del referendum 2020, analisis por precinto' },
					{ num: 6, slug: 'geography', title: 'Divididos por Diseno', desc: 'Patrones geograficos, autocorrelacion espacial' },
				]
			},
			{
				part: 'Parte III: La Batalla por La Fortaleza',
				items: [
					{ num: 7, slug: 'fortaleza', title: 'La Fortaleza', desc: 'Carreras para gobernador 2012-2024, dinamica de partidos' },
					{ num: 8, slug: 'battlegrounds', title: '78 Campos de Batalla', desc: 'Resultados municipales, municipios indecisos' },
					{ num: 9, slug: 'precincts', title: 'Hasta el Precinto', desc: 'Variacion intramunicipal en ciudades principales' },
				]
			},
			{
				part: 'Parte IV: La Legislatura',
				items: [
					{ num: 10, slug: 'senate', title: 'Los Distritos Senatoriales', desc: 'Analisis de 8 distritos, composicion intermunicipal' },
					{ num: 11, slug: 'house', title: '40 Carreras de Representantes', desc: 'Distritos representativos, escanos competitivos vs seguros' },
				]
			},
			{
				part: 'Parte V: Sintesis',
				items: [
					{ num: 12, slug: 'future', title: 'El Futuro Electoral de Puerto Rico', desc: 'Proyecciones y trayectoria demografica' },
				]
			}
		]
	};

	// Reactive content based on language
	let t = $derived(content[$language]);
	let chapters = $derived(chaptersData[$language]);
</script>

<section class="hero">
	<div class="container">
		<div class="hero-content">
			<span class="label">{t.label}</span>
			<div class="accent-line"></div>
			<h1>{t.title}</h1>
			<p class="lead">{t.lead}</p>
			<a href="#chapters" class="cta-button">
				{t.cta}
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M12 5v14M19 12l-7 7-7-7"/>
				</svg>
			</a>
		</div>
		<div class="hero-stats">
			<div class="stat">
				<span class="stat-value">12</span>
				<span class="stat-label">{t.stats.chapters}</span>
			</div>
			<div class="stat">
				<span class="stat-value">78</span>
				<span class="stat-label">{t.stats.municipalities}</span>
			</div>
			<div class="stat">
				<span class="stat-value">12+</span>
				<span class="stat-label">{t.stats.years}</span>
			</div>
		</div>
	</div>
</section>

<section id="chapters" class="chapters-section">
	<div class="container">
		<h2>{t.chaptersTitle}</h2>

		{#each chapters as part}
			<div class="part-group">
				<h3 class="part-title">{part.part}</h3>
				<div class="chapter-grid">
					{#each part.items as chapter}
						<a href="{base}/chapters/{chapter.slug}" class="chapter-card">
							<span class="chapter-num">{String(chapter.num).padStart(2, '0')}</span>
							<h4 class="chapter-title">{chapter.title}</h4>
							<p class="chapter-desc">{chapter.desc}</p>
							<span class="chapter-arrow">
								<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M5 12h14M12 5l7 7-7 7"/>
								</svg>
							</span>
						</a>
					{/each}
				</div>
			</div>
		{/each}
	</div>
</section>

<section class="about-section">
	<div class="container content">
		<h2>{t.about.title}</h2>
		<p>{t.about.p1}</p>
		<p>{t.about.p2}</p>
	</div>
</section>

<style>
	.hero {
		min-height: calc(100vh - var(--header-height));
		display: flex;
		align-items: center;
		padding: var(--space-3xl) 0;
		background: radial-gradient(ellipse at 50% 0%, var(--color-surface) 0%, var(--color-bg) 70%);
	}

	.hero .container {
		display: grid;
		grid-template-columns: 1fr auto;
		gap: var(--space-3xl);
		align-items: center;
	}

	.hero-content h1 {
		margin-bottom: var(--space-lg);
	}

	.hero-content .lead {
		margin-bottom: var(--space-xl);
		max-width: 50ch;
	}

	.cta-button {
		display: inline-flex;
		align-items: center;
		gap: var(--space-sm);
		padding: var(--space-md) var(--space-xl);
		background: var(--color-accent);
		color: var(--color-bg);
		font-weight: var(--font-semibold);
		border-radius: var(--radius-md);
		transition: all var(--transition-base);
	}

	.cta-button:hover {
		background: var(--color-accent-light);
		color: var(--color-bg);
		transform: translateY(-2px);
		box-shadow: var(--shadow-lg), var(--shadow-glow);
	}

	.hero-stats {
		display: flex;
		flex-direction: column;
		gap: var(--space-lg);
	}

	.stat {
		text-align: right;
		padding: var(--space-md) var(--space-lg);
		background: var(--color-surface);
		border-radius: var(--radius-lg);
		border: 1px solid var(--color-border);
	}

	.stat-value {
		display: block;
		font-family: var(--font-display);
		font-size: var(--text-4xl);
		font-weight: var(--font-bold);
		color: var(--color-accent);
		line-height: 1;
	}

	.stat-label {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.chapters-section {
		padding: var(--space-3xl) 0;
	}

	.chapters-section h2 {
		margin-bottom: var(--space-2xl);
	}

	.part-group {
		margin-bottom: var(--space-2xl);
	}

	.part-title {
		font-size: var(--text-sm);
		font-weight: var(--font-semibold);
		letter-spacing: var(--tracking-wide);
		text-transform: uppercase;
		color: var(--color-accent);
		margin-bottom: var(--space-lg);
	}

	.chapter-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: var(--space-lg);
	}

	.chapter-card {
		position: relative;
		display: block;
		padding: var(--space-lg);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		text-decoration: none;
		transition: all var(--transition-base);
	}

	.chapter-card:hover {
		border-color: var(--color-border-light);
		transform: translateY(-4px);
		box-shadow: var(--shadow-lg);
	}

	.chapter-num {
		font-family: var(--font-mono);
		font-size: var(--text-xs);
		color: var(--color-accent);
		margin-bottom: var(--space-sm);
		display: block;
	}

	.chapter-title {
		font-size: var(--text-lg);
		margin-bottom: var(--space-sm);
		color: var(--color-text);
	}

	.chapter-desc {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		margin: 0;
	}

	.chapter-arrow {
		position: absolute;
		bottom: var(--space-lg);
		right: var(--space-lg);
		color: var(--color-text-light);
		transition: all var(--transition-fast);
	}

	.chapter-card:hover .chapter-arrow {
		color: var(--color-accent);
		transform: translateX(4px);
	}

	.about-section {
		padding: var(--space-3xl) 0;
		background: var(--color-surface);
	}

	.about-section h2 {
		margin-bottom: var(--space-lg);
	}

	@media (max-width: 768px) {
		.hero .container {
			grid-template-columns: 1fr;
			gap: var(--space-xl);
		}

		.hero-stats {
			flex-direction: row;
			justify-content: space-between;
		}

		.stat {
			text-align: center;
			flex: 1;
		}

		.chapter-grid {
			grid-template-columns: 1fr;
		}
	}

	/* Mobile adjustments */
	@media (max-width: 640px) {
		.hero {
			min-height: auto;
			padding: var(--space-xl) 0;
		}

		.hero-content .lead {
			font-size: var(--text-base);
		}

		.hero-stats {
			flex-wrap: wrap;
			gap: var(--space-sm);
		}

		.stat {
			padding: var(--space-sm) var(--space-md);
			flex: 1 1 30%;
			min-width: 80px;
		}

		.stat-value {
			font-size: var(--text-2xl);
		}

		.stat-label {
			font-size: var(--text-xs);
		}

		.cta-button {
			width: 100%;
			justify-content: center;
			padding: var(--space-md);
		}

		.chapters-section {
			padding: var(--space-xl) 0;
		}

		.part-title {
			font-size: var(--text-xs);
		}

		.chapter-card {
			padding: var(--space-md);
		}

		.chapter-title {
			font-size: var(--text-base);
			padding-right: var(--space-xl);
		}

		.chapter-desc {
			font-size: var(--text-xs);
		}

		.about-section {
			padding: var(--space-xl) 0;
		}

		.about-section p {
			font-size: var(--text-sm);
		}
	}
</style>
