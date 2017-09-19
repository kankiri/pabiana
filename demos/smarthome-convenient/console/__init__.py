import signal
from pabiana import Node, repo, trigger
from .setup import setup


class Runner(Node):
	def run(self):
		self.goon = True
		signal.signal(signal.SIGINT, self.stop)
		try:
			while self.goon:
				s = input('--> ').lower()
				if 'quit' in s:
					self.stop()
				if 'open' in s:
					self.publish({'signal': 'window-open'}, slot='input')
				elif 'close' in s:
					self.publish({'signal': 'window-close'}, slot='input')
		finally:
			trigger('association', 'exit')
			trigger('smarthome', 'exit')
			trigger('weather', 'exit')
			trigger('clock', 'exit')


runner = Runner(repo['area-name'], host='0.0.0.0')

