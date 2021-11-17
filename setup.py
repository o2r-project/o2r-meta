
import setuptools
from o2rmeta.lib import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="o2r-meta",
    version=__version__,
    author="o2r-project",
    author_email="o2r.team@uni-muenster.de",
    description="A package to extract metadata from files and directories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/o2r-project/o2r-meta",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['PyYAML',
    'dicttoxml',
    'guess_language-spirit',
    'jsonschema',
    'lxml',
    'pygeoj',
    'python-dateutil',
    'requests',
    'netCDF4',
    'StringDist',
    'filelock'
    ],
    entry_points={
        "console_scripts": [
            "o2r-meta = o2rmeta.o2rmeta:main",
        ]
    },
)
