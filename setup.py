# -*- coding: utf-8 -*-

# Learn more: https://github.com/AshtonIzmev/covid-19-pandemic-simulation/setup.py
from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pandemic-simulator',
    version='0.1.0',
    description='"Life simulation" of a SEIR inspired model to better understand pandemic using python',
    long_description=readme,
    author='Issam El Alaoui',
    author_email='issam.github@issam.ma',
    url='https://github.com/AshtonIzmev',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)