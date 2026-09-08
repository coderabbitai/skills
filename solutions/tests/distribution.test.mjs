import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';

const root = fileURLToPath(new URL('../../', import.meta.url));
const defaultSkills = ['autofix', 'code-review'];

test('ordinary skill source contains only the default skills', () => {
  const names = readdirSync(new URL('../../skills/', import.meta.url))
    .filter((name) => existsSync(new URL(`../../skills/${name}/SKILL.md`, import.meta.url)))
    .sort();
  assert.deepEqual(names, defaultSkills);
  const cursor = JSON.parse(readFileSync(new URL('../../.cursor-plugin/plugin.json', import.meta.url)));
  assert.equal(cursor.skills, './skills/');
});

test('the committed release archive excludes the entire assisted suite', () => {
  const archive = execFileSync('git', ['archive', '--format=tar', 'HEAD'], { cwd: root });
  const entries = execFileSync('tar', ['-tf', '-'], { input: archive, encoding: 'utf8' })
    .trim()
    .split('\n');
  assert.equal(entries.some((path) => path.startsWith('solutions/')), false);
  const skills = entries.filter((path) => path.endsWith('/SKILL.md')).sort();
  assert.deepEqual(skills, defaultSkills.map((name) => `skills/${name}/SKILL.md`));
});
