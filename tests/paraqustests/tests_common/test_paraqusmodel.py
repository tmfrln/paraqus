"""
Tests for the ParaqusModel class.

These tests can be executed in Abaqus Python or in standard Python >= 2.7.

"""
import unittest

import numpy as np

from paraqus.constants import NODES, ELEMENTS, SCALAR, VECTOR, TENSOR
from paraqus.paraqusmodel import (ElementRepository,
                                  NodeRepository,
                                  ElementFieldRepository,
                                  NodeFieldRepository,
                                  Field)

import paraqustests.tests_common as common


class TestScalarField(unittest.TestCase):
    """Tests related to scalar fields."""

    def setUp(self):
        """Create a scalar field for testing."""
        self.field_name = "TEST_FIELD_NAME"
        self.field_position = NODES
        self.field_type = SCALAR
        _, self.field_values = common.get_test_field_data(NODES, SCALAR)
        self.field = Field(self.field_name,
                           self.field_values,
                           self.field_position,
                           self.field_type)

    def test_field_creation(self):
        """A scalar field can be created with correct attributes."""
        # Convert field values to column array
        field_values = (np.asarray(self.field_values)
                        .reshape((len(self.field_values), -1)))

        assert self.field.field_name == self.field_name
        np.testing.assert_array_equal(self.field.field_values, field_values)
        assert self.field.field_position == self.field_position
        assert self.field.field_type == self.field_type

    def test_get_3d_field_values(self):
        """A 3d representation of a scalar field is obtained correctly."""
        # Convert field values to column array
        field_values = (np.asarray(self.field_values)
                        .reshape((len(self.field_values), -1)))

        np.testing.assert_array_equal(self.field.get_3d_field_values(),
                                      field_values)


class TestVectorField(unittest.TestCase):
    """Tests related to vector fields."""

    def setUp(self):
        """Create a vector field for testing."""
        self.field_name = "TEST_FIELD_NAME"
        self.field_position = NODES
        self.field_type = VECTOR
        _, self.field_values = common.get_test_field_data(NODES, VECTOR)
        self.field = Field(self.field_name,
                           self.field_values,
                           self.field_position,
                           self.field_type)

    def test_get_3d_field_values(self):
        """A 3d representation of a vector field is obtained correctly."""
        _, field_values = common.get_test_field_data(NODES, VECTOR)
        field_values = np.asarray(field_values)
        zero_column = np.zeros((len(field_values), 1))
        field_values = np.hstack((field_values, zero_column))

        np.testing.assert_array_equal(self.field.get_3d_field_values(),
                                      field_values)


class TestTensorField(unittest.TestCase):
    """Tests related to tensor fields."""

    def setUp(self):
        """Create a tensor field for testing."""
        self.field_name = "TEST_FIELD_NAME"
        self.field_position = ELEMENTS
        self.field_type = TENSOR
        _, self.field_values = common.get_test_field_data(ELEMENTS, TENSOR)
        self.field = Field(self.field_name,
                           self.field_values,
                           self.field_position,
                           self.field_type)

    def test_get_3d_field_values(self):
        """A 3d representation of a tensor field is obtained correctly."""
        _, field_values = common.get_test_field_data(ELEMENTS, TENSOR)
        field_values = np.asarray(field_values)
        zero_column = np.zeros((len(field_values), 1))
        field_values = np.hstack((field_values, zero_column, zero_column))

        np.testing.assert_array_equal(self.field.get_3d_field_values(),
                                      field_values)


class TestFieldExceptions(unittest.TestCase):
    """Tests related to exceptions occuring in the Fields class."""

    def test_field_position_exception(self):
        """ValueError is raised in case of an invalid field position."""
        with self.assertRaises(ValueError):
            Field("TEST_FIELD_NAME", [1, 2, 3], SCALAR, SCALAR)

    def test_field_type_exception(self):
        """ValueError is raised in case of an invalid field type."""
        with self.assertRaises(ValueError):
            Field("TEST_FIELD_NAME", [1, 2, 3], NODES, NODES)

    def test_1d_data_shape_exception(self):
        """ValueError is raised when scalar data does not have 1d shape."""
        with self.assertRaises(ValueError):
            Field("TEST_FIELD_NAME", [[1, 2], [3, 4], [5, 6]], NODES, SCALAR)


