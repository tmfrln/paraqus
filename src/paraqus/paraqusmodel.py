# -*- coding: utf-8 -*-
"""
This module containts all classes that contribute to paraqus models,
i.e. not just the model class itself but also repositories for nodes,
elements and fields.

"""
import itertools
import warnings
import numpy as np
from abc import ABCMeta, abstractmethod

from constants import USER, NODES, ELEMENTS, SCALAR, VECTOR, TENSOR


class ParaqusModel(object):
    """
    Paraqus representation of a finite element model.

    The paraqus model can be used to manipulate and export any finite
    element model as a set of VTK files.

    Parameters
    ----------
    element_tags : Sequence
        Tags of all elements being part of the model. Tags have to be
        unique.
    connectivity : Sequence of Sequence
        Connectivity list in order of the element tags. The respective
        nodes have to be in order as defined for VTK cells.
    element_types : Sequence
        The VTK cell types for all elements in order of the element
        tags.
    node_tags : Sequence
        Tags of all nodes being part of the model. Tags have to be
        unique.
    node_coords : Sequence of Sequence
        Nodal coordinates in order of the node tags. The coordinates
        can be defined in 1d-, 2d- or 3d-space as an array of shape
        (number of nodes x number of dimensions).
    model_name : str, optional
        Name of the main model. In case of multiple frames or parts
        every paraqus model should have the same mode name. Default is
        'MODEL NAME'.
    part_name : str, optional
        Name of the part instance. Default is 'PART NAME'.
    step_name : str, optional
        Name of the load step. Default is 'STEP NAME'.
    frame_tag : int, optional
        Tag of the current freame. Default is the absolute number of
        defined paraqus models.
    frame_time : float, optional
        Current frame time. Default is the absolute number of defined
        paraqus models.
    source : ParaqusConstant, optional
        This is just for informational purpose and defines the source
        of the model, e.g. ABAQUS. Default is USER.

    Attributes
    ----------
    model_name : str
        Name of the main model.
    part_name : str
        Name of the part instance.
    step_name : str
        Name of the load step.
    frame_tag : int
        Tag of the frame.
    frame_time : float
        Current frame time of the model frame.
    source : ParaqusConstant
        This is a constant for informational purpose and describes the
        source of the model, e.g. ABAQUS or USER.
    elements : ElementRepository
        A repository storing all information on elements, e.g. tags and
        element types.
    nodes : NodeRepository
        Repository storing all information on nodes, e.g. tags and
        coordinates.
    node_fields : NodeFieldRepository
        Repository storing all node fields.
    element_fields : ElementRepository
        Repository sotring all element fields.

    Methods
    -------
    add_field
        Add a field to the paraqus model.
    add_node_group
        Add a node group to the model.
    add_element_group
        Add an element group to the model.
    extract_submodel_by_elements
        Extract a submodel based on element tags.
    get_fields_by_type
        Extract all stored fields of a specific type, e.g. all
        scalar element fields.
    get_node_field
        Extract a node field by its name.
    get_element_field
        Extract an element field by its name.

    Example
    -------
    >>> import numpy as np
    >>> from paraqusmodel import ParaqusModel
    >>> from writers import BinaryWriter
    >>>
    >>> # Define the model parameters
    >>> element_tags = np.array([1,2])
    >>> connectivity = [np.array([1,2,3,4]),np.array([4,3,5])]
    >>> element_types = np.array([9,5])
    >>> node_tags = np.array([1,2,3,4,5])
    >>> node_coords = np.array([[0,0],[1,0],[1,1],[0,1],[0.5,1.5]])
    >>>
    >>> # Create a new model
    >>> model = ParaqusModel(element_tags,
    >>>                      connectivity,
    >>>                      element_types,
    >>>                      node_tags,
    >>>                      node_coords,
    >>>                      model_name="foo",
    >>>                      part_name="bar",
    >>>                      step_name="foobar",
    >>>                      frame_tag=1,
    >>>                      frame_time=0.1)
    >>>
    >>> # Export model as VTK
    >>> writer = BinaryWriter()
    >>> writer.initialise_collection()
    >>> writer.write(model)
    >>> writer.finalize_collection()

    """

    model_counter = 0

    def __init__(self,
                 element_tags,
                 connectivity,
                 element_types,
                 node_tags,
                 node_coords,
                 **kwargs):

        # Check keyword arguments
        self.model_name = kwargs.pop("model_name", "MODEL NAME")
        self.part_name = kwargs.pop("part_name", "PART NAME")
        self.step_name = kwargs.pop("step_name", "STEP NAME")
        self.frame_tag = kwargs.pop("frame_tag", ParaqusModel.model_counter)
        self.frame_time = kwargs.pop("frame_time", ParaqusModel.model_counter)
        self.source = kwargs.pop("source", USER)

        # Check for unrecognized kwargs
        if len(kwargs) > 0:
            err_msg = "Unrecognized kwarg: '{}'.".format(str(kwargs.keys()[0]))
            raise ValueError(err_msg)

        # Create model geometry
        self.elements = ElementRepository(element_tags, connectivity,
                                          element_types)
        self.nodes = NodeRepository(node_tags, node_coords)

        # Add field repositories
        self.node_fields = NodeFieldRepository()
        self.element_fields = ElementFieldRepository()

        ParaqusModel.model_counter += 1


    # Methods
    def __str__(self):
        """String representation of the model."""
        description = ("ParaqusModel\n"
                       + "  model_name: '" + self.model_name + "'\n"
                       + "  part_name:  '" + self.part_name + "'\n"
                       + "  step_name:  '" + self.step_name + "'\n"
                       + "  frame_tag:   " + str(self.frame_tag) + "\n")

        return description

    def add_field(self, field_name, field_tags, field_values,
                         field_position, field_type):
        """
        Add a field to the model.

        The field will also be part of any exported VTK model.

        Parameters
        ----------
        field_name : str
            Name of the field.
        field_tags : numpy.ndarray
            Tags of the nodes or elements at which the field is stored.
        field_values : Sequence
            Values of the field in order of the field tags. At nodes or
            elements that are not part of the field tags, the values will be
            set to NaN automatically.
        field_position : ParaqusConstant
            A constant defining the storage position of the field, i.e.
            NODES or ELEMENTS.
        field_type : ParaqusConstant
            A constant defining the field type, i.e. SCALAR, VECTOR or
            TENSOR.

        Returns
        -------
        None.

        """
        # Create field object
        # An error will be thrown in case of invalid choices
        # of field_position and field_type
        field = Field(field_name, field_values,
                            field_position, field_type)

        # Add a node field
        if field_position == NODES:

            if len(self.nodes.tags) < len(field_tags):
                msg = ("Values array '{}'".format(field_name)
                       + " has more entries than the model has nodes.")
                raise ValueError(msg)

            # If there are more nodes than field values set the missing
            # value to nan
            elif len(self.nodes.tags) > len(field_tags):
                field.field_values = self._pad_field_values(field_tags,
                                                            field_values,
                                                            self.nodes.tags)

            self.node_fields.add_field(field)

        # Add an element field
        elif field_position == ELEMENTS:

            if len(self.elements.tags) < len(field_tags):
                msg = ("Values array '{}'".format(field_name)
                       + " has more entries than the model has elements.")
                raise ValueError(msg)

            # If there are more elements than field values set the
            # missing value to nan
            elif len(self.elements.tags) > len(field_tags):
                field.field_values = self._pad_field_values(field_tags,
                                                            field_values,
                                                            self.elements.tags)

            self.element_fields.add_field(field)

        else:
            msg = "Invalid field position: {}.".format(field_position)
            raise ValueError(msg)

    def add_node_group(self, group_name, node_tags):
        """
        Add a node group to the model.

        The nodes must have been added beforehand, this method just
        stores the information that they form a named group.

        Parameters
        ----------
        group_name : str
            Name of the group. Must be unique.
        node_tags : Sequence
            Integer tags of the nodes in the group.

        Returns
        -------
        None.

        """
        self.nodes.add_group(group_name, node_tags)

    def add_element_group(self, group_name, element_tags):
        """
        Add an element group to the model.

        The elements must have been added beforehand, this method just
        stores the information that the elements form a named group.

        Parameters
        ----------
        group_name : str
            Name of the group. Must be unique.
        element_tags : Sequence
            Integer tags of the elements in the group.

        Returns
        -------
        None.

        """
        self.elements.add_group(group_name, element_tags)

    def extract_submodel_by_elements(self, element_tags):
        """
        Extract a submodel based on element tags.

        Parameters
        ----------
        element_tags : Sequence
            List of tags of the elements that will be part of the
            submodel.

        Returns
        -------
        submodel : ParaqusModel
            The resulting submodel including all fields and groups.

        """
        # Get nodes and elements of the current piece
        sub_element_repo = self.elements.get_subset(*element_tags)
        node_tags = sub_element_repo.get_node_tags()
        sub_node_repo = self.nodes.get_subset(*node_tags)

        # Create a new paraqus model representing the submodel
        submodel = ParaqusModel(sub_element_repo.tags,
                             sub_element_repo.connectivity,
                             sub_element_repo.types,
                             sub_node_repo.tags,
                             sub_node_repo.coordinates,
                             model_name=self.model_name,
                             part_name=self.part_name,
                             step_name=self.step_name,
                             frame_tag=self.frame_tag,
                             frame_time=self.frame_time,
                             source=self.source)

        # Add field to the submodel
        for nf in self.node_fields.get_subset(sub_node_repo):
            submodel.node_fields.add_field(nf)

        for ef in self.element_fields.get_subset(sub_element_repo):
            submodel.element_fields.add_field(ef)

        # Add groups to the submodel
        for group_name, group_elements in sub_element_repo.groups.items():
            submodel.add_element_group(group_name, group_elements)

        for group_name, group_nodes in sub_node_repo.groups.items():
            submodel.add_node_group(group_name, group_nodes)

        return submodel

    def get_fields_by_type(self, field_type, field_position):
        """
        Return all fields of a specific type, e.g. of type SCALAR.

        Fields stored at nodes as well as fields stored at elements can be
        returned.

        Parameters
        ----------
        field_type : ParaqusConstant
            Type of the field, i.e. TENSOR, VECTOR or SCALAR.
        field_position : ParaqusConstant
            Position of the field, i.e. NODES or ELEMENTS.

        Returns
        -------
        list of Field
            All fields that match the requested type and position.

        """
        if field_position == NODES:
            return self.node_fields.get_fields_by_type(field_type)

        elif field_position == ELEMENTS:
            return self.element_fields.get_fields_by_type(field_type)

        else:
            msg = "Invalid field position: {}".format(field_position)
            raise Exception(msg)

    def get_node_field(self, field_name):
        """
        Request a node field of a given name.

        If there is no field found, None will be returned.

        Parameters
        ----------
        field_name : str
            Name of the requested node field.

        Returns
        -------
        Field
            The requested field.

        """
        return self.node_fields[field_name]

    def get_element_field(self, field_name):
        """
        Request an element field of a given name.

        If there is no field found, None will be returned.

        Parameters
        ----------
        field_name : str
            Name of the requested element field.

        Returns
        -------
        Field
            The requested field.

        """
        return self.element_fields[field_name]

    def _pad_field_values(self, field_tags, field_values, pad_tags):
        """Extend a field value array with nan values for unset tags."""
        field_values = field_values.reshape(len(field_values), -1)

        if all(np.in1d(field_tags, pad_tags)):
            # All field tags are there, so we pad the values

            # Indices of the field_tags in pad_tags
            sorter = np.argsort(pad_tags)
            indices = sorter[np.searchsorted(pad_tags, field_tags,
                                             sorter=sorter)]

            # New array pre-filled with nans
            shape = (len(pad_tags), field_values.shape[1])

            new_field_values = np.empty(shape, dtype=field_values.dtype)
            new_field_values[:,:] = np.nan

            # Fill in the old values
            new_field_values[indices,:] = field_values

            return new_field_values

        else:
            raise ValueError("Cannot pad values: not all tags are found.")


