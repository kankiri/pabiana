from pathlib import Path
from setuptools import setup, find_packages

root = Path(__file__).parent
version = root / 'VERSION.txt'
requirements = root / 'requirements.txt'
readme = root / 'README.md'

setup(
	name='Pabiana',
	version=version.read_text('utf-8').strip(),
	packages=find_packages(),
	install_requires=requirements.read_text('utf-8').split('\n'),
	setup_requires=['pytest-runner >= 4.4'],
	tests_require=['pytest >= 4.4.1'],
	zip_safe=False,
	
	url='https://github.com/kankiri/pabiana',
	author='Alexander Schöberl',
	author_email='alexander.schoeberl@gmail.com',
	description='A minimalistic framework to build distributed cognitive applications based on ØMQ',
	long_description=readme.read_text('utf-8'),
	long_description_content_type='text/markdown',
	keywords=['framework', 'cognitive', 'distributed', 'ØMQ'],
	license='MIT'
)
