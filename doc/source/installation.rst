.. _installation:

Installation
============

The installation procedure for Paraqus is dependent on whether you want to use it inside the software Abaqus (which is the typical use case).

Using Paraqus only outside Abaqus
---------------------------------

If you do not use Abaqus, you are in luck: the installation is pretty simple. Assuming Python is already available on your machine, Paraqus can be installed from the Python Package Index:

  .. code-block::

      $ pip install paraqus

This will install Paraqus for the Python version that ``pip`` is connected to. 

Using Paraqus inside Abaqus
---------------------------

Abaqus is shipped with its own Python interpreter (we will call it Abaqus Python in the following), which unfortunately does not allow installations through ``pip``. To use Paraqus in Abaqus, first of all, you need to install Paraqus and then let Abaqus Python know where to find it. There is a number of different ways to achieve this, and they might be dependent on your operating system.

If you already have Python installed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Follow the instructions above and install Paraqus outside Abaqus.
- Open a Python interpreter (type ``python`` in a terminal).
- Enter the following commands::

    >>> import paraqus
    >>> print(paraqus.__path__)
	
- Take note of the output by removing the ending ``/paraqus`` term; the resulting string represents the path to the location where the Paraqus package is installed. For instance, should the output be ['/home/user/lib/python3.11/site-packages/paraqus'], you need to note down the path ``/home/user/lib/python3.11/site-packages``. 
- In every Python script that is executed by Abaqus Python, before you import Paraqus, add the following lines of code (replace ``<path>`` with the path you noted)::

  .. code-block::
     
      import sys
      sys.path.append("<path>")

If you do not have Python installed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Clone the repositroy into a directory of your choice, e.g. ``/home/user/paraqus-files/``. Alternatively download and unpack the directory manually.
- Locate the ``src`` directory inside the repository folder. In the above example, this would be ``/home/user/paraqus-files/src/``. Note this path down.
- In every Python script that is executed by Abaqus Python, before you import Paraqus, add the following lines of code (replace ``path`` with the path you noted)::

  .. code-block::
     
      import sys
      sys.path.append("<path>")

Adding Paraqus to the Python path (advanced, but recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you would like to avoid adding the code lines above to all your Python scripts when using Paraqus, you can add the directory ``path`` to the environment variable ``PYTHONPATH``. Since this step is dependent on the operating system, it is not described here in detail, but you have to google for your system.

Dependencies
------------

The only dependency for Paraqus is NumPy. When the Abaqus Python interpreter is used, NumPy is already installed by default. If Paraqus is installed via ``pip``, NumPy will be automatically installed as well.

