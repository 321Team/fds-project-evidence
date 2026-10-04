import contextlib, importlib.util, io, json, pathlib, tempfile, unittest
from unittest.mock import patch

def load(name):
 s=importlib.util.spec_from_file_location(name,pathlib.Path(__file__).parent/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
c=load('collect_surface');d=load('precheck')

class Checks(unittest.TestCase):
 def test_wrong_host_stops_before_commands(self):
  with patch.object(c.socket,'gethostname',return_value='wrong'),patch.object(c,'command') as cmd,contextlib.redirect_stdout(io.StringIO()): self.assertEqual(c.main(),1);cmd.assert_not_called()
 def test_wrong_address_stops_before_second_command(self):
  with patch.object(c.socket,'gethostname',return_value='harbor01'),patch.object(c.os,'geteuid',return_value=0),patch.object(c,'command',return_value={'rc':0,'stdout':'[]'}) as cmd,contextlib.redirect_stdout(io.StringIO()): self.assertEqual(c.main(),1);self.assertEqual(cmd.call_count,1)
 def test_no_general_process_argv(self):
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td)/'42';p.mkdir();(p/'exe').symlink_to('/usr/bin/server');(p/'comm').write_text('server');(p/'cmdline').write_bytes(b'server\0password\0')
   v=c.process_record(42,pathlib.Path(td));self.assertNotIn('password',json.dumps(v));self.assertEqual(v['argv'],'NOT_COLLECTED_NON_DOCKER_PROXY')
 def test_proxy_argv_filter(self):
  v=c.selected_proxy_args(['docker-proxy','-host-ip','::','-host-port','443','--secret','private']);self.assertEqual(v['selected_args']['-host-port'],'443');self.assertNotIn('private',json.dumps(v))
 def test_comment_and_active_include_distinct(self):
  v=c.nft_lines('# include "main.nft"\ninclude "active.nft"\nflush ruleset\n');self.assertTrue(v[0]['commented']);self.assertFalse(v[1]['commented']);self.assertEqual(len(v),3)
 def test_read_rejects_symlink(self):
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td)/'x';p.symlink_to('/etc/passwd')
   with self.assertRaises(ValueError):c.bounded_read(p)
 def test_read_size_bound(self):
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td)/'x';p.write_bytes(b'12345')
   with self.assertRaises(ValueError):c.bounded_read(p,4)
 def test_command_timeout_fails(self):
  with patch.object(c.subprocess,'run',side_effect=c.subprocess.TimeoutExpired('ss',45)),contextlib.redirect_stdout(io.StringIO()):self.assertEqual(c.command('ss',['ss'])['rc'],124)
 def test_pid_parse_deduplicates(self):self.assertEqual(c.listener_pids('pid=12,fd=3 pid=12 pid=13'),[12,13])
 def test_pr_head_drift_stops(self):
  with self.assertRaises(d.Stop):d.validate_pr({'number':63,'state':'open','head':{'sha':'different'}})

if __name__=='__main__':unittest.main()
