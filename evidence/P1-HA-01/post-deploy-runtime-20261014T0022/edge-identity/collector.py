import datetime,json,os,pathlib,socket,shutil
assert socket.gethostname()=='edge01'
print(json.dumps({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':socket.gethostname(),'uid':os.geteuid(),'gid':os.getegid(),'home':str(pathlib.Path.home()),'home_writable':os.access(pathlib.Path.home(),os.W_OK),'python3':shutil.which('python3'),'pwd':os.getcwd(),'writes':0}))
