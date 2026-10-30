import { globSync } from 'node:fs';
import { readFile } from 'node:fs/promises';

const files = globSync('src/content/weekly/**/*.{md,mdx}', { windowsPathsNoEscape: true });
const allIssues = process.argv.includes('--all');

async function loadIssue(file) {
  const source = await readFile(file, 'utf8');
  const frontmatter = source.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!frontmatter) return { file, source, date: '' };
  const date = frontmatter[1].match(/^date:\s*(.+)$/m)?.[1] ?? '';
  return { file, source: frontmatter[1], date };
}

const issues = await Promise.all(files.map(loadIssue));
const targets = allIssues ? issues : [issues.sort((a, b) => b.date.localeCompare(a.date))[0]].filter(Boolean);
const failures = [];

for (const issue of targets) {
  const missing = [];
  for (const field of ['periodStart', 'periodEnd', 'readerFor', 'sourcesCount']) {
    if (!new RegExp(`^${field}:\\s*.+$`, 'm').test(issue.source)) missing.push(field);
  }
  const takeaways = issue.source.match(/^\s{2}-\s+.+$/gm) ?? [];
  if (takeaways.length < 3) missing.push('three takeaways');
  const tags = issue.source.match(/^tags:\s*\[([^\]]*)\]/m)?.[1] ?? '';
  if (!tags.split(',').some((tag) => !['AI', '周刊'].includes(tag.trim()))) missing.push('a discovery tag');
  if (missing.length > 0) failures.push({ file: issue.file, missing });
}

if (failures.length === 0) {
  console.log(`Content gate passed for ${targets.length} issue${targets.length === 1 ? '' : 's'}.`);
} else {
  for (const failure of failures) console.error(`${failure.file}: missing ${failure.missing.join(', ')}`);
  process.exitCode = 1;
}
