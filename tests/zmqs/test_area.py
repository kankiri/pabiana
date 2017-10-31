from typing import Any, Callable, Dict

import pytest

from pabiana.utils import Interfaces
from pabiana.zmqs.area import Area

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
		'area2-rcv': {'ip': '130.0.0.2', 'port': 8284},
		'clock100-pub': {'ip': '130.0.0.4', 'port': 8285}
	})
	subscriptions.update({
		'area1': ['area1-slot1', 'area1-slot2'],
		'area2': None
	})


def test_decorators():
	area = Area(name='test', interfaces=interfaces)
	func = lambda: None
	assert isinstance(area.scheduling(func=func), Callable)
	assert isinstance(area.register(func=func), Callable)
	assert isinstance(area.alteration(func=func), Callable)
	assert isinstance(area.alteration(source='area'), Callable)
	assert isinstance(area.alteration(source='area', slot='slot'), Callable)
	assert isinstance(area.pulse(func), Callable)


def test_register_comply():
	area = Area(name='test', interfaces=interfaces)
	test_vals = []

	@area.register
	def trigger_1():
		test_vals.append('t1')

	@area.register
	def trigger_2(value1='v1', value2='v2'):
		test_vals.append('t2({}, {})'.format(value1, value2))

	area.comply(trigger='trigger_1')
	area.comply(trigger='trigger_2', parameters={'value2': 'v2'})
	area.proceed()

	assert 't1' in test_vals and 't2(v1, v2)' in test_vals and len(test_vals) == 2


def test_register_autoloop():
	area = Area(name='test', interfaces=interfaces)
	test_vals = []

	@area.register
	def trigger_1():
		test_vals.append('t1')

	@area.register
	def trigger_2(value1, value2='v2'):
		test_vals.append('t2({}, {})'.format(value1, value2))

	area.autoloop(trigger='trigger_1')
	area.autoloop(trigger='trigger_2', parameters={'value1': 'v1'})
	area.proceed()

	assert 't1' in test_vals and 't2(v1, v2)' in test_vals and len(test_vals) == 2


def test_pulse():
	area = Area(name='test', interfaces=interfaces)
	test_vals = []

	@area.pulse
	def routine():
		test_vals.append('t1')

	area.proceed()
	area.proceed()

	assert test_vals == ['t1', 't1']


def test_alternation_process():
	area = Area(name='test', interfaces=interfaces)
	area.setup = lambda *args, **kwargs: None
	area.subscribe(clock_name='clock100', subscriptions=subscriptions)
	test_vals = []

	@area.alteration
	def f1():
		test_vals.append('unspecified')

	@area.alteration(source='area2')
	def f2():
		test_vals.append('area2')

	@area.alteration(source='area1', slot='area1-slot1')
	def f3():
		test_vals.append('area1')

	area.process(source='area2', message={})
	area.process(source='area1', message={}, slot='area1-slot1')
	area.process(source='area1', message={}, slot='area1-slot2')
	area.proceed()

	assert 'unspecified' in test_vals and 'area2' in test_vals and 'area1' in test_vals
	assert len(test_vals) == 3


def test_alternation_alter():
	area = Area(name='test', interfaces=interfaces)
	area.setup = lambda *args, **kwargs: None
	area.subscribe(clock_name='clock100', subscriptions=subscriptions)
	test_vals = []

	@area.alteration
	def f1():
		test_vals.append('unspecified')

	@area.alteration(source='area2')
	def f2():
		test_vals.append('area2')

	@area.alteration(source='area1', slot='area1-slot1')
	def f3():
		test_vals.append('area1')

	area.alter()
	area.alter(source='area2')
	area.alter(source='area1', slot='area1-slot1')
	area.proceed()

	assert 'unspecified' in test_vals and 'area2' in test_vals and 'area1' in test_vals
	assert len(test_vals) == 3
