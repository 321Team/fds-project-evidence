import contextlib,importlib.util,io,pathlib,tempfile,unittest
from unittest.mock import patch
s=importlib.util.spec_from_file_location('collector',pathlib.Path(__file__).parent/'collect_surface.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
class Tests(unittest.TestCase):
 def test_wrong_host_no_commands(self):
  with patch.object(c.socket,'gethostname',return_value='wrong'),patch.object(c,'command') as cmd,contextlib.redirect_stdout(io.StringIO()):self.assertEqual(c.main(),1);cmd.assert_not_called()
 def test_wrong_address_no_profile(self):
  with patch.object(c.socket,'gethostname',return_value='harbor01'),patch.object(c.os,'geteuid',return_value=0),patch.object(c,'command',return_value={'rc':0,'stdout':'[]'}) as cmd,contextlib.redirect_stdout(io.StringIO()):self.assertEqual(c.main(),1);self.assertEqual(cmd.call_count,1)
 def test_bad_uuid_stops(self):
  identity={'rc':0,'stdout':'[{"ifname":"ens160","addr_info":[{"local":"10.1.93.54"}]}]'}
  with patch.object(c.socket,'gethostname',return_value='harbor01'),patch.object(c.os,'geteuid',return_value=0),patch.object(c,'command',side_effect=[identity,{'rc':0,'stdout':'bad uuid'}]) as cmd,contextlib.redirect_stdout(io.StringIO()):self.assertEqual(c.main(),1);self.assertEqual(cmd.call_count,2)
 def test_only_disable_ipv6_keys(self):
  v=c.selected_lines('# net.ipv6.conf.ens160.disable_ipv6=0\nnet.ipv6.conf.ens160.disable_ipv6 = 1\nsecret.password=private\nnet.ipv4.ip_forward=1');self.assertEqual(len(v),1);self.assertEqual(v[0]['value'],'1')
 def test_missing_file_explicit(self):
  with tempfile.TemporaryDirectory() as td:self.assertEqual(c.config_record(pathlib.Path(td)/'missing')['status'],'ABSENT')
 def test_link_not_followed(self):
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td)/'x';p.symlink_to('/etc/passwd');self.assertEqual(c.config_record(p)['status'],'SYMLINK_REVIEW_REQUIRED')
 def test_large_config_fails(self):
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td)/'x';p.write_bytes(b'x'*1048577);self.assertEqual(c.config_record(p)['status'],'READ_FAILED')
 def test_timeout_explicit(self):
  with patch.object(c.subprocess,'run',side_effect=c.subprocess.TimeoutExpired('nmcli',45)),contextlib.redirect_stdout(io.StringIO()):self.assertEqual(c.command('nmcli',['nmcli'])['rc'],124)
if __name__=='__main__':unittest.main()
