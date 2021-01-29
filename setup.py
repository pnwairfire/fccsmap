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
        "Programming Language :: Python :: 3.8",
        "Operating System :: POSIX",
        "Operating System :: MacOS"
    ],
    url='https://github.com/pnwairfire/fccsmap/',
    description='supports the look-up of FCCS fuelbed information by lat/lng or vector geo spatial data.',
    install_requires=[
        "afscripting>=2.0.0",
        # Note: numpy and gdal must now be installed manually beforehand
        "shapely==1.7.1",
        "pyproj==3.0.0.post1",
        "rasterstats==0.15.0"
    ],
    dependency_links=[
        "https://pypi.airfire.org/simple/afscripting/",
    ],
    tests_require=test_requirements
)