class ElementRepository(object):
    """
    Repository to store a set of elements.

    Parameters
    ----------
    element_tags : Sequence
        Tags of all elements that will be stored in the repository.
    connectivity : Sequence of Sequence
        Connectivity of all elements in order of the element tags.
    element_types : Sequence
        Type of all elements in order of the element tags.

    Attributes
    ----------
    tags : numpy.ndarray
        Tags of all elements stored in the repository.
    connectivity : list of numpy.ndarray
        Connectivity list of all elements in the same order as the tags.
    types : numpy.ndarray
        Types of all elements in the same order as the tags.
    index_mapper : dict
        Mapping element tag -> index in list of tags.
    groups : dict
        Mapping group name -> element tags.

    Methods
    -------
    add_group
        Add an element group to the repository.
    get_subset
        Create a new ElementRepository containing only a subset of
        elements based on element tags.
    get_subset_by_type
        Create a new ElementRepository containing only a subset of
        elements based on element types.
    get_node_tags
        Get the tags of the nodes needed for all elements in the
        repository.

    """

    def __init__(self,
                 element_tags,
                 connectivity,
                 element_types):

        assert len(element_tags) == len(connectivity) == len(element_types)

        # The connectivity cannot be stored as one array in case of
        # elements with different numbers of element nodes
        self.tags = element_tags
        self.connectivity = connectivity
        self.types = element_types
        self.groups = {}


    # Properties
    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, element_tags):

        self._tags = np.array(element_tags).reshape(-1)
        self.index_mapper = dict(zip(element_tags, range(len(element_tags))))

    @property
    def connectivity(self):
        return self._connectivity

    @connectivity.setter
    def connectivity(self, connectivity):
        self._connectivity = [np.array(c).reshape(-1) for c in connectivity]

    @property
    def types(self):
        return self._types

    @types.setter
    def types(self, element_types):
        self._types = np.array(element_types,
                               dtype=np.uint8).reshape(-1)


    # Methods
    def __getitem__(self, key):
        """Index-based access."""
        if key > len(self) - 1:
            raise IndexError("Index out of bounds: {}.".format(key))

        return (self.tags[key], self.connectivity[key],
                self.types[key], self.index_mapper[self.tags[key]])

    def __iter__(self):
        """Repository iterator."""
        for i in range(len(self)):
            yield self[i]

    def __len__(self):
        """Repository size."""
        return len(self.tags)

    def add_group(self, group_name, element_tags):
        """
        Add an element group to the repository.

        The elements must have been added beforehand, this method just
        stores the information that the elements form a named group.

        Parameters
        ----------
        group_name : str
            Name of the group. Must be unique.
        element_tags : Sequence
            Integer tags of the elements in the group.

        Returns
        -------
        None.

        """
        assert group_name not in self.groups, \
            "Group '{}' already exists.".format(group_name)

        assert set(element_tags) <= set(self.tags), \
            "Some element tags in the set are not in the model."

        element_tags = np.asarray(element_tags)
        element_tags.sort()
        self.groups[group_name] = element_tags


    def get_subset(self, *element_tags):
        """
        Create a new ElementRepository containing only a subset of elements.

        The subset contains all elements with the requested tags.

        Parameters
        ----------
        *element_tags : Sequence
            Elements that will be contained in the new repository.

        Returns
        -------
        ElementRepository
            Repository containing the elements of the subset.

        """
        # If there is in anvalid element tag, an error will be raised
        # by the index mapper, thus there is no need to check for valid
        # inputs here
        indices = np.array([self.index_mapper[e]
                            for e in element_tags])

        tags = self.tags[indices]
        connectivity = [self.connectivity[i] for i in indices]
        types = self.types[indices]

        # Generate a new element repository to return
        return_repo = ElementRepository(tags, connectivity, types)

        # Make sure the indices are coherent with the original model
        return_repo.index_mapper = dict(zip(tags, indices))

        # Extract group elements that are present in the subset
        for group_name, group_tags in self.groups.items():
            new_group_tags = np.intersect1d(group_tags, element_tags)
            return_repo.add_group(group_name, new_group_tags)

        return return_repo

    def get_subset_by_type(self, *element_types):
        """
        Create a new ElementRepository containing only a subset of elements.

        The subset contains all elements of the requested VTK types.

        Parameters
        ----------
        *element_types : Sequence
            Types of the elements that will be part of the repository.
            The element types must follow the VTK type convention.

        Returns
        -------
        ElementRepository
            Repository containing the elements of the subset.

        """
        indices = []
        for element_type in element_types:
            indices.append(np.asarray(self.types == element_type)
                           .nonzero()[0])

        # Flatten the list of indices
        indices = np.concatenate(indices)

        # Return None in case nothing was found
        if len(indices) == 0:
            return None

        # Build the new repo
        tags = self.tags[indices]
        connectivity = [self.connectivity[i] for i in indices]
        types = self.types[indices]

        return_repo = ElementRepository(tags, connectivity, types)
        return_repo.index_mapper = dict(zip(tags, indices))

        return return_repo

    def get_node_tags(self):
        """
        Return an array of node tags used for the element in the repository.

        Returns
        -------
        tags : numpy.ndarray
            Sorted node tags.

        """
        tags = np.unique(list(itertools.chain(*self.connectivity)))
        tags.sort()
        return tags


