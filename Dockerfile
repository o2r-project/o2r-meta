FROM frolvlad/alpine-python3
MAINTAINER <https://github.com/o2r-project>

RUN apk add python3-dev g++ gcc libxml2-dev libxslt-dev --update-cache
RUN apk add gdal gdal-dev py-gdal --update-cache --repository http://nl.alpinelinux.org/alpine/edge/testing
RUN apk add git
RUN git clone --depth 1 -b master https://github.com/o2r-project/o2r-meta.git
WORKDIR /o2r-meta
RUN pip install -r requirements.txt
RUN apk del git py-pip

ENTRYPOINT ["python3"]