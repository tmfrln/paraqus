# -*- coding: utf-8 -*-
import os
import sys
import unittest

def print_cae_and_terminal(msg):
    print >> sys.__stdout__, msg
    print(msg)
    
def main():
    LOG_FILE_NAME = "test_report.txt"
    
    # Tests for the context manager
    loader = unittest.TestLoader()
    suite = loader.discover(os.getcwd())
    
        
    msg = "Starting test run..."
    print_cae_and_terminal(msg)
    
    with open(LOG_FILE_NAME, "w") as logfile:
        runner = unittest.TextTestRunner(logfile, verbosity=3)
    
        result = runner.run(suite)
        
    msg = ("Test run finished.\n   tests run: %d\n   failures: %d\n   errors: %d"
          % (result.testsRun, len(result.failures), len(result.errors))
          )
    print_cae_and_terminal(msg)
    
    
if __name__ == "__main__":
    main()