.. Re2o documentation master file, created by
   sphinx-quickstart on Sat May 16 14:17:06 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Re2o's documentation!
================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :glob:

   autodoc/*

I collected the files with ::

   sphinx-apidoc -o source/autodoc/ -f /var/www/re2o/ ../*/migrations/*

Then ::

   make markdown




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
