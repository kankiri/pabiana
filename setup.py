from os import path
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

here = path.abspath(path.dirname(__file__))

# copied from https://docs.pytest.org/en/latest/goodpractices.html
class PyTest(TestCommand):
	user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

	def initialize_options(self):
		TestCommand.initialize_options(self)
		self.pytest_args = []

	def run_tests(self):
		import shlex
		#import here, cause outside the eggs aren't loaded
		import pytest
		errno = pytest.main(shlex.split(self.pytest_args))
		sys.exit(errno)


setup(
	name='Pabiana',
	version='0.0.1',
	packages=find_packages(),
	install_requires=['pyzmq'],
	tests_require=['pytest'],
	cmdclass = {'test': PyTest}
)
