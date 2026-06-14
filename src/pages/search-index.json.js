import { getCollection } from 'astro:content';
import { getWeekTitle } from '../utils/date.js';

/**
 * 将 Markdown 内容转换为纯文本摘要
 * 移除 markdown 语法，保留可读文本
 */
function markdownToPlainText(md) {
  if (!md) return '';
  return md
    // 移除图片 ![alt](url)
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, '$1')
    // 移除链接 [text](url) 但保留文本
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    // 移除标题标记 #
    .replace(/^#{1,6}\s+/gm, '')
    // 移除水平分隔线 ---
    .replace(/^\s*-{3,}\s*$/gm, '')
    // 移除粗体和斜体标记
    .replace(/(\*\*|__)(.+?)\1/g, '$2')
    .replace(/(\*|_)(.+?)\1/g, '$2')
    // 移除行内代码和代码块
    .replace(/`{1,3}[^`]*`{1,3}/g, '')
    // 移除 HTML 标签
    .replace(/<[^>]+>/g, '')
    // 移除列表标记
    .replace(/^\s*[-*+]\s+/gm, '')
    .replace(/^\s*\d+\.\s+/gm, '')
    // 移除引用标记
    .replace(/^\s*>\s+/gm, '')
    // 合并多余空行
    .replace(/\n{3,}/g, '\n\n')
    // 移除首尾空白
    .trim();
}

export async function GET() {
  const weekly = await getCollection('weekly');

  const index = weekly.map((entry) => ({
    slug: entry.slug,
    title: entry.data.title,
    displayTitle: getWeekTitle(entry.data.date),
    description: entry.data.description || entry.data.excerpt || '',
    date: entry.data.date,
    tags: entry.data.tags,
    content: markdownToPlainText(entry.body || '').substring(0, 3000),
  }));

  return new Response(JSON.stringify(index), {
    headers: { 'Content-Type': 'application/json' },
  });
}
