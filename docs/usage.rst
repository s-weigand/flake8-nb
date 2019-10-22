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

flake8 ``noqa`` comments
^^^^^^^^^^^^^^^^^^^^^^^^
The most intuitive way for experienced ``flake8`` users is
to utilize the known `flake8 noqa`_ comment on a line, to ignore specific
or all errors, ``flake8`` would report on that given line.

.. note::

    If a normal ``flake8 noqa comment`` ends with a string, which doesn't
    match the error code patter (``\w+\d+``), this comment will be ignored.


Cell tags
^^^^^^^^^
Cell tags are meta information, which can be added to cells,
to augment their behavior.
Depending on the editor you use for the notebook, they aren't
directly visible, which is a nice way to hide certain internals
which aren't important for the user/reader.
For example if write a book like notebook and want to demonstrate
some bad code examples an still pass your ``flake8_nb`` tests you
can use ``flake8-noqa-tags``.
Or if you want to demonstrate a raised exception and still want
then whole notebook to be executed when you run all cells, you
can use the ``raises-exception`` tag.

The patterns for `flake8-noqa-tags` are the following:

* ``flake8-noqa-cell``
    ignores all reports from a cell

* ``flake8-noqa-cell-<rule1>-<rule2>``
    ignores given rules for the cell
    i.e. ``flake8-noqa-cell-F401-F811``

* ``flake8-noqa-line-<line_nr>``
    ignores all reports from a given line in a cell,
    i.e. ``flake8-noqa-line-1``

* ``flake8-noqa-line-<line_nr>-<rule1>-<rule2>``
    ignores given rules from a given line for the cell
    i.e. ``flake8-noqa-line-1-F401-F811``


Inline cell tags
^^^^^^^^^^^^^^^^
If you want your users/reader to directly see which ``flake8`` rules
are ignored, you can also use the ``flake8-noqa-tag`` pattern as
comment in a cell.


.. note::

    If you use jupyter magic to run code other than Python (i.e. ``%%bash``)
    you should ignore the whole cell with ``flake8-noqa-cell``.


.. _`flake8 invocation`: http://flake8.pycqa.org/en/latest/user/invocation.html
.. _`flake8 configuration`: http://flake8.pycqa.org/en/latest/user/configuration.html
.. _`flake8 documentation`: http://flake8.pycqa.org/en/latest/index.html
.. _`flake8 noqa`: http://flake8.pycqa.org/en/latest/user/violations.html#in-line-ignoring-errors
.. _`jupyterlab-celltags`: https://github.com/jupyterlab/jupyterlab-celltags
