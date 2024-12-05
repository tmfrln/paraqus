Development
===========

Contributions to improve Paraqus are welcome and should be made as pull requests in the github repository.
In the following, some details of the package structure, implementation, and code style are summarised to help new contributors get up to speed.

Python versions
---------------

Since Paraqus is written as a tool to export Abaqus results, the code must be compatible with the Python version used by Abaqus, which is Python 2.7 for releases before Abaqus 2024. Abaqus-specific code in `paraqus.abaqus` does not habe to be compatible to Python 3.X however.


Code style
----------

The Paraqus code style is based on `PEP 8 <https://peps.python.org/pep-0008/>`_, and is documented using numpy-style docstrings - a style guide can be found e.g. `here <https://numpydoc.readthedocs.io/en/latest/format.html>`_. We refrain from enforcing linting for commmits, but encourage contributions to adapt the style in the present code.


Repository structure
--------------------




Releases
--------

When new functionality is merged into the main branch of Paraqus, a version bump should be performed (by changing the version number in the pyproject.toml)



