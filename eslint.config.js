// ESLint flat config: code quality + architecture guardrails.
import js from '@eslint/js';
import globals from 'globals';
import tseslint from 'typescript-eslint';

// ARCHITECTURE: which folders may NOT import from which.
// Each rule = files matching `from` may not import `forbid`. See docs/decisions/0003.
const ARCHITECTURE = [
  { from: ['web/engine/**'], forbid: ['**/ui/**'], why: 'The engine is pure calculation. It must never depend on the page (web/ui).' },
];

export default tseslint.config(
  { ignores: ['node_modules', '**/node_modules', 'dist', 'build', 'coverage', 'CODEMAP.md', 'web/data/**'] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    languageOptions: { globals: { ...globals.browser, ...globals.node } },
    rules: {
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      'max-lines': ['warn', { max: 400, skipBlankLines: true, skipComments: true }],
      complexity: ['warn', 15],
    },
  },
  { files: ['scripts/**'], rules: { 'no-console': 'off' } },
  { files: ['**/*.cjs'], rules: { '@typescript-eslint/no-require-imports': 'off', '@typescript-eslint/no-implied-eval': 'off' } },
  ...ARCHITECTURE.map((r) => ({
    files: r.from,
    rules: {
      'no-restricted-imports': ['error', { patterns: [{ group: r.forbid, message: r.why }] }],
      'no-restricted-globals': ['error', { name: 'document', message: 'No page access in the engine.' }, { name: 'window', message: 'No page access in the engine.' }],
    },
  })),
);
