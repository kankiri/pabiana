import importlib
import logging
import multiprocessing as mp
import os
import signal
from os import path

import pip

from . import load_interfaces, repo


def main(*args):
	stop_pip = False
	if '-X' in args:
		stop_pip = True
	if len(args)-int(stop_pip) > 1:
		logging.info('Starting %s processes', len(args))
		signal.signal(signal.SIGINT, lambda *args, **kwargs: None)
		mp.set_start_method('spawn')
		for module_area_name in args:
			process = mp.Process(target=run, args=(module_area_name, stop_pip))
			process.start()
	else:
		run(*args, stop_pip)


def run(module_area_name, stop_pip=False):
	module_name, area_name = module_area_name.split(':')
	repo['base-path'] = os.getcwd()
	repo['module-name'] = module_name
	repo['area-name'] = area_name
	
	intf_path = path.join(repo['base-path'], 'interfaces.json')
	if path.isfile(intf_path):
		load_interfaces(intf_path)
	
	req_path = path.join(repo['base-path'], module_name, 'requirements.txt')
	if not stop_pip and path.isfile(req_path):
		pip.main(['install', '--upgrade', '-r', req_path])
	
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
				params.update(mod.config)
			mod.runner.setup(**params)
		mod.runner.run()