class TestElementRepository(unittest.TestCase):
    """Tests regarding the ElementRepository class."""

    def setUp(self):
        """Create an element repository for testing."""
        (self.node_tags,
         _,
         self.element_tags,
         self.element_types,
         self.connectivity) = common.get_test_mesh()

        self.repo = ElementRepository(self.element_tags,
                                      self.connectivity,
                                      self.element_types)

    def test_repository_creation(self):
        """An ElementRepository with correct attributes can be created based on element info."""
        np.testing.assert_array_equal(self.repo.tags, self.element_tags)
        np.testing.assert_array_equal(self.repo.types, self.element_types)
        assert all(np.all(i == j) for i, j in zip(self.repo.connectivity,
                                                  self.connectivity))
        assert all(self.repo.index_mapper[j] == i
                   for i, j in enumerate(self.element_tags))

    def test_add_group(self):
        """An element group can be added to the element repository."""
        group_name = "TEST_ELEMENT_GROUP"
        group_tags = [3, 1, 5]

        self.repo.add_group(group_name, group_tags)

        assert group_name in self.repo.groups.keys()
        np.testing.assert_array_equal(self.repo.groups[group_name],
                                      sorted(group_tags))
        del self.repo.groups[group_name]

    def test_get_node_tags(self):
        """The nodes of the elements in the repository can be obtained in correct order."""
        np.testing.assert_array_equal(self.repo.get_node_tags(),
                                      sorted(self.node_tags))

    def test_get_subset(self):
        """A repository subset can be generated from element tags."""
        subset_indices = [2, 0, 4]
        subset_tags = [self.element_tags[i] for i in subset_indices]
        subset_types = [self.element_types[i] for i in subset_indices]
        subset_conn = [self.connectivity[i] for i in subset_indices]
        subset = self.repo.get_subset(*subset_tags)

        np.testing.assert_array_equal(subset.tags, subset_tags)
        np.testing.assert_array_equal(subset.types, subset_types)
        assert all(np.all(i == j) for i, j in zip(subset.connectivity,
                                                  subset_conn))
        assert all(subset.index_mapper[j] == i for i, j in zip(subset_indices,
                                                               subset_tags))

    def test_get_subset_by_type(self):
        """A repository subset can be generated from element types."""
        subset_indices = [2, 3, 4]  # All triangle elements
        subset_tags = [self.element_tags[i] for i in subset_indices]
        subset_types = [self.element_types[i] for i in subset_indices]
        subset_conn = [self.connectivity[i] for i in subset_indices]
        subset = self.repo.get_subset(*subset_tags)
        subset = self.repo.get_subset_by_type(subset_types[0])

        np.testing.assert_array_equal(subset.tags, subset_tags)
        np.testing.assert_array_equal(subset.types, subset_types)
        assert all(np.all(i == j) for i, j in zip(subset.connectivity,
                                                  subset_conn))
        assert all(subset.index_mapper[j] == i for i, j in zip(subset_indices,
                                                               subset_tags))

    def test_wrong_input_shapes_exception(self):
        """AssertionError is raised in case of wrong input array shapes."""
        with self.assertRaises(AssertionError):
            ElementRepository([1, 2, 3], [[1, 2, 3]], [1, 2])

    def test_group_with_wrong_tags_exception(self):
        """AssertionError is raised in case the group tags do not exist."""
        with self.assertRaises(AssertionError):
            self.repo.add_group("WRONG_GROUP", [100, 200, 300])

    def test_group_with_existing_name_exception(self):
        """AssertionError is raised in case the group tags do not exist."""
        self.repo.add_group("EXISTING_GROUP", [1, 2, 3])
        with self.assertRaises(AssertionError):
            self.repo.add_group("EXISTING_GROUP", [4, 5])


