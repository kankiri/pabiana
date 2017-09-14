import json

import pytest

from pabiana import load_interfaces, Node, node, rslv

ifs_path = None


@pytest.fixture(scope='module', autouse=True)
def interfaces_file(tmpdir_factory):
	global ifs_path
	ifs = {
		'test-pub': {'ip': '127.0.0.1', 'port': 8279},
		'test-rcv': {'ip': '127.0.0.1', 'port': 8280},
		'area1-pub': {'ip': '127.0.0.1', 'port': 8281},
		'area1-rcv': {'ip': '127.0.0.1', 'port': 8282},
		'area2-pub': {'ip': '127.0.0.1', 'port': 8283},
		'area2-rcv': {'ip': '127.0.0.1', 'port': 8284},
		'clock100-pub': {'ip': '127.0.0.1', 'port': 8285}
	}
	ifs_path = str(tmpdir_factory.mktemp('ifs-area').join('interfaces.json'))
	with open(ifs_path, 'w') as f:
		json.dump(ifs, f)
	load_interfaces(ifs_path)


def test_load_interfaces():
	node.interfaces.clear()
	load_interfaces({
		'test-pub': {'ip': '127.0.0.1', 'port': 8279},
		'test-rcv': {'ip': '127.0.0.1', 'port': 8280}
	})
	assert len(node.interfaces) == 2
	assert node.interfaces['test-pub']['port'] == 8279
	assert node.interfaces['test-rcv']['ip'] == '127.0.0.1'
	node.interfaces.clear()
	load_interfaces(ifs_path)
	assert len(node.interfaces) == 7
	assert node.interfaces['test-pub']['port'] == 8279
	assert node.interfaces['area1-rcv']['port'] == 8282
	assert node.interfaces['clock100-pub']['ip'] == '127.0.0.1'


def test_rslv():
	result = rslv('area2-pub')
	assert len(result) == 2
	assert result['ip'] == '127.0.0.1'
	assert result['port'] == 8283
	node.interfaces.clear()