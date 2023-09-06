"""
Unit tests for Paraqus.

The unit tests are grouped in two separate modules.
The module paraqus.tests.tests_common contains all tests that are independent
of Abaqus, while the module paraqus.tests.tests_abaqus contains tests that
need the Abaqus python interpreter to work.

To run the tests, use the functions ``run_abaqus_tests()`` or
``run_python_tests()``, respectively. Note that ``run_abaqus_tests()``
also includes the tests that do not need Abaqus.

"""
import unittest


def run_abaqus_tests():
    """
    Run all unit tests using Abaqus python.

    Test results are exported to a text file ``test_report_abaqus.txt`` in the
    current working directory.

    If you are using a python interpreter outside of Abaqus, use the function
    ``run_python()`` instead.

    Raises
    ------
    RuntimeError
        If this function is not able to import modules from Abaqus.

    Returns
    -------
    None.

    """
    # make sure abaqus is importable
    try:
        import abaqus
    except ImportError:
        raise RuntimeError("The method run_abaqus() must only be used in "
                            "Abaqus python.")

    # import the modules with tests - tests will be discovered based on their
    # paths
    from paraqus.tests import tests_common, tests_abaqus

    modules = [tests_common, tests_abaqus]

    # create a test suite from each model
    suites = [_find_tests(module) for module in modules]

    # combine the test suites
    suite = unittest.TestSuite(suites)

    # run the actual tests
    _run_tests(suite, "test_report_abaqus.txt")


def run_python_tests():
    """
    Run all unit tests using standard python.

    Test results are exported to a text file ``test_report_python.txt`` in the
    current working directory.

    This function runs only the subset of tests that does not need Abaqus to
    work. If you use Abaqus, use the function ``run_abaqus()`` in the Abaqus
    python interpreter instead.

    Returns
    -------
    None.

    """
    # import the tests module, discovery is based off its path
    from paraqus.tests import tests_common

    # create a suite of tests
    suite = _find_tests(tests_common)

    # run the actual tests
    _run_tests(suite, "test_report_python.txt")

def _find_tests(module):
    """Helper function to build a test suite of all tests in a package."""
    loader = unittest.TestLoader()

    tests_path = module.__path__[0]

    suite = loader.discover(tests_path)

    return suite

def _run_tests(suite, file_name):
    """
    Run a suite of tests and generate an output file.

    Parameters
    ----------
    suite : unittest.TestSuite
        All the tests that will be run.
    file_name : str
        Output file name for the test report.

    Returns
    -------
    None.

    """
    msg = "Starting test run..."
    print(msg)

    with open(file_name, "w") as logfile:
        runner = unittest.TextTestRunner(logfile, verbosity=3)

        result = runner.run(suite)

    msg = ("Test run finished.\n   tests run: %d\n   failures: %d\n   errors: %d"
          % (result.testsRun, len(result.failures), len(result.errors))
          )
    print(msg)

    if not result.wasSuccessful():
        raise RuntimeError("Not all tests passed.")
