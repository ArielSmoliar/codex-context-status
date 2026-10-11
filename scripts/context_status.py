#!/usr/bin/env python3
"""Read allowlisted telemetry for one verified local Codex chat. Stdlib only."""
import argparse
import datetime as dt
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import sys

COUNTERS = ('input_tokens', 'cached_input_tokens', 'cache_write_input_tokens',
            'output_tokens', 'reasoning_output_tokens', 'total_tokens')


class TelemetryError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def diagnostics(data, failure=None):
    """Describe observed evidence, never infer unsupported formats from silence."""
    verified = failure is None
    checks = [{'label': 'Session identity', 'status': 'observed' if verified else 'unavailable',
               'detail': 'Exact chat verified.' if verified else data['reason']}]
    for label, present, detail in [
        ('Model metadata', bool(data.get('model')), 'Recorded model and turn metadata.'),
        ('Usage events', any(value is not None for value in (data.get('latest_request') or {}).values()), 'Recognized request usage record.'),
        ('Context limit', bool(data.get('reported_context_window')), 'Runtime-reported limit for the recorded model.'),
        ('Cache counters', (data.get('latest_request') or {}).get('cached_input_tokens') is not None,
         'Cached input is included in the latest recorded request.'),
    ]:
        checks.append({'label': label,
                       'status': 'not_checked' if not verified else 'observed' if present else 'not_observed',
                       'detail': 'The session could not be verified or read.' if not verified else detail if present
                       else 'Not observed in this snapshot; this does not prove it is unsupported.'})
    return {'checks': checks, 'failure_code': failure,
            'note': 'Checks describe local recorded evidence, not a guarantee of compatibility with future Codex versions.'}


def collect(home, thread, session_file=None):
    try:
        if not thread or not re.fullmatch(r'[a-zA-Z0-9_-]{1,128}', thread):
            raise TelemetryError('invalid_thread', 'A verified current chat ID is required.')
        path = session_file or locate(home.expanduser(), thread)
        return inspect(path.expanduser(), thread)
    except (OSError, ValueError, sqlite3.Error) as error:
        # Never expose filesystem paths or arbitrary exception content to the app.
        code = error.code if isinstance(error, TelemetryError) else 'read_failed'
        reason = str(error) if isinstance(error, TelemetryError) else 'Local telemetry could not be read. Check local filesystem access.'
        result = {'status': 'unavailable', 'reason': reason, 'thread_id': thread,
                  'observed_at': dt.datetime.now(dt.timezone.utc).isoformat()}
        result['diagnostics'] = diagnostics(result, code)
        return result


def number(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0:
        return value
    return None


def counts(value):
    value = value if isinstance(value, dict) else {}
    return {k: number(value.get(k)) for k in COUNTERS}


def usage_counts(value):
    parsed = counts(value)
    return parsed if any(value is not None for value in parsed.values()) else None


def age(value, now):
    try:
        return max(0, round((now - dt.datetime.fromisoformat(value.replace('Z', '+00:00'))).total_seconds(), 1))
    except (TypeError, ValueError, AttributeError):
        return None


def locate(home, thread):
    if not home.is_dir():
        raise TelemetryError('home_unavailable', 'The local Codex data directory is unavailable.')
    def version(path):
        match = re.search(r'state_(\d+)', path.name)
        return int(match.group(1)) if match else 0
    for database in sorted(home.glob('state*.sqlite'), key=version, reverse=True):
        try:
            con = sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True, timeout=1)
            try:
                row = con.execute('SELECT rollout_path FROM threads WHERE id = ?', (thread,)).fetchone()
            finally:
                con.close()
            if row and Path(row[0]).is_file():
                return Path(row[0])
        except (sqlite3.Error, OSError, TypeError):
            continue
    matches = []
    for directory in ('sessions', 'archived_sessions'):
        matches.extend((home / directory).rglob('*' + thread + '.jsonl'))
    if len(matches) == 1:
        return matches[0]
    raise TelemetryError('session_not_found', 'No unique readable session log found for the exact chat ID.')


