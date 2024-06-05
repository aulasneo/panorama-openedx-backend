panorama-openedx-backend
#############################

This is a Django app for Open edX that implements all backend functions
needed by the Panorama MFE to work.

|pypi-badge| |ci-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge| |status-badge|

Purpose
*******

Django app that implements backend functions for Panorama MFE

`Panorama <https://aulasneo.com/open-edx-analytics/>`_ is the ultimate
analytics system for Open edX and more.

This code is not intended to be installed by itself.
To install Panorama in your Open edX instance please install the
`Panorama Tutor plugin <https://github.com/aulasneo/tutor-contrib-panorama>`_.

Getting Started with Development
********************************

Please see the Open edX documentation for `guidance on Python development <https://docs.openedx.org/en/latest/developers/how-tos/get-ready-for-python-dev.html>`_ in this repo.

Deploying
*********

To deploy for development, add a simple Tutor plugin with:

.. code-block:: python

    from tutor import hooks as tutor_hooks

    tutor_hooks.Filters.MOUNTED_DIRECTORIES.add_item(("openedx", "panorama-openedx-backend"))

Then use `tutor mounts` to mount your local copy of the repo.

Getting Help
************

Contact
=============

Contact us at https://aulasneo.com if you need support.


License
*******

The code in this repository is licensed under the Not open source unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.

Contributing
************

Contributions are very welcome.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to have a discussion about your new feature idea with the maintainers prior to
beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

Reporting Security Issues
*************************

Please do not report security issues in public. Please email info@aulasneo.com.

.. |pypi-badge| image:: https://img.shields.io/pypi/v/panorama-openedx-backend.svg
    :target: https://pypi.python.org/pypi/panorama-openedx-backend/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/aulasneo/panorama-openedx-backend/workflows/Python%20CI/badge.svg?branch=main
    :target: https://github.com/aulasneo/panorama-openedx-backend/actions
    :alt: CI

.. |codecov-badge| image:: https://codecov.io/github/aulasneo/panorama-openedx-backend/coverage.svg?branch=main
    :target: https://codecov.io/github/aulasneo/panorama-openedx-backend?branch=main
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/panorama-openedx-backend/badge/?version=latest
    :target: https://docs.openedx.org/projects/panorama-openedx-backend
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/panorama-openedx-backend.svg
    :target: https://pypi.python.org/pypi/panorama-openedx-backend/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/aulasneo/panorama-openedx-backend.svg
    :target: https://github.com/aulasneo/panorama-openedx-backend/blob/main/LICENSE.txt
    :alt: License

.. .. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
.. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Deprecated-orange
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Unsupported-red
