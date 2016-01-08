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

RUN apt-get update
RUN apt-get install -y g++ gcc make python python-dev python-pip libnetcdf-dev proj
RUN pip install --upgrade pip
RUN pip install numpy==1.8.0
RUN apt-get install -y libgdal1-1.7.0
#RUN pip install gdal==1.7.0
RUN apt-get install -y python-gdal libxml2-dev libxslt1-dev
