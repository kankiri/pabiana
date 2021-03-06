import time
from threading import Thread
from typing import Any, Dict

import pytest

from pabiana.utils import Interfaces
from pabiana.zmqs.node import Node

interfaces = {}  # type: Interfaces
subscriptions = {}  # type: Dict[str, Any]


@pytest.fixture(scope='module', autouse=True)
def setup():
	interfaces.update({
		'test-pub': {'ip': '127.0.0.1', 'port': 8279},
		'test-rcv': {'ip': '127.0.0.1', 'port': 8280},
		'area1-pub': {'ip': '130.0.0.2', 'port': 8281},
		'area1-rcv': {'ip': '130.0.0.2', 'port': 8282},
		'area2-pub': {'ip': '130.0.0.2', 'port': 8283, 'host': '0.0.0.0'},
		'area2-rcv': {'ip': '130.0.0.2', 'port': 8284}
	})
	subscriptions.update({
		'area1': {'slots': ['area1-slot1', 'area1-slot2']},
		'area2': {'slots': None, 'buffer-length': 100}
	})


def test_run_stop():
	class TestNode(Node): pass
	TestNode.__abstractmethods__ = set()

	def stop(value):
		time.sleep(0.5)
		value.stop()

	node = TestNode(name='area2', interfaces=interfaces)
	t = Thread(target=stop, args=(node,))

	t.start()
	node.run(timeout=0, linger=0)
	assert not t.isAlive()


def test_setup_run_stop():
	class TestNode(Node): pass
	TestNode.__abstractmethods__ = set()

	def stop(value):
		time.sleep(0.5)
		value.stop()

	node = TestNode(name='area2', interfaces=interfaces)
	node.setup(puller=False, subscriptions=subscriptions)
	t = Thread(target=stop, args=(node,))

	t.start()
	node.run(timeout=0, linger=0)
	assert not t.isAlive()
