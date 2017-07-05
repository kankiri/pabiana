import json

import pytest

from pabiana import area
from pabiana import node
from pabiana.area import alteration, autoloop, call_triggers, load_interfaces, pulse, register, rslv, scheduling, subscribe

ifs_path = None


@pytest.fixture(scope='module', autouse=True)
def interfaces_file(tmpdir_factory):
	global ifs_path
	ifs = {
		'test-pub': {
			'ip': '127.0.0.1',
			'port': 8281
		},
		'test-rcv': {
			'ip': '127.0.0.1',
			'port': 8282
		}
	}
	ifs_path = str(tmpdir_factory.mktemp('ifs-area').join('interfaces.json'))
	with open(ifs_path, 'w') as f:
		json.dump(ifs, f)


def test_register():
	area._triggers.clear()
	result = register(test_register)
	assert result is test_register
	assert len(area._triggers) == 1
	assert 'test_register' in area._triggers
	assert area._triggers['test_register'] is test_register
	area._triggers.clear()


def test_alteration():
	result = alteration(test_alteration)
	assert result is test_alteration
	assert area._alt_function is test_alteration
	area._alt_function = None


def test_pulse():
	result = pulse(test_pulse)
	assert result is test_pulse
	assert area._pulse_function is test_pulse
	area._pulse_function = None


def test_scheduling():
	test_value = ''
	
	def old():
		nonlocal test_value
		test_value += 'old'
	
	def new():
		nonlocal test_value
		test_value += 'new'
	
	restore = area.call_triggers
	area.call_triggers = old
	result = scheduling(new)
	assert result is new
	area.call_triggers()
	assert test_value == 'newold'
	area.call_triggers = restore


def test_call_triggers():
	area.demand.clear()
	test_value = ''
	
	def test1(value):
		nonlocal test_value
		test_value += value
	
	def test2(value):
		nonlocal test_value
		test_value += value
	
	area.demand[test1] = {'value': 'test1'}
	area.demand[test2] = {'value': 'test2'}
	call_triggers()
	assert test_value == 'test1test2' or test_value == 'test2test1'
	area.demand.clear()


def test_subscribe():
	node.subscriptions.clear()
	sub1 = ('area1', 'slot2')
	sub2 = ('area2', 'slot1')
	subscribe([sub1, sub2], 'area1', 'slot1')
	assert area._pulse_name == 'area1'
	assert area._pulse_slot == 'slot1'
	assert len(node.subscriptions) == 3
	assert sub1 in node.subscriptions
	assert sub2 in node.subscriptions
	assert node.subscriber_cb == area._subscriber_callback
	assert node.trigger_cb == area._trigger_callback
	node.subscriptions.clear()
	node.subscriber_cb = None
	node.trigger_cb = None


def test_autoloop():
	area._received = False
	autoloop()
	assert area._received
	area._received = False
	
	area._loop.clear()
	autoloop(test_autoloop, {'value': 5})
	assert len(area._loop) == 1
	assert test_autoloop in area._loop
	assert area._loop[test_autoloop]['value'] == 5
	area._loop.clear()


def test_load_interfaces():
	node.interfaces.clear()
	load_interfaces(ifs_path)
	assert len(node.interfaces) == 2
	assert node.interfaces['test-pub']['port'] == 8281
	assert node.interfaces['test-rcv']['ip'] == '127.0.0.1'
	node.interfaces.clear()


def test_rslv():
	node.interfaces.clear()
	node.interfaces['area1'] = {'ip': '127.0.0.1', 'port': 54316}
	node.interfaces['area2'] = {'ip': '127.0.0.1', 'port': 54317}
	result = rslv('area1')
	assert result['ip'] == '127.0.0.1'
	assert result['port'] == 54316
	node.interfaces.clear()
