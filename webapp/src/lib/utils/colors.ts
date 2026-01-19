/**
 * Color utilities for data visualization
 * Matches OpenDataPR/MojaveDataOps design system
 */

// Categorical palette for multi-series charts
export const CATEGORY_COLORS = [
	'#4a9eda',  // Blue (OpenDataPR)
	'#d4a373',  // Gold
	'#7c9a5e',  // Green
	'#c9695a',  // Red
	'#6b9080',  // Teal
	'#9b8bb3',  // Purple
	'#e8c49a',  // Light tan
] as const;

// Diverging palette (Blue to Red) for bipolar data
export const DIVERGING_COLORS = [
	'#2166ac',  // Strong blue (low)
	'#67a9cf',
	'#d1e5f0',
	'#f7f7f7',  // White (mid)
	'#fddbc7',
	'#ef8a62',
	'#b2182b',  // Strong red (high)
] as const;

// Sequential palette for single-variable gradients
export const SEQUENTIAL_COLORS = [
	'#0c0b0a',
	'#1a3a5c',
	'#2166ac',
	'#4a9eda',
	'#8fc4eb',
] as const;

// Puerto Rico political party colors
export const PARTY_COLORS: Record<string, string> = {
	'PNP': '#1e4d8c',    // Partido Nuevo Progresista (statehood)
	'PPD': '#c41e3a',    // Partido Popular Democrático (commonwealth)
	'PIP': '#228b22',    // Partido Independentista (independence)
	'MVC': '#9b59b6',    // Movimiento Victoria Ciudadana
	'PD': '#ff6b35',     // Proyecto Dignidad
	'IND': '#888888',    // Independent
};

/**
 * Get party color with fallback
 */
export function getPartyColor(party: string): string {
	return PARTY_COLORS[party.toUpperCase()] || PARTY_COLORS['IND'];
}

/**
 * Create a diverging color interpolator
 * @param domain [min, mid, max] values
 */
export function createDivergingScale(domain: [number, number, number]) {
	const [min, mid, max] = domain;
	const colors = DIVERGING_COLORS;
	const midIndex = Math.floor(colors.length / 2);

	return (value: number): string => {
		if (value <= min) return colors[0];
		if (value >= max) return colors[colors.length - 1];

		if (value < mid) {
			const t = (value - min) / (mid - min);
			const index = Math.floor(t * midIndex);
			return colors[Math.min(index, midIndex)];
		} else {
			const t = (value - mid) / (max - mid);
			const index = midIndex + Math.floor(t * (colors.length - midIndex - 1));
			return colors[Math.min(index, colors.length - 1)];
		}
	};
}

/**
 * Create a sequential color interpolator
 * @param domain [min, max] values
 */
export function createSequentialScale(domain: [number, number]) {
	const [min, max] = domain;
	const colors = SEQUENTIAL_COLORS;

	return (value: number): string => {
		if (value <= min) return colors[0];
		if (value >= max) return colors[colors.length - 1];

		const t = (value - min) / (max - min);
		const index = Math.floor(t * (colors.length - 1));
		return colors[index];
	};
}

// Sequential scale for loss data (light = no loss, dark red = severe loss)
export const SEQUENTIAL_LOSS_COLORS = ['#f7f7f7', '#fddbc7', '#f4a582', '#d6604d', '#b2182b'] as const;

// Sequential scale for percentage data (light = low, dark blue = high)
export const SEQUENTIAL_BLUE_COLORS = ['#f7fbff', '#c6dbef', '#6baed6', '#2171b5', '#084594'] as const;

// Sequential scale for poverty data (light = low poverty, dark orange-red = high poverty)
export const SEQUENTIAL_POVERTY_COLORS = ['#fff5eb', '#fdd49e', '#fdae6b', '#f16913', '#8c2d04'] as const;

/**
 * Create a sequential blue color scale (light = low, dark blue = high)
 * Good for turnout, participation rates, positive metrics
 * @param domain [min, max] values
 */
export function createSequentialBlueScale(domain: [number, number]) {
	const [min, max] = domain;
	return (value: number): string => {
		const t = Math.max(0, Math.min(1, (value - min) / (max - min)));
		const colors = SEQUENTIAL_BLUE_COLORS;
		const idx = Math.min(Math.floor(t * (colors.length - 1)), colors.length - 2);
		return colors[idx + 1];
	};
}

/**
 * Create a loss scale for negative change data
 * Light = no loss, dark red = severe loss
 * @param domain [worst_loss, no_loss] e.g., [-30, 0]
 */
export function createLossScale(domain: [number, number]) {
	const [min, max] = domain;
	return (value: number): string => {
		// Invert so worst loss (most negative) = darkest
		const t = Math.max(0, Math.min(1, (max - value) / (max - min)));
		const colors = SEQUENTIAL_LOSS_COLORS;
		const idx = Math.min(Math.floor(t * (colors.length - 1)), colors.length - 2);
		return colors[idx + 1];
	};
}

/**
 * Create a poverty scale (light = low poverty, dark orange-red = high poverty)
 * @param domain [min, max] poverty rates e.g., [20, 65]
 */
export function createPovertyScale(domain: [number, number]) {
	const [min, max] = domain;
	return (value: number): string => {
		const t = Math.max(0, Math.min(1, (value - min) / (max - min)));
		const colors = SEQUENTIAL_POVERTY_COLORS;
		const idx = Math.min(Math.floor(t * (colors.length - 1)), colors.length - 2);
		return colors[idx + 1];
	};
}

/**
 * Get a categorical color by index (cycles through palette)
 * @param index The index of the item
 */
export function getCategoryColor(index: number): string {
	return CATEGORY_COLORS[index % CATEGORY_COLORS.length];
}

/**
 * Create a categorical color scale for a list of items
 * @param items Array of unique identifiers
 */
export function createCategoricalScale(items: string[]): (item: string) => string {
	const colorMap = new Map<string, string>();
	items.forEach((item, index) => {
		colorMap.set(item, getCategoryColor(index));
	});
	return (item: string): string => colorMap.get(item) || CATEGORY_COLORS[0];
}

/**
 * Lighten a hex color by a percentage
 * @param hex The hex color (e.g., '#4a9eda')
 * @param percent Percentage to lighten (0-100)
 */
export function lightenColor(hex: string, percent: number): string {
	const num = parseInt(hex.replace('#', ''), 16);
	const r = Math.min(255, ((num >> 16) & 255) + Math.round(255 * percent / 100));
	const g = Math.min(255, ((num >> 8) & 255) + Math.round(255 * percent / 100));
	const b = Math.min(255, (num & 255) + Math.round(255 * percent / 100));
	return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
}

/**
 * Darken a hex color by a percentage
 * @param hex The hex color (e.g., '#4a9eda')
 * @param percent Percentage to darken (0-100)
 */
export function darkenColor(hex: string, percent: number): string {
	const num = parseInt(hex.replace('#', ''), 16);
	const r = Math.max(0, ((num >> 16) & 255) - Math.round(255 * percent / 100));
	const g = Math.max(0, ((num >> 8) & 255) - Math.round(255 * percent / 100));
	const b = Math.max(0, (num & 255) - Math.round(255 * percent / 100));
	return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
}

/**
 * Get a contrasting text color (black or white) for a given background
 * @param hex The background hex color
 */
export function getContrastColor(hex: string): string {
	const num = parseInt(hex.replace('#', ''), 16);
	const r = (num >> 16) & 255;
	const g = (num >> 8) & 255;
	const b = num & 255;
	// Use relative luminance formula
	const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
	return luminance > 0.5 ? '#0c0b0a' : '#f5f5f4';
}
