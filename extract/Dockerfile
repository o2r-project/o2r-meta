FROM python:3-onbuild
MAINTAINER m-schu <https://github.com/m-schu>

WORKDIR /metaextract
COPY metaextract.py metaextract.py
COPY list_crantop100.txt list_crantop100.txt
COPY list_geopack.txt list_geopack.txt

ENTRYPOINT ["python", "metaextract.py"]