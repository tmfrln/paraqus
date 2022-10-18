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
        """Scalar node fields can be added to models, value order is ok."""
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
        """Vector node fields can be added to models, value order is ok."""
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
        """Tensor node fields can be added to models, value order is ok."""
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
        """Scalar element fields can be added to models, value order is ok."""
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
        """Vector element fields can be added to models, value order is ok."""
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
        """Tensor element fields can be added to models, value order is ok."""
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

    def test_pad_scalar_field_values(self):
        """Missing values in scalar fields are padded with Nans."""
        # no value for node 4
        field_tags = [1, 3, 2, 5]
        field_vals = [1, 2, 3, 5]

        self.model.add_field("scalar element field",
                             field_tags,
                             field_vals,
                             "elements",
                             "scalar")

        field = self.model.get_element_field("scalar element field")

        assert field.field_name == "scalar element field"
        assert field.field_type == "SCALAR"
        assert field.field_position == "ELEMENTS"
        np.testing.assert_array_equal(field.field_values, [[1],
                                                           [3],
                                                           [2],
                                                           [np.nan],
                                                           [5]])

    def test_pad_vector_field_values(self):
        """Missing values in vector fields are padded with Nans."""
        # no value for node 4
        field_tags = [1, 3, 2, 5]
        field_vals = [[11, 12, 13],
                      [21, 22, 23],
                      [31, 32, 33],
                      [51, 52, 53]]

        self.model.add_field("vector element field",
                             field_tags,
                             field_vals,
                             "elements",
                             "vector")

        field = self.model.get_element_field("vector element field")

        assert field.field_name == "vector element field"
        assert field.field_type == "VECTOR"
        assert field.field_position == "ELEMENTS"
        np.testing.assert_array_equal(field.field_values, [[11, 12, 13],
                                                           [31, 32, 33],
                                                           [21, 22, 23],
                                                           [np.nan]*3,
                                                           [51, 52, 53]])

    def test_error_scalar_field_multiple_components(self):
        """An exception is raised when data for a scalar field is not 1d."""
        field_tags = [1, 2, 3, 4, 5]
        field_vals = [[1, 1], [2, 2], [3, 3], [4, 4], [5, 5]]

        with self.assertRaises(ValueError) as context:
            self.model.add_field("scalar element field",
                             field_tags,
                             field_vals,
                             "elements",
                             "scalar")





class TestParaqusModelSplitting(unittest.TestCase):

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



    def test_partition_model(self):
        """The model can be split into multiple submodels."""
        num_models = 2

        submodels = list(self.model.split_model(num_models))

        assert len(submodels) == 2

        assert all([len(m.elements.tags) > 0 for m in submodels])

        etags1 = submodels[0].elements.tags
        etags2 = submodels[1].elements.tags

        # elements can only be in one submodel!
        assert set(self.model.elements.tags) == set(etags1) ^ set(etags2)

        ntags1 = submodels[0].nodes.tags
        ntags2 = submodels[1].nodes.tags

        # nodes can be shared
        assert set(self.model.nodes.tags) == set(ntags1) | set(ntags2)



class TestParaqusModelFieldAccess(unittest.TestCase):

    def test_fields_by_type(self):
        """Fields stored in the model can be accessed via their type."""

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

        scalar_node_vals = [1, 2, 3, 4, 5, 6, 7, 8]

        self.model.add_field("scalar node field",
                             node_tags,
                             scalar_node_vals,
                             "nodes",
                             "scalar")

        vector_node_vals = [[11, 12],
                            [21, 22],
                            [31, 32],
                            [41, 42],
                            [51, 52],
                            [61, 62],
                            [71, 72],
                            [81, 82]]

        self.model.add_field("vector node field",
                             node_tags,
                             vector_node_vals,
                             "nodes",
                             "vector")

        scalar_element_vals = [1, 2, 3, 4, 5]

        self.model.add_field("scalar element field",
                             element_tags,
                             scalar_element_vals,
                             "elements",
                             "scalar")

        vector_element_vals = [[11, 12],
                               [21, 22],
                               [31, 32],
                               [41, 42],
                               [51, 52]]

        self.model.add_field("vector element field",
                             element_tags,
                             vector_element_vals,
                             "elements",
                             "vector")

        node_fields_scalar = self.model.get_fields_by_type("scalar", "nodes")
        assert len(node_fields_scalar) == 1
        assert node_fields_scalar[0]._field_type == "scalar"
        assert node_fields_scalar[0]._field_position == "nodes"

        node_fields_vector = self.model.get_fields_by_type("vector", "nodes")
        assert len(node_fields_vector) == 1
        assert node_fields_vector[0]._field_type == "vector"
        assert node_fields_vector[0]._field_position == "nodes"

        element_fields_scalar = self.model.get_fields_by_type("scalar", "elements")
        assert len(element_fields_scalar) == 1
        assert element_fields_scalar[0]._field_type == "scalar"
        assert element_fields_scalar[0]._field_position == "elements"

        element_fields_vector = self.model.get_fields_by_type("vector", "elements")
        assert len(element_fields_vector) == 1
        assert element_fields_vector[0]._field_type == "vector"
        assert element_fields_vector[0]._field_position == "elements"
