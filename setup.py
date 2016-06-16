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
        'bin/fccsmap'
    ],
    package_data={
        'fccsmap': ['data/*.nc']
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 2",
        "Operating System :: POSIX",
        "Operating System :: MacOS"
    ],
    url='https://github.com/pnwairfire/fccsmap/',
    description='supports the look-up of FCCS fuelbed information by lat/lng or vector geo spatial data.',
    install_requires=[
        "pyairfire>=1.1.1",
        "numpy==1.8.0",
        # Note: gdal must now be installed manually beforehand
        #"pygdal==1.11.2.1",
        #"gdal==1.11.2",
        "shapely==1.5.16",
        "pyproj==1.9.5.1",
        "rasterstats==0.10.3"
    ],
    dependency_links=[
        "https://pypi.smoke.airfire.org/simple/pyairfire/"
    ],
    tests_require=test_requirements
)
