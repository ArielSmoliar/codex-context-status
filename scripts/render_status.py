"""Render an inline inspector from allowlisted telemetry; no network access."""
import json
from pathlib import Path
from zoneinfo import ZoneInfo

DISPLAY_FIELDS = (
    'status', 'reason', 'observed_at', 'model', 'reasoning_effort',
    'usage_timestamp', 'usage_age_seconds', 'usage_record_type',
    'reported_context_window', 'window_timestamp', 'latest_request',
    'current_turn_cumulative', 'thread_cumulative', 'capacity_estimate',
    'capacity_unavailable_reason', 'latest_cache_hit_percent',
    'latest_noncached_input_tokens', 'compactions_observed', 'last_compaction_at',
    'ignored_malformed_lines',
)


def render(data, output, timezone='UTC'):
    ZoneInfo(timezone)
    public = {key: data.get(key) for key in DISPLAY_FIELDS}
    public['display_timezone'] = timezone
    # JSON embedded in a script element must not contain HTML delimiters.
    payload = json.dumps(public, ensure_ascii=True, allow_nan=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    template = (Path(__file__).resolve().parents[1] / 'assets/inspector.html').read_text()
    if template.count('@@CONTEXT_STATUS_DATA@@') != 1:
        raise ValueError('Invalid inspector template: expected one data slot.')
    fragment = template.replace('@@CONTEXT_STATUS_DATA@@', payload)
    if len(fragment.encode()) >= 1_000_000:
        raise ValueError('Inspector exceeds the inline visualization size limit.')
    output = Path(output).expanduser().absolute()
    if output.suffix != '.html':
        raise ValueError('Visualization output must have an .html suffix.')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(fragment)
    return str(output)
