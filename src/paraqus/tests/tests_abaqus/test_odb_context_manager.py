"""
Tests for the ODBObject context manager.

These tests can only be executed in Abaqus python.

"""
import os
import shutil
import unittest
from abaqus import session

from paraqus.abaqus.abaqustools import ODBObject
from paraqus.abaqus.abaqustools import upgrade_odb

RESOURCE_PATH  = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                              "resources")

class TestODBContextManager(unittest.TestCase):
    
    def setUp(self):
        # close all open odbs
        for odb in session.odbs.values():
            odb.close()
        
        self.odb_path = os.path.join(RESOURCE_PATH, 
                                     'element_test_current.odb')
    
    
    def test_open_close(self):
        """An odb is opened and closed by the context manager if it was not open."""
        self.assertEqual(len(session.odbs), 0)
        
        with ODBObject(self.odb_path):
            self.assertEqual(len(session.odbs), 1)
            
        self.assertEqual(len(session.odbs), 0)
           
    
    def test_readonly(self):
        """Odbs are correctly opened as readonly or writable."""
        with ODBObject(self.odb_path) as odb:
            self.assertTrue(odb.isReadOnly)
        
        with ODBObject(self.odb_path, readonly=True) as odb:
            self.assertTrue(odb.isReadOnly)
            
        with ODBObject(self.odb_path, readonly=False) as odb:
            self.assertFalse(odb.isReadOnly)
            
    
    def test_odb_stays_open(self):
        """An odb that was already opened stays open after leaving the context."""
        odb = session.openOdb(self.odb_path)
        
        self.assertEqual(len(session.odbs), 1)
        
        with ODBObject(self.odb_path) as odb_new:
            self.assertEqual(odb, odb_new)
            
        self.assertEqual(len(session.odbs), 1)
                    
    
    def tearDown(self):
        # close all open odbs
        for odb in session.odbs.values():
            odb.close()
            
        
        
class TestODBUpgrade(unittest.TestCase):
    def setUp(self):
        # close all open odbs
        for odb in session.odbs.values():
            odb.close()
            
        # base odb for the tests
        abq2018_odb = os.path.join(RESOURCE_PATH,
                                   'element_test_old.odb')
        
        # backup folder has to be consistent with the upgrade_odb function
        self.backup_folder = 'odbs_before_upgrades'
        
        # new name for the odb (so wie dont change the original version for
        # the tests)
        self.test_odb_name = (
            os.path.splitext(os.path.basename(abq2018_odb))[0] + '_test.odb')
         
        # create a copy of the odb that we can upgrade
        shutil.copy(abq2018_odb, self.test_odb_name)
        
        # remove the backup folder if one exists already
        if os.path.isdir(self.backup_folder):
            shutil.rmtree(self.backup_folder)
            
            
    def tearDown(self):
        if os.path.isdir(self.backup_folder):
            shutil.rmtree(self.backup_folder)
            
        if os.path.isfile(self.test_odb_name):
            os.remove(self.test_odb_name)
            
        # close all open odbs
        for odb in session.odbs.values():
            odb.close()
            
        
    def test_upgrade_old_odb(self):
        """Odbs from a previous version of abaqus are upgraded and backed up."""
        upgrade_required = upgrade_odb(self.test_odb_name)
        self.assertTrue(upgrade_required)
        
        # a backup has been created
        backup_file_path = os.path.join(self.backup_folder, self.test_odb_name)
        self.assertTrue(os.path.isfile(backup_file_path))
        
        # remove the backup
        shutil.rmtree(self.backup_folder)
        
        # now an up-to-date odb is present and no upgrade required
        upgrade_required = upgrade_odb(self.test_odb_name)
        self.assertFalse(upgrade_required)
        
        # therefore no backup folder is created
        self.assertFalse(os.path.isdir(self.backup_folder))
        
    
    def test_absolute_path(self):
        """The updater for old odbs works also with absolute paths"""
        # Tests that the old odb is required to upgraded
        upgrade_required = upgrade_odb(os.path.abspath(self.test_odb_name))
        self.assertTrue(upgrade_required)
        
        # TODO: check that the backup folder is where it is supposed to be
        
    def test_update_in_context_manager(self):
        """The odb updater works in the context manager."""
        with ODBObject(self.test_odb_name) as odb:
            pass
        
        # a backup has been created
        backup_file_path = os.path.join(self.backup_folder, self.test_odb_name)
        self.assertTrue(os.path.isfile(backup_file_path))
    
        # remove the backup
        shutil.rmtree(self.backup_folder)
        
        
            
        
         