class TestNodeRepository(unittest.TestCase):
    """Tests regarding the node repository class."""

    def setUp(self):
        """Create a node repository for testing."""
        self.node_tags, self.node_coords, _, _, _ = common.get_test_mesh()
        self.repo = NodeRepository(self.node_tags, self.node_coords)

    def test_repository_creation(self):
        """A NodeRepository can be created based on node info."""
        np.testing.assert_array_equal(self.repo.tags, self.node_tags)
        np.testing.assert_array_equal(self.repo.coordinates, self.node_coords)
        assert all(self.repo.index_mapper[j] == i
                   for i, j in enumerate(self.node_tags))

    def test_get_subset(self):
        """A repository subset can be generated from node tags."""
        subset_indices = [2, 0, 4]
        subset_tags = [self.node_tags[i] for i in subset_indices]
        subset_coords = [self.node_coords[i] for i in subset_indices]
        subset = self.repo.get_subset(*subset_tags)

        np.testing.assert_array_equal(subset.tags, subset_tags)
        np.testing.assert_array_equal(subset.coordinates, subset_coords)
        assert all(subset.index_mapper[j] == i for i, j in zip(subset_indices,
                                                               subset_tags))

    def test_wrong_input_shapes_exception(self):
        """AssertionError is raised in case of wrong input array shapes."""
        with self.assertRaises(AssertionError):
            NodeRepository([1, 2, 3], [[1, 2], [3, 4]])


class TestElementFieldRepository(unittest.TestCase):
    """Tests regarding the ElementFieldRepository class."""

    def setUp(self):
        """Create an ElementFieldRepository and some fields for testing."""
        _, scalar_field_vals = common.get_test_field_data(ELEMENTS, SCALAR)
        _, vector_field_vals = common.get_test_field_data(ELEMENTS, VECTOR)
        _, tensor_field_vals = common.get_test_field_data(ELEMENTS, TENSOR)

        self.scalar_fields = [
            Field("SCALAR_FIELD_1", scalar_field_vals, ELEMENTS, SCALAR),
            Field("SCALAR_FIELD_2", scalar_field_vals, ELEMENTS, SCALAR)
        ]

        self.vector_fields = [
            Field("VECTOR_FIELD_1", vector_field_vals, ELEMENTS, VECTOR),
            Field("VECTOR_FIELD_2", vector_field_vals, ELEMENTS, VECTOR)
        ]

        self.tensor_fields = [
            Field("TENSOR_FIELD_1", tensor_field_vals, ELEMENTS, TENSOR),
            Field("TENSOR_FIELD_2", tensor_field_vals, ELEMENTS, TENSOR)
        ]

        self.repo = ElementFieldRepository()

        # Add fields to the repository
        for field in (self.scalar_fields
                      + self.vector_fields
                      + self.tensor_fields):
            self.repo.add_field(field)

    def test_add_field(self):
        """Element fields can be added successfully to the repository."""
        field_names = {"SCALAR_FIELD_1", "SCALAR_FIELD_2", "VECTOR_FIELD_1",
                       "VECTOR_FIELD_2", "TENSOR_FIELD_1", "TENSOR_FIELD_2"}
        assert field_names == set(self.repo.fields.keys())
        assert self.repo.fields["SCALAR_FIELD_1"] is self.scalar_fields[0]

    def test_get_fields_by_type(self):
        """Element fields are obtained correctly based on their type."""
        scalar_fields = self.repo.get_fields_by_type(SCALAR)
        vector_fields = self.repo.get_fields_by_type(VECTOR)
        tensor_fields = self.repo.get_fields_by_type(TENSOR)

        assert set(self.scalar_fields) == set(scalar_fields)
        assert set(self.vector_fields) == set(vector_fields)
        assert set(self.tensor_fields) == set(tensor_fields)

    def test_field_position_exception(self):
        """ValueError is raised in case a node field is added to the repository."""
        node_field = Field("TENSOR_FIELD_1", [1, 2, 3], NODES, SCALAR)
        with self.assertRaises(ValueError):
            self.repo.add_field(node_field)


