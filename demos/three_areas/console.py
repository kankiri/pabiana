#!/usr/bin/env python3

import json
import logging

from pabiana.area import create_publisher, trigger

NAME = 'console'
publisher = None


def main():
	try:
		while True:
			s = input('--> ').lower()
			if 'quit' in s:
				raise KeyboardInterrupt
			if 'good' in s and 'night' in s:
				data = {'signal': 'sleep'}
			elif 'morning' in s or 'awake' in s:
				data = {'signal': 'awake'}
			elif 'away' in s:
				data = {'signal': 'away'}
			elif 'home' in s:
				data = {'signal': 'home'}
			elif 'update' in s:
				data = {'signal': 'update'}
			else:
				data = {}
			if data:
				publisher.send_multipart(['input'.encode('utf-8'), json.dumps(data).encode('utf-8')])
	except KeyboardInterrupt:
		trigger('association', 'shutdown')
		trigger('smarthome', 'shutdown')
		trigger('getter', 'shutdown')


if __name__ == '__main__':
	logging.basicConfig(
		format='%(asctime)s %(levelname)s %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
		level=logging.DEBUG
	)
	
	publisher = create_publisher(own_name=NAME, host='0.0.0.0')
	main()