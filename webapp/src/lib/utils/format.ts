/**
 * Number and date formatting utilities
 */

/**
 * Format a number as a percentage
 */
export function formatPercent(value: number, decimals = 1): string {
	return `${value.toFixed(decimals)}%`;
}

/**
 * Format a number with thousand separators
 */
export function formatNumber(value: number): string {
	return new Intl.NumberFormat('en-US').format(value);
}

/**
 * Format a number as compact (e.g., 1.2M, 500K)
 */
export function formatCompact(value: number): string {
	return new Intl.NumberFormat('en-US', {
		notation: 'compact',
		maximumFractionDigits: 1,
	}).format(value);
}

/**
 * Format a date for display
 */
export function formatDate(date: Date | string): string {
	const d = typeof date === 'string' ? new Date(date) : date;
	return new Intl.DateTimeFormat('en-US', {
		year: 'numeric',
		month: 'long',
		day: 'numeric',
	}).format(d);
}

/**
 * Format election year
 */
export function formatElectionYear(year: number): string {
	return `${year} Election`;
}

/**
 * Format change with +/- prefix
 */
export function formatChange(value: number, decimals = 1): string {
	const prefix = value > 0 ? '+' : '';
	return `${prefix}${value.toFixed(decimals)}`;
}

/**
 * Format change as percentage with +/- prefix
 */
export function formatPercentChange(value: number, decimals = 1): string {
	const prefix = value > 0 ? '+' : '';
	return `${prefix}${value.toFixed(decimals)}%`;
}
