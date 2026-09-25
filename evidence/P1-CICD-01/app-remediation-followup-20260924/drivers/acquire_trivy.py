import hashlib, json, pathlib, tarfile, urllib.request

root = pathlib.Path(__file__).resolve().parent
(root / 'bin').mkdir(parents=True, exist_ok=True)
def download(name, expected):
    target = root / name
    with urllib.request.urlopen('https://github.com/aquasecurity/trivy/releases/download/v0.74.0/' + name, timeout=45) as src, target.open('xb') as dst:
        while chunk := src.read(1024 * 1024):
            dst.write(chunk)
    assert hashlib.sha256(target.read_bytes()).hexdigest() == expected, name
    return target
checksums = download('trivy_0.74.0_checksums.txt', 'bc701c3c3ee8b9acbea2c23257e41381e3854888f51281616a6ba5dc96963821')
archive = download('trivy_0.74.0_Linux-64bit.tar.gz', '2ae6fe3ee734b7fdf11335663e18c75ea12dccc76062f09f164a3b0f8be4371a')
assert any(line.split() == ['2ae6fe3ee734b7fdf11335663e18c75ea12dccc76062f09f164a3b0f8be4371a', archive.name] for line in checksums.read_text().splitlines())
with tarfile.open(archive) as package:
    matches = [m for m in package.getmembers() if m.name == 'trivy']
    assert len(matches) == 1 and matches[0].isfile()
    binary = package.extractfile(matches[0]).read()
expected = 'd89bcc6510a267f11b773398cbf1be5520ce39f9e8b6633178c4487f05b7d791'
assert hashlib.sha256(binary).hexdigest() == expected, 'PROJECT_BINARY_PIN_MISMATCH'
path = root / 'bin/trivy'
path.write_bytes(binary)
path.chmod(0o755)
(root / 'binary-verification.json').write_text(json.dumps({'version':'0.74.0','binary_sha256':expected,'archive_sha256':'2ae6fe3ee734b7fdf11335663e18c75ea12dccc76062f09f164a3b0f8be4371a','release_checksums_match':True,'project_binary_pin_match':True,'path':str(path)},indent=2)+'\n')
print('TRIVY_PROJECT_PIN=PASS')
