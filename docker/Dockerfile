# Server to run fccsmap
FROM ubuntu:12.04

MAINTAINER Joel Dubowy

RUN apt-get update
RUN apt-get install -y g++ gcc make python python-dev python-pip libnetcdf-dev proj
RUN pip install --upgrade pip
RUN pip install numpy==1.8.0
RUN apt-get install -y libgdal1-1.7.0
#RUN pip install gdal==1.7.0
RUN apt-get install -y python-gdal libxml2-dev libxslt1-dev

RUN pip install --no-binary gdal --trusted-host pypi.smoke.airfire.org -i http://pypi.smoke.airfire.org/simple fccsmap

### To install from github instead of from AirFire's pypi server
#RUN pip install --no-binary gdal  --trusted-host pypi.smoke.airfire.org -i http://pypi.smoke.airfire.org/simple   https://github.com/pnwairfire/fccsmap/archive/branch-name.tar.gz

CMD ["fccsmap", "-h"]
