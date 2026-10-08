import gzip,importlib.util,json,pathlib,time,unittest
p=pathlib.Path(__file__).with_name('edge-w4-access-collector.py');s=importlib.util.spec_from_file_location('collector',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def line(at,status=503):return ('192.0.2.9 - hidden-user ['+at+'] "POST /api/v1/transactions?token=SECRET HTTP/1.1" '+str(status)+' 12 "PRIVATE_REF" "PRIVATE_UA"\n').encode()
class Tests(unittest.TestCase):
    def test_window_boundaries_and_no_payload(self):
        raw=b''.join(line('08/Oct/2026:20:'+at+' +0900') for at in ('26:48','26:49','27:52','27:53'))
        r=m.aggregate(raw,False,time.monotonic()+2)
        self.assertEqual(sum(x['count'] for x in r['w4_counts']),2)
        self.assertEqual(r['parsed_records'],4)
        for word in ('SECRET','192.0.2.9','hidden-user','PRIVATE'):self.assertNotIn(word,json.dumps(r))
    def test_utc_equivalent(self):
        r=m.aggregate(line('08/Oct/2026:11:26:49 +0000',201),False,time.monotonic()+2)
        self.assertEqual(r['w4_counts'][0]['status'],'201')
    def test_gzip(self):
        raw=line('08/Oct/2026:20:27:00 +0900');self.assertEqual(m.aggregate(raw,False,time.monotonic()+2),m.aggregate(gzip.compress(raw),True,time.monotonic()+2))
    def test_malformed_and_partial(self):
        r=m.aggregate(b'not combined\n'+line('08/Oct/2026:20:27:00 +0900')[:-1],False,time.monotonic()+2)
        self.assertEqual(r['unparsed_chunks'],2);self.assertEqual(r['w4_counts'],[])
    def test_cap(self):
        r=m.aggregate(line('08/Oct/2026:20:27:00 +0900'),False,time.monotonic()+2,8)
        self.assertFalse(r['stream_complete']);self.assertLessEqual(r['decoded_bytes'],8)
    def test_long_line_continuation_not_request(self):
        raw=b'x'*65536+line('08/Oct/2026:20:27:00 +0900')
        r=m.aggregate(raw,False,time.monotonic()+2)
        self.assertEqual(r['w4_counts'],[]);self.assertEqual(r['unparsed_chunks'],2)
    def test_expired(self):
        r=m.aggregate(line('08/Oct/2026:20:27:00 +0900'),False,time.monotonic()-1)
        self.assertFalse(r['stream_complete']);self.assertEqual(r['w4_counts'],[])
if __name__=='__main__':unittest.main()
