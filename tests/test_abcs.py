import pytest

from pabiana.abcs import Node
from pabiana.utils import Interfaces

interfaces = {}  # type: Interfaces


@pytest.fixture(scope='module', autouse=True)
def interfaces():
	interfaces.update({
		'test-pub': {'ip': '127.0.0.1', 'port': 8279},
		'test-rcv': {'ip': '127.0.0.1', 'port': 8280},
		'area1-pub': {'ip': '130.0.0.2', 'port': 8281},
		'area1-rcv': {'ip': '130.0.0.2', 'port': 8282},
		'area2-pub': {'ip': '130.0.0.2', 'port': 8283, 'host': '0.0.0.0'},
		'area2-rcv': {'ip': '130.0.0.2', 'port': 8284},
		'clock100-pub': {'ip': '130.0.0.4', 'port': 8285}
	})


def test_rslv():
	class TestNode(Node): pass
	TestNode.__abstractmethods__ = set()

	node = Node(name='test', interfaces=interfaces)
	ip, port, host = node.rslv('pub')
	assert ip == '127.0.0.1' and port == 8279 and host is None
	ip, port, host = node.rslv('rcv')
	assert ip == '127.0.0.1' and port == 8280 and host is None
	ip, port, host = node.rslv(name='area1', interface='pub')
	assert ip == '130.0.0.2' and port == 8281 and host is None
	ip, port, host = node.rslv(name='area2', interface='pub')
	assert ip == '130.0.0.2' and port == 8283 and host is '0.0.0.0'
	ip, port, host = node.rslv(name='clock100', interface='pub')
	assert ip == '130.0.0.4' and port == 8285 and host is None
