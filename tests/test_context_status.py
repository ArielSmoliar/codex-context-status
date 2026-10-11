import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('context_status', Path(__file__).resolve().parents[1] / 'scripts/context_status.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def event(kind, payload):
    return {'type': kind, 'timestamp': '2026-10-10T13:00:00Z', 'payload': payload}


def context(model='example', turn='turn1'):
    return event('turn_context', {'model': model, 'effort': 'high', 'turn_id': turn})


def usage(last=None, window=1000):
    return event('event_msg', {'type': 'token_count', 'info': {
        'last_token_usage': last if last is not None else {'input_tokens': 100, 'cached_input_tokens': 80, 'output_tokens': 20, 'reasoning_output_tokens': 5, 'total_tokens': 120},
        'total_token_usage': {'total_tokens': 50000}, 'model_context_window': window}})


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'session.jsonl'

    def read(self, records, tail=b''):
        self.path.write_bytes(b''.join((json.dumps(x)+'\n').encode() for x in [event('session_meta', {'id': 'test-chat'})] + records) + tail)
        return mod.inspect(self.path, 'test-chat')

    def test_capacity_uses_latest_not_cumulative_and_no_double_count(self):
        r = self.read([context(), usage()])
        self.assertEqual(r['capacity_estimate']['used_tokens'], 120)
        self.assertEqual(r['capacity_estimate']['remaining_tokens'], 880)
        self.assertEqual(r['latest_cache_hit_percent'], 80)
        self.assertEqual(r['latest_noncached_input_tokens'], 20)

    def test_missing_is_not_zero(self):
        r = self.read([context(), usage({'input_tokens': 0}, None)])
        self.assertEqual(r['latest_request']['input_tokens'], 0)
        self.assertIsNone(r['latest_request']['cached_input_tokens'])
        self.assertIsNone(r['latest_cache_hit_percent'])
        self.assertIsNone(r['capacity_estimate'])

    def test_partial_and_malformed_lines_do_not_leak(self):
        r = self.read([context(), usage(), event('response_item', {'secret': 'NEVER_EMIT_THIS'})], b'broken\n{"unfinished":')
        self.assertEqual(r['ignored_malformed_lines'], 1)
        self.assertNotIn('NEVER_EMIT_THIS', json.dumps(r))
        self.assertIsNotNone(r['capacity_estimate'])

    def test_mismatched_identity_rejected(self):
        with self.assertRaises(ValueError):
            self.read([event('session_meta', {'id': 'other-chat'}), usage()])

    def test_no_usage_unavailable(self):
        self.assertEqual(self.read([context()])['status'], 'unavailable')

    def test_compaction_invalidates_then_new_usage_restores(self):
        compact = event('compacted', {'message': 'SECRET SUMMARY'})
        r = self.read([context(), usage(), compact])
        self.assertIsNone(r['capacity_estimate'])
        self.assertEqual(r['compactions_observed'], 1)
        self.assertNotIn('SECRET SUMMARY', json.dumps(r))
        self.assertIsNotNone(self.read([context(), usage(), compact, usage()])['capacity_estimate'])

    def test_model_change_clears_window(self):
        r = self.read([context(), usage(), context('different')])
        self.assertIsNone(r['reported_context_window'])
        self.assertIsNone(r['capacity_estimate'])
        self.assertEqual(r['latest_usage_model'], 'example')
        self.assertEqual(r['usage_state'], 'awaiting_model_usage')
        self.assertEqual(r['model_switch_count'], 1)
        self.assertEqual(r['model_switches'][0]['to_model'], 'different')

    def test_switch_back_does_not_reuse_old_model_measurement(self):
        r = self.read([context(), usage(), context('different'), context()])
        self.assertEqual(r['usage_state'], 'awaiting_model_usage')
        self.assertEqual(r['model_switch_count'], 2)
        self.assertIsNone(r['capacity_estimate'])

    def test_empty_usage_does_not_clear_model_waiting_state(self):
        r = self.read([context(), usage(), context('different'), usage({}, 2000)])
        self.assertEqual(r['usage_state'], 'awaiting_model_usage')
        self.assertEqual(r['latest_usage_model'], 'example')
        self.assertIsNone(r['capacity_estimate'])
        r = self.read([context(), usage({'unrecognized_field': 3}, 2000)])
        self.assertEqual(r['status'], 'unavailable')

    def test_late_previous_turn_usage_cannot_be_attributed_to_new_model(self):
        late = event('token_usage_record', {'thread_id': 'test-chat', 'turn_id': 'turn1',
                     'usage': {'input_tokens': 999, 'total_tokens': 999}})
        r = self.read([context(), usage(), context('new-model', 'turn2'), late])
        self.assertEqual(r['latest_usage_model'], 'example')
        self.assertEqual(r['latest_request']['total_tokens'], 120)
        self.assertEqual(r['usage_state'], 'awaiting_model_usage')
        fresh = event('token_usage_record', {'thread_id': 'test-chat', 'turn_id': 'turn2',
                      'usage': {'input_tokens': 300, 'output_tokens': 20, 'total_tokens': 320}})
        r = self.read([context(), usage(), context('new-model', 'turn2'), late, fresh])
        self.assertEqual(r['latest_usage_model'], 'new-model')
        self.assertEqual(r['usage_state'], 'recorded')
        self.assertIsNone(r['capacity_estimate'])  # still no new runtime limit
        r = self.read([context(), usage(), context('new-model', 'turn2'), fresh, usage(window=2000)])
        self.assertIsNotNone(r['capacity_estimate'])

    def test_switch_history_bounded_and_duplicate_contexts_ignored(self):
        records = [context(), usage()]
        for n in range(15):
            records.extend([context('model'+str(n)), context('model'+str(n))])
        r = self.read(records)
        self.assertEqual(r['model_switch_count'], 15)
        self.assertEqual(len(r['model_switches']), 10)

    def test_diagnostics_survive_missing_usage(self):
        r = self.read([context()])
        self.assertEqual(r['model'], 'example')
        checks = {x['label']: x['status'] for x in r['diagnostics']['checks']}
        self.assertEqual(checks['Session identity'], 'observed')
        self.assertEqual(checks['Model metadata'], 'observed')
        self.assertEqual(checks['Usage events'], 'not_observed')

    def test_collect_reports_missing_home_and_identity_without_paths(self):
        r = mod.collect(Path(self.tmp.name) / 'private-missing-directory', 'test-chat')
        self.assertEqual(r['diagnostics']['failure_code'], 'home_unavailable')
        self.assertNotIn('private-missing-directory', json.dumps(r))
        self.read([context(), usage()])
        r = mod.collect(Path(self.tmp.name), 'other-chat', self.path)
        self.assertEqual(r['diagnostics']['failure_code'], 'identity_mismatch')
        self.assertNotIn(str(self.path), json.dumps(r))
        with patch.object(mod, 'inspect', side_effect=PermissionError('/private/SECRET-PATH')):
            r = mod.collect(Path(self.tmp.name), 'test-chat', self.path)
        self.assertEqual(r['diagnostics']['failure_code'], 'read_failed')
        self.assertEqual(r['diagnostics']['checks'][1]['status'], 'not_checked')
        self.assertNotIn('SECRET-PATH', json.dumps(r))

    def test_new_usage_record_and_current_turn_totals(self):
        record = event('token_usage_record', {'thread_id': 'test-chat', 'turn_id': 'turn1',
                       'usage': {'input_tokens': 200, 'output_tokens': 30},
                       'turn_token_usage': {'total_tokens': 700}, 'thread_token_usage': {'total_tokens': 800}})
        r = self.read([context(), usage(), record])
        self.assertEqual(r['capacity_estimate']['used_tokens'], 230)
        self.assertEqual(r['current_turn_cumulative']['total_tokens'], 700)
        self.assertIsNone(self.read([context(), usage(), record, context(turn='turn2')])['current_turn_cumulative'])

    def test_wrong_thread_usage_record_ignored(self):
        r = self.read([context(), usage(), event('token_usage_record', {'thread_id': 'wrong', 'usage': {'total_tokens': 9999}})])
        self.assertEqual(r['latest_request']['total_tokens'], 120)

    def test_quota_only_preserves_usage(self):
        r = self.read([context(), usage(), event('event_msg', {'type': 'token_count', 'info': None, 'rate_limits': {'primary': {'used_percent': 10}, 'credits': {'balance': 'SECRET'}}})])
        self.assertEqual(r['latest_request']['total_tokens'], 120)
        self.assertNotIn('SECRET', json.dumps(r))

    def test_database_exact_id_and_read_only(self):
        home = Path(self.tmp.name)
        db = home / 'state_5.sqlite'
        with sqlite3.connect(db) as con:
            con.execute('CREATE TABLE threads (id TEXT, rollout_path TEXT)')
            con.execute('INSERT INTO threads VALUES (?,?)', ('test-chat', str(self.path)))
        self.read([context(), usage()])
        before = db.read_bytes()
        self.assertEqual(mod.locate(home, 'test-chat'), self.path)
        self.assertEqual(before, db.read_bytes())
        with self.assertRaises(ValueError):
            mod.locate(home, 'missing-chat')


if __name__ == '__main__':
    unittest.main()
