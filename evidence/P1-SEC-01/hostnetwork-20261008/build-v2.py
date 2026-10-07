import ast,json,pathlib
root=pathlib.Path(__file__).resolve().parent
tree=ast.parse((root/'build.py').read_text())
runner=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='runner' for t in n.targets))
guard=(root/'guard.py').read_text();child=(root/'socket-v2.py').read_text()
old="identity();assert p.returncode==0,'UNEXPECTED_RESULT_STOP'"
assert old in runner
runner=runner.replace(old,"identity();last=r['cases'][-1];last['corroborated']=corroborate(c,json.loads(last['stdout']),last['before']['lines'],last['after']['lines']);assert p.returncode==0 and last['corroborated'],'UNEXPECTED_OR_UNCORROBORATED_STOP'")
runner=runner.replace('def now():',guard+'\ndef now():')
for n in ('105','107','108'):
 tree=ast.parse((root/('probe'+n+'.py')).read_text())
 config=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CONFIG' for t in x.targets))
 if n=='105':config['cases']=config['cases'][-1:]
 for c in config['cases']:
  if c['expect']=='TIMEOUT':c['expect']='BLOCKED'
 source=runner.replace('__CONFIG__',repr(config)).replace('__CHILD__',repr(child));compile(source,'v2','exec')
 (root/('probe'+n+'-v2.py')).write_text(source,encoding='utf-8',newline='\n')
