import importlib
import logging
import multiprocessing as mp
import os
import signal
from os import path

import pip

from . import repo
from .templates import create_director, create_clock
from .utils import read_interfaces


def setup_logging():
	logging.basicConfig(
		format='%(asctime)s %(levelname)s %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
		level=logging.INFO
	)


def resolve(*args):
	result = []
	for module_area_name in args:
		module_name, area_name = module_area_name.split(':')
		base_path = os.getcwd()
		intf_path = path.join(repo['base-path'], 'interfaces.json')
		req_path = path.join(repo['base-path'], module_name, 'requirements.txt')
		result.append([module_name, area_name, base_path, intf_path, req_path])
	return result


def main(*args):
	setup_logging()
	
	args = list(args)
	stop_pip = False
	if '-X' in args:
		stop_pip = True
		args.remove('-X')
	if '-C' in args:
		args.append('def_clock:clock')
		args.remove('-C')
	elif '-D' in args:
		args.append('def_director:clock')
		args.remove('-C')
	
	areas = resolve(args)
	
	for i in range(len(areas)):
		module_name, area_name, base_path, intf_path, req_path = areas[i]
		areas[i][3] = read_interfaces(intf_path)
		if not stop_pip and path.isfile(req_path):
			pip.main(['install', '-U', '-r', req_path])
	
	if len(areas) > 1:
		pids = []
		signal.signal(signal.SIGINT, lambda *args, **kwargs: None)
		mp.set_start_method('spawn')
		for area in areas:
			module_name, area_name, base_path, interfaces, req_path = area
			process = mp.Process(target=run, args=(module_name, area_name, interfaces, base_path))
			process.start()
			pids.append(process.pid)
		logging.info('Spawned processes: %s', pids)
	else:
		module_name, area_name, base_path, interfaces, req_path = areas[0]
		run(module_name, area_name, interfaces, base_path)


def run(module_name, area_name, interfaces, base_path):
	repo['module-name'] = module_name
	repo['area-name'] = area_name
	repo['interfaces'] = interfaces
	repo['base-path'] = base_path
	
	try:
		mod = importlib.import_module(module_name)
	except ImportError:
		setup_logging()
		if module_name == 'def_director' and area_name == 'clock':
			area = create_director(name=area_name, interfaces=repo['interfaces'])
			area.run()
			return
		if module_name == 'def_clock' and area_name == 'clock':
			area = create_clock(name=area_name, interfaces=repo['interfaces'])
			area.run()
			return
		else:
			raise
	
	if hasattr(mod, 'premise'):
		mod.premise()
	
	if hasattr(mod, 'area'):
		if hasattr(mod, 'config'):
			params = {
				'clock_name': mod.config.get('clock-name'),
				'clock_slots': mod.config.get('clock-slots')
			}
			if mod.config.get('subscriptions') is not None:
				params['subscriptions'] = mod.config['subscriptions']
			mod.area.subscribe(**params)
			if 'context-values' in mod.config:
				mod.area.context.update(mod.config['context-values'])
		mod.area.run()
	
	elif hasattr(mod, 'runner'):
		if hasattr(mod.runner, 'setup'):
			params = {}
			if hasattr(mod, 'config'):
				params.update(mod.config)
			mod.runner.setup(**params)
		mod.runner.run()

