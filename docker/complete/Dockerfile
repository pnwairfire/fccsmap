# Container to run fccsmap
FROM fccsmap-base

RUN pip install --no-binary gdal --trusted-host pypi.smoke.airfire.org -i http://pypi.smoke.airfire.org/simple fccsmap

### To install from github instead of from AirFire's pypi server
#RUN pip install --no-binary gdal  --trusted-host pypi.smoke.airfire.org -i http://pypi.smoke.airfire.org/simple   https://github.com/pnwairfire/fccsmap/archive/branch-name.tar.gz

CMD ["fccsmap", "-h"]
