Tests
=====

Paraqus comes with a small number of unit tests. There are two groups of tests:

- Tests for functionality related to Abaqus: These tests must be run in the python interpreter shipped with Abaqus.
- Tests for general functionality: These tests can be run in the python interpreter shipped with Abaqus or in any other python interpreter.

Creating test ressources
------------------------

Paraqus comes with two small example Abaqus output databases for tests. One of the databases is supposed to match your current Abaqus installation, while the other database should be from an older release. If your current Abaqus version is not Abaqus 2021, you should recreate the file ``element_test_current.odb``. If your Abaqus version is older than Abaqus 2019, you should also recreate the file ``element_test_old.odb``.

To recreate the file ``element_test_current.odb``, navigate to the directory ``tests/resources`` and run the command ``abaqus job=element_test_current``, where ``abaqus`` should be replaced with the command for the version of Abaqus you are currently using. 

To recreate the file ``element_test_old.odb``, navigate to the directory ``paraqus/tests/resources`` and run the command ``abaqusOLD job=element_test_current``, where ``abaqusOLD`` should be replaced with the command for a previous release of Abaqus (e.g. if you are using Abaqus 2021 normally, this should be Abaqus 2020 or older). If you do not have access to a previous Abaqus release, just skip this and let the corresponding tests fail - this is no big deal, since the tests only cover edge cases of working with older files.


Run tests using Abaqus
----------------------

In the python console of Abaqus  CAE, run the following commands:

>>> import paraqus.tests as tests
>>> tests.run_abaqus()

The report file for the tests is generated in the current working directory, and a small summary is displayed in Abaqus.


Run tests using an external python interpreter
----------------------------------------------

In a python session (or a script file) run the following commands:

>>> import paraqus.tests as tests
>>> tests.run_python()

The report file for the tests is generated in the current working directory, and a small summary is displayed.

