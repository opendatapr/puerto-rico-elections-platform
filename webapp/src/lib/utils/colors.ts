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
