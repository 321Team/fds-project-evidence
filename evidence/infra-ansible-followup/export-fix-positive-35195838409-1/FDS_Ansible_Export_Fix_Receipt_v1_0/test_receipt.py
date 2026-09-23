import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('collect', Path(__file__).with_name('collect.py'))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

def samples():
    run = dict(id=c.RUN, run_attempt=c.ATTEMPT, head_sha=c.SOURCE,
               repository={'full_name': c.REPO}, event='pull_request',
               status='completed', conclusion='success', check_suite_id=500)
    steps = [dict(name=n,status='completed',conclusion='success') for n in
             ('Checkout exact source','Syntax and both pinned engines','Preserve result and original logs on success or failure')]
    job = dict(id=c.JOB,run_id=c.RUN,run_attempt=c.ATTEMPT,head_sha=c.SOURCE,name='regression',
               status='completed',conclusion='success',runner_id=c.RUNNER,runner_name=c.RUNNER_NAME,
               labels=sorted(c.LABELS),steps=steps)
    check = dict(id=c.JOB,head_sha=c.SOURCE,name='regression',status='completed',conclusion='success',
                 check_suite={'id':500},app={'slug':'github-actions'})
    pr = dict(number=c.PR,state='open',draft=True,head={'sha':c.SOURCE,'ref':c.BRANCH,'repo':{'full_name':c.REPO}},
              base={'ref':'main','repo':{'full_name':c.REPO}})
    return run,dict(total_count=1,jobs=[job]),check,pr

