import os.path
import codecs
import re

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='pyMeterBus',
    description='Python implementation of the Meter-Bus protocol',
    version=find_version("meterbus", "__init__.py"),
    url='https://github.com/ganehag/pyMeterBus',
    author='Mikael Ganehag Brorsson',
    author_email='mikael.brorsson@gmail.com',
    license="BSD-3-Clause",

    python_requires='>=3.6',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries'
    ],

    packages=find_packages(),

    install_requires=[
        'pyaml',
        'pycryptodome',
        'pyserial',
        'simplejson'
    ],

    entry_points={
      'console_scripts': [
          'mbus-serial-scan-primary = meterbus.tools:serial_scan_primary',
          'mbus-serial-scan-secondary = meterbus.tools:serial_scan_secondary',
          'mbus-serial-req-single = meterbus.tools:serial_request_single',
          'mbus-serial-req-multi = meterbus.tools:serial_request_multi'
      ]
    }
)
