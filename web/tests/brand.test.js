// Brand rules for the lookup page (decision 0006): The Spiritual Weather Report's name, and its naming rules.
import { readdirSync, readFileSync } from 'node:fs';
import { expect, it } from 'vitest';

const dir = new URL('../ui/', import.meta.url);
const files = readdirSync(dir).map((name) => [name, readFileSync(new URL(name, dir), 'utf8')]);
const all = files.map(([, text]) => text).join('\n');

it('carries the brand name and the Gift Index name', () => {
  expect(all).toContain('THE SPIRITUAL WEATHER REPORT');
  expect(all).toContain('The Gift Index');
});

it('follows the site naming rules: always "Jennie Marie", never the other business name', () => {
  for (const [name, text] of files) {
    expect(/Heavenly Activations/i.test(text), name).toBe(false);
    expect(/\bJen\b(?!nie)/.test(text), name).toBe(false);
  }
});

it('keeps one theme: the brand colors do not flip in dark mode', () => {
  const css = files.find(([name]) => name === 'style.css')[1];
  expect(css).not.toMatch(/prefers-color-scheme/);
  expect(css).toMatch(/--plum:\s*#2b0b45/);
  expect(css).toMatch(/--gold:\s*#ffc62e/);
});
