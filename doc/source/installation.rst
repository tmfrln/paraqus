.. _installation:

Installation
------------

The easiest way to install Paraqus is through pip:

.. code-block:: console

   $ pip install paraqus

Another option is to just download the Paraqus repository from github. Since the only dependency is numpy, you can simply add the folder ``src/paraqus/`` to your path, e.g. by adding the lines

.. code-block:: python

   import sys
   sys.path.append("<PATH ON YOUR PC>/paraqus/src")

to your document. If you use Paraqus with Abaqus, you need to add paraqus to the python path even if you installed it with pip. If you do not know how to do that permanently, just use the lines above in your Abaqus scripts.


