import re
from setuptools import setup, find_packages

from fccsmap import __version__

test_requirements = []
with open('requirements-test.txt') as f:
    test_requirements = [r for r in f.read().splitlines()]

setup(
    name='fccsmap',
    version=__version__,
    author='Joel Dubowy',
    license='MIT',
    author_email='jdubowy@gmail.com',
    packages=find_packages(),
    scripts=[
        'bin/fccsmap'
    ],
    package_data={
        'fccsmap': ['data/*.nc']
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Operating System :: POSIX",
        "Operating System :: MacOS"
    ],
    url='https://github.com/pnwairfire/fccsmap/',
    description='.',
    install_requires=[
        "pyairfire==0.6.14",
        "gdal==1.11.2",
        "numpy==1.8.0",
        "shapely==1.5.7",
        "pyproj==1.9.4",
        "rasterstats==0.6.2"
    ],
    dependency_links=[
    "https://github.com/pnwairfire/pyairfire/archive/v0.6.14.zip#egg=pyairfire-0.6.14"
    ],
    tests_require=test_requirements
)
