# Build ROSA HCP --registry-config-additional-trusted-ca JSON from a PEM file.
# Rule: keys sorted, separators (",", ":"), ASCII-only, PEM value byte-identical, no trailing newline.
import hashlib, json, sys
pem_path, out_path, *keys = sys.argv[1:]
pem = open(pem_path, "rb").read().decode("ascii")
assert pem.count("-----BEGIN CERTIFICATE-----") == 1 and "PRIVATE KEY" not in pem
doc = json.dumps({k: pem for k in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
open(out_path, "wb").write(doc.encode("ascii"))
back = json.loads(open(out_path, "rb").read())
assert sorted(back) == sorted(keys) and all(v == pem for v in back.values())
print("pem_sha256", hashlib.sha256(pem.encode()).hexdigest())
print("json_sha256", hashlib.sha256(doc.encode()).hexdigest(), "bytes", len(doc))
print("keys", sorted(back))
