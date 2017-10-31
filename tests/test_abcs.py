import pytest

from pabiana.abcs import Area, Node
from pabiana.utils import Interfaces

interfaces = {}  # type: Interfaces


@pytest.fixture(scope='module', autouse=True)
def setup():
	interfaces.update({
		'test-pub': {'ip': '127.0.0.1', 'port': 8279},
		'test-rcv': {'ip': '127.0.0.1', 'port': 8280},
		'area1-pub': {'ip': '130.0.0.2', 'port': 8281},
		'area1-rcv': {'ip': '130.0.0.2', 'port': 8282},
		'area2-pub': {'ip': '130.0.0.2', 'port': 8283, 'host': '0.0.0.0'},
		'area2-rcv': {'ip': '130.0.0.2', 'port': 8284},
		'clock100-pub': {'ip': '130.0.0.4', 'port': 8285}
	})


def test_Node_init():
	class TestNode(Node): pass
	TestNode.__abstractmethods__ = set()

	node = TestNode(name='area1', interfaces=interfaces)
	assert node.name == 'area1'
	assert node.interfaces is interfaces
	assert isinstance(node.time, int)


def test_Node_rslv():
	class TestNode(Node): pass
	TestNode.__abstractmethods__ = set()

	node = TestNode(name='test', interfaces=interfaces)
	ip, port, host = node.rslv('pub')
	assert ip == '127.0.0.1' and port == 8279 and host is None
	ip, port, host = node.rslv('rcv')
	assert ip == '127.0.0.1' and port == 8280 and host is None
	ip, port, host = node.rslv(name='area1', interface='pub')
	assert ip == '130.0.0.2' and port == 8281 and host is None
	ip, port, host = node.rslv(name='area2', interface='pub')
	assert ip == '130.0.0.2' and port == 8283 and host == '0.0.0.0'
	ip, port, host = node.rslv(name='clock100', interface='pub')
	assert ip == '130.0.0.4' and port == 8285 and host is None


def test_Area_init():
	class TestArea(Area): pass
	TestArea.__abstractmethods__ = set()

	area = TestArea(name='area2', interfaces=interfaces)
	assert isinstance(area.context, dict)
	assert hasattr(area, 'clock_name') and hasattr(area, 'clock_slot')
