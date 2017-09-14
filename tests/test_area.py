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
	result = area.alteration(test_alteration)
	assert result is test_alteration
	assert area.alt_function is test_alteration


def test_pulse():
	area = Area('test')
	result = area.pulse(test_pulse)
	assert result is test_pulse
	assert area.pulse_function is test_pulse


def test_scheduling():
	area = Area('test')
	test_value = ''
	
	def old():
		nonlocal test_value
		test_value += 'old'
	
	def new():
		nonlocal test_value
		test_value += 'new'
	
	area.call_triggers = old
	result = area.scheduling(new)
	assert result is new
	area.call_triggers()
	assert test_value == 'newold'


def test_call_triggers():
	area = Area('test')
	test_value = ''
	
	def test1(value):
		nonlocal test_value
		test_value += value
	
	def test2(value):
		nonlocal test_value
		test_value += value
	
	area.demand[test1] = {'value': 'test1'}
	area.loop[test2] = {'value': 'test2'}
	area.call_triggers()
	assert test_value == 'test1test2' or test_value == 'test2test1'


def test_setup_1():
	area = Area('test')
	area.setup_receiver = lambda *args, **kwargs: None
	area.setup_subscibers = lambda *args, **kwargs: None
	
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
	area.setup_subscibers = lambda *args, **kwargs: None
	area.setup('clock101', '002')
	assert area.clock_name == 'clock101'
	assert area.clock_slot == '002'
	assert len(area.context) == 0
	assert len(area.parsers) == 0


def test_autoloop_1():
	area = Area('test')
	assert not area.received
	area.autoloop()
	assert area.received is True


def test_autoloop_2():
	area = Area('test')
	assert len(area.loop) == 0
	area.autoloop(test_autoloop_2, {'value': 5})
	assert len(area.loop) == 1
	assert test_autoloop_2 in area.loop
	assert area.loop[test_autoloop_2]['value'] == 5


def test_area():
	area = Area('test')
	area.setup_receiver = lambda *args, **kwargs: None
	area.setup_subscibers = lambda *args, **kwargs: None
	
	test_value = ''
	
	@area.register
	def demand_me_1(value):
		nonlocal test_value
		test_value += value
	
	@area.register
	def demand_me_2(value):
		nonlocal test_value
		test_value += value
	
	@area.alteration
	def forward():
		nonlocal test_value
		test_value += 'forward'
	
	@area.pulse
	def everytime():
		nonlocal test_value
		test_value += 'everytime'
	
	@area.scheduling
	def scheduler():
		nonlocal test_value
		test_value += 'scheduler'
	
	def parser(area_name, slot, message):
		nonlocal test_value
		test_value += area_name
	
	subs = {
		'area1': {'slot1': {'init': lambda *args, **kwargs: None, 'parser': parser}},
		'area2': {
			'slot1': {'init': area.init_slot, 'parser': parser},
			'slot2': {'init': area.init_slot, 'parser': parser}
		}
	}
	area.setup('clock100', '001', subs)
	
	area.autoloop(demand_me_1, {'value': 'dm_1_value'})
	area.subscriber_message('clock100', '001', {})
	assert test_value == 'scheduler' + 'dm_1_value' + 'everytime'
	test_value = ''
	
	area.receiver_message('demand_me_2', {'value': 'dm_2_value'})
	area.subscriber_message('clock100', '001', {})
	assert test_value == 'scheduler' + 'dm_2_value' + 'everytime'
	test_value = ''
	
	area.autoloop(demand_me_2, {'value': 'dm_2_value'})
	area.subscriber_message('area1', 'slot1', {'value': 'area1_value'})
	area.receiver_message('demand_me_1', {'value': 'dm_1_value'})
	assert test_value == 'area1'
	area.subscriber_message('clock100', '001', {})
	assert test_value == 'area1' + 'scheduler' + 'dm_1_value' + 'dm_2_value' + 'forward' + 'everytime' \
		or test_value == 'area1' + 'scheduler' + 'dm_2_value' + 'dm_1_value' + 'forward' + 'everytime'

