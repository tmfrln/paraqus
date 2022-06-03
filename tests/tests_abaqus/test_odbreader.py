"""
Tests for the ODBReader class.

These tests can only be executed in Abaqus python.

"""
import os
import unittest

import numpy as np

from paraqus.abaqus import ODBReader


class TestElementTestMesh(unittest.TestCase):
    
    def setUp(self):
        self.odb_path = os.path.join('resources', 
                                     'element_test_2021.odb')
        
        self.step_name = "Apply Force"
        self.frame_index = -1
        
        self.reader = ODBReader(odb_path=self.odb_path,
                                    model_name='test_model')
    
        # self.reader.add_field_export_request('U')
                
        
        

    def test_read_mesh(self):
        """..."""  
        
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        assert len(instance_model.nodes) == 4
        assert np.all(instance_model.nodes.tags == [1,2,3,4])
        
        assert len(instance_model.elements) == 1
        assert np.all(instance_model.elements.tags == [1])
        
    
    def test_read_node_field(self):
        """..."""
        self.reader.add_field_export_request('U')
        
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        u = instance_model.get_node_field('U')
        assert len(u.field_values) == 4
        
        assert u.field_type == "vector"
        assert u.field_position == "nodes"
        
        
    def test_read_element_field(self):
        """..."""
        self.reader.add_field_export_request('S')
        
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        s = instance_model.get_element_field('S')
        assert len(s.field_values) == 1 #1 value per element
        
        assert s.field_type == "tensor"
        assert s.field_position == "elements"
        
        
    def test_error_missing_node_field(self):
        """..."""
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        with self.assertRaises(KeyError) as context:
            s = instance_model.get_node_field('U')
         
        
    def test_error_missing_element_field(self):
        """..."""
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        with self.assertRaises(KeyError) as context:
            s = instance_model.get_element_field('S')