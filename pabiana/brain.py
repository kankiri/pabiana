import logging
import importlib
import multiprocessing as mp
import os
from os import path
import pip
import signal

from . import load_interfaces, repo


def main(*args):
	if len(args) > 2:
		logging.info('Starting %s processes', len(args)/2.0)
		signal.signal(signal.SIGINT, lambda *args, **kwargs: None)
		mp.set_start_method('spawn')
		for module_name, area_name in zip(args[0::2], args[1::2]):
			process = mp.Process(target=run, args=(module_name, area_name))
			process.start()
	else:
		run(*args)


def run(module_name, area_name):
	intf_path = path.join(os.getcwd(), 'interfaces.json')
	if path.isfile(intf_path):
		load_interfaces(intf_path)

	req_path = path.join(os.getcwd(), module_name, 'requirements.txt')
	if path.isfile(req_path):
		pip.main(['install', '--upgrade', '-r', req_path])
	
	repo['area-name'] = area_name
	mod = importlib.import_module(module_name)
	
	if hasattr(mod, 'setup'):
		mod.setup()
	
	if hasattr(mod, 'area'):
		if hasattr(mod, 'config'):
			params = {'clock_name': mod.config['clock-name']}
			if 'clock-slot' in mod.config:
				if mod.config['clock-slot'] is not None:
					params['clock_slot'] = mod.config['clock-slot']
			if 'subscriptions' in mod.config:
				if mod.config['subscriptions'] is not None:
					params['subscriptions'] = mod.config['subscriptions']
			mod.area.setup(**params)
			if 'context-values' in mod.config:
				mod.area.context.update(mod.config['context-values'])
		mod.area.run()
	
	elif hasattr(mod, 'clock'):
		if hasattr(mod, 'config'):
			params = {}
			if 'timeout' in mod.config:
				if mod.config['timeout'] is not None:
					params['timeout'] = mod.config['timeout']
			if 'use-template' in mod.config:
				if mod.config['use-template'] is not None:
					params['use_template'] = mod.config['use-template']
			mod.clock.setup(**params)
		mod.clock.run()
	
	elif hasattr(mod, 'runner'):
		if hasattr(mod.runner, 'setup'):
			params = {}
			if hasattr(mod, 'config'):
				params.update(config)
			mod.runner.setup(**params)
		mod.runner.run()

