# -*- coding: utf-8 -*-
import os
import sys
import unittest

    
def main():
    LOG_FILE_NAME = "test_report_common.txt"
    
    # Tests for the context manager
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.join(os.getcwd(), "tests_common"))
    
        
    msg = "Starting test run..."
    print(msg)
    
    with open(LOG_FILE_NAME, "w") as logfile:
        runner = unittest.TextTestRunner(logfile, verbosity=3)
    
        result = runner.run(suite)
        
    msg = ("Test run finished.\n   tests run: %d\n   failures: %d\n   errors: %d"
          % (result.testsRun, len(result.failures), len(result.errors))
          )
    print(msg)
    
    
if __name__ == "__main__":
    main()