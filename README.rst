============
mini_fiction
============

Library CMS for fanfics. Currently in development.

Short feature list: fanfics with genres, characters and events; comments with trees;
search (by Sphinx); user profiles with contacts; moderation of fanfics and comments;
favorites and bookmarks; notices from administrator; PJAX-like loading of page content;
customizable design; primitive plugin system.

CMS currently in Russian, and we would be grateful for the translation of all phrases
in English.


Quick start
-----------

`Install lxml <http://lxml.de/installation.html>`_. Then:

.. code::

    pip install mini_fiction
    mini_fiction seed
    mini_fiction createsuperuser
    mini_fiction runserver

Website will be available at ``http://localhost:5000/``, administration page is
``https://localhost:5000/admin/``.


Configuration file
------------------

Save ``local_settings.example.py`` as ``local_settings.py`` and enable it:

.. code::

    PYTHONPATH=.; export PYTHONPATH
    MINIFICTION_SETTINGS=local_settings.Local; export MINIFICTION_SETTINGS

Then ``mini_fiction runserver`` in the same directory with this file.

For more information see ``INSTALL.md`` (in Russian).