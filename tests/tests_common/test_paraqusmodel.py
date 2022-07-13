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
        node_tags = [1, 2, 3, 4, 5, 6, 7, 8]
        node_coords = [[0, 0],
                       [1, 0],
                       [2, 0],
                       [0, 1],
                       [1, 1],
                       [2, 1],
                       [0.5, 1.5],
                       [1.5, 1.5]]
        element_tags = [1, 2, 3, 4, 5]
        connectivity = [[1, 2, 5, 4],
                        [2, 3, 6, 5],
                        [4, 5, 7],
                        [5, 6, 8],
                        [5, 8, 7]]
        element_types = [9, 9, 5, 5, 5]
    
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
        node_tags = [1, 2, 3, 4, 5, 6, 7, 8]
        node_coords = [[0, 0],
                       [1, 0],
                       [2, 0],
                       [0, 1],
                       [1, 1],
                       [2, 1],
                       [0.5, 1.5],
                       [1.5, 1.5]]
        element_tags = [1, 2, 3, 4, 5]
        connectivity = [[1, 2, 5, 4],
                        [2, 3, 6, 5],
                        [4, 5, 7],
                        [5, 6, 8],
                        [5, 8, 7]]
        element_types = [9, 9, 5, 5, 5]
    
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
        
        self.model.add_field("scalar node field",
                             field_tags,
                             field_vals,
                             "nodes",
                             "scalar")
        
        field = self.model.get_node_field("scalar node field")
        
        assert field.field_name == "scalar node field"
        assert field.field_type == "SCALAR"
        assert field.field_position == "NODES"
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
        
        self.model.add_field("vector node field",
                             field_tags,
                             field_vals,
                             "nodes",
                             "vector")
        
        field = self.model.get_node_field("vector node field")
        
        assert field.field_name == "vector node field"
        assert field.field_type == "VECTOR"
        assert field.field_position == "NODES"
        assert np.all(field.field_values == [[11, 12],
                                             [31, 32],
                                             [21, 22],
                                             [41, 42],
                                             [51, 52],
                                             [61, 62],
                                             [71, 72],
                                             [81, 82]])
        
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
        
        self.model.add_field("tensor node field",
                             field_tags,
                             field_vals,
                             "nodes",
                             "tensor")
        
        field = self.model.get_node_field("tensor node field")
        
        assert field.field_name == "tensor node field"
        assert field.field_type == "TENSOR"
        assert field.field_position == "NODES"
        assert np.all(field.field_values == [[11, 12, 13, 14],
                                             [31, 32, 33, 34],
                                             [21, 22, 23, 24],
                                             [41, 42, 43, 44],
                                             [51, 52, 53, 54],
                                             [61, 62, 63, 64],
                                             [71, 72, 73, 74],
                                             [81, 82, 83, 84]])
        
    def test_scalar_element_field(self):
        """TODO"""
        field_tags = [1, 3, 2, 4, 5]
        field_vals = [1, 2, 3, 4, 5]
        
        self.model.add_field("scalar element field",
                             field_tags,
                             field_vals,
                             "elements",
                             "scalar")
        
        field = self.model.get_element_field("scalar element field")
        
        assert field.field_name == "scalar element field"
        assert field.field_type == "SCALAR"
        assert field.field_position == "ELEMENTS"
        assert np.all(field.field_values == [[1],[3],[2],[4],[5]])
        
    def test_vector_element_field(self):
        """TODO"""
        field_tags = [1,3,2,4,5]
        field_vals = [[11, 12],
                      [21, 22],
                      [31, 32],
                      [41, 42],
                      [51, 52]]
        
        self.model.add_field("vector element field",
                             field_tags,
                             field_vals,
                             "elements",
                             "vector")
        
        field = self.model.get_element_field("vector element field")
        
        assert field.field_name == "vector element field"
        assert field.field_type == "VECTOR"
        assert field.field_position == "ELEMENTS"
        assert np.all(field.field_values == [[11, 12],
                                             [31, 32],
                                             [21, 22],
                                             [41, 42],
                                             [51, 52]])
        
    def test_tensor_element_field(self):
        """TODO"""
        field_tags = [1, 3, 2, 4, 5]
        field_vals = [[11, 12, 13, 14],
                      [21, 22, 23, 24],
                      [31, 32, 33, 34],
                      [41, 42, 43, 44],
                      [51, 52, 53, 54]]
        
        self.model.add_field("tensor element field",
                             field_tags,
                             field_vals,
                             "elements",
                             "tensor")
        
        field = self.model.get_element_field("tensor element field")
        
        assert field.field_name == "tensor element field"
        assert field.field_type == "TENSOR"
        assert field.field_position == "ELEMENTS"
        assert np.all(field.field_values == [[11, 12, 13, 14],
                                             [31, 32, 33, 34],
                                             [21, 22, 23, 24],
                                             [41, 42, 43, 44],
                                             [51, 52, 53, 54]])
        
    def test_pad_field_values(self):
        pass
            
        