import importlib.util,json,pathlib,shlex,subprocess,unittest
p=pathlib.Path(__file__).with_name('verify-ansible-sftp.py')
spec=importlib.util.spec_from_file_location('v',p);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class Tests(unittest.TestCase):
 def receipt(self,host='k8s-worker01',**data):
  row={'changed':False,'ping':'pong'};row.update(data)
  return {'rc':0,'stdout':'<10.1.93.105> SSH: EXEC sftp -b -\nput source target\n'+host+' | SUCCESS => '+json.dumps(row)+'\n','stderr':''}
 def test_options_separated(self):
  x=v.transport_vars(pathlib.Path('/home/server01_ansible'))
  self.assertNotIn('-T',shlex.split(x['ansible_ssh_common_args']));self.assertEqual(x['ansible_ssh_extra_args'],'-T')
  self.assertEqual(x['ansible_ssh_transfer_method'],'sftp');self.assertFalse(x['ansible_pipelining'])
 def test_positive(self):self.assertTrue(v.valid_ping('k8s-worker01',self.receipt()))
 def test_wrong_host(self):self.assertFalse(v.valid_ping('k8s-control01',self.receipt()))
 def test_duplicate(self):
  r=self.receipt();r['stdout']*=2;self.assertFalse(v.valid_ping('k8s-worker01',r))
 def test_warning(self):
  r=self.receipt();r['stderr']='[WARNING]: transfer failed';self.assertFalse(v.valid_ping('k8s-worker01',r))
 def test_missing_put(self):
  r=self.receipt();r['stdout']=r['stdout'].replace('put source target','');self.assertFalse(v.valid_ping('k8s-worker01',r))
 def test_nonzero(self):
  r=self.receipt();r['rc']=1;self.assertFalse(v.valid_ping('k8s-worker01',r))
 def test_changed(self):self.assertFalse(v.valid_ping('k8s-worker01',self.receipt(changed=True)))
 def test_local_invalid_t_no_network(self):
  r=subprocess.run(['/usr/bin/sftp','-T'],text=True,capture_output=True)
  self.assertNotEqual(r.returncode,0);self.assertRegex(r.stderr,r'(unknown|illegal|invalid) option[^\n]*T')
if __name__=='__main__':unittest.main(verbosity=2)
