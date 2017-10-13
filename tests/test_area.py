import json

import pytest

from pabiana import Area, load_interfaces

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


def test_register():
	area = Area('test')
	result = area.register(test_register)
	assert result is test_register
	assert len(area.triggers) == 1
	assert 'test_register' in area.triggers
	assert area.triggers['test_register'] is test_register


def test_alteration():
	area = Area('test')
	
	@area.alteration
	def test1():
		pass
	
	@area.alteration(area_name='test-area1')
	def test2():
		pass
	
	@area.alteration(area_name='test-area2', slot='test-slot')
	def test3():
		pass
	
	assert area.processors[None] is test1
	assert area.processors['test-area1'][None] is test2
	assert area.processors['test-area2']['test-slot'] is test3


def test_pulse():
	area = Area('test')
	result = area.pulse(test_pulse)
	assert result is test_pulse
	assert area.pulse_function is test_pulse


def test_clock_callback():
	area = Area('test')
	test_value = ''
	
	def test1(value):
		nonlocal test_value
		test_value += value
	
	def test2(value):
		nonlocal test_value
		test_value += value
	
	area.demand[test1] = {'value': 'test1'}
	area.demand_loop[test2] = {'value': 'test2'}
	area.clock_callback()
	assert test_value == 'test1test2' or test_value == 'test2test1'


def test_setup_1():
	area = Area('test')
	area.setup_receiver = lambda *args, **kwargs: None
	area.setup_subscribers = lambda *args, **kwargs: None
	
	def test1(area_name, slot):
		area.context[area_name][slot] = 'test1'
	
	def test2(area_name, slot, message):
		area.context[area_name][slot] = 'test2'
	
	subs = {
		'area1': ['slot1'],
		'area2': {'slot1': {'init': test1, 'parser': test2}, 'slot2': None}
	}
	area.setup('clock100', '001', subs)
	assert area.clock_name == 'clock100'
	assert area.clock_slot == '001'
	assert len(area.context['area1']['slot1']) == 0
	assert len(area.context['area2']['slot2']) == 0
	assert area.context['area2']['slot1'] == 'test1'
	assert area.parsers['area1']['slot1'] == area.imprint
	assert area.parsers['area2']['slot2'] == area.imprint
	assert area.parsers['area2']['slot1'] == test2


def test_setup_2():
	area = Area('test')
	area.setup_receiver = lambda *args, **kwargs: None
	area.setup_subscribers = lambda *args, **kwargs: None
	area.setup('clock101', '002')
	assert area.clock_name == 'clock101'
	assert area.clock_slot == '002'
	assert len(area.context) == 0
	assert len(area.parsers) == 0


def test_autoloop_2():
	area = Area('test')
	assert len(area.demand_loop) == 0
	area.autoloop(test_autoloop_2, {'value': 5})
	assert len(area.demand_loop) == 1
	assert test_autoloop_2 in area.demand_loop
	assert area.demand_loop[test_autoloop_2]['value'] == 5
