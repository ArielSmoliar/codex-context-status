# Refresh performance

The reader scans a fixed-size snapshot on every refresh. It now tracks the bytes
remaining instead of asking the file for its position twice per line. Parsing,
identity checks, and telemetry selection are unchanged. There is no persistent
cache or retained conversation content.

## Reproduce

```sh
npm run benchmark
```

The benchmark creates temporary synthetic 10 MiB and 100 MiB logs, with either
256-byte or 64 KiB message payloads and interleaved telemetry. It measures five
repetitions of the reader and one-shot CLI, reporting medians as JSON. It checks
that results match, excluding the wall-clock observation time and record age.
Temporary logs are deleted when the run finishes. No personal Codex data is used.

For a paired comparison with the implementation before this optimization:

```sh
benchmark_dir="$(mktemp -d)"
git show 0833f14:scripts/context_status.py > "$benchmark_dir/context_status.py"
npm run benchmark -- --baseline-reader "$benchmark_dir/context_status.py"
```

The baseline file is Python code and is executed; use only a trusted revision.
Both implementations read identical fixtures, and their complete results are
compared apart from observation time and age. Execution order alternates between
repetitions. `--sizes-mib 1 --repeats 1` provides a quick functional smoke check;
CI uses this without a timing threshold.

## Recorded comparison

Measured October 11, 2026, on macOS arm64 with Python 3.14.5; five repetitions,
warm filesystem. Approximate log sizes are shown because the generator finishes
the last record before appending final telemetry.

| Log size | Message payload | Reader before → after | CLI before → after |
| --- | --- | --- | --- |
| 10 MiB | 256 bytes | 48.68 → 34.75 ms | 84.67 → 70.82 ms |
| 10 MiB | 64 KiB | 8.23 → 8.01 ms | 40.81 → 40.31 ms |
| 100 MiB | 256 bytes | 535.02 → 355.37 ms | 568.82 → 398.93 ms |
| 100 MiB | 64 KiB | 88.13 → 87.73 ms | 121.25 → 119.77 ms |

The improvement is concentrated in logs with many short records: the 100 MiB
reader case took about 34% less time. Large-record cases were roughly unchanged.
These are local synthetic measurements, not a UI latency guarantee. They exclude
session lookup, MCP transport, browser rendering, cold-disk effects, and concurrent
session writes. Startup overhead is included only in the CLI measurements.

## Boundaries and next steps

Regression tests cover appending after the opening size was captured, completing
a partial trailing record, truncating before the read, and replacing the file
while the old handle is open. Appends wait for the next refresh; the next read
reopens the path and verifies identity again. This is a size-bounded read, not an
atomic filesystem snapshot: concurrent in-place rewriting can still affect it.

Full scans remain linear in log size. These measurements do not justify adding
incremental state yet. Revisit if larger or slower real environments show refresh
delays; any future cache must handle truncation, rotation, same-size rewrites,
identity changes, compaction, and incomplete trailing records without retaining
message contents or silently presenting stale telemetry.
