import { globSync } from 'node:fs';
import { readFile } from 'node:fs/promises';

const files = globSync('src/content/weekly/**/*.{md,mdx}', { windowsPathsNoEscape: true });
const linkPattern = /(?<!!)\[[^\]]*\]\((https?:\/\/[^\s)]+)(?:\s+[^)]*)?\)/g;
const timeoutMs = 12_000;
const verbose = process.argv.includes('--verbose');

async function checkLink(url) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    let response = await fetch(url, { method: 'HEAD', redirect: 'follow', signal: controller.signal });
    if (response.status === 405 || response.status === 501) {
      response = await fetch(url, { method: 'GET', redirect: 'follow', signal: controller.signal });
    }
    return { url, ok: response.ok, status: response.status };
  } catch (error) {
    return { url, ok: false, status: error.name === 'AbortError' ? 'timeout' : 'network error' };
  } finally {
    clearTimeout(timeout);
  }
}

const links = new Map();
for (const file of files) {
  const content = await readFile(file, 'utf8');
  for (const match of content.matchAll(linkPattern)) {
    const url = match[1];
    links.set(url, [...(links.get(url) ?? []), file]);
  }
}

const results = await Promise.all([...links.keys()].map(checkLink));
// 401/403/429 and transient network failures often indicate bot protection rather
// than a dead page. Report them, but reserve a failing exit code for links that
// an HTTP response can positively identify as unavailable.
const failures = results.filter((result) =>
  typeof result.status === 'number'
  && result.status >= 400
  && ![401, 403, 429].includes(result.status),
);
const inconclusive = results.filter((result) => !result.ok && !failures.includes(result));

console.log(`Checked ${results.length} unique source links across ${files.length} weekly issues.`);
for (const failure of failures) {
  console.error(`[${failure.status}] ${failure.url}`);
  for (const file of links.get(failure.url)) console.error(`  - ${file}`);
}

if (failures.length > 0) process.exitCode = 1;

if (inconclusive.length > 0) {
  console.warn(`Could not automatically verify ${inconclusive.length} links (bot protection or transient network errors).`);
  const byDomain = new Map();
  for (const result of inconclusive) {
    const domain = new URL(result.url).hostname;
    byDomain.set(domain, (byDomain.get(domain) ?? 0) + 1);
  }
  for (const [domain, count] of [...byDomain.entries()].sort((a, b) => b[1] - a[1])) {
    console.warn(`  - ${domain}: ${count}`);
  }
  if (verbose) {
    for (const result of inconclusive) console.warn(`[${result.status}] ${result.url}`);
  }
}
