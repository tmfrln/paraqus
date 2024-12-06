Tests
=====

Paraqus comes with a small number of unit tests. There are two groups of tests:

- Tests for functionality related to Abaqus: these tests must be run in the Python interpreter shipped with Abaqus.
- Tests for general functionality: these tests can be run in the Python interpreter shipped with Abaqus or in any other Python interpreter.

Creating test resources
------------------------

Paraqus comes with a number of reference files for tests, which are located in the directory ``paraqus/tests/resources``. Only two Abaqus-specific files are described here, since they might need to be recreated by the user for tests to pass.

- ``element_test_current odb`` is supposed to match your current Abaqus installation. If your current Abaqus version is not Abaqus 2023, you should recreate the file as described below.
- ``element_test_old.odb`` is supposed to be from an Abaqus version older than your current one. If your Abaqus version is older than Abaqus 2019, you should recreate the file as described below.

To create the files, you first need to find out where Paraqus is installed on your system. Follow the steps outlined in the :ref:`installation instructions<installation>` to find the folder containing the directory ``paraqus``.

To recreate the file ``element_test_current.odb``, navigate to the directory ``paraqus/tests/resources`` and run the command ``abaqus job=element_test_current``, where ``abaqus`` should be replaced with the command for the version of Abaqus you are currently using. 

To recreate the file ``element_test_old.odb``, navigate to the directory ``paraqus/tests/resources`` and run the command ``abaqusOLD job=element_test_old``, where ``abaqusOLD`` should be replaced with the command for a previous release of Abaqus (e.g. if you are using Abaqus 2021 normally, this should be Abaqus 2020 or older). If you do not have access to a previous Abaqus release, just skip this and let the corresponding tests fail - this is no big deal, since the tests only cover edge cases of working with older files.


Run tests using Abaqus
----------------------

In the Python console of Abaqus CAE, run the following commands:

>>> import paraqus.tests as tests
>>> tests.run_abaqus_tests()

The report file for the tests is generated in the current working directory, and a small summary is displayed in Abaqus.


Run tests using an external Python interpreter
----------------------------------------------

In a Python session (or a script file) run the following commands:

>>> import paraqus.tests as tests
>>> tests.run_python_tests()

The report file for the tests is generated in the current working directory, and a small summary is displayed.

