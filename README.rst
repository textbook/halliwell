Halliwell
=========

.. image:: https://travis-ci.org/textbook/halliwell.svg
    :target: https://travis-ci.org/textbook/halliwell
    :alt: Travis Build Status

.. image:: https://coveralls.io/repos/textbook/halliwell/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/textbook/halliwell?branch=master
    :alt: Code Coverage

.. image:: https://www.quantifiedcode.com/api/v1/project/537a5b1f07184938a383949eb6705ad5/badge.svg
    :target: https://www.quantifiedcode.com/app/project/537a5b1f07184938a383949eb6705ad5
    :alt: Code Issues

.. image:: https://img.shields.io/badge/license-ISC-blue.svg
    :target: https://github.com/textbook/halliwell/blob/master/LICENSE
    :alt: ISC License

Halliwell is a Slack bot, built using aSlack_, that can give you useful
information about movies. It's a work in progress!

Compatibility
-------------

Halliwell uses asyncio_ with the ``async`` and ``await`` syntax, so is only
compatible with Python versions 3.5 and above.

Installation
------------

Halliwell is not available through the Python Package Index, PyPI_, but you can
clone or fork the repository and use e.g.::

    python setup.py develop

to install locally for development. You should also install the development
dependencies (ideally in a ``virtualenv``) using::

    pip install -r requirements.txt

.. _aSlack: https://pythonhosted.org/aslack
