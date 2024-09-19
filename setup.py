from setuptools import setup, find_packages

from fccsmap import __version__

test_requirements = []
with open('requirements-test.txt') as f:
    test_requirements = [r for r in f.read().splitlines()]

setup(
    name='fccsmap',
    version=__version__,
    author='Joel Dubowy',
    license='GPLv3+',
    author_email='jdubowy@gmail.com',
    packages=find_packages(),
    scripts=[
        'bin/fccsmap',
        'bin/fccscreatetiles'
    ],
    package_data={
        'fccsmap': ['data/*.nc']
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX",
        "Operating System :: MacOS"
    ],
    url='https://github.com/pnwairfire/fccsmap/',
    description='supports the look-up of FCCS fuelbed information by lat/lng or vector geo spatial data.',
    install_requires=[
        "afscripting>=3.0.0,<4.0.0",
        "numpy==2.1.1",
        "shapely==2.0.6",
        "rasterstats==0.19.0",
        "GDAL==3.8.4",
        "geopandas==1.0.1",
        "matplotlib==3.9.2",
        "rioxarray==0.17.0"
    ],
    dependency_links=[
        "https://pypi.airfire.org/simple/afscripting/",
    ],
    tests_require=test_requirements
)
