FROM python:3.5-alpine
MAINTAINER <https://github.com/o2r-project>

WORKDIR /metaextract
COPY metaextract.py metaextract.py
COPY list_crantop100.txt list_crantop100.txt
COPY list_geosci.txt list_geosci.txt
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "metaextract.py"]