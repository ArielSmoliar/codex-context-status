#!/usr/bin/env python3
"""Preview or apply a local context-status install; never edit Codex configuration."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import stat
import sys
import tempfile
import uuid

MANIFEST = '.context-status-install.json'
PACKAGE_FILES = ('SKILL.md', 'README.md', 'ROADMAP.md', 'agents/openai.yaml',
                 'assets/inspector.html', 'scripts/context_status.py', 'scripts/mcp_snapshot.py',
                 'scripts/render_status.py', 'scripts/install.py', 'references/telemetry.md',
                 'references/installation.md', 'references/performance.md', 'references/compatibility.md', 'references/handoffs.md',
                 'mcp/server.mjs', 'mcp/inspector.html',
                 'mcp/package.json', 'mcp/package-lock.json', 'mcp/build_widget.py',
                 'mcp/bridge.js', 'mcp/theme.css', 'mcp/README.md')


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def safe_path(root, name):
    parts = PurePosixPath(name).parts
    if not parts or PurePosixPath(name).is_absolute() or '..' in parts or '\\' in name or str(PurePosixPath(name)) != name:
        raise ValueError('Invalid manifest path.')
    path = root
    for index, part in enumerate(parts):
        path = path / part
        if path.is_symlink():
            raise ValueError(f'Managed path is a symlink: {name}')
        if index < len(parts) - 1 and path.exists() and not path.is_dir():
            raise ValueError(f'Managed path has a non-directory parent: {name}')
    return path


def package_files(source):
    return {name: digest(safe_path(source, name)) for name in PACKAGE_FILES}


def manifest_files(target):
    path = safe_path(target, MANIFEST)
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or data.get('schema') != 1 or not isinstance(data.get('files'), dict) or not data['files']:
        raise ValueError('Unrecognized installation manifest; existing files were left intact.')
    for name, value in data['files'].items():
        safe_path(target, name)
        if name == MANIFEST or not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
            raise ValueError('Invalid installation manifest.')
    return data['files']


def plan(source, home, adopt=False):
    source, home = source.resolve(), home.resolve()
    target = home / 'skills' / 'context-status'
    incoming = package_files(source)
    result = {'target': str(target), 'state': 'new', 'changes': [], 'conflicts': [],
              'files': incoming, 'previous': {}}
    if target.is_symlink():
        result.update(state='linked', conflicts=['Existing skill is a symlink; update its checkout directly.'])
        return result
    if target.parent.is_symlink() or (target.exists() and not target.is_dir()):
        raise ValueError('Installation destination must be a regular directory, not a symlink or file.')
    if target == source or target in source.parents or source in target.parents:
        raise ValueError('Source and installation directories must not overlap.')
    previous = manifest_files(target) if target.exists() else None
    if target.exists() and previous is None and not adopt:
        result.update(state='unmanaged', conflicts=['Existing copy has no manifest. Preview with --adopt to compare it.'])
        return result
    if target.exists():
        result['state'] = 'adopt' if previous is None else 'upgrade'
    previous = previous or {}
    result['previous'] = previous
    for name in sorted(incoming.keys() | previous.keys()):
        path = safe_path(target, name)
        if path.exists() and not path.is_file():
            result['conflicts'].append(name)
            continue
        actual = digest(path) if path.exists() else None
        expected, desired = previous.get(name), incoming.get(name)
        # A matching new version is safe. Otherwise replace only an unchanged
        # managed file; untracked collisions and local deletions are conflicts.
        if actual != desired and actual != expected:
            result['conflicts'].append(name)
        elif actual != desired:
            result['changes'].append({'path': name, 'action': 'remove' if desired is None else 'add' if actual is None else 'update'})
    if result['state'] == 'upgrade' and previous == incoming and not result['changes'] and not result['conflicts']:
        result['state'] = 'current'
    return result


def tree_stamp(root):
    """Check copied user files too; never follow symlinks outside the tree."""
    if not root.exists():
        return None
    result = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(directory) / name
            info = path.lstat()
            relative = path.relative_to(root).as_posix()
            if stat.S_ISLNK(info.st_mode):
                value = ('link', os.readlink(path))
            elif stat.S_ISREG(info.st_mode):
                value = ('file', stat.S_IMODE(info.st_mode), digest(path))
            elif stat.S_ISDIR(info.st_mode):
                value = ('directory', stat.S_IMODE(info.st_mode))
            else:
                raise ValueError('Installation contains a special file; resolve it before upgrading.')
            result[relative] = value
    return result


def apply(source, home, adopt=False):
    source, home = source.resolve(), home.resolve()
    initial = plan(source, home, adopt)
    if initial['conflicts']:
        raise ValueError('Installation has conflicts; no files were changed.')
    if initial['state'] == 'current':
        return initial, None
    home.mkdir(parents=True, exist_ok=True)
    lock = home / '.context-status-install.lock'
    try:
        lock.mkdir()
    except FileExistsError:
        raise ValueError('Another installation may be running. Inspect the install lock before retrying.')
    staging = None
    backup = None
    target = Path(initial['target'])
    try:
        current = plan(source, home, adopt)
        if current != initial:
            raise ValueError('Installation changed during planning; rerun the preview.')
        before = tree_stamp(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix='.context-status-stage-', dir=home))
        if target.exists():
            shutil.copytree(target, staging, dirs_exist_ok=True, symlinks=True)
            if tree_stamp(staging) != before:
                raise ValueError('Installation changed while copying; rerun the preview.')
        for change in current['changes']:
            name = change['path']
            destination = safe_path(staging, name)
            if change['action'] == 'remove':
                destination.unlink()
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(safe_path(source, name), destination)
        # Verify all staged package files, including files retained on adoption.
        for name, expected in current['files'].items():
            if digest(safe_path(staging, name)) != expected:
                raise ValueError('Source changed during staging; rerun the preview.')
        safe_path(staging, MANIFEST).write_text(json.dumps({'schema': 1, 'files': current['files']}, indent=2) + '\n')
        if plan(source, home, adopt) != current or tree_stamp(target) != before:
            raise ValueError('Source or installation changed before apply; rerun the preview.')
        if target.exists():
            backups = home / 'context-status-backups'
            if backups.is_symlink():
                raise ValueError('Backup directory must not be a symlink.')
            backups.mkdir(exist_ok=True)
            backup = backups / uuid.uuid4().hex
            target.rename(backup)
        try:
            staging.rename(target)
            staging = None
        except OSError:
            if backup is not None:
                backup.rename(target)
                backup = None
            raise
        return current, backup
    finally:
        if staging is not None:
            shutil.rmtree(staging)
        lock.rmdir()


def commands(target, home):
    node = shutil.which('node')
    python = str(Path(sys.executable).resolve())
    output = ['npm ci --prefix ' + shlex.quote(str(target / 'mcp')) + ' --ignore-scripts',
              'CODEX_HOME=' + shlex.quote(str(home)) + ' codex mcp get context-status --json']
    if node:
        args = ['codex', 'mcp', 'add', 'context-status', '--env', 'CONTEXT_STATUS_PYTHON=' + python,
                '--env', 'CODEX_HOME=' + str(home), '--', str(Path(node).resolve()), str(target / 'mcp/server.mjs')]
        output.append('CODEX_HOME=' + shlex.quote(str(home)) + ' ' + shlex.join(args))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME', '~/.codex')))
    parser.add_argument('--apply', action='store_true', help='Apply a conflict-free plan; default is read-only preview.')
    parser.add_argument('--adopt', action='store_true', help='Accept an existing copy only if packaged files match or are absent.')
    args = parser.parse_args()
    source, home = args.source.expanduser().resolve(), args.codex_home.expanduser().resolve()
    try:
        result = plan(source, home, args.adopt)
        print(f"{'Apply' if args.apply else 'Preview'}: {result['state']} at {result['target']}")
        for change in result['changes']:
            print(f"  {change['action']}: {change['path']}")
        for conflict in result['conflicts']:
            print(f'  Conflict: {conflict}')
        if result['conflicts']:
            return 2
        if args.apply:
            result, backup = apply(source, home, args.adopt)
            print('Files ready.' if result['state'] != 'current' else 'Already current; no files changed.')
            if backup:
                print(f'Previous installation retained at: {backup}')
        else:
            print('No files changed. Add --apply to install this plan.')
        print('\nSetup commands (not executed):')
        for command in commands(Path(result['target']), home):
            print(command)
        if not shutil.which('node'):
            print('Node was not found on PATH; install Node 20+ before registering the MCP server.')
        print('Inspect an existing MCP registration before replacing it; preserve custom settings.')
        print('Requires Node 20+, Python 3.10+ and IANA timezone data. Runtime readiness is not verified by this file installer.')
        print('After registration or server changes, restart Codex if tools remain unavailable or old. Reopen the inspector for UI updates; Refresh updates data only.')
        return 0
    except (OSError, ValueError) as error:
        print(f'Installation stopped: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
