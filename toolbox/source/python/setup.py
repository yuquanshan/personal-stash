#!/usr/bin/python

from distutils.core import setup

setup(name='ada',
      version='1.0',
      description='Ada: the script that can answer questions regarding date',
      author='yuquanshan',
      packages = ['ada'],
      package_data={'ada': ['data/*.dat', 'data/*.txt']},
      scripts=['bin/ada']
     )
