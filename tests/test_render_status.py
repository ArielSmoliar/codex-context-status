import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('renderer', Path(__file__).resolve().parents[1] / 'scripts/render_status.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class RenderTests(unittest.TestCase):
    def test_embedded_data_is_allowlisted_and_script_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'result.html'
            hostile='</script><script>window.bad=true</script>'
            module.render({'status':'unavailable','reason':hostile,'thread_id':'PRIVATE-ID','source_path':'PRIVATE-PATH','recorded_account_rate_limits':{'secret':True}},output,'America/New_York')
            html=output.read_text()
            self.assertNotIn(hostile,html)
            self.assertNotIn('PRIVATE-',html)
            payload=re.search(r'<script type="application/json" id="context-status-data">(.*?)</script>',html,re.S).group(1)
            self.assertEqual(json.loads(payload)['reason'],hostile)
            self.assertNotIn('@@CONTEXT_STATUS_DATA@@',html)

    def test_invalid_timezone_and_extension_fail_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'result.html'
            with self.assertRaises(KeyError): module.render({},output,'Not/A_Timezone')
            self.assertFalse(output.exists())
            with self.assertRaises(ValueError): module.render({},Path(tmp)/'result.txt')

if __name__=='__main__':unittest.main()
