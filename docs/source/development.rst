Development
===========

Notes for developers of ``o2r-meta``. The current development version is in the branch dev.

Environment
-----------

All commands in this file assume you work in a virtual environment created with virtualenvwrapper_ as follows (please keep up to date!):

.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/en/latest/install.html

::

    # pip install virtualenvwrapper

    # Add to .bashrc:
    # export WORKON_HOME=$HOME/.virtualenvs
    # source ~/.local/bin/virtualenvwrapper.sh

    # Where are my virtual envs stored?
    # echo $WORKON_HOME

    # Create environment using Python 3
    #mkvirtualenv -p $(which python3) o2r-meta

    # Activate env
    workon o2r-meta

    # Deactivate env
    deactivate


Adding new parsers to the extractor tool
-----------------------------------------

The extractor tool uses Python classes as parser modules. Each parser can process specific formats and the full list of supported file formats can be retrieved via CLI (see above).

In order to add a new custom parser, you have to write a parser class and add it to the parser directory.

Note that future versions of o2r-meta (:pr:`95`) might be able to register all parsers based on the files in the parsers directory. Until then it is necessary to register a new parser in the extractor script

The use of classes as parsers is currently implemented in a rather naïve way. However, in order to be able to take advantage of non static methods, all parsers are designed as classes already.

The general process of parsing is the following:

#.the parser accesses a target file, which was encountered by the extractor during a recursive scan of the target directory and identified based on the file extension.
#.the target file is read and processed by a specific parser
#.the results of the processing are written to a dictionary data structure that is globally known to the program; the structure of the data dictionary is implicitly defined in ``metaextract.py`` and can be seen in ``dummy.json``

Structure of your parser Python class
-------------------------------------

In this example we will call your new parser file ``parse_abc.py`` and the class in that file ``ParseAbc``.

Here is a commented template for your parser file:

::

	# Class name keyword to signal availability to importing files
	__all__ = ['ParseAbc']

	# Optionally import the o2r-meta helping functions if want to have access to them
	from helpers.helpers import *

	# Import further external modules you would need and also add them to the requirements.txt file!
	import myABC

	# If (some of) the formats you want to parse depend on a successful import of external modules, which might be missing, use the following structure to support as much formats as possible
	try:
	    from myABC import *
	    FORMATS = ['.abc']
	except ImportError as iexc:
	    FORMATS = []
	    availability_issues = str(iexc)

	# The identifying name of your parser
	ID = 'o2r meta abc parser'

	# Declare your class
	class ParseAbc:
	    # Required method to return the ID
	    @staticmethod
	    def get_id():
		return str(ID)

	    # Required method to return the available formats of this parser
	    @staticmethod
	    def get_formats():
		if not FORMATS:
		    # Status notes are available via the helpers module
		    status_note([__class__, ' unavailable (', str(availability_issues), ')'])
		return FORMATS

	    # Required method. This is the place for your actual parsing code
	    @staticmethod
	    def parse(**kwargs):
		is_debug = False
		try:
		    # The extractor provides the path of your target file
		    path_file = kwargs.get('p', None)
		    # And the metadata dictionary to which you want to write
		    MASTER_MD_DICT = kwargs.get('md', None)
		    is_debug = kwargs.get('is_debug', None)
		    # Fictional example to add parsed data
		    my_parsed_data = myABC.Dataset(path_file)
		    my_return = {path_file: {}}
		    my_return[path_file].update(my_parsed_data)
		    if 'ABC' in MASTER_MD_DICT:
		        if 'abc_files' in MASTER_MD_DICT['ABC']:
		            MASTER_MD_DICT['ABC']['abc_files'].append(my_return)
		    return MASTER_MD_DICT
		except Exception as exc:
		    status_note(str(exc), d=is_debug)
		    return 'error'

Steps to integrate your own parser
----------------------------------

#. Save a copy of your parser file parse_abc.py at o2rmeta\lib\parsers
#. Open ``o2rmeta\lib\metaextract.py`` and find the function ``register_parsers``
#. Add the following to that function using your own filename and class name:

::

   # From your file import your class
   from .parsers.parse_abc.py import ParseAbc
   # To global list of parsers add an instance of your class
   PARSERS_CLASS_LIST.append(ParseAbc())

Implement test for your new parser and add them into the ``tests`` folder.

Either install the lib and run ``pytest``, or run ``python -m pytest``.

#. test if the extractor recognizes your new parser by calling

::

    o2r-meta -debug extract -f


Documentation
-------------

The documentation is based on Sphinx_.
The source files can be found in the directory ``docs/`` and the rendered online documentation is at https://o2r.info/geoextent/.

Build documentation locally
^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    cd docs/
    pip install -r requirements-docs.txt
    make html


Build documentation website
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deployed documentation website is built on github actions, see file ``.github/workflows/documentation.yml`` for details.
In short, an extra stage ``build docs`` is executed only on the ``master`` branch and not for pull requests.

.. _Sphinx: https://www.sphinx-doc.org

Release
-------

Prerequisites
^^^^^^^^^^^^^

Required tools:

- ``setuptools``
- ``wheel``
- ``twine``

::

    pip install --upgrade setuptools wheel twine

Run tests
^^^^^^^^^

Make sure that all tests work locally by running

::

    cd tests
		pytest


Bump version for release
^^^^^^^^^^^^^^^^^^^^^^^^

Follow the `Semantic Versioning specification`_ to clearly mark changes as a new major version, minor changes, or patches.
The version number is centrally managed in the file ``o2rmeta/lib/__init__.py ``.

.. _Semantic Versioning specification: https://semver.org/

Update changelog
^^^^^^^^^^^^^^^^

Update the changelog in file ``docs/source/changelog.rst``, use the `sphinx-issues`_ syntax for referring to pull requests and contributors for changes where appropriate.

.. _sphinx-issues: https://github.com/sloria/sphinx-issues

Update citation and authors information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Make sure the following files have the current information (version, commit, contributors, dates, ...):

- ``CITATION.cff``, see https://citation-file-format.github.io/
- ``codemeta.json``, see https://codemeta.github.io/codemeta-generator/
- ``README.md`` and ``docs/source/index.rst``, the "How to cite" sections.

Build distribution archive
^^^^^^^^^^^^^^^^^^^^^^^^^^

See the PyPI documentation on generating a distribution archive, https://packaging.python.org/tutorials/packaging-projects/, for details.

::

    # remove previous releases and builds
    rm dist/*
    rm -rf build *.egg-info

    python3 setup.py sdist bdist_wheel

Upload to test repository
^^^^^^^^^^^^^^^^^^^^^^^^^

First upload to the test repository and check everything is in order.

::

	# upload with twine, make sure only one wheel is in dist/
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

Check if the information on https://test.pypi.org/project/o2rmeta/ is correct.
Then switch to a new Python environment to get an "empty" setup.

Upload to PyPI
^^^^^^^^^^^^^^

::

    twine upload dist/*


Check if information on https://pypi.org/project/geoextent/ is all correct.
Install the library from PyPI into a new environment, e.g., by reusing the container session from above, and check that everything works.


Add tag
^^^^^^^

Add a version tag to the commit of the release and push it to the main repository.
Go to GitHub and create a new release by using the "Draft a new release" button and using the just pushed tag.
