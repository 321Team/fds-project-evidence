"""Read the approved builder archive; no extraction, execution or server writes."""
import datetime, hashlib, json, os, pathlib, socket, stat, tarfile
assert socket.gethostname() == 'cicd-runner01' and os.getuid() == 1000
p = pathlib.Path('/home/server01_cicd-runner/FDS_CICD_Runtime/FDS_CICD_ApkoSupply.affbc69beef9.6ab02000437a/builder.oci.tar')
s = p.lstat()
assert stat.S_ISREG(s.st_mode) and s.st_uid == 1000 and not p.is_symlink()
out = {'started_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'read_only': True, 'path': str(p), 'archive_bytes': s.st_size}
h = hashlib.sha256()
with p.open('rb') as f:
    for chunk in iter(lambda: f.read(1024*1024), b''): h.update(chunk)
out['archive_sha256'] = h.hexdigest()
assert out['archive_sha256'] == 'e30bd4788d4a9b446cd91107dfe8597ee7ded9cbdc05414d6db8dcd42a456266'
with tarfile.open(p, 'r:*') as archive:
    manifest = json.load(archive.extractfile('manifest.json'))
    assert len(manifest) == 1 and len(manifest[0]['Layers']) == 1
    raw = archive.extractfile(manifest[0]['Config']).read(1024*1024)
    out['config_digest'] = 'sha256:' + hashlib.sha256(raw).hexdigest()
    assert out['config_digest'] == 'sha256:76cfebb7af7d22c528da8cda75aa8e3f35cb9bbcdcdfc1f70e71be4aaa350b4a'
    config = json.loads(raw)
    path_values = [v[5:] for v in config['config']['Env'] if v.startswith('PATH=')]
    assert len(path_values) == 1
    out['image_path'] = path_values[0]
    assert '/usr/bin' in path_values[0].split(':')
    entries = {}
    with tarfile.open(fileobj=archive.extractfile(manifest[0]['Layers'][0]), mode='r|*') as layer:
        for member in layer:
            name = member.name.removeprefix('./').rstrip('/')
            if name in ('usr', 'usr/bin', 'usr/bin/python3.13'):
                entries[name] = {'regular': member.isfile(), 'directory': member.isdir(), 'mode': oct(member.mode), 'uid': member.uid, 'gid': member.gid, 'linkname': member.linkname}
                assert member.mode & 0o001
                if name == 'usr/bin/python3.13': assert member.isfile() and member.mode & 0o004
    assert len(entries) == 3
    out['entries'] = entries
out['archive_unchanged_during_read'] = p.stat().st_mtime_ns == s.st_mtime_ns and p.stat().st_size == s.st_size
assert out['archive_unchanged_during_read']
out['python313_present_executable'] = True
out['finished_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
print(json.dumps(out))
