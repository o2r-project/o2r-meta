FROM python:3.5-alpine
MAINTAINER <https://github.com/o2r-project>

WORKDIR /metabroker
COPY metabroker.py metabroker.py
COPY mappings mappings
COPY tests tests
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "metabroker.py"]