import { getWeekTitle } from './date';

/** Combine the stable issue label with the editor's descriptive headline. */
export function formatWeeklyTitle(date: string | Date, title: string) {
  return `${getWeekTitle(date)}｜${title}`;
}