class NodeRepository(object):
    """
    Repository to store a set of nodes.

    Parameters
    ----------
    node_tags : Sequence
        Tags of all nodes that will be stored in the repository.
    node_coords : Sequence of Sequence
        Nodal coordinates in order of the node tags. The coordinates
        can be defined in 1d-, 2d- or 3d-space as an array of shape
        (number of nodes x number of dimensions).

    Attributes
    ----------
    tags : numpy.ndarray
        Tags of all nodes stored in the repository.
    coordinates : numpy.ndarray
        Coordinates of all nodes in order of the node tags.
    index_mapper : dict
        Mapping node tag -> index in list of tags.
    groups : dict
        Mapping group name -> node tags.

    Methods
    -------
    add_group
        Add a node group to the repository.
    get_subset
        Create a new NodeRepository containing only a subset of nodes
        based on node tags.

    """

    def __init__(self,
                 node_tags,
                 node_coords):

        assert len(node_tags) == len(node_coords)

        self.tags = node_tags
        self.coordinates = node_coords
        self.groups = {}

    # Properties
    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, node_tags):

        self._tags = np.array(node_tags).reshape(-1)
        self.index_mapper = dict(zip(node_tags, range(len(node_tags))))

    @property
    def coordinates(self):
        return self._coordinates

    @coordinates.setter
    def coordinates(self, node_coords):

        node_coords = np.array(node_coords)
        rows, columns = node_coords.shape

        if columns == 3:
            pass
        elif columns == 2:
            node_coords = np.hstack((node_coords, np.zeros((rows,1))))
        elif columns == 1:
            node_coords = np.hstack((node_coords, np.zeros((rows,2))))
        else:
            msg = "Invalid nodal coordinates."
            raise ValueError(msg)

        self._coordinates = node_coords


    # Methods
    def __getitem__(self, key):
        """Index-based access."""
        return (self.tags[key], self.coordinates[key],
                self.index_mapper[self.tags[key]])

    def __iter__(self):
        """Repository iterator."""
        for i in range(len(self)):
            yield self[i]

    def __len__(self):
        """Repository size."""
        return len(self.tags)

    def add_group(self, group_name, node_tags):
        """
        Add a node group to the repository.

        The nodes must have been added beforehand, this method just
        stores the information that they form a named group.

        Parameters
        ----------
        group_name : str
            Name of the group. Must be unique.
        node_tags : Sequence
            Integer tags of the nodes in the group.

        Returns
        -------
        None.

        """
        assert group_name not in self.groups, \
            "Group '{}' already exists.".format(group_name)

        assert set(node_tags) <= set(self.tags), \
            "Some node tags in the set are not in the model."

        node_tags = np.asarray(node_tags)
        node_tags.sort()
        self.groups[group_name] = node_tags

    def get_subset(self, *node_tags):
        """
        Create a new NodeRepository containing only a subset of nodes.

        The subset contains all nodes with the requested tags.

        Parameters
        ----------
        *node_tags : Sequence
            Nodes that will be contained in the new repository.

        Returns
        -------
        NodeRepository
            Repository containing the nodes of the subset.

        """
        # If there is in anvalid element tag, an error will be raised
        # by the index mapper, thus there is no need to check for valid
        # inputs here
        indices = np.array([self.index_mapper[n] for n in node_tags])

        tags = self.tags[indices]
        coords = self.coordinates[indices]

        # Generate a new element repository to return
        return_repo = NodeRepository(tags, coords)

        # make sure the indices are coherent with the original model
        return_repo.index_mapper = dict(zip(tags, indices))

        # extract group elements that are present in the subset
        for group_name, group_tags in self.groups.items():
            new_group_tags = np.intersect1d(group_tags, node_tags)
            return_repo.add_group(group_name, new_group_tags)

        return return_repo


