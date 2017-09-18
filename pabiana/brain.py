import importlib
import os
from os import path
import pip

from . import load_interfaces, repo

def main(module_name, area_name):
	req_path = path.join(os.getcwd(), module_name, 'requirements.txt')
	if os.path.isfile(req_path):
		pip.main(['install', '--upgrade', '-r', req_path])
	
	repo['area-name'] = area_name
	mod = importlib.import_module(module_name)
	
	if hasattr(mod, 'area'):
		if hasattr(mod, 'config'):
			params = {'clock_name': mod.config['clock-name']}
			if 'clock-slot' in mod.config:
				if mod.config['clock-slot'] is not None:
					params['clock_slot'] = mod.config['clock-slot']
			if 'subscriptions' in mod.config:
				if mod.config['subscriptions'] is not None:
					params['subscriptions'] = mod.config['subscriptions']
			mod.area.setup(params**)
			if 'context-values' in mod.config:
				mod.area.context.update(mod.config['context-values'])
		mod.area.run()
	
	elif hasattr(mod, 'clock'):
		mod.clock.run()
