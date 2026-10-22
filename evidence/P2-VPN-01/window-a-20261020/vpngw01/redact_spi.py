"""Byte-exact SPI redaction: only 8-hex SPI values after 'SPI=' or '<0x'/'>0x' are replaced."""
import re, sys
src, dst = sys.argv[1], sys.argv[2]
data = open(src, 'rb').read()
out, n1 = re.subn(rb'SPI=[0-9a-f]{8}\b', b'SPI=SPI_REDACTED', data)
out, n2 = re.subn(rb'([<>])0x[0-9a-f]{8}\b', rb'\g<1>0xSPI_REDACTED', out)
open(dst, 'wb').write(out)
print(f'{n1 + n2} replaced, {len(data)} -> {len(out)} bytes, CR {data.count(b"\r")} -> {out.count(b"\r")}')