class TestNodeFieldRepository(unittest.TestCase):
    """Tests regarding the NodeFieldRepository class."""

    def setUp(self):
        """Create a NodeFieldRepository and some fields for testing."""
        _, scalar_field_vals = common.get_test_field_data(NODES, SCALAR)
        _, vector_field_vals = common.get_test_field_data(NODES, VECTOR)
        _, tensor_field_vals = common.get_test_field_data(NODES, TENSOR)

        self.scalar_fields = [
            Field("SCALAR_FIELD_1", scalar_field_vals, NODES, SCALAR),
            Field("SCALAR_FIELD_2", scalar_field_vals, NODES, SCALAR)
        ]

        self.vector_fields = [
            Field("VECTOR_FIELD_1", vector_field_vals, NODES, VECTOR),
            Field("VECTOR_FIELD_2", vector_field_vals, NODES, VECTOR)
        ]

        self.tensor_fields = [
            Field("TENSOR_FIELD_1", tensor_field_vals, NODES, TENSOR),
            Field("TENSOR_FIELD_2", tensor_field_vals, NODES, TENSOR)
        ]

        self.repo = NodeFieldRepository()

        # Add fields to the repository
        for field in (self.scalar_fields
                      + self.vector_fields
                      + self.tensor_fields):
            self.repo.add_field(field)

    def test_add_field(self):
        """Node fields can be added successfully to the repository."""
        field_names = {"SCALAR_FIELD_1", "SCALAR_FIELD_2", "VECTOR_FIELD_1",
                       "VECTOR_FIELD_2", "TENSOR_FIELD_1", "TENSOR_FIELD_2"}
        assert field_names == set(self.repo.fields.keys())
        assert self.repo.fields["SCALAR_FIELD_1"] is self.scalar_fields[0]

    def test_get_fields_by_type(self):
        """Node fields are obtained correctly based on their type."""
        scalar_fields = self.repo.get_fields_by_type(SCALAR)
        vector_fields = self.repo.get_fields_by_type(VECTOR)
        tensor_fields = self.repo.get_fields_by_type(TENSOR)

        assert set(self.scalar_fields) == set(scalar_fields)
        assert set(self.vector_fields) == set(vector_fields)
        assert set(self.tensor_fields) == set(tensor_fields)

    def test_field_position_exception(self):
        """ValueError is raised in case a node field is added to the repository."""
        element_field = Field("TENSOR_FIELD_1", [1, 2, 3], ELEMENTS, SCALAR)
        with self.assertRaises(ValueError):
            self.repo.add_field(element_field)


class TestParaqusModelCreation(unittest.TestCase):
    """Test class for ParaqusModel creation."""

    def setUp(self):
        """Create a small ParaqusModel."""
        self.model = common.get_test_model()

    def test_model_creation(self):
        """A ParaqusModel can be created based on mesh info."""
        assert self.model.model_name == "TEST_MODEL"
        assert self.model.part_name == "TEST_PART"
        assert self.model.step_name == "TEST_STEP"
        assert len(self.model.nodes) == 8
        assert len(self.model.elements) == 5


