FROM python:3.5-alpine
MAINTAINER <https://github.com/o2r-project>

WORKDIR /metavalidate
COPY metavalidate.py metavalidate.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "metavalidate.py"]