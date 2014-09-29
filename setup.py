from setuptools import setup, find_packages

setup(name="meterbus",
      version="0.1dev",
      description="Python implementation of the Meter-Bus protocol",
      author="Mikael Ganehag Brorsson",
      author_email="mikael.brorsson@gmail.com",
      packages=find_packages(exclude=['tests', 'mbus_ref']),
      install_requires=["enum34"],
)
