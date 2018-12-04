============================
ndex-webapp-python-exporters
============================


.. image:: https://img.shields.io/pypi/v/ndex_webapp_python_exporters.svg
        :target: https://pypi.python.org/pypi/ndex_webapp_python_exporters

.. image:: https://img.shields.io/travis/ndexbio/ndex_webapp_python_exporters.svg
        :target: https://travis-ci.org/ndexbio/ndex_webapp_python_exporters

.. image:: https://coveralls.io/repos/github/ndexbio/ndex_webapp_python_exporters/badge.svg?branch=master
        :target: https://coveralls.io/github/ndexbio/ndex_webapp_python_exporters?branch=master

Command line exporters written in Python used by the NDEx REST service.

**Supported Exporters**

* `Graphml`_

Tools
-----

* **ndex_exporters.py** Takes file in `NDEx CX`_ format and converts to format specified as a command line argument


Dependencies
------------

* `argparse <https://pypi.python.org/pypi/argparse>`_
* `ndex2 <https://pypi.org/project/ndex2/>`_

Compatibility
-------------

* Python 3.5+

Installation
------------


::

 pip install ndex_webapp_python_exporters

Or directly from repo (requires git)

::

 git clone https://github.com/ndexbio/ndex_webapp_python_exporters.git
 cd ndex_webapp_python_exporters
 python setup.py install

Example usage
-------------


The example below assumes **foo.cx** is a file in `NDEx CX`_ format

::

 cat foo.cx | ndex_exporters.py graphml > foo.graphml

**NOTE:** For the above example, the network `Thyroid Cancer <http://www.ndexbio.org/#/network/54a9a35b-1e5f-11e8-b939-0ac135e8bacf>`_ can be downloaded
as a file named **foo.cx** in `NDEx CX`_ format.



Credits
-------

* `Graphml`_ exporter derived from code developed by Cecilia Zhang

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`NDEx CX`: http://www.home.ndexbio.org/data-model/
.. _`Graphml`: http://graphml.graphdrawing.org/
