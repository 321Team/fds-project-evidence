# Collector source copy clarification

The remote stdin was UTF-8/LF and its SHA256 is recorded in invocation.json. Windows write_text saved collector.py using CRLF. executed-stdin.py reconstructs the exact LF stdin bytes and matches the recorded SHA256. collector.py is preserved as the local saved copy; it is not the byte-exact executed source. No server file or response was modified; no second remote execution was performed for this correction.
