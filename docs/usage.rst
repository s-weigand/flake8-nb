.. highlight:: shell

=====
Usage
=====

Since ``flake8_nb`` is basically a hacked version of
``flake8`` its usage is identically.
The only key difference is the appended ``_nb`` is the commands and
configurations name.

Command line usage
------------------

The basic usage is to call ``flake8_nb`` with the files/paths,
which should be checked as arguments (see `flake8 invocation`_).

.. code-block:: console

    $ flake8_nb path-to-notebooks-or-folder

To customize the behavior you can use the many options provided
by ``flake8``'s CLI. To see all the provided option just call:

.. code-block:: console

    $ flake8_nb --help

The only additional flag that is provided by ``flake8_nb`` and
isn't part of the original ``flake8`` is ``--keep-parsed-notebooks``.
If this flag is activated the the parsed notebooks will be kept
and the path they were saved in will be displayed, for further
debugging or trouble shooting.

Project wide configuration
--------------------------

Configuration of a project can be saved in one of the following files
``setup.cfg``, ``tox.ini`` or ``.flake8``, on the top level of your project
(see `flake8 configuration`_).

.. code-block:: ini

    [flake8_nb]

For a detailed explanation on how to use and configure it,
you can consult the official `flake8 documentation`_


Per cell/line configuration
---------------------------

There are multiple ways to fine grade configure ``flake8_nb``
on a line or cell basis.

flake8 ``noqa``
^^^^^^^^^^^^^^^
The most intuitive way for experienced ``flake8`` users is
to utilize the known `flake8 noqa`_ comment on line, to ignore specific
or all errors, ``flake8`` would report on that given line.

.. note::

    If a normal ``flake8 noqa comment`` ends with a string, which doesn't
    match the error code patter (``\w+\d+``), this comment will be ignored.


Cell tags
^^^^^^^^^


Inline cell tags
^^^^^^^^^^^^^^^^


.. _`flake8 invocation`: http://flake8.pycqa.org/en/latest/user/invocation.html
.. _`flake8 configuration`: http://flake8.pycqa.org/en/latest/user/configuration.html
.. _`flake8 documentation`: http://flake8.pycqa.org/en/latest/index.html
.. _`flake8 noqa`: http://flake8.pycqa.org/en/latest/user/violations.html#in-line-ignoring-errors
