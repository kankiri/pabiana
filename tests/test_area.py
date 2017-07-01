from io import StringIO
import json
import logging
from threading import Thread
import time

import pytest
import zmq

log_stream = StringIO()


# @pytest.fixture(scope='module', autouse=True)
# def interfaces_file(tmpdir_factory):
# 	ifs = {
# 		'timer-pub': {
# 			'ip': '127.0.0.1',
# 			'port': 18281
# 		},
# 		'timer-rcv': {
# 			'ip': '127.0.0.1',
# 			'port': 18282
# 		}
# 	}
# 	path = str(tmpdir_factory.mktemp('ifs').join('interfaces.json'))
# 	with open(path, 'w') as f:
# 		json.dump(ifs, f)
# 	area.config['ifs-path'] = path
#
#
# def truncate():
# 	print(log_stream.getvalue())
# 	log_stream.truncate()
# 	log_stream.seek(0)
#
#
# def sleeper(term):
# 	cntr = 0
# 	while term not in log_stream.getvalue() and cntr < 50:
# 		time.sleep(0.1)
# 		cntr = cntr + 1
# 	time.sleep(0.1)
# 	return cntr < 30
#
#
# def test_rslv():
# 	result = rslv('timer-pub')
# 	assert result['ip'] == '127.0.0.1'
# 	assert result['port'] == 18281
# 	result = rslv('timer-rcv')
# 	assert result['ip'] == '127.0.0.1'
# 	assert result['port'] == 18282
#
#
# def test_basic_area():
# 	truncate()
# 	result = create_publisher('timer')
# 	assert str(type(result)) == '<class \'zmq.sugar.socket.Socket\'>'
# 	Thread(target=run, args=('timer',), kwargs={'timeout_ms':100}, daemon=True).start()
# 	assert sleeper('Listening to')
# 	trigger('timer', 'test', context=zmq.Context())
# 	assert sleeper('Trigger test of timer')
# 	area.goon = False
# 	assert sleeper('Context destroyed')
# 	assert 'Waiting for Connections on 127.0.0.1:18282' in log_stream.getvalue()
# 	assert 'Receiver Message: {\'function\': \'test\'}' in log_stream.getvalue()
# 	assert 'Unavailable Trigger called' in log_stream.getvalue()
#
#
# def teardown_module(module):
# 	print(log_stream.getvalue())
#
#
# logging.basicConfig(
# 	format='%(asctime)s %(levelname)s %(message)s',
# 	datefmt='%Y-%m-%d %H:%M:%S',
# 	level=logging.DEBUG,
# 	stream=log_stream
# )