class FieldRepositoryBaseClass(object):
    """
    Base class for field repositories.

    Attributes
    ----------
    fields : dict
        Mapping field name -> Field.

    Methods
    -------
    get_fields_by_type
        Export fields based on the field type.
    add_field
        Add a new field to the repository.
    get_subset
        Export fields for a subset of nodes or elements.

    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self.fields = {}

    def __getitem__(self, field_name):
        """Key-based access."""
        return self.fields[field_name]

    def __iter__(self):
        """Repository iterator."""
        return self.fields.values().__iter__()

    def __len__(self):
        """Repository size."""
        return len(self.fields)

    def get_fields_by_type(self, field_type):
        """
        Export fields based on a requested field type.

        Parameters
        ----------
        field_type : ParaqusConstant
            Type of the field, i.e. TENSOR, VECTOR or SCALAR.

        Returns
        -------
        list of Field
            Fields that match the requested type.

        """
        return [f for f in self.fields.values() if f.field_type == field_type]

    @abstractmethod
    def add_field(self, field):
        """
        Add a new node or element field to the repository.

        This method is abstract since one must differ between node and
        element fields when adding them to the respective repository.
        """
        pass

    @abstractmethod
    def get_subset(self):
        """
        Export node or element fields for a subset of nodes or elements.

        This method is abstract since one must differ between working
        with subsets of nodes or elements.
        """
        return


class NodeFieldRepository(FieldRepositoryBaseClass):
    """
    Repository to stored nodal fields.

    Attributes
    ----------
    fields : dict
        Mapping field name -> Field.

    Methods
    -------
    get_fields_by_type
        Export node fields based on the field type.
    add_field
        Add a new node field to the repository.
    get_subset
        Export node fields for a subset of nodes.

    """

    def __init__(self):
        super(NodeFieldRepository, self).__init__()

    def add_field(self, field):
        """
        Add a new node field to the repository.

        Parameters
        ----------
        field : Field
            The field with position NODES to add to the
            repository.

        Returns
        -------
        None.

        """
        if field.field_position == NODES:

            if self.fields.get(field.field_name) != None:
                msg = ("Node field '{}'".format(field.field_name)
                       + " has already been stored and will be overwritten.")
                warnings.warn(msg)

            self.fields[field.field_name] = field

        else:
            msg = ("Provided field's position is '{}' and not '{}'."
                   .format(field.field_position, NODES))
            raise ValueError(msg)

    def get_subset(self, node_repository):
        """
        Export node fields for a subset of nodes.

        The nodes are specified by a NodeRepository, which should be
        derived from a common main model by model.nodes.get_subset()
        to ensure coherent indexing.

        Parameters
        ----------
        node_repository : NodeRepository
            Node repository containing the subset of nodes.

        Returns
        -------
        sub_fields : list of Field
            The fields matching the subset of nodes.

        """
        tags = node_repository.tags
        index_mapper = node_repository.index_mapper
        indices = np.array([index_mapper[i] for i in tags])

        sub_fields = [Field(f.field_name,
                                  f.field_values[indices],
                                  f.field_position,
                                  f.field_type) for f in self.fields.values()]

        return sub_fields


class ElementFieldRepository(FieldRepositoryBaseClass):
    """
    Repository to stored elemental fields.

    Attributes
    ----------
    fields : dict
        Mapping field name -> Field.

    Methods
    -------
    get_fields_by_type
        Export element fields based on the field type.
    add_field
        Add a new element field to the repository.
    get_subset
        Export element fields for a subset of elements.

    """

    def __init__(self):
        super(ElementFieldRepository, self).__init__()

    def add_field(self, field):
        """
        Add a new element field to the repository.

        Parameters
        ----------
        field : Field
            The field with position ELEMENTS to add to the
            repository.

        Returns
        -------
        None.

        """
        if field.field_position == ELEMENTS:

            if self.fields.get(field.field_name, None) != None:
                msg = ("Element field '{}'".format(field.field_name)
                       + " has already been stored and will be overwritten.")
                warnings.warn(msg)

            self.fields[field.field_name] = field

        else:
            msg = ("Provided field's position is '{}' and not '{}'."
                   .format(field.field_position, ELEMENTS))
            raise ValueError(msg)

    def get_subset(self, element_repository):
        """
        Export element fields for a subset of elements.

        The elements are specified by an ElementRepository, which should
        be derived from a common main model by model.elements.get_subset()
        to ensure coherent indexing.

        Parameters
        ----------
        element_repository : ElementRepository
            Element repository containing the subset of elements.

        Returns
        -------
        sub_fields : list of Field
            The fields matching the subset of elements.

        """
        tags = element_repository.tags
        index_mapper = element_repository.index_mapper
        indices = np.array([index_mapper[i] for i in tags])

        sub_fields = [Field(f.field_name,
                                  f.field_values[indices],
                                  f.field_position,
                                  f.field_type) for f in self.fields.values()]

        return sub_fields


class Field(object):
    """
    Definition of nodal or elemental fields.

    Parameters
    ----------
    field_name : str
        Name of the field.
    field_values : Sequence
        Values of the field. In case the field will be added to a model, the
        values must be in order of the respective node or element tags.
    field_position : ParaqusConstant
        Position of the field, i.e. NODES or ELEMENTS.
    field_type : ParaqusConstant
        Type of the field, i.e. TENSOR, VECTOR or SCALAR.

    Attributes
    ----------
    field_name : str
        Name of the field.
    field_position : ParaqusConstant
        Position of the field, i.e. NODES or ELEMENTS.
    field_type : ParaqusConstant
        Type of the field, i.e. TENSOR, VECTOR or SCALAR.
    field_values : numpy.ndarray
        Field values of the field.

    Methods
    -------
    get_3d_field_values
        Get a copy of the field values in 3d representation.

    """

    def __init__(self,
                 field_name,
                 field_values,
                 field_position,
                 field_type):

        self.field_name = field_name
        self.field_position = field_position
        self.field_type = field_type
        self.field_values = field_values


    # Properties
    @property
    def field_values(self):
        return self._field_values

    @field_values.setter
    def field_values(self, field_values):

        if self.field_type == SCALAR:
            self._field_values = np.array(field_values).reshape((-1,1))
        else:
            self._field_values = np.array(field_values)

    @property
    def field_position(self):
        return self._field_position

    @field_position.setter
    def field_position(self, field_position):

        if field_position not in (NODES, ELEMENTS):
            msg = "Invalid field position: {}".format(field_position)
            raise Exception(msg)

        self._field_position = field_position

    @property
    def field_type(self):
        return self._field_type

    @field_type.setter
    def field_type(self, field_type):

        if field_type not in (SCALAR, VECTOR, TENSOR):
            msg = "Invalid field type: {}".format(field_type)
            raise Exception(msg)

        self._field_type = field_type


    # Methods
    def __repr__(self):
        descr = "Field '{}' of type '{}' at position '{}'".format(
            self.field_name, self.field_type, self.field_position)
        return descr

    def __len__(self):
        return len(self.field_values)

    def get_3d_field_values(self):
        """
        Get a copy of the field values in 3d representation.

        Vectors are in order (x, y, z) and tensors are in order
        (xx, yy, zz, xy, yz, xz). Non-symmetric tensors are not
        suppurted.

        Returns
        -------
        numpy.ndarray
            The 3d representation of the field values.

        """
        if self.field_type == SCALAR:
            return self.field_values

        elif self.field_type == VECTOR:
            nvals, ndim = self.field_values.shape
            if ndim < 3:
                return np.hstack((self.field_values, np.zeros((nvals, 3-ndim))))
            return self.field_values

        elif self.field_type == TENSOR:
            nvals, ndim = self.field_values.shape
            if ndim < 6:
                return np.hstack((self.field_values, np.zeros((nvals, 6-ndim))))
            return self.field_values

        else:
            raise NotImplementedError(
                "Only SCALAR, VECTOR and TENSOR are supported."
                )

#------------------------------------------------------------------
# Short test
if __name__ == "__main__":

    from writers import BinaryWriter, AsciiWriter

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
    model_1 = ParaqusModel(element_tags,
                           connectivity,
                           element_types,
                           node_tags,
                           node_coords,
                           model_name=model_name,
                           part_name=part_name)

    # Add some fields
    tensor_field_vals = [[1,1,1,1],[2,2,2,2],[3,3,3,3],[4,4,4,4],[5,5,5,5]]
    vector_field_vals = [[1,1,1],[2,2,2],[3,3,3],[4,4,4],[5,5,5]]
    model_1.add_field("tensor_field", [1,2,3,4,5], tensor_field_vals,
                             "elements", "tensor")
    model_1.add_field("vector_field", [1,2,3,4,5], vector_field_vals,
                             "elements", "vector")

    # Test writer class
    vtu_writer = BinaryWriter(clear_output_dir=True)
    vtu_writer.encoding = "RAW"
    # vtu_writer = AsciiWriter()
    vtu_writer.number_of_pieces = 2

    # vtu_writer.write(model_1)

    print("*** FINISHED SUCCESFULLY ***")
