import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export type Language = 'en' | 'es';

// Initialize from localStorage or default to Spanish for PR audience
const storedLang = browser ? localStorage.getItem('language') as Language : null;
const initialLang: Language = storedLang === 'en' || storedLang === 'es' ? storedLang : 'es';

export const language = writable<Language>(initialLang);

// Persist to localStorage on change
if (browser) {
	language.subscribe((value) => {
		localStorage.setItem('language', value);
	});
}
