"""Targeted server boundaries: session completion and failed-refresh retention."""
import copy
from datetime import datetime,timezone
import json
from pathlib import Path
import tempfile
import shutil
import unittest
from unittest.mock import patch
import catalog_server as server

class CatalogServerTests(unittest.TestCase):
    def test_early_close_today_is_not_used_until_actual_declared_end(self):
        # Nov27 is only a fixture label; the provider end, not a holiday table,
        # decides admission. A future timestamp is excluded by the cutoff.
        previous=1795713000;today=1795799400;end=1795802400
        payload={'chart':{'result':[{'meta':{'symbol':'^GSPC','currentTradingPeriod':{'regular':{'end':end}}},'timestamp':[previous,today],'indicators':{'quote':[{'close':[100,101]}]}}]}}
        class Result:stdout=json.dumps(payload).encode()
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);(out/'raw').mkdir()
            with patch.object(server.subprocess,'run',return_value=Result()):
                before,_=server.probe_completed_session(out,datetime.fromtimestamp(end-10,timezone.utc))
                after,_=server.probe_completed_session(out,datetime.fromtimestamp(end+61,timezone.utc))
        self.assertNotEqual(before,after)
        self.assertEqual(after,datetime.fromtimestamp(today,server.ET).date().isoformat())

    def test_failed_probe_preserves_last_successful_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=server.Store(tmp)
            before=store.state_path.read_bytes();version=store.snapshot()['version']
            store.running=True
            with patch.object(server,'probe_completed_session',side_effect=RuntimeError('fixture source unavailable')):
                store._refresh('failure-test')
            self.assertEqual(before,store.state_path.read_bytes())
            self.assertEqual(version,store.snapshot()['version'])
            self.assertEqual(store.status_snapshot()['status'],'failed')
            self.assertFalse(store.running)

    def test_refresh_concurrency_and_cooldown(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=server.Store(tmp,cooldown=60)
            with patch.object(server.threading,'Thread'):
                self.assertEqual(store.start_refresh()[0],202)
                self.assertEqual(store.start_refresh()[0],409)
                store.running=False
                code,status=store.start_refresh()
                self.assertEqual(code,429)
                self.assertGreater(status['retry_after_seconds'],0)

    def test_all_stale_history_does_not_replace_last_good_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=server.Store(tmp)
            before=store.state_path.read_bytes();version=store.snapshot()['version']
            with patch.object(server,'probe_completed_session',return_value=('2026-10-29',{})), patch.object(server,'process',return_value={'asof_session':'2026-10-28'}):
                store._refresh('all-stale-test')
            self.assertEqual(before,store.state_path.read_bytes())
            self.assertEqual(version,store.snapshot()['version'])
            self.assertEqual(store.status_snapshot()['status'],'failed')
            self.assertTrue(all(e['phase']=='history_freshness' for e in store.status_snapshot()['errors']))

    def test_new_reviewed_source_updates_facts_preserving_live_quotes(self):
        reference=server.latest_reference()
        source=json.loads((reference/'catalog.json').read_text())
        risks=json.loads((reference/'risk_metrics.json').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            archive=Path(tmp);first=archive/'2026-10-30/watchlist_catalog';first.mkdir(parents=True)
            (first/'catalog.json').write_text(json.dumps(source));(first/'risk_metrics.json').write_text(json.dumps(risks))
            with patch.object(server,'ARCHIVE',archive):
                store=server.Store(archive/'live_catalog',first)
                old=store.snapshot();old_voo=next(a for g in old['catalog']['groups'] for a in g['assets'] if a['symbol']=='VOO')
                updated=copy.deepcopy(source);updated['report_date']='2026-10-31'
                voo=next(a for g in updated['groups'] for a in g['assets'] if a['symbol']=='VOO')
                voo['facts']['name']='Reviewed new description';voo['role']='New reviewed role';voo['quote']['close']=999
                second=archive/'2026-10-31/watchlist_catalog';second.mkdir(parents=True);(second/'catalog.json').write_text(json.dumps(updated))
                latest=store.snapshot();latest_voo=next(a for g in latest['catalog']['groups'] for a in g['assets'] if a['symbol']=='VOO')
                self.assertEqual(latest_voo['facts']['name'],'Reviewed new description')
                self.assertEqual(latest_voo['role'],'New reviewed role')
                self.assertEqual(latest_voo['quote'],old_voo['quote'])
                self.assertNotEqual(latest['version'],old['version'])
                self.assertEqual(latest['reviewed_source']['report_date'],'2026-10-31')

    def test_registry_cannot_reintroduce_removed_symbols(self):
        source=json.loads((server.latest_reference()/'catalog.json').read_text())
        old=copy.deepcopy(source);old['groups'][0]['assets'].append({'symbol':'QQQ','name':'Retired'})
        result=server.sync_registry(old)
        self.assertNotIn('QQQ',[a['symbol'] for g in result['groups'] for a in g['assets']])

if __name__=='__main__':unittest.main()
