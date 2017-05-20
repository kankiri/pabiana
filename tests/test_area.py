from io import StringIO
import json
import logging
import os
from threading import Thread
import time

import pytest
import zmq

from pabiana import area
from pabiana.area import create_publisher, rslv, run, trigger

log_stream = StringIO()


@pytest.fixture(scope='module', autouse=True)
def interfaces_file(tmpdir_factory):
	ifs = {
		'timer-pub': {
			'ip': '127.0.0.1',
			'port': 18281
		},
		'timer-rcv': {
			'ip': '127.0.0.1',
			'port': 18282
		}
	}
	path = str(tmpdir_factory.mktemp('ifs').join('interfaces.json'))
	with open(path, 'w') as f:
		json.dump(ifs, f)
	area.config['main-path'] = os.path.dirname(path)
	area.config['global-path'] = os.path.dirname(path)
	area.config['ifs-path'] = path


def teardown_module(module):
	print(log_stream.getvalue())


def test_rslv():
	result = rslv('timer-pub')
	assert result['ip'] == '127.0.0.1'
	assert result['port'] == 18281
	result = rslv('timer-rcv')
	assert result['ip'] == '127.0.0.1'
	assert result['port'] == 18282


def test_basic_area():
	result = create_publisher('timer')
	assert str(type(result)) == '<class \'zmq.sugar.socket.Socket\'>'
	Thread(target=run, args=('timer',), daemon=True).start()
	time.sleep(3)
	trigger('timer', 'test', context=zmq.Context())
	time.sleep(3)
	area.goon = False
	time.sleep(3)
	assert 'Waiting for Connections on 127.0.0.1:18282' in log_stream.getvalue()
	assert 'Receiver Message: {\'function\': \'test\'}' in log_stream.getvalue()
	assert 'Unavailable Trigger called' in log_stream.getvalue()


logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s',
	datefmt='%Y-%m-%d %H:%M:%S',
	level=logging.DEBUG,
	stream=log_stream
)
