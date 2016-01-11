# Container with all of fccsmap's dependencies, to be used
# as dev environment and as base for container in which fccsmap
# is to be installed.
#
# Example of how to use in dev environment, assuming you've built the
# image with tag 'fccsmap-base':
#
#   docker run --name fccsmap-base \
#      -v /path/to/fccsmap/repo/:/fccsmap/ -w /fccsmap/ \
#      fccsmap-base pip install --no-binary gdal \
#      --trusted-host pypi.smoke.airfire.org -r requirements.txt
#   docker commit fccsmap-base fccsmap-base
#   docker run -v /path/to/fccsmap/repo/:/fccsmap/ \
#      fccsmap-base /fccsmap/bin/bsp ...

FROM ubuntu:12.04

MAINTAINER Joel Dubowy

# Install base dependencies
RUN apt-get update \
    && apt-get install -y \
        g++ \
        gcc \
        make \
        python \
        python-dev \
        python-pip \
    && apt-get install -y \
        libnetcdf-dev \
        proj \
    && pip install --upgrade pip

# Install numpy and gdal
# Note: numpy 1.8.0 needs to be installed before libgdal
RUN pip install \
        numpy==1.8.0 \
    && apt-get install -y \
        libgdal1-1.7.0 \
    && apt-get install -y \
        python-gdal \
    && apt-get install -y \
        libxml2-dev \
        libxslt1-dev