def inspect(path, thread, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    result = {'status': 'unavailable', 'thread_id': thread, 'observed_at': now.isoformat(),
              'source': 'local_session_log', 'source_path': str(path), 'direct_event_subscription': False}
    identity = latest = None
    cumulative = counts(None)
    turn_usage = current_turn = model = effort = None
    window = window_at = window_model = None
    usage_at = usage_kind = usage_model = None
    compactions = []
    invalidated = False
    quota = quota_at = None
    malformed = 0
    model_epoch = 0
    usage_epoch = None
    switches = []
    switch_count = 0
    with path.open('rb') as handle:
        # Bound this scan to the opening size without seeking twice per record.
        # Appended bytes belong to the next refresh; EOF also handles truncation.
        remaining = os.fstat(handle.fileno()).st_size
        while remaining > 0:
            line = handle.readline(remaining)
            remaining -= len(line)
            if not line.endswith(b'\n'):
                break
            try:
                record = json.loads(line)
            except (ValueError, UnicodeDecodeError):
                malformed += 1
                continue
            if not isinstance(record, dict) or not isinstance(record.get('payload'), dict):
                continue
            payload = record['payload']
            kind, at = record.get('type'), record.get('timestamp')
            if kind == 'session_meta':
                identity = payload.get('id')
                if identity != thread:
                    raise TelemetryError('identity_mismatch', 'Session identity does not match the requested chat.')
            elif kind == 'turn_context':
                new_model = payload.get('model')
                new_model = new_model if isinstance(new_model, str) and new_model else None
                if model is not None and new_model is not None and model != new_model:
                    switch_count += 1
                    switches.append({'from_model': model, 'to_model': new_model, 'timestamp': at})
                    switches = switches[-10:]
                    model_epoch += 1
                    window = window_at = window_model = None
                    invalidated = True
                model = new_model if isinstance(new_model, str) else model
                effort = payload.get('effort') if isinstance(payload.get('effort'), str) else None
                if payload.get('turn_id') != current_turn:
                    turn_usage = None
                current_turn = payload.get('turn_id')
            elif kind == 'compacted' or (kind == 'event_msg' and payload.get('type') == 'context_compaction'):
                compactions.append(at)
                invalidated = True
            elif kind == 'token_usage_record' and payload.get('thread_id') == thread:
                candidate = usage_counts(payload.get('usage'))
                if candidate is not None and payload.get('turn_id') == current_turn:
                    latest = candidate
                    usage_at, usage_kind, usage_model = at, kind, model
                    usage_epoch = model_epoch
                    invalidated = False
                if isinstance(payload.get('thread_token_usage'), dict):
                    cumulative = counts(payload['thread_token_usage'])
                if payload.get('turn_id') == current_turn and isinstance(payload.get('turn_token_usage'), dict):
                    turn_usage = counts(payload['turn_token_usage'])
            elif kind == 'event_msg' and payload.get('type') == 'token_count':
                info = payload.get('info')
                if isinstance(info, dict):
                    candidate = usage_counts(info.get('last_token_usage'))
                    if candidate is not None:
                        latest = candidate
                        usage_at, usage_kind, usage_model = at, 'event_msg/token_count', model
                        usage_epoch = model_epoch
                        invalidated = False
                    if isinstance(info.get('total_token_usage'), dict):
                        cumulative = counts(info['total_token_usage'])
                    if 'model_context_window' in info:
                        window = number(info['model_context_window'])
                        window_at, window_model = at, model
                raw_quota = payload.get('rate_limits')
                if isinstance(raw_quota, dict):
                    quota = {}
                    for key in ('primary', 'secondary'):
                        value = raw_quota.get(key)
                        if isinstance(value, dict):
                            quota[key] = {k: number(value.get(k)) for k in ('used_percent', 'window_minutes', 'resets_at')}
                    quota_at = at
    if identity != thread:
        raise TelemetryError('identity_unverified', 'No matching session identity found; refusing unverified telemetry.')
    result.update(model=model, reasoning_effort=effort, latest_usage_model=usage_model,
                  model_switches=switches, model_switch_count=switch_count,
                  reported_context_window=window, ignored_malformed_lines=malformed)
    if latest is None:
        result['reason'] = 'The verified log contains no supported usage measurements.'
        result['usage_state'] = 'not_observed'
        result['diagnostics'] = diagnostics(result)
        return result
    footprint = latest['total_tokens']
    if footprint is None and latest['input_tokens'] is not None and latest['output_tokens'] is not None:
        footprint = latest['input_tokens'] + latest['output_tokens']
    estimate = None
    if not invalidated and window and footprint is not None:
        estimate = {'basis': 'last_recorded_input_plus_output', 'used_tokens': footprint,
                    'remaining_tokens': max(0, window - footprint),
                    'used_percent': round(100 * footprint / window, 2),
                    'exceeds_reported_window': footprint > window}
    cache_ratio = noncached = None
    inp, cached = latest['input_tokens'], latest['cached_input_tokens']
    if inp is not None and cached is not None and cached <= inp:
        noncached = inp - cached
        if inp:
            cache_ratio = round(100 * cached / inp, 2)
    result.update(status='ok', model=model, reasoning_effort=effort,
                  latest_usage_model=usage_model, usage_timestamp=usage_at,
                  usage_state=('awaiting_model_usage' if usage_epoch != model_epoch else
                               'awaiting_post_compaction_usage' if invalidated else 'recorded'),
                  usage_age_seconds=age(usage_at, now), usage_record_type=usage_kind,
                  reported_context_window=window, window_timestamp=window_at, window_model=window_model,
                  latest_request=latest, current_turn_cumulative=turn_usage, thread_cumulative=cumulative,
                  capacity_estimate=estimate,
                  capacity_unavailable_reason=('Compaction or a model change occurred after the last usage measurement.'
                      if invalidated else 'Missing context limit or latest token count.' if estimate is None else None),
                  latest_cache_hit_percent=cache_ratio, latest_noncached_input_tokens=noncached,
                  compactions_observed=len(compactions), last_compaction_at=compactions[-1] if compactions else None,
                  recorded_account_rate_limits=quota, rate_limits_timestamp=quota_at,
                  ignored_malformed_lines=malformed,
                  unavailable=['exact_live_context_occupancy', 'per_source_token_breakdown',
                               'cache_miss_diagnostics', 'automatic_compaction_threshold', 'compaction_content_diff'])
    result['diagnostics'] = diagnostics(result)
    return result


def markdown(data):
    if data['status'] != 'ok':
        return 'Context status unavailable: ' + data.get('reason', 'No measurements.')
    def fmt(value):
        return 'Unavailable' if value is None else f'{value:,}' if isinstance(value, (int, float)) else str(value).replace('|', '\\|').replace('\n', ' ')
    rows = [('Model', data['model']), ('Latest usage model', data.get('latest_usage_model')),
            ('Usage state', data.get('usage_state')), ('Reasoning effort', data['reasoning_effort']),
            ('Reported context limit', data['reported_context_window'])]
    estimate = data['capacity_estimate']
    if estimate:
        rows.extend([('Estimated context used', f"{estimate['used_tokens']:,} ({estimate['used_percent']}%)"),
                     ('Estimated remaining capacity', estimate['remaining_tokens'])])
    else:
        rows.append(('Capacity estimate', data['capacity_unavailable_reason']))
    labels = {'input_tokens': 'Input', 'cached_input_tokens': 'Cached input',
              'cache_write_input_tokens': 'Cache-write input', 'output_tokens': 'Output',
              'reasoning_output_tokens': 'Reasoning output', 'total_tokens': 'Total'}
    rows.extend(('Latest request: ' + label, data['latest_request'][key]) for key, label in labels.items())
    rows.extend([('Latest noncached input', data['latest_noncached_input_tokens']),
                 ('Latest input cache reuse', None if data['latest_cache_hit_percent'] is None else str(data['latest_cache_hit_percent']) + '%'),
                 ('Current turn cumulative tokens', (data['current_turn_cumulative'] or {}).get('total_tokens')),
                 ('Thread cumulative tokens', data['thread_cumulative']['total_tokens']),
                 ('Compactions observed in available log', data['compactions_observed']),
                 ('Last compaction', data['last_compaction_at'] if data['compactions_observed'] else 'None observed')])
    return (f"Recorded usage: {data['usage_timestamp']} (age: {fmt(data['usage_age_seconds'])} seconds).\n\n"
            'Source: read-only local session log; not a direct live subscription.\n\n'
            '| Measurement | Value |\n|---|---|\n' +
            '\n'.join(f'| {name} | {fmt(value)} |' for name, value in rows) +
            '\n\nCapacity is an estimate from the last recorded request and excludes unreported work. '
            'Cumulative tokens are consumption, not context occupancy. Cached input and reasoning output are subsets, not additional tokens.\n\n'
            'Unavailable: exact live occupancy, per-source breakdown, cache-miss causes, automatic compaction threshold, and compaction content changes.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--thread-id')
    parser.add_argument('--codex-home', type=Path)
    parser.add_argument('--session-file', type=Path)
    parser.add_argument('--format', choices=('json', 'markdown'), default='json')
    parser.add_argument('--visualization', type=Path, help='Write the default inline inspector to this authorized .html path.')
    parser.add_argument('--timezone', default='UTC', help='Client IANA timezone for the visualization; defaults to UTC.')
    args = parser.parse_args()
    thread = args.thread_id or os.environ.get('CODEX_THREAD_ID') or os.environ.get('CODEX_SESSION_ID')
    home = args.codex_home or Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    result = collect(home, thread, args.session_file)
    if args.visualization:
        from render_status import render
        try:
            result['visualization_path'] = render(result, args.visualization, args.timezone)
        except (ValueError, OSError, KeyError) as exc:
            print(json.dumps({'status': 'visualization_error', 'reason': str(exc)}))
            return 2
    print(markdown(result) if args.format == 'markdown' else json.dumps(result, indent=2, allow_nan=False))
    return 0 if result['status'] == 'ok' else 2


if __name__ == '__main__':
    sys.exit(main())
