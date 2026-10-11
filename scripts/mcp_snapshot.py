#!/usr/bin/env python3
"""Return only display telemetry plus exact view binding for the local MCP app."""
import argparse
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo
from context_status import locate, inspect
from render_status import DISPLAY_FIELDS

parser = argparse.ArgumentParser()
parser.add_argument('--thread-id', required=True)
parser.add_argument('--timezone', default='UTC')
args = parser.parse_args()
ZoneInfo(args.timezone)
try:
    home = Path(os.environ.get('CODEX_HOME', '~/.codex')).expanduser()
    data = inspect(locate(home, args.thread_id), args.thread_id)
except (OSError, ValueError) as error:
    data = {'status': 'unavailable', 'reason': str(error)}
public = {key: data.get(key) for key in DISPLAY_FIELDS}
public.update(thread_id=args.thread_id, display_timezone=args.timezone)
print(json.dumps(public, allow_nan=False))
