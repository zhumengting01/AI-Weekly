import { format, getISOWeek, getISOWeekYear } from 'date-fns';
import { zhCN } from 'date-fns/locale';

/**
 * 将日期字符串或 Date 对象格式化为中文可读格式
 * @param {string|Date} date - 要格式化的日期
 * @returns {string} - 格式化后的日期字符串
 */
export function formatDate(date) {
  const dateObject = typeof date === 'string' ? new Date(date) : date;
  return format(dateObject, 'yyyy年M月d日', { locale: zhCN });
}

/**
 * 根据日期生成周刊标题，格式为 "YYYY年第X周"
 * @param {string|Date} date - 日期
 * @returns {string} - 格式如 "2026年第24周"
 */
export function getWeekTitle(date) {
  const dateObject = typeof date === 'string' ? new Date(date) : date;
  const year = getISOWeekYear(dateObject);
  const week = getISOWeek(dateObject);
  return `${year}年第${week}周`;
}
