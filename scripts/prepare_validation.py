"""Prepare offline synthetic trials. Never reads chats or starts model calls."""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys

from render_status import render

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'tests/fixtures/handoff-evaluation.json'


def prompts(template):
    """Static template literals only; fail rather than silently evaluate JS."""
    block = re.search(r'const handoffPrompts = \{(.*?)\n    \};', template, re.S)
    if not block:
        raise ValueError('Canonical handoff prompt block not found')
    pairs = re.findall(r'(prepare|resume): `([^`]*)`', block.group(1))
    if [name for name, _ in pairs] != ['prepare', 'resume']:
        raise ValueError('Canonical prompt format changed')
    result = dict(pairs)
    if any('\\' in text or '${' in text for text in result.values()):
        raise ValueError('Canonical prompts must remain plain static text')
    if result['resume'].count('[Paste the reviewed handoff here]') != 1:
        raise ValueError('Canonical resume placeholder changed')
    return result


def safe_files(files):
    for name, content in files.items():
        path = PurePosixPath(name)
        if (not name or path.is_absolute() or '..' in path.parts or
                '.git' in path.parts or '\\' in name or ':' in name or
                str(path) != name or not isinstance(content, str)):
            raise ValueError(f'Unsafe fixture path or content: {name!r}')


def write_files(directory, files):
    for name, content in files.items():
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')


def git(directory, *args):
    # Local fixtures must not inherit a contributor's Git target, hooks or signing.
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
               GIT_CONFIG_SYSTEM=os.devnull, GIT_TERMINAL_PROMPT='0')
    return subprocess.run(
        ['git', '-c', 'core.hooksPath=' + os.devnull,
         '-c', 'commit.gpgSign=false', '-c', 'user.name=Synthetic Evaluator',
         '-c', 'user.email=synthetic@example.invalid', *args],
        cwd=directory, env=env, check=True, capture_output=True, text=True).stdout.strip()


def make_workspace(directory, files, use_git=False, dirty=None):
    directory.mkdir(parents=True)
    write_files(directory, files)
    if use_git:
        git(directory, 'init', '-b', 'trial-main')
        git(directory, 'add', '.')
        git(directory, 'commit', '-m', 'Synthetic baseline')
    write_files(directory, dirty or {})


def generate(output):
    data = json.loads(CATALOG.read_text())
    canonical = prompts((ROOT / 'assets/inspector.html').read_text())
    cases = data['cases']
    if [case['id'] for case in cases] != ['01', '02', '03', '04', '05', '06']:
        raise ValueError('Expected six opaque fixture IDs, 01 through 06')
    for case in cases:
        for key in ('files', 'source_files', 'dirty'):
            safe_files(case.get(key, {}))
        if not set(case.get('dirty', {})) <= set(case['files']):
            raise ValueError('Dirty edits must modify existing baseline files')
    output = Path(output).expanduser().absolute()
    # mkdir is the ownership boundary: never remove or reuse an existing target.
    output.mkdir(parents=False, exist_ok=False)
    try:
        for case in cases:
            facilitator = output / 'facilitator' / case['id']
            facilitator.mkdir(parents=True)
            make_workspace(output / 'receivers' / case['id'], case['files'],
                           case.get('git', False), case.get('dirty'))
            if case['handoff'] is not None:
                make_workspace(facilitator / 'source-workspace',
                               case.get('source_files', case['files']),
                               case.get('git', False), case.get('dirty'))
            (facilitator / 'source-history.txt').write_text(case['history'] + '\n')
            (facilitator / 'prepare-prompt.txt').write_text(canonical['prepare'] + '\n')
            example = canonical['resume']
            if case['handoff'] is not None:
                example = example.replace('[Paste the reviewed handoff here]', case['handoff'])
            if case['request']:
                example += '\n\nCurrent request:\n' + case['request']
            (facilitator / 'resume-example.txt').write_text(example + '\n')
            rubric = {k: case[k] for k in ('id', 'title', 'phase', 'criteria')}
            rubric.update(status='NOT RUN', note='Canned example is resume-only. For a full trial, transfer the actual reviewed preparation output.', current_request=case['request'])
            (facilitator / 'rubric.json').write_text(json.dumps(rubric, indent=2) + '\n')
        (output / 'resume-template.txt').write_text(canonical['resume'] + '\n')
        shutil.copyfile(ROOT / 'references/validation-results.md', output / 'results.md')
        shutil.copyfile(ROOT / 'references/validation.md', output / 'protocol.md')
        sources = ['scripts/prepare_validation.py', 'scripts/render_status.py',
                   'tests/fixtures/handoff-evaluation.json', 'assets/inspector.html',
                   'mcp/theme.css', 'references/validation.md', 'references/validation-results.md']
        metadata = {'kind': 'synthetic-validation-kit', 'model_trials': 'NOT RUN',
                    'sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sources}}
        try:
            metadata.update(commit=git(ROOT, 'rev-parse', 'HEAD'),
                            checkout_dirty=bool(git(ROOT, 'status', '--porcelain')))
        except (OSError, subprocess.CalledProcessError):
            metadata.update(commit=None, checkout_dirty=None)
        (output / 'SOURCE.json').write_text(json.dumps(metadata, indent=2) + '\n')
        fragment = output / 'demo-fragment.html'
        render(data['demo'], fragment)
        inner = ('<!doctype html><html><head><meta charset="utf-8">'
                 '<meta name="viewport" content="width=device-width,initial-scale=1">'
                 '<style>' + (ROOT / 'mcp/theme.css').read_text() + '</style></head><body>' +
                 fragment.read_text() + '</body></html>')
        fragment.unlink()
        # Sandboxed srcdoc has no host bridge, same-origin access or network.
        demo = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; frame-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'">
<title>Context status — synthetic walkthrough</title>
<style>body{font:16px/1.5 system-ui;max-width:1000px;margin:auto;padding:20px}iframe{width:100%;height:1900px;border:1px solid #999}li{margin:8px 0}</style>
<h1>Synthetic walkthrough</h1>
<p>Example data only. This is an offline snapshot, not a live Codex chat. Refresh and auto-refresh are not demonstrated. No model or host messages are sent.</p>
<ol><li>Read the recorded timestamp and estimated capacity. This is not a model-quality score.</li>
<li>Try the Next step choices and expand Handoff checklist &amp; prompts.</li>
<li>Review the current-chat preparation prompt, then switch to the new-chat resume prompt. Copy manually if the browser blocks clipboard access.</li>
<li>For an actual trial, follow protocol.md and record results. This demo has not tested whether a model follows either prompt.</li></ol>
<iframe title="Synthetic context inspector" sandbox="allow-scripts" srcdoc="''' + html.escape(inner, quote=True) + '"></iframe></html>'
        (output / 'demo.html').write_text(demo)
        return output
    except BaseException:
        shutil.rmtree(output)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, help='New directory under an existing parent; preferably outside any checkout')
    args = parser.parse_args()
    try:
        result = generate(args.output)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f'Kit not created: {exc}', file=sys.stderr)
        return 1
    print(f'Synthetic kit: {result}\nOpen protocol.md and demo.html. Model trials: NOT RUN.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
