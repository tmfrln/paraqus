"""
Tests for the ParaqusModel class.

These tests can be executed in Abaqus python or in standard python 2.7+.

"""
import unittest
import numpy as np

from paraqus.paraqusmodel import ParaqusModel

class TestParaqusModelCreation(unittest.TestCase):
    
    def test_model_creation(self):
        """A ParaqusModel can be created based on mesh info."""
        # Define geometry consisting of two first-order quad elements and
        # three first-order tri elements
        node_tags = [1,2,3,4,5,6,7,8]
        node_coords = [[0,0],[1,0],[2,0],[0,1],[1,1],[2,1],[0.5,1.5],[1.5,1.5]]
        element_tags = [1,2,3,4,5]
        connectivity = [[1,2,5,4],[2,3,6,5],[4,5,7],[5,6,8],[5,8,7]]
        element_types = [9,9,5,5,5]
    
        # Create four element base model
        model_name = "2D_TEST_MODEL"
        part_name = "2D_TEST_PART"
        model = ParaqusModel(element_tags,
                             connectivity,
                             element_types,
                             node_tags,
                             node_coords,
                             model_name=model_name,
                             part_name=part_name)
        
        assert model.model_name == model_name
        assert model.part_name == part_name
        assert len(model.nodes.tags) == 8
        assert len(model.elements.tags) == 5
    
    
class TestParaqusModelFields(unittest.TestCase):
    
    def setUp(self):
        """Create a small ParaqusModel."""
        # Define geometry consisting of two first-order quad elements and
        # three first-order tri elements
        node_tags = [1,2,3,4,5,6,7,8]
        node_coords = [[0,0],[1,0],[2,0],[0,1],[1,1],[2,1],[0.5,1.5],[1.5,1.5]]
        element_tags = [1,2,3,4,5]
        connectivity = [[1,2,5,4],[2,3,6,5],[4,5,7],[5,6,8],[5,8,7]]
        element_types = [9,9,5,5,5]
    
        # Create four element base model
        model_name = "2D_TEST_MODEL"
        part_name = "2D_TEST_PART"
        self.model = ParaqusModel(element_tags,
                                  connectivity,
                                  element_types,
                                  node_tags,
                                  node_coords,
                                  model_name=model_name,
                                  part_name=part_name)
        
    
    def test_scalar_node_field(self):
        """TODO"""
        field_tags = [1, 3, 2, 4, 5, 6, 7, 8]
        field_vals = [1, 2, 3, 4, 5, 6, 7, 8]
        
        self.model.add_field("scalar field",
                             field_tags,
                             field_vals,
                             "nodes",
                             "scalar")
        
        field = self.model.get_node_field("scalar field")
        
        assert field.field_name == "scalar field"
        assert np.all(field.field_values == [[1],[3],[2],[4],[5],[6],[7],[8]])
        
        
    def test_vector_node_field(self):
        """TODO"""
        field_tags = [1,3,2,4,5,6,7,8]
        field_vals = [[11, 12],
                      [21, 22],
                      [31, 32],
                      [41, 42],
                      [51, 52],
                      [61, 62],
                      [71, 72],
                      [81, 82]]
        
        self.model.add_field("scalar field",
                             field_tags,
                             field_vals,
                             "nodes",
                             "vector")
        
    def test_tensor_node_field(self):
        """TODO"""
        field_tags = [1, 3, 2, 4, 5, 6, 7, 8]
        field_vals = [[11, 12, 13, 14],
                      [21, 22, 23, 24],
                      [31, 32, 33, 34],
                      [41, 42, 43, 44],
                      [51, 52, 53, 54],
                      [61, 62, 63, 64],
                      [71, 72, 73, 74],
                      [81, 82, 83, 84]]
        
        
        self.model.add_field("scalar field",
                             field_tags,
                             field_vals,
                             "nodes",
                             "tensor")
        
        
        
        # pass    
        # # Add some field outputs
        # tensor_field_vals = [[1,1,1,1],[2,2,2,2],[3,3,3,3],[4,4,4,4],[5,5,5,5]]
        # vector_field_vals = [[1,1,1],[2,2,2],[3,3,3],[4,4,4],[5,5,5]]
        # model.add_field_output("tensor_field", [1,2,3,4,5], tensor_field_vals,
        #                           "elements", "tensor")
        # model.add_field_output("vector_field", [1,2,3,4,5], vector_field_vals,
        #                           "elements", "vector")



        
         
