#!/usr/bin/env python3
"""Execute the documented Bash primitives against offline GitHub responses."""

import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [ROOT / 'skills/autofix/SKILL.md', ROOT / 'skills/autofix/github.md']


def block(source, marker):
    return next(code for code in re.findall(r'```bash\n(.*?)\n```', source.read_text(), re.S)
                if marker in code)


def thread(number):
    return {'isResolved': False, 'isOutdated': False, 'comments': {'nodes': [{
        'databaseId': number, 'body': 'A finding', 'path': 'src/example.ts',
        'line': 7, 'startLine': None, 'originalLine': 7,
        'author': {'login': 'coderabbitai[bot]'},
    }]}}


def page(nodes, more=False, cursor=None):
    return {'data': {'repository': {'pullRequest': {'reviewThreads': {
        'nodes': nodes, 'pageInfo': {'hasNextPage': more, 'endCursor': cursor},
    }}}}}


GH_STUB = '''#!/usr/bin/env python3
import json, os, pathlib, subprocess, sys
args = sys.argv[1:]
responses = json.loads(pathlib.Path(os.environ['AUTOFIX_TEST_RESPONSES']).read_text())
state = pathlib.Path(os.environ['AUTOFIX_TEST_STATE'])
index = int(state.read_text()) if state.exists() else 0
state.write_text(str(index + 1))
if index >= len(responses):
    sys.exit(1)
response = responses[index]
if any(arg not in args for arg in response.get('requires', [])):
    print('Missing expected argument', file=sys.stderr)
    sys.exit(2)
if response.get('exit', 0):
    print('fixture API failure', file=sys.stderr)
    sys.exit(response['exit'])
text = response.get('raw', json.dumps(response.get('data')))
if '--jq' in args:
    result = subprocess.run(['jq', '-r', args[args.index('--jq') + 1]], input=text, text=True)
    sys.exit(result.returncode)
print(text)
'''


class WorkflowTests(unittest.TestCase):
    def run_block(self, source, marker, responses, tail='', detached=False):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            subprocess.run(['git', 'init', '-q', '-b', 'topic', directory], check=True)
            if detached:
                subprocess.run(['git', '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.com',
                                'commit', '-q', '--allow-empty', '-m', 'fixture'], cwd=work, check=True)
                subprocess.run(['git', 'checkout', '-q', '--detach'], cwd=work, check=True)
            (work / 'gh').write_text(GH_STUB)
            (work / 'gh').chmod(0o755)
            (work / 'responses.json').write_text(json.dumps(responses))
            env = {**os.environ, 'PATH': f'{work}:{os.environ["PATH"]}',
                   'AUTOFIX_TEST_RESPONSES': str(work / 'responses.json'),
                   'AUTOFIX_TEST_STATE': str(work / 'calls')}
            result = subprocess.run(['bash'], input='owner=fixture\nrepo=repo\npr_number=77\n' +
                                    block(source, marker) + '\n' + tail,
                                    cwd=work, env=env, text=True, capture_output=True, timeout=5)
            return result

    def test_unique_pr(self):
        for source in SOURCES:
            with self.subTest(source=source):
                result = self.run_block(source, 'pr_number=$(', [{'data': [{'number': 77}]}],
                                        'printf "%s" "$pr_number"')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, '77')

    def test_no_pr_is_explicit(self):
        for source in SOURCES:
            result = self.run_block(source, 'pr_number=$(', [{'data': []}], 'printf "%s" "$pr_number"')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, 'none')

    def test_pr_lookup_failures_stop(self):
        for response in [{'exit': 1}, {'raw': 'invalid JSON'}, {'data': None},
                         {'data': [{'number': 1}, {'number': 2}]}, {'data': [{}]},
                         {'data': [{'number': -1}]}, {'data': [{'number': 1.5}]},
                         {'raw': '[{"number":77}]\n[{"number":78}]'}]:
            for source in SOURCES:
                with self.subTest(source=source, response=response):
                    result = self.run_block(source, 'pr_number=$(', [response], 'echo CONTINUED')
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn('CONTINUED', result.stdout)

    def test_detached_head_stops(self):
        for source in SOURCES:
            result = self.run_block(source, 'pr_number=$(', [{'data': [{'number': 77}]}],
                                    'echo CONTINUED', detached=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('CONTINUED', result.stdout)

    def test_multiple_pages_preserve_all_threads(self):
        for source in SOURCES:
            result = self.run_block(source, "all_threads='[]'", [
                {'data': page([thread(1)], True, 'next')}, {'data': page([thread(2)]), 'requires': ['cursor=next']}],
                'printf "%s" "$all_threads"')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), [thread(1), thread(2)])

    def test_empty_complete_fetch(self):
        for source in SOURCES:
            result = self.run_block(source, "all_threads='[]'", [{'data': page([])}],
                                    'printf "%s" "$all_threads"')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), [])

    def test_failed_second_page_does_not_expose_partial_results(self):
        for response in [{'exit': 1}, {'raw': 'not JSON'}, {'data': None}, {'data': {}},
                         {'data': {'errors': [{'message': 'rate limited'}], **page([])}},
                         {'data': page(None)}, {'data': page([{}])},
                         {'data': page([], True, None)}, {'data': page([], 'false')},
                         {'raw': json.dumps(page([])) + '\n' + json.dumps(page([]))}]:
            for source in SOURCES:
                with self.subTest(source=source, response=response):
                    result = self.run_block(source, "all_threads='[]'", [
                        {'data': page([thread(1)], True, 'next')}, response],
                        'printf "CONTINUED:%s" "$all_threads"')
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, '')

    def test_cursor_cycle_stops(self):
        for source in SOURCES:
            result = self.run_block(source, "all_threads='[]'", [
                {'data': page([], True, 'a')}, {'data': page([], True, 'b')},
                {'data': page([], True, 'a')}], 'echo CONTINUED')
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('CONTINUED', result.stdout)

    def test_review_status_success(self):
        for source in SOURCES:
            for entries, count in [([], '0'), ([{'author': {'login': 'coderabbitai[bot]'},
                                               'body': 'Come back again in a few minutes'}], '1')]:
                result = self.run_block(source, '--json comments,reviews', [
                    {'data': {'comments': entries, 'reviews': []}}])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), count)

    def test_review_status_failure_stops(self):
        for source in SOURCES:
            for response in [{'exit': 1}, {'data': {}}, {'raw': 'not JSON'},
                             {'data': {'comments': [], 'reviews': None}}]:
                with self.subTest(source=source, response=response):
                    result = self.run_block(source, '--json comments,reviews', [response], 'echo CONTINUED')
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn('CONTINUED', result.stdout)


if __name__ == '__main__':
    unittest.main()
