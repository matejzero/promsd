# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

setup(
    name='promsd',
    version='0.0.1',
    description='Prometheus service discovery',
    long_description=readme,
    author='Matej Zerovnik',
    author_email='matej@zunaj.si',
    url='https://github.com/matejzero/promsd',
    #license=license,
    packages=find_packages(exclude=('tests'))
)