class TestParaqusModelFields(unittest.TestCase):
    """Tests for methods dealing with fields withing a ParaqusModel."""

    def setUp(self):
        """Create a small ParaqusModel."""
        self.model = common.get_test_model()

    def test_add_node_field(self):
        """Node fields can be added to models."""
        field_tags, field_vals = common.get_test_field_data(NODES, SCALAR)
        self.model.add_field("NODE_FIELD", field_tags, field_vals, NODES,
                             SCALAR)

        assert "NODE_FIELD" in self.model.node_fields.keys()
        del self.model.node_fields["NODE_FIELD"]

    def test_add_element_field(self):
        """Element fields can be added to models."""
        field_tags, field_vals = common.get_test_field_data(ELEMENTS, VECTOR)
        self.model.add_field("ELEMENT_FIELD", field_tags, field_vals, ELEMENTS,
                             VECTOR)

        assert "ELEMENT_FIELD" in self.model.element_fields.keys()
        del self.model.element_fields["ELEMENT_FIELD"]

    def test_pad_scalar_field_values(self):
        """Missing values in scalar fields are padded with NaNs."""
        field_tags, field_vals = common.get_test_field_data(ELEMENTS, SCALAR)

        # Assume there is no field value available for the last element
        field_tags = field_tags[:-1]
        field_vals = field_vals[:-1]

        self.model.add_field("SCALAR_PAD_FIELD", field_tags, field_vals,
                             ELEMENTS, SCALAR)
        field = self.model.get_element_field("SCALAR_PAD_FIELD")

        # Reference is a column array with NaN in last position
        ref_field_vals = [[i] for i in field_vals]
        ref_field_vals.append([np.nan])

        np.testing.assert_array_equal(field.field_values, ref_field_vals)
        del self.model.element_fields["SCALAR_PAD_FIELD"]

    def test_pad_vector_field_values(self):
        """Missing values in vector fields are padded with NaNs."""
        field_tags, field_vals = common.get_test_field_data(NODES, VECTOR)

        # Assume there is no field value available for the last element
        field_tags = field_tags[:-1]
        field_vals = field_vals[:-1]

        self.model.add_field("VECTOR_PAD_FIELD", field_tags, field_vals,
                             NODES, VECTOR)
        field = self.model.get_node_field("VECTOR_PAD_FIELD")

        # Reference is an array with NaNs in last row
        field_vals.append([np.nan]*2)

        np.testing.assert_array_equal(field.field_values, field_vals)
        del self.model.node_fields["VECTOR_PAD_FIELD"]

    def test_pad_tensor_field_values(self):
        """Missing values in tensor fields are padded with NaNs."""
        field_tags, field_vals = common.get_test_field_data(ELEMENTS, TENSOR)

        # Assume there is no field value available for the last element
        field_tags = field_tags[:-1]
        field_vals = field_vals[:-1]

        self.model.add_field("TENSOR_PAD_FIELD", field_tags, field_vals,
                             ELEMENTS, TENSOR)
        field = self.model.get_element_field("TENSOR_PAD_FIELD")

        # Reference is an array with NaN in last row
        field_vals.append([np.nan]*4)

        np.testing.assert_array_equal(field.field_values, field_vals)
        del self.model.element_fields["TENSOR_PAD_FIELD"]

    def test_get_node_fields_by_type(self):
        """Node fields can be requested based on the field type."""
        scalar_tags, scalar_vals = common.get_test_field_data(NODES, SCALAR)
        vector_tags, vector_vals = common.get_test_field_data(NODES, VECTOR)
        tensor_tags, tensor_vals = common.get_test_field_data(NODES, TENSOR)

        self.model.add_field("SCALAR_FIELD", scalar_tags, scalar_vals, NODES,
                             SCALAR)
        self.model.add_field("VECTOR_FIELD", vector_tags, vector_vals, NODES,
                             VECTOR)
        self.model.add_field("TENSOR_FIELD", tensor_tags, tensor_vals, NODES,
                             TENSOR)

        scalar_fields = self.model.get_fields_by_type(SCALAR, NODES)
        vector_fields = self.model.get_fields_by_type(VECTOR, NODES)
        tensor_fields = self.model.get_fields_by_type(TENSOR, NODES)

        assert len(scalar_fields) == 1
        assert len(vector_fields) == 1
        assert len(tensor_fields) == 1
        assert scalar_fields[0].field_type == SCALAR
        assert vector_fields[0].field_type == VECTOR
        assert tensor_fields[0].field_type == TENSOR

        del self.model.node_fields["SCALAR_FIELD"]
        del self.model.node_fields["VECTOR_FIELD"]
        del self.model.node_fields["TENSOR_FIELD"]

    def test_get_element_fields_by_type(self):
        """Element fields can be requested based on the field type."""
        scalar_tags, scalar_vals = common.get_test_field_data(ELEMENTS,
                                                              SCALAR)
        vector_tags, vector_vals = common.get_test_field_data(ELEMENTS,
                                                              VECTOR)
        tensor_tags, tensor_vals = common.get_test_field_data(ELEMENTS,
                                                              TENSOR)

        self.model.add_field("SCALAR_FIELD", scalar_tags, scalar_vals,
                             ELEMENTS, SCALAR)
        self.model.add_field("VECTOR_FIELD", vector_tags, vector_vals,
                             ELEMENTS, VECTOR)
        self.model.add_field("TENSOR_FIELD", tensor_tags, tensor_vals,
                             ELEMENTS, TENSOR)

        scalar_fields = self.model.get_fields_by_type(SCALAR, ELEMENTS)
        vector_fields = self.model.get_fields_by_type(VECTOR, ELEMENTS)
        tensor_fields = self.model.get_fields_by_type(TENSOR, ELEMENTS)

        assert len(scalar_fields) == 1
        assert len(vector_fields) == 1
        assert len(tensor_fields) == 1
        assert scalar_fields[0].field_type == SCALAR
        assert vector_fields[0].field_type == VECTOR
        assert tensor_fields[0].field_type == TENSOR

        del self.model.element_fields["SCALAR_FIELD"]
        del self.model.element_fields["VECTOR_FIELD"]
        del self.model.element_fields["TENSOR_FIELD"]


