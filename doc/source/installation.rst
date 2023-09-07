.. _installation:

Installation
============

The installation procedure for Paraqus is dependent on whether you want to use it inside of the software Abaqus (which is the typical use case).

Using Paraqus only outside of Abaqus
------------------------------------

If you do not use Abaqus, you are in luck: The installation is pretty simple. Assuming you have Python already installed, Paraqus can be installed from the Python package index:

  .. code-block::

      $ pip install paraqus

This will install paraqus for the python installation that pip is connected to. 

Using Paraqus within Abaqus
---------------------------

Abaqus is shipped with its own python interpreter (we will call it Abaqus Python in the following), which unfortunately does not allow installations through pip. To use Paraqus in Abaqus, we need to download or install Paraqus, and then let Abaqus Python know where to find it. There is a number of different ways to achieve this, and they might be dependent on your operating system.

If you already have Python installed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- follow the instructions above and install Paraqus outside of Abaqus
- open a Python interpreter (type ``python`` in a terminal)
- enter the following commands::

    >>> import paraqus
    >>> print(paraqus.__path__)

  for an example output ``['/home/user/lib/python3.11/site-packages/paraqus']``, we need to note down the path ``/home/user/lib/python3.11/site-packages``. 

- In every Python script that is executed by Abaqus Python, before you import paraqus, add the following lines of code (replace *path* with the path you noted)

  .. code-block::
     
      import sys
      sys.path.append("path")

If you do not have Python installed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- download the repository, and unpack it to a path of your choice, e.g. ``/home/user/paraqus-files/``.
- locate the ``src`` directory inside of the directory. In our example, this would be ``/home/user/paraqus-files/src/``. Note this path down.
- In every Python script that is executed by Abaqus Python, before you import paraqus, add the following lines of code (replace *path* with the path you noted)

  .. code-block::
     
      import sys
      sys.path.append("path")

Adding Paraqus to the python path (advanced, but recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you would like to avoid adding the code lines above to all your files when using Paraqus, you can add the directory *path* to the environment variable ``PYTHONPATH``. Since this step is dependent on the operating system, it is not described here in detail, but you have to google for your system.

Dependencies
------------

The only dependency for Paraqus is Numpy. When the Abaqus python interpreter is used, numpy is already installed by default. If Paraqus is installed via pip, numpy will be automatically installed as well.

