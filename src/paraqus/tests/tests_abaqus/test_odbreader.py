"""
Tests for the ODBReader class.

These tests can only be executed in Abaqus python.

"""
import os
import unittest

import numpy as np

from paraqus.abaqus import ODBReader

RESOURCE_PATH  = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                              "resources")

class TestElementTestMesh(unittest.TestCase):
    """Class docsrt"""
    def setUp(self):
        self.odb_path = os.path.join(RESOURCE_PATH, 
                                     'element_test_current.odb')
        
        self.step_name = "Apply Force"
        self.frame_index = -1
        self.instance_name = "Rectangular Instance"
        
        self.reader = ODBReader(odb_path=self.odb_path,
                                    model_name='test_model')
            

    def test_read_mesh(self):
        """The model built from the element test odb has the correct mesh."""  
        
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        assert len(instance_model.nodes) == 9
        assert np.all(instance_model.nodes.tags == [1,2,3,4,5,6,7,8,9])
        
        assert len(instance_model.elements) == 4
        assert np.all(instance_model.elements.tags == [1,2,3,4])
        
    
    def test_read_node_field(self):
        """The model has a nodal vector field 'U'."""
        self.reader.add_field_export_request('U')
        
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        u = instance_model.get_node_field('U')
        assert len(u.field_values) == 9
        
        assert u.field_type == "vector"
        assert u.field_position == "nodes"
        
        
    def test_read_element_field(self):
        """The model has an elemental tensor field 'S'."""
        self.reader.add_field_export_request('S')
        
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        s = instance_model.get_element_field('S')
        assert len(s.field_values) == 4 #1 value per element
        
        assert s.field_type == "tensor"
        assert s.field_position == "elements"
        
        
    def test_error_missing_node_field(self):
        """A KeyError is raised for missing node fields."""
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        with self.assertRaises(KeyError) as context:
            s = instance_model.get_node_field('U')
         
        
    def test_error_missing_element_field(self):
        """A KeyError is raised for missing element fields."""
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        with self.assertRaises(KeyError) as context:
            s = instance_model.get_element_field('S')
            
            
    def test_read_instance_node_set(self):
        """A group is stored in the model for an instance node set."""
        self.reader.add_set_export_request('Left Edge',
                                           set_type="nodes",
                                           instance_name=self.instance_name)
        
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        # instance-level sets have the instance name prepended
        grp_name = self.instance_name + '.' + 'Left Edge'
        
        grp_nodes = instance_model.nodes.groups[grp_name]
        
        assert len(grp_nodes) == 3
    
    def test_read_instance_element_set(self):
        """A group is stored in the model for an instance element set."""
        self.reader.add_set_export_request('Left Edge',
                                           set_type="elements",
                                           instance_name=self.instance_name)
        
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        # instance-level sets have the instance name prepended
        grp_name = self.instance_name + '.' + 'Left Edge'
        
        grp_nodes = instance_model.elements.groups[grp_name]
        
        assert len(grp_nodes) == 2
        
        
    def test_read_assembly_node_set(self):
        """A group is stored in the model for an assembly node set."""
        self.reader.add_set_export_request('Bottom Edge',
                                           set_type="nodes")
        
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        # instance-level sets have the instance name prepended
        grp_name = 'Bottom Edge'
        
        grp_nodes = instance_model.nodes.groups[grp_name]
        
        assert len(grp_nodes) == 3
    
    
    def test_read_assembly_element_set(self):
        """A group is stored in the model for an assembly element set."""
        self.reader.add_set_export_request('Bottom Edge',
                                           set_type="elements")
        
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        # instance-level sets have the instance name prepended
        grp_name = 'Bottom Edge'
        
        grp_nodes = instance_model.elements.groups[grp_name]
        
        assert len(grp_nodes) == 2
        
    
    def test_read_instance_surface_nodes(self):
        """A group is stored in the model for nodes of an instance surface."""
        self.reader.add_surface_export_request('Right Edge',
                                               surface_type="nodes",
                                               instance_name=self.instance_name)
        
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        # instance-level sets have the instance name prepended
        grp_name = 'surface.%s.Right Edge' % self.instance_name
        
        grp_nodes = instance_model.nodes.groups[grp_name]
        
        assert len(grp_nodes) == 3
        
        
    def test_read_instance_surface_elements(self):
        """A group is stored in the model for elements of an instance surface."""
        self.reader.add_surface_export_request('Right Edge',
                                               surface_type="elements",
                                               instance_name=self.instance_name)
        
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        # instance-level sets have the instance name prepended
        grp_name = 'surface.%s.Right Edge' % self.instance_name
        
        grp_elements = instance_model.elements.groups[grp_name]
        
        assert len(grp_elements) == 2
    
    
    def test_read_assembly_surface_nodes(self):
        """A group is stored in the model for nodes of an assembly surface."""
        self.reader.add_surface_export_request('Top Surface',
                                               surface_type="nodes")
        
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        grp_name = 'surface.Top Surface'
        
        grp_nodes = instance_model.nodes.groups[grp_name]
        
        assert len(grp_nodes) == 3
        
        
    def test_read_assembly_surface_elements(self):
        """A group is stored in the model for elements of an assembly surface."""
        self.reader.add_surface_export_request('Top Surface',
                                               surface_type="elements")
        
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        grp_name = 'surface.Top Surface'
        
        grp_elements = instance_model.elements.groups[grp_name]
        
        assert len(grp_elements) == 2
        
        
    def test_multiple_sets(self):
        """Multiple sets and surfaces can be exported."""
        self.reader.add_set_export_request('Bottom Edge',
                                           set_type="nodes")
        
        self.reader.add_set_export_request('Bottom Edge',
                                           set_type="elements")
        
        self.reader.add_set_export_request('Left Edge',
                                           set_type="nodes",
                                           instance_name=self.instance_name)
        
        self.reader.add_set_export_request('Left Edge',
                                           set_type="elements",
                                           instance_name=self.instance_name)
        
        self.reader.add_surface_export_request('Top Surface',
                                               surface_type="nodes")
        
        self.reader.add_surface_export_request('Top Surface',
                                               surface_type="elements")
        
        self.reader.add_surface_export_request('Right Edge',
                                               surface_type="nodes",
                                               instance_name=self.instance_name)
        
        self.reader.add_surface_export_request('Right Edge',
                                               surface_type="elements",
                                               instance_name=self.instance_name)
        
        instance_models = list(
            self.reader.read_instances(step_name = self.step_name,
                                       frame_index = self.frame_index)
                              )
    
        assert len(instance_models) == 1
            
        instance_model = instance_models[0]
        
        assert len(instance_model.nodes.groups) == 4
        assert len(instance_model.elements.groups) == 4
        