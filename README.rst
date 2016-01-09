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

Halliwell is not currently available through the Python Package Index, PyPI_,
but you can clone or fork the repository and use e.g.::

    python setup.py develop

to install it locally for development. You should also install the development
dependencies (ideally in a ``virtualenv``) using::

    pip install -r requirements.txt

These aren't required for running or using the app, but are necessary for
running the tests and building the documentation.

Deployment
----------

The project is set up to be deployed to `Pivotal Web Services`_. Due to some
issues around `migrating to Diego`_, you should disable health checking for the
app with::

    cf set-health-check halliwell none

You will also need to set the environment variable ``$SLACK_API_TOKEN`` to allow
the bot to interact on Slack::

   cf set-env halliwell SLACK_API_TOKEN <your-bot-api-token>

To automatically deploy from Travis_, you'll need to add environment variables
for your PWS name (``$CF_USERNAME``) and password (``$CF_PASSWORD``) through the
Travis control panel (``http://travis-ci.org/<your-name>/halliwell/settings``).
You may also need to alter the ``org`` and ``space`` settings in
``manifest.yml``.

.. _aSlack: https://pythonhosted.org/aslack
.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _migrating to Diego: https://support.run.pivotal.io/entries/105844873-Migrating-Applications-from-DEAs-to-Diego
.. _Pivotal Web Services: http://run.pivotal.io/
.. _PyPI: https://pypi.python.org/pypi
.. _Travis: https://travis-ci.org/
