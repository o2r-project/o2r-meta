# (C) Copyright 2017 o2r project. https://o2r.info
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
FROM alpine:3.6

# Python, based on frolvlad/alpine-python3
RUN apk add --no-cache \
  python3 \
  && python3 -m ensurepip \
  && rm -r /usr/lib/python*/ensurepip \
  && pip3 install --upgrade pip setuptools \
  && if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi \
  && rm -r /root/.cache

RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" > /etc/apk/repositories \
  && echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
  && echo "http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories

RUN apk add --update-cache \
    python3-dev \
    g++ \
    gcc \
    libxml2-dev \
    libxslt-dev \
    gdal \
    gdal-dev \
    py-gdal \
    git

WORKDIR /o2r-meta
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY broker broker
COPY extract extract
COPY harvest harvest
COPY helpers helpers
COPY parsers parsers
COPY schema schema
COPY validate validate
COPY o2rmeta.py o2rmeta.py

RUN apk del git py-pip

# Metadata http://label-schema.org/rc1/
LABEL maintainer="o2r-project <https://o2r.info>" \
  org.label-schema.vendor="o2r project" \
  org.label-schema.url="http://o2r.info" \
  org.label-schema.name="o2r meta" \
  org.label-schema.description="Metadata toolsuite for an extract-map-validate workflow supporting ERC" \    
  org.label-schema.version=$VERSION \
  org.label-schema.vcs-url=$VCS_URL \
  org.label-schema.vcs-ref=$VCS_REF \
  org.label-schema.build-date=$BUILD_DATE \
  org.label-schema.docker.schema-version="rc1" \
  info.o2r.meta.version=$META_VERSION

ENTRYPOINT ["python3", "/o2r-meta/o2rmeta.py"]