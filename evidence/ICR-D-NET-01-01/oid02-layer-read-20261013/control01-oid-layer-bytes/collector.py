import datetime,hashlib,json,os,re,socket,subprocess,time
assert os.geteuid()==0 and socket.gethostname()=='k8s-control01'
layers={'sha256:02eb3ae99b2b94ea214a8fe31e4935315f99484c5c167ba40c374dfc398201a9': 2952457, 'sha256:8ec9c2e1b1d69f40b703012b83971982e1d567a7c63a9e8a6ca0bb242dc9e937': 58139954, 'sha256:03c9b64681eef07f903b45cfbe5c064db1f1c7f682863b895104ac2680a271a7': 84728, 'sha256:2e4cf50eeb92ac3a7afe75e15d96a26dee99449f86b46c75b5d95f4418a5bca0': 12579, 'sha256:56ce5a7a0a8cc3aded9e8cab00fd85f0a1c50376aa9f2318c4e66beb03eadf8f': 458603, 'sha256:e1089d61b200106053b1717881bf0c1c47551478f01569d9224d33cccf3e4692': 28389, 'sha256:0f8b424aa0b96c1c388a5fd4d90735604459256336853082afb61733438872b5': 75, 'sha256:d557676654e572af3e3173c90e7874644207fda32cd87e9d3d66b5d7b98a7b21': 193, 'sha256:d82bc7a76a838c9a4a6025192429c2fed58f73742ef1fb9c8bb7b995fc3b7213': 130, 'sha256:68e4cd60e60fed4486d5b4b40b079e57781e828d93d80a7411e8760dcccfbbf7': 168, 'sha256:0783a66ae7492bb16937c7723c534e431404aa3ebbdcaaed65d264a95a266b9e': 84, 'sha256:efae86a3fb38e05e6e2584bc2f48534a0d82f8d9e9a4163d04885d5c65423105': 358, 'sha256:6b72b81ed96620b324f40ade069bbd3fcee69d62182bb03681c3976b6909eec4': 320, 'sha256:6cdd517ba90571b01009637268b5fddb4e3eea409bb6dae0bf40ed8ad9e33ef4': 130874, 'sha256:7bae8e7097d7983932f15870289838ba42ce97e13c38fda26cbdd9ba09d17e87': 22532938}
out={'host':socket.gethostname(),'boot':open('/proc/sys/kernel/random/boot_id').read().strip(),'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'fixed 15 layer bytes read and hash only; no export/import/pull/unpack','layers':[]}
for digest,size in layers.items():
 assert re.fullmatch(r'sha256:[0-9a-f]{64}',digest)
 cmd=['/usr/bin/ctr','--address','/run/containerd/containerd.sock','--namespace','k8s.io','content','get',digest]
 start=time.monotonic()
 try:
  p=subprocess.run(cmd,capture_output=True,timeout=10)
  observed='sha256:'+hashlib.sha256(p.stdout).hexdigest()
  row={'digest':digest,'expected_size':size,'observed_size':len(p.stdout),'observed_digest':observed,'rc':p.returncode,'stderr':p.stderr.decode(errors='replace'),'seconds':round(time.monotonic()-start,3),'argv':cmd}
  row['verified']=p.returncode==0 and observed==digest and len(p.stdout)==size
  del p
 except subprocess.TimeoutExpired:
  row={'digest':digest,'expected_size':size,'verified':False,'error':'READ_TIMEOUT_NO_RETRY'}
 out['layers'].append(row)
 if not row['verified']:break
out['verified_bytes']=sum(x['observed_size'] for x in out['layers'] if x['verified'])
out['status']='LAYER_BYTES_VERIFIED' if len(out['layers'])==15 and all(x['verified'] for x in out['layers']) else 'INCOMPLETE'
out['historical_provenance_verified']=False;out['export_import_executed']=False
print(json.dumps(out));raise SystemExit(0 if out['status']=='LAYER_BYTES_VERIFIED' else 2)