class TestParaqusModelSplitting(unittest.TestCase):
    """Tests to check if a ParaqusModel is partitioned correctly."""

    def setUp(self):
        """Create a small ParaqusModel."""
        self.model = common.get_test_model()

        # Add fields
        field_tags, field_vals = common.get_test_field_data(ELEMENTS, SCALAR)
        self.model.add_field("ELEMENT_FIELD", field_tags, field_vals, ELEMENTS,
                             SCALAR)
        field_tags, field_vals = common.get_test_field_data(NODES, VECTOR)
        self.model.add_field("NODE_FIELD", field_tags, field_vals, NODES,
                             VECTOR)

        # Add groups
        self.model.add_element_group("ELEMENT_GROUP", self.model.elements.tags)
        self.model.add_node_group("NODE_GROUP", self.model.nodes.tags)

        # Create two submodels
        self.submodels = list(self.model.split_model(2))

    def test_partition_model(self):
        """The model can be split into multiple submodels."""
        assert len(self.submodels) == 2
        assert all(len(m.elements.tags) > 0 for m in self.submodels)

        sub_element_tags_1 = self.submodels[0].elements.tags
        sub_element_tags_2 = self.submodels[1].elements.tags

        # Elements can only be in one submodel
        assert set(self.model.elements.tags) == (set(sub_element_tags_1)
                                                 ^ set(sub_element_tags_2))

        sub_node_tags_1 = self.submodels[0].nodes.tags
        sub_node_tags_2 = self.submodels[1].nodes.tags

        # Nodes can be shared
        assert set(self.model.nodes.tags) == (set(sub_node_tags_1)
                                              | set(sub_node_tags_2))

    def test_partition_fields(self):
        """The fields are partitioned correctly."""
        element_field = self.model.get_element_field("ELEMENT_FIELD")
        element_sub_field_1 = self.submodels[0].get_element_field(
            "ELEMENT_FIELD")
        element_sub_field_2 = self.submodels[1].get_element_field(
            "ELEMENT_FIELD")

        # Values at elements must be in one submodel
        assert set(element_field.field_values.reshape(-1)) == (
            set(element_sub_field_1.field_values.reshape(-1))
            ^ set(element_sub_field_2.field_values.reshape(-1)))

        node_field = self.model.get_node_field("NODE_FIELD")
        node_sub_field_1 = self.submodels[0].get_node_field("NODE_FIELD")
        node_sub_field_2 = self.submodels[1].get_node_field("NODE_FIELD")

        # Values at nodes can be shared
        assert set(node_field.field_values.reshape(-1)) == (
            set(node_sub_field_1.field_values.reshape(-1))
            | set(node_sub_field_2.field_values.reshape(-1)))

    def test_partition_groups(self):
        """The node and element groups are partitioned correctly."""
        element_group = self.model.elements.groups[
            "ELEMENT_GROUP"]
        element_sub_group_1 = self.submodels[0].elements.groups[
            "ELEMENT_GROUP"]
        element_sub_group_2 = self.submodels[1].elements.groups[
            "ELEMENT_GROUP"]

        assert set(element_group) == (set(element_sub_group_1)
                                      ^ set(element_sub_group_2))

        node_group = self.model.nodes.groups["NODE_GROUP"]
        node_sub_group_1 = self.submodels[0].nodes.groups["NODE_GROUP"]
        node_sub_group_2 = self.submodels[1].nodes.groups["NODE_GROUP"]

        assert set(node_group) == (set(node_sub_group_1)
                                   | set(node_sub_group_2))
