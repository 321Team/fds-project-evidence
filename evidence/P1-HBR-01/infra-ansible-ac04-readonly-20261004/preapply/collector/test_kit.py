import contextlib, importlib.util, io, json, pathlib, unittest
from unittest.mock import patch
ROOT = pathlib.Path(__file__).resolve().parent
def module(name, filename):
    s=importlib.util.spec_from_file_location(name,ROOT/filename)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
collector=module("surface_collector","collect_surface.py")
driver=module("surface_driver","precheck.py")
class SurfaceTests(unittest.TestCase):
    def test_identity_rejects_wrong_host(self):
        with self.assertRaises(ValueError):collector.validate_host("ansible01",["10.1.93.54"])
    def test_identity_rejects_wrong_address(self):
        with self.assertRaises(ValueError):collector.validate_host("harbor01",["10.1.93.53"])
    def test_hostname_refusal_precedes_commands(self):
        with patch.object(collector.socket,"gethostname",return_value="ansible01"),patch.object(collector,"command") as cmd,contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(collector.main(),1);cmd.assert_not_called()
    def run_mock(self,fail=None):
        commands=[]
        def cmd(name,argv,required=True):
            commands.append(argv)
            out='[]'
            if name=="identity-addresses":out=json.dumps([{"addr_info":[{"local":"10.1.93.54"}]}])
            if name=="docker-container-ids":out="a"*64
            return {"name":name,"required":required,"rc":1 if name==fail else 0,"stdout":out}
        output=io.StringIO()
        with patch.object(collector.socket,"gethostname",return_value="harbor01"),patch.object(collector,"command",side_effect=cmd),patch.object(pathlib.Path,"is_file",return_value=False),patch.object(pathlib.Path,"is_symlink",return_value=False),contextlib.redirect_stdout(output):
            rc=collector.main()
        return rc,output.getvalue(),commands
    def test_mock_success_remains_review_required(self):
        rc,out,commands=self.run_mock()
        self.assertEqual(rc,0)
        self.assertIn("NETWORK_SURFACE_CAPTURED_REVIEW_REQUIRED",out)
        self.assertIn("NOT_PROVEN",out)
        fmt=next(c for c in commands if c[:2]==["docker","inspect"])[3]
        self.assertNotIn(".Config",fmt);self.assertNotIn(".Env",fmt)
        self.assertNotIn("restart",[word for c in commands for word in c])
        self.assertNotIn("shell=True",(ROOT/"collect_surface.py").read_text())
    def test_required_failure_is_not_capture_success(self):
        rc,out,_=self.run_mock("nft-ruleset");self.assertEqual(rc,1);self.assertIn("COLLECTION_FAILED",out)
    def test_optional_unavailable_stays_explicit(self):
        rc,out,_=self.run_mock("443-conntrack");self.assertEqual(rc,0);self.assertIn("443-conntrack",out)
    def test_source_head_drift_rejected(self):
        with self.assertRaises(driver.Stop):
            driver.validate_pr({"number":63,"state":"open","head":{"sha":"different"}})
    def test_inventory_extra_host_rejected(self):
        with self.assertRaises(driver.Stop):
            driver.validate_inventory({"hbr":{"hosts":["harbor01","other"]}})
if __name__=="__main__":unittest.main()

