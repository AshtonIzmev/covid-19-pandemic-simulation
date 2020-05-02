# -*- coding: utf-8 -*-

# Learn more: https://github.com/AshtonIzmev/covid-19-pandemic-simulation/setup.py
from setuptools import setup, find_packages

setup(
    name='pandemic-simulation',
    version='0.1.3',
    description='"Life simulation" of a SEIR inspired model to better understand pandemic using python',
    long_description_content_type="text/plain",
    long_description="Check https://github.com/AshtonIzmev/covid-19-pandemic-simulation/blob/master/README.md",
    url='https://github.com/AshtonIzmev',
    license="MIT License",
    packages=find_packages(exclude=('tests', 'docs')),
    python_requires='>=3.6',
    install_requires=['pandas', 'scipy', 'numpy', 'argparse', 'sklearn', 'matplotlib', 'seaborn']
)


