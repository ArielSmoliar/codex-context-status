#!/usr/bin/env python3
"""Benchmark full refresh reads using disposable synthetic logs, never Codex data."""
import argparse
import datetime as dt
import importlib.util
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

THREAD = 'synthetic-benchmark'
NOW = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
READER = Path(__file__).with_name('context_status.py')


def record(kind, payload):
    return (json.dumps({'type': kind, 'timestamp': NOW.isoformat(), 'payload': payload}) + '\n').encode()


def make_log(path, mib, payload_bytes):
    """Mix irrelevant conversation-shaped records with supported telemetry."""
    filler = record('response_item', {'text': 'x' * payload_bytes})
    telemetry = record('event_msg', {'type': 'token_count', 'info': {
        'last_token_usage': {'input_tokens': 100, 'cached_input_tokens': 80,
                            'output_tokens': 20, 'total_tokens': 120},
        'model_context_window': 1000}})
    lines = 0
    with path.open('wb') as handle:
        handle.write(record('session_meta', {'id': THREAD}))
        handle.write(record('turn_context', {'model': 'synthetic-model', 'turn_id': 'turn-1'}))
        lines += 2
        while handle.tell() < mib * 1024 * 1024:
            handle.write(filler)
            lines += 1
            if lines % 1000 == 0:
                handle.write(telemetry)
                lines += 1
        handle.write(telemetry)
        lines += 1
    return lines


def load_reader(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def comparable(result):
    return {key: value for key, value in result.items()
            if key not in ('observed_at', 'usage_age_seconds')}


def positive(value):
    value = int(value)
    if value <= 0:
        raise argparse.ArgumentTypeError('must be positive')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sizes-mib', nargs='+', type=positive, default=[10, 100])
    parser.add_argument('--repeats', type=positive, default=5)
    parser.add_argument('--baseline-reader', type=Path,
                        help='Optional earlier context_status.py for paired comparisons.')
    args = parser.parse_args()
    readers = {'current': (READER, load_reader(READER, 'current_reader'))}
    if args.baseline_reader:
        readers['baseline'] = (args.baseline_reader.resolve(), load_reader(args.baseline_reader, 'baseline_reader'))
    results = []
    with tempfile.TemporaryDirectory(prefix='context-status-benchmark-') as tmp:
        path = Path(tmp) / 'synthetic.jsonl'
        for mib in args.sizes_mib:
            for payload_bytes in (256, 65536):
                lines = make_log(path, mib, payload_bytes)
                expected = comparable(readers['current'][1].inspect(path, THREAD, NOW))
                timings = {name: {'reader_ms': [], 'cli_ms': []} for name in readers}
                # Warm the filesystem and imports before timing. This is not cold-disk latency.
                for _, module in readers.values():
                    assert comparable(module.inspect(path, THREAD, NOW)) == expected
                for iteration in range(args.repeats):
                    order = list(readers.items())
                    if iteration % 2:
                        order.reverse()
                    for name, (reader_path, module) in order:
                        start = time.perf_counter()
                        result = module.inspect(path, THREAD, NOW)
                        timings[name]['reader_ms'].append((time.perf_counter() - start) * 1000)
                        assert comparable(result) == expected
                        start = time.perf_counter()
                        proc = subprocess.run([sys.executable, str(reader_path), '--thread-id', THREAD,
                                               '--session-file', str(path)], check=True, capture_output=True, text=True)
                        timings[name]['cli_ms'].append((time.perf_counter() - start) * 1000)
                        assert comparable(json.loads(proc.stdout)) == expected
                results.append({'target_mib': mib, 'actual_bytes': path.stat().st_size,
                                'payload_bytes': payload_bytes, 'records': lines,
                                'median_ms': {name: {key: round(statistics.median(values), 2)
                                                     for key, values in metrics.items()}
                                              for name, metrics in timings.items()}})
    print(json.dumps({'python': platform.python_version(), 'os': platform.system(),
                      'architecture': platform.machine(), 'repeats': args.repeats,
                      'scope': 'Warm filesystem; reader and one-shot CLI only. Excludes MCP transport, UI and session lookup.',
                      'results': results}, indent=2))


if __name__ == '__main__':
    main()
