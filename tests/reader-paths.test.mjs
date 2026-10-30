import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

async function builtPage(path) {
  return readFile(new URL(`../dist/${path}`, import.meta.url), 'utf8');
}

test('homepage includes the editorial briefing and topic hub', async () => {
  const html = await builtPage('index.html');
  assert.match(html, /本期导读/);
  assert.match(html, /href="\/topics"/);
});

test('archive includes both filtering controls', async () => {
  const html = await builtPage('journal/index.html');
  assert.match(html, /id="archive-year"/);
  assert.match(html, /id="archive-tag"/);
});

test('topic and search pages expose discovery paths', async () => {
  const topics = await builtPage('topics/index.html');
  const search = await builtPage('search/index.html');
  assert.match(topics, /模型发布/);
  assert.match(search, /输入关键词开始搜索/);
});
