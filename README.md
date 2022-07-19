# o2r meta

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2203843.svg)](https://doi.org/10.5281/zenodo.2203843) [![SWH](https://archive.softwareheritage.org/badge/swh:1:dir:e2528f972e275208b6259a70f514b6bd83da2c87/)](https://archive.softwareheritage.org/swh:1:dir:e2528f972e275208b6259a70f514b6bd83da2c87;origin=https://github.com/o2r-project/o2r-meta.git;visit=swh:1:snp:2046e0128947faa0309da908e24d70eab898d6db;anchor=swh:1:rev:fb1a32f9819aef9ff37af4984048ab5b0a85e81f;path=//)

This is python library with a set of tools for extract-map-validate workflows as part of the o2r project:

0. schema & documentation of the o2r metadata
1. extract - collect meta information from files in a workspace
2. broker - translate metadata from o2r to third party schemas
3. validate - check if metadata set is valid to the schema
4. harvest - collect metadata from external sources via OAI-PMH
5. adding new parsers to the program

For their role within o2r, please refer to [o2r-architecture](https://github.com/o2r-project/architecture).

## Getting started

The full functionality of o2r-meta, including building the documentation and running the tests, requires Python >= 3.7.


### Installation from source code

```bash
git clone https://github.com/o2r-project/o2r-meta.git
cd o2r-meta
pip install -r requirements.txt
pip install -e .
```

**Common pitfall**: pygdal version has to match the system GDAL version. Verify the system GDAL version like this:

```bash
gdal-config --version
```

and, if necessary, force pygdal version to be installed as following:
```bash
pip install pygdal==2.4.2.10
```


### Installation with Docker

Another way of installation is provided by the Dockerfile. Build it like this:

```bash
git clone https://github.com/o2r-project/o2r-meta.git
cd o2r-meta
docker build -t meta .
```

And start a tool of o2r-meta like this:

```bash
docker run --rm -v $(pwd)/extract/tests/:/testdata:ro meta -debug extract -i /testdata -s
```

### Build the documentation

To familiarise with the use of o2r-meta and get access to the How-to guide, we recommend the installation of the documentation before using the tool.

```bash
cd docs/
pip install -r requirements-docs.txt
make html
```

This will create directory build/html under docs, which contains the documentation. The entry point is file index.html.


## How to cite

To cite this software please use

> _Nüst, Daniel, 2018. Reproducibility Service for Executable Research Compendia: Technical Specifications and Reference Implementation. Zenodo. doi:[10.5281/zenodo.2203843](https://doi.org/10.5281/zenodo.2203843)_

## License

o2r-meta is licensed under Apache License, Version 2.0, see file LICENSE. Copyright (C) 2016-2020 - o2r project.