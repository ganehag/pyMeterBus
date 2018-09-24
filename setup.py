from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('VERSION') as f:
    version = f.readline()

with open('LICENSE') as f:
    license = f.readline()

setup(name='pyMeterBus',
      description='Python implementation of the Meter-Bus protocol',
      long_description=readme,
      long_description_content_type='text/markdown',
      version=version,
      url='https://github.com/ganehag/pyMeterBus',
      author='Mikael Ganehag Brorsson',
      author_email='mikael.brorsson@gmail.com',
      license=license,

      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development :: Libraries'
      ],

#      packages=find_packages(exclude=['tests', 'mbus_ref']),
      packages=['meterbus'],
      install_requires=['enum34', 'simplejson', 'pyaml',
                        'pyserial', 'future', 'pycryptodome'],
)
