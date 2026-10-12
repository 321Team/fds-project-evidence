from pathlib import Path
import importlib.util
W=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('transport',W.parent/'p1-redistribution-20261013/read_transport.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);t.OUT=W
source=(W/'read_final_test_inputs.py').read_bytes();compile(source,'read_final_test_inputs.py','exec')
t.run('final-test-inputs-control01','10.1.93.102',source,timeout=210)
