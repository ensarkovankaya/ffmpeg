#!/usr/bin/env python

from distutils.core import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(name='Ffmpeg Command Generator',
      version='1.0',
      description='Generates ffmpeg commands programmatically with python.',
      long_description=long_description,
      author='Ensar Kovankaya',
      author_email='ensar@kovankaya.com',
      url='https://github.com/ensarkovankaya/ffmpeg',
      packages=['utils', 'generator', 'tests'],
      install_requires=['django']
      )