class ReceiptTests(unittest.TestCase):
    def test_exact_target_and_tampering(self):
        run,jobs,check,pr=samples()
        self.assertTrue(c.bind_execution(run,jobs,check));self.assertTrue(c.bind_pr(pr))
        cases=[(0,('head_sha',),'0'*40),(0,('run_attempt',),2),(0,('id',),1),
               (0,('conclusion',),'failure'),(0,('event',),'push'),
               (1,('jobs',0,'id'),1),(1,('jobs',0,'runner_id'),5),(1,('jobs',0,'runner_name'),'other'),
               (1,('jobs',0,'labels'),['self-hosted']), (1,('jobs',0,'steps'),[]),
               (2,('id',),1),(2,('head_sha',),'0'*40),(2,('check_suite','id'),1),
               (2,('app','slug'),'other'),(2,('conclusion',),'failure'),(2,('status',),'queued')]
        for idx,path,value in cases:
            with self.subTest(path=path,value=value):
                values=copy.deepcopy([run,jobs,check]);node=values[idx]
                for key in path[:-1]: node=node[key]
                node[path[-1]]=value
                self.assertFalse(c.bind_execution(*values))
        for key,val in [('number',20),('draft',False),('state','closed'),('head',None)]:
            bad=copy.deepcopy(pr);bad[key]=val;self.assertFalse(c.bind_pr(bad))

    def test_malformed_execution_rejected(self):
        for value in (None,[],{},'bad'):
            self.assertFalse(c.bind_execution(value,value,value));self.assertFalse(c.bind_pr(value))

    def test_complete_absence_with_other_runners(self):
        self.assertTrue(c.absence([{'total_count':0,'runners':[]}])['absent'])
        pages=[{'total_count':2,'runners':[{'id':900,'name':'other1'}]},
               {'total_count':2,'runners':[{'id':901,'name':'other2'}]}]
        self.assertTrue(c.absence(pages)['absent'])

    def test_later_page_target_id_or_name(self):
        for target in ({'id':c.RUNNER,'name':'renamed'},{'id':999,'name':c.RUNNER_NAME}):
            result=c.absence([{'total_count':2,'runners':[{'id':900,'name':'other'}]},
                              {'total_count':2,'runners':[target]}])
            self.assertTrue(result['complete_query']);self.assertFalse(result['absent'])

    def test_incomplete_malformed_duplicate_pages(self):
        cases=[None,[],{},[{'message':'Forbidden'}],[{'total_count':1,'runners':[]}],
               [{'total_count':0,'runners':None}],
               [{'total_count':1,'runners':[{'id':True,'name':'bad'}]}],
               [{'total_count':2,'runners':[{'id':900,'name':'a'},{'id':900,'name':'b'}]}],
               [{'total_count':1,'runners':[{'id':900,'name':'a'}]},{'total_count':2,'runners':[]}]]
        for pages in cases:
            with self.subTest(pages=pages):
                result=c.absence(pages);self.assertFalse(result['complete_query']);self.assertIsNone(result['absent'])

    def test_api_only_get_and_no_stderr_leak(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ,GH_DEBUG='api',GH_TOKEN='test-only-secret'):
            for rc in (0,1):
                calls=[]
                def fake(command,**kwargs):
                    self.assertEqual(command[command.index('--method')+1],'GET')
                    self.assertIn('--paginate',command);self.assertIn('--slurp',command)
                    self.assertNotIn('GH_DEBUG',kwargs['env'])
                    self.assertEqual(kwargs['env']['GH_TOKEN'],'test-only-secret')
                    return subprocess.CompletedProcess(command,rc,stderr=b'test-only-secret')
                with patch.object(c.subprocess,'run',side_effect=fake):
                    self.assertEqual(c.api('gh','repos/'+c.REPO+'/actions/runners',Path(td)/str(rc),calls,True),rc==0)
                self.assertNotIn('test-only-secret',json.dumps(calls))

    def test_api_timeout_is_not_absence(self):
        with tempfile.TemporaryDirectory() as td, patch.object(c.subprocess,'run',side_effect=subprocess.TimeoutExpired('gh',180)):
            commands=[];self.assertFalse(c.api('gh','fixed',Path(td)/'response',commands))
            self.assertTrue(commands[0]['timed_out'])

    def run_collection(self, failed=False, present=False, old_clock=False, wrong_check=False):
        run,jobs,check,pr=samples()
        if wrong_check: check['head_sha']='0'*40
        rows=[{'id':c.RUNNER,'name':c.RUNNER_NAME}] if present else []
        data={'pr.json':pr,'run-attempt1.json':run,'jobs-attempt1.json':jobs,'check.json':check,
              'runner-pages.json':[{'total_count':len(rows),'runners':rows}]}
        seen=[]
        def fake_api(gh,endpoint,path,commands,paginate=False):
            seen.append(endpoint)
            path.write_text(json.dumps(data[path.name]))
            commands.append({'command':[gh,'api','--method','GET',endpoint],'rc':1 if failed and path.name=='runner-pages.json' else 0})
            return not (failed and path.name=='runner-pages.json')
        with tempfile.TemporaryDirectory() as td:
            home=Path(td);before=home.stat().st_mode
            with patch.object(c,'api',side_effect=fake_api),patch.object(c,'now',return_value='2026-09-17T08:00:00+00:00' if old_clock else '2026-09-17T09:00:00+00:00'),contextlib.redirect_stdout(io.StringIO()):
                rc=c.collect(home,'gh')
            archive=next(home.rglob(c.ARCHIVE_NAME))
            self.assertEqual(home.stat().st_mode,before)
            self.assertEqual(Path(str(archive)+'.sha256').read_text().split(),[c.sha(archive),archive.name])
            with tarfile.open(archive) as t:
                files={m.name:t.extractfile(m).read() for m in t if m.isfile()}
            for line in files['evidence/SHA256SUMS'].decode().splitlines():
                digest,name=line.split('  ',1);self.assertEqual(digest,hashlib.sha256(files['evidence/'+name]).hexdigest())
            result=json.loads(files['evidence/RESULT.json'])
            self.assertEqual(len(seen),5);self.assertFalse(any('/zip' in e for e in seen))
            self.assertFalse(result['token_issuance']);self.assertFalse(result['server_changes'])
            return rc,result

    def test_collection_success_and_manifest(self):
        rc,result=self.run_collection();self.assertEqual(rc,0)
        self.assertEqual(result['status'],'COLLECTED_BOUND_REVIEW_REQUIRED')
        self.assertFalse(result['artifact_download'])

    def test_failed_get_target_present_old_clock_bad_check_preserve_receipt(self):
        for kw in ({'failed':True},{'present':True},{'old_clock':True},{'wrong_check':True}):
            with self.subTest(kw=kw):
                rc,result=self.run_collection(**kw);self.assertEqual(rc,1)
                self.assertEqual(result['status'],'COLLECTION_INCOMPLETE')

if __name__=='__main__':
    unittest.main(verbosity=2)
