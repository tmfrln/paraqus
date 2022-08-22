#
#   Paraqus - A VTK exporter for FEM results.
#
#   Copyright (C) 2022, Furlan and Stollberg
#
#    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
"""
The main purpose of this file is to implement a model class that is
instantiated based on an abaqus odb.

One model instance is created for each time frame that is exported.

"""

# TODO: Looping over instances instead of set export requests makes it hard to
# check if all requests were executed. Right now, no error is raised when a
# set does not exist.

import os.path
import warnings

import numpy as np

from paraqus.paraqusmodel import ParaqusModel

from paraqus.abaqus.abaqustools import ODBObject
from paraqus.abaqus.elementlibrary import ABQ_ELEMENT_LIBRARY
from paraqus.constants import (ABAQUS, NODES, ELEMENTS,
                               SCALAR, TENSOR, VECTOR,
                               MEAN, ABSMAX)

from abaqusConstants import MISES, MAGNITUDE

import abaqusConstants

# lookup for invariants in field outputs
ABAQUS_INVARIANTS = {"mises": MISES,
                     "magnitude": MAGNITUDE}

# remark: surface tensors are not yet supported
PARAQUS_FIELD_TYPES = {abaqusConstants.SCALAR: SCALAR,
                       abaqusConstants.VECTOR: VECTOR,
                       abaqusConstants.TENSOR_3D_FULL: TENSOR,
                       abaqusConstants.TENSOR_3D_PLANAR: TENSOR,
                       abaqusConstants.TENSOR_2D_PLANAR: TENSOR}


class ODBReader():
    """
    Reads an odb file and exports selected results to a ParaqusModel instance.

    Attributes
    ----------
    odb_path : str
        Path to the underlying odb.
    model_name : str
        Name of the model returned by the reader.
    field_export_requests : list
        Contains one request per field that will be exported to vtk format.
    group_export_requests : list
        Contains one request per node or element set that will be exported.
    instance_names : list
        Instances that will be exported to individual models.
    time_offset : float
        Assume the simulation started at this time when exporting. Useful to
        create vtk files that are ordered in time from multiple odbs.

    Parameters
    ----------
    odb_path : str
        Name of the underlying odb.
    model_name : str, optional
        Name of the model returned by the reader. When `model_name` is omitted,
        it is set based on `odb_path`. Default: None.
    instance_names : list, optional
        Instances that will be exported to individual models. If
        `instance_names` is omitted, all instances in the odb will be exported.
        Default: None.
    time_offset : float, optional
        Assume the simulation started at this time when exporting. Useful to
        create vtk files that are ordered in time from multiple odbs.
        Default: 0.0

    Examples
    --------
    >>> from paraqus.abaqus import ODBReader
    >>> # Define the odb/model/instances that will be read
    >>> reader = ODBReader(odb_path="example.odb",
    >>>                    model_name="example model",
    >>>                    instance_names=["instance-1", "instance-2"],
    >>>                    )
    >>> # Export the node field 'U' (displacements)
    >>> reader.add_field_export_request("U", field_position="nodes")
    >>> # export the element set 'element set name' only for 'instance-1'
    >>> reader.add_set_export_request("element set name",
    >>>                               set_type="elements",
    >>>                               instance_name="instance-1")
    >>> # store the models for both instances in a list
    >>> instance_models = list(reader.read_instances(step_name="Step-1",
    >>>                                              frame_index=-1)
    >>>                       )

    """

    def __init__(self,
                 odb_path,
                 model_name=None,
                 instance_names=None,
                 time_offset=0.0):

        self.odb_path = odb_path
        self.model_name = model_name
        self.field_export_requests = []
        self.group_export_requests = []
        self.instance_names = instance_names
        self.time_offset = time_offset


    def get_number_of_frames(self, step_name):
        """
        Return the number of frames for a given step in the underlying odb.

        The reader does NOT check that all output is available in each frame.

        Parameters
        ----------
        step_name : str
            Name of the step in the odb.

        Returns
        -------
        number_of_frames : int
            Number of frames in the step, including the initial (0th) frame.

        """
        with ODBObject(self.odb_path) as odb:
            step = odb.steps[step_name]
            return len(step.frames)



    def add_field_export_request(self,
                                 field_name,
                                 **kwargs):
        """
        Request export of an output field.

        Parameters
        ----------
        field_name : str
            Abaqus identifier for the field, e.g. 'S' for stress.
        **kwargs : dict
            Additional parameters that will be passed to the underlying
            FieldExportRequest.

        Returns
        -------
        None

        """
        request = FieldExportRequest(field_name, **kwargs)

        self.field_export_requests.append(request)

    def add_set_export_request(self,
                               set_name,
                               set_type,
                               instance_name=None):
        """
        Request that a node or element set is exported.

        Parameters
        ----------
        set_name : str
            Name of the set in the odb
        set_type : str
            Type of the set. Valid values are 'nodes' or 'elements'.
        instance_name : str, optional
            If `instance_name` is not None, look for an instance-level set
            in the odb. Otherwise look for an assembly-level set.
            Default: None.

        Returns
        -------
        None

        """
        request = GroupExportRequest(set_name, set_type, instance_name)

        self.group_export_requests.append(request)


    def add_surface_export_request(self,
                                   surface_name,
                                   surface_type,
                                   instance_name=None):
        """
        Request that a node or element set is exported.

        Parameters
        ----------
        surface_name : str
            Name of the surface in the odb
        surface_type : str
            Type of the surface. Valid values are 'nodes' or 'elements'.
        instance_name : str, optional
            If `instance_name` is not None, look for an instance-level surface
            in the odb. Otherwise look for an assembly-level surface.
            Default: None.

        Returns
        -------
        None

        """
        request = GroupExportRequest(surface_name,
                                     surface_type,
                                     instance_name,
                                     surface_set=True)

        self.group_export_requests.append(request)


    def get_frame_time(self, step_name, frame_index):
        """
        Get the highest time value of any frame in the odb.

        The `time_offset` specified for the reader is added to the value.

        Parameters
        ----------
        step_name : str
            Name of the step in Abaqus.
        frame_index : int
            Index of the frame in the step in Abaqus.

        Returns
        -------
        frame_time : float
            The total time passed (includes time offset).

        """
        with ODBObject(self.odb_path) as odb:
            step = odb.steps[step_name]
            frame = step.frames[frame_index]
            frame_time =  self.time_offset + step.totalTime + frame.frameValue

        return frame_time


    def read_instances(self, step_name, frame_index):
        """
        Read a frame from the underlying odb.

        Each instance is read separately and returns an individual
        ParaqusModel. Models are generated lazily, so memory-efficient
        iteration over the return values is possible.

        Parameters
        ----------
        step_name : str
            Name of the step in Abaqus.
        frame_index : int
            Index of the frame in the step in Abaqus.

        Yields
        ------
        model : ParaqusModel
            Model representing the geometry and output for one part instance
            at the step/frame.

        """
        if self.model_name is None:
            model_name =  os.path.splitext(os.path.basename(self.odb_path))[0]
        else:
            model_name = self.model_name

        with ODBObject(self.odb_path) as odb:
            # TODO: Input checking
            step = odb.steps[step_name]
            frame = step.frames[frame_index]

            frame_time =  self.time_offset + step.totalTime + frame.frameValue

            # if no instances are specified, export all of them
            if self.instance_names is None:
                instance_names = list(odb.rootAssembly.instances.keys())
            else:
                instance_names = self.instance_names


            # loop over the requested instances
            for instance_name in instance_names:

                instance = odb.rootAssembly.instances[instance_name]

                # extract nodes/elements and instance-level sets
                mesh = InstanceMesh(instance)

                # create a model object based on the mesh info
                model = ParaqusModel(mesh.element_labels,
                                     mesh.element_connectivities,
                                     mesh.element_types,
                                     mesh.node_labels,
                                     mesh.node_coords,
                                     model_name=model_name,
                                     part_name=instance_name,
                                     step_name=step_name,
                                     frame_time=frame_time,
                                     source=ABAQUS)

                # loop to add field outputs
                for request in self.field_export_requests:
                    fo = self._get_field_output(request,
                                                frame,
                                                instance=instance)

                    if fo is None:
                        # skip empty outputs when exporting
                        msg = ("Field output {} ".format(request.field_name)
                              + "not available in instance "
                              + "{}. ".format(instance_name)
                              + "Export skipped." )
                        warnings.warn(msg)
                        continue

                    (field_tags,
                     field_data,
                     field_position,
                     field_type,
                     export_name) = self._read_field_output(request, fo, mesh)

                    model.add_field(export_name,
                                    field_tags,
                                    field_data,
                                    field_position,
                                    field_type)

                # loop to export node/element sets
                for request in self.group_export_requests:
                    group_tags = self._get_group_tags(request, odb, instance)

                    # do nothing if the request is not for this instance
                    if group_tags is None:
                        continue

                    # add the actual groups to the model
                    if request.group_type == NODES:
                        model.nodes.add_group(request.export_name,
                                              group_tags)
                    elif request.group_type == ELEMENTS:
                        model.elements.add_group(request.export_name,
                                                 group_tags)
                    else:
                        raise ValueError(
                            "Request type must be 'nodes' or 'elements'.")

                yield model


    def _get_group_tags(self, request, odb, instance):
        """
        Return the node/element tags for a node/element set.

        Parameters
        ----------
        request : GroupExportRequest
            Describes a set or surface that will be exported.
        odb : Abaqus ODB object
            The open odb.
        instance : Abaqus part instance object
            The part instance that is currently exported.

        Returns
        -------
        tags : ArrayLike or None
            Node/element numbers in the surface or set. If the export request
            is for another instance, None is returned.

        """
        # we will read the attributes based on the group type
        if request.group_type == NODES:
            group_type = "nodes"
            set_type = "nodeSets"
        elif request.group_type == ELEMENTS:
            group_type = "elements"
            set_type = "elementSets"


        if request.instance_name is None:
            # assembly-level set/surface

            # extract an odbSet representing the surface or set
            if request.surface_set:
                # the surface returns as an odbSet directly
                set_object = odb.rootAssembly.surfaces[request.group_name]
            else:
                # for node/element sets, we need to take one more step
                set_repository = odb.rootAssembly.__getattribute__(set_type)
                set_object = set_repository[request.group_name]

            # for assembly-level sets or surfaces, the nodes/elements are
            # stored per instance, so we extract the index for the current
            # instance
            try:
                index = set_object.instances.index(instance)
            except ValueError:
                # instance has no nodes/elements in the set
                return np.array([], dtype=int)

            # extract the nodes/elements as an odbMeshNodeArray or
            # odbMeshElementArray. This array has only nodes/elements of
            # the instance under consideration
            array_object = set_object.__getattribute__(group_type)[index]

            labels = np.array([o.label for o in array_object])

            # sort the array
            labels.sort()

            # remove duplicates (these do actually occur)
            return np.unique(labels)

        elif request.instance_name == instance.name:
            # instance-level set/surface

            # extract an odbSet representing the surface or set
            if request.surface_set:
                # the surface returns as an odbSet directly
                set_object = instance.surfaces[request.group_name]
            else:
                # for node/element sets, we need to take one more step
                set_repository = instance.__getattribute__(set_type)
                set_object = set_repository[request.group_name]

            # extract the nodes/elements as an odbMeshNodeArray or
            # odbMeshElementArray
            array_object = set_object.__getattribute__(group_type)

            # return an array of node or element labels
            labels = np.array([o.label for o in array_object])

            # sort the array
            labels.sort()

            # remove duplicates (these do actually occur)
            return np.unique(labels)

        else:
            # The request was not for this instance
            return None


    def _get_field_output(self,
                          request,
                          frame,
                          instance=None):
        """Get a field output object for the requested field."""
        field_name = request.field_name
        invariant = request.invariant

        # get the field output for the current field
        field_out = frame.fieldOutputs[field_name]

        # reduce to the instance
        if instance is not None:
            field_out = field_out.getSubset(region=instance)

        # output should be uniform in terms of location (node or qp output)
        # FIXME: This is propably not needed anymore
        # assert len(field_out.locations) == 1

        # if an invariant is specified, apply the reduction
        if invariant is not None:
            abq_invar = ABAQUS_INVARIANTS[invariant.lower().strip()]
            field_out = field_out.getScalarField(invariant=abq_invar)

        # if a field position is specified, reduce the output correspondingly
        if request.field_position is not None:
            if request.field_position == NODES:
                field_out = field_out.getSubset(position=abaqusConstants.NODAL)
            elif request.field_position == ELEMENTS:
                field_out = field_out.getSubset(position=abaqusConstants.CENTROID)
            else:
                raise ValueError("Position not implemented.")

        if len(field_out.values) == 0:
            # no data for the field at this position
            return None

        return field_out


    def _read_field_output(self, request, field_out, instance_mesh):
        """
        Read the data for one field output.

        Parameters
        ----------
        request : FieldExportRequest
            Specifies which field will be read from the odb.
        field_out : Abaqus FieldOutput
            Field output corresponding to the request (may still have values
            at other points than requested etc).
        instance_mesh : InstanceMesh
            Mesh representation of the instance the output is requested for,
            used to extract the correct values.

        Returns
        -------
        labels : ArrayLike
            Node or element labels.
        data : ArrayLike
            Field values in the same order as `labels`.
        paraqus_position
            Specifies where the output is evaluated ('nodes' or 'elements').
        field_type
            What type of field (scalar/vector/tensor).

        """
        blocks = field_out.bulkDataBlocks

        position = blocks[0].position

        assert all([b.position == position for b in blocks]), \
            "All data for one field must exist at the same output position."

        # make sure element output is actually per element
        if position in (abaqusConstants.INTEGRATION_POINT,
                        abaqusConstants.ELEMENT_NODAL):
            field_out = field_out.getSubset(position=abaqusConstants.CENTROID)

            blocks = field_out.bulkDataBlocks
            position = blocks[0].position

        # possible values for the position at this point:
        # NODAL, CENTROID, WHOLE_ELEMENT
        if position == abaqusConstants.NODAL:
            paraqus_position = NODES

            (labels,
             data,
             field_type,
             field_description) = self._get_node_data(request,
                                                      field_out,
                                                      instance_mesh)

        elif position in (abaqusConstants.CENTROID,
                          abaqusConstants.WHOLE_ELEMENT):
            paraqus_position = ELEMENTS

            (labels,
             data,
             field_type,
             field_description) = self._get_element_data(request,
                                                         field_out,
                                                         instance_mesh)
        else:
            raise ValueError("Position not implemented.")

        # change 5th and 6th component to be compatible to vtk element order
        if field_type == TENSOR and data.shape[1] == 6:
            data = data[:,[0,1,2,3,5,4]]

        return labels, data, paraqus_position, field_type, field_description


    def _get_node_data(self, request, field_out, instance_mesh):
        """Extract node values from a FieldOutput."""
        instance_nodes = instance_mesh.node_labels

        blocks = field_out.bulkDataBlocks
        dtype = blocks[0].data.dtype
        ncomponents = blocks[0].data.shape[1]
        field_type = PARAQUS_FIELD_TYPES[blocks[0].type]

         # initialize data as NaNs
        data = np.ones((len(instance_nodes), ncomponents), dtype=dtype)*np.nan

        # create a description for the field
        description_str = request.field_name

        if request.invariant is not None:
            description_str += "_{}".format(request.invariant)

        # for each node there is only a single value
        for block in blocks:
            block_nodes = block.nodeLabels
            block_data = block.data

            # indices of the block nodes in instance_nodes
            # this assumes that instance_nodes is sorted!
            indices = np.searchsorted(instance_nodes, block_nodes)

            data[indices,:] = block_data

        return instance_nodes, data, field_type, description_str


    def _get_element_data(self, request, field_out, instance_mesh):
        """Extract element values from a FieldOutput."""
        instance_elements = instance_mesh.element_labels

        blocks = field_out.bulkDataBlocks
        dtype = blocks[0].data.dtype
        ncomponents = blocks[0].data.shape[1]
        field_type = PARAQUS_FIELD_TYPES[blocks[0].type]

        # section point number for every block
        # since abaqus numbers section points from 1, we use 0 for None values
        section_points = np.zeros(len(blocks), dtype=int)

        for ib, block in enumerate(blocks):
            if block.sectionPoint is not None:
                section_points[ib] = block.sectionPoint.number

        # mapping section point number -> index in data array
        section_point_indices = {n: i
             for (i,n) in enumerate(np.unique(section_points))}

        # assume these is only one data value for each (element, sectionPoint)
        nel = len(instance_elements)
        nsp = len(section_point_indices)

        # initialize data as NaNs
        data = np.ones((nel, nsp, ncomponents), dtype=dtype)*np.nan

        # create a description for the field
        description_str = request.field_name

        if request.invariant is not None:
            description_str += "_{}".format(request.invariant)

        if request.section_point_number is not None:
            description_str += "_sp{}".format(request.section_point_number)
        elif nsp > 1:
            # triggers only if there is no explicit specification of the
            # section point
            description_str += "_{}".format(request.section_point_reduction)

        # extract the data by looping over the data blocks
        for block, sp_number in zip(blocks, section_points):
            sp_index = section_point_indices[sp_number]

            block_elements = block.elementLabels
            block_data = block.data

            assert len(np.setdiff1d(block_elements, instance_elements)) == 0, \
                "not all block element labels are part of the instance."

            # indices iof the block elements in instance_elements
            # this assumes that instance_elements is sorted!
            el_indices = np.searchsorted(instance_elements, block_elements)

            data[el_indices,sp_index,:] = block_data

        # if a specific section point was requested:
        if request.section_point_number is not None:
            assert request.section_point_number in section_point_indices, \
                "Requested section point number not in output."

            sp_index = section_point_indices[request.section_point_number]
            return (instance_elements,
                    data[:,sp_index,:],
                    field_type,
                    description_str)

        if nsp == 1:
            # "standard" case where there are not section points (or only 1)
            return (instance_elements,
                    data[:,0,:],
                    field_type,
                    description_str)
        else:
            # reductions for multiple section points
            if request.section_point_reduction == MEAN:
                # average data ignoring nans
                data = np.nanmean(data, axis=1)
            elif request.section_point_reduction == ABSMAX:
                data = np.nanmax(np.abs(data), axis=1)
            else:
                raise ValueError("Reduction method invalid.")

            return (instance_elements,
                    data,
                    field_type,
                    description_str)


class InstanceMesh():
    """
    Represent the mesh for one part instance.

    Attributes
    ----------
    node_labels : ArrayLike
        Node numbers for the part instance.
    node_coords : ArrayLike
        Coordinates of the nodes.
    element_labels : ArrayLike
        Element number for each element in the instance.
    element_types : ArrayLike
        VTK element type for each element, in the same order as
        `element_labels`.
    element_connectivities : List[Tuple[int]]
        Nodes in each element, in the same order as `element_labels`.

    Parameters
    ----------
    instance : Abaqus odb instance object
        The instance the mesh is extracted from.
    sort_values : Bool, optional
        Whether the nodes and elements are sorted by label. Default: True.

    """

    def __init__(self, instance, sort_values=True):

        self._read_nodes(instance, sort=sort_values)
        self._read_elements(instance, sort=sort_values)
        self._read_node_sets(instance)
        self._read_element_sets(instance)

    def _read_nodes(self, instance, sort=True):
        """
        Extract node info.

        Sets the attributes `node_tags` and `node_coords`.

        Parameters
        ----------
        instance : abaqus odb instance object
            The instance in question.
        sort : bool, optional
            Whether to sort the return by node label. Default: True.

        """
        labels, coords = zip(*[(n.label, n.coordinates)
                               for n in instance.nodes])

        labels = np.array(labels, dtype=int)
        coords = np.array(coords)

        # sort output by node label
        if sort:
            sorter = np.argsort(labels)
            labels = labels[sorter]
            coords = coords[sorter]

        self.node_labels = labels
        self.node_coords = coords


    def _read_elements(self, instance, sort=True):
        """
        Extract element info.

        Sets the attributes `element_tags` , `element_types` and
        `element_connectivities`.

        Parameters
        ----------
        instance : abaqus odb instance object
            The instance in question.
        sort : bool, optional
            Whether to sort the return by element label. Default: True.

        """
        # using zip as its own inverse is faster than multiple comprehensions
        labels, types, connectivities = zip(*[(e.label, e.type, e.connectivity)
                                              for e in instance.elements])

        labels = np.array(labels)

        # conversion to integer vtk element codes
        types = np.array([ABQ_ELEMENT_LIBRARY[str(el_type)]
                          for el_type in types],
                         dtype=int)

        # since connectivities are tuples of possibly different lengths,
        # we do not convert these to arrays

        # sort output by element label
        if sort:
            sorter = np.argsort(labels)

            labels = labels[sorter]
            types = types[sorter]

            # convert back to tuples so return type stays the same
            types = tuple([types[i] for i in sorter])

            connectivities = tuple([connectivities[i] for i in sorter])

        self.element_labels = labels
        self.element_types = types
        self.element_connectivities = connectivities


    def _read_node_sets(self, instance):
        """
        Extract instance-level node sets as indicator arrays.

        Sets the attribute `node_sets`.

        Parameters
        ----------
        instance : abaqus odb instance object
            The instance in question.

        """
        self.node_sets = {}

        for set_name, nset in instance.nodeSets.items():
            set_labels = np.array([n.label for n in nset.nodes])
            set_indicators = np.array([label in set_labels
                                       for label in self.node_labels])

            self.node_sets[set_name] = set_indicators.astype(int)


    def _read_element_sets(self, instance):
        """
        Extract instance-level element sets as indicator arrays.

        Sets the attribute `element_sets`.

        Parameters
        ----------
        instance : abaqus odb instance object
            The instance in question.

        """
        self.element_sets = {}

        for set_name, eset in instance.elementSets.items():
            set_labels = np.array([e.label for e in eset.elements])
            set_indicators = np.array([label in set_labels
                                       for label in self.element_labels])

            self.element_sets[set_name] = set_indicators.astype(int)


class FieldExportRequest():
    """
    Specify a field output that will be exported.

    Attributes
    ----------
    See parameters.

    Parameters
    ----------
    field_name : str
        Abaqus identifier for the field, e.g. 'S' for stress.
    field_position : str, optional
        What type of field. valid values: 'nodes' or 'elements'.
    invariant : str, optional
        Invariant of the field, if applicable. E.g. 'mises', 'magnitude'.
    section_point_number : int, optional
        Section point for shell elements. If no section point number is
        specified, the section point values are reduced according to
        `section_point_reduction`.
    section_point_reduction : str
        How to reduce values of multiple section points for the same node or
        element. Valid values are 'mean' or 'absmax'.

    """

    def __init__(self,
                 field_name,
                 field_position=None,
                 invariant=None,
                 section_point_number=None,
                 section_point_reduction="absmax"):

        self.field_name = field_name
        self.field_position = field_position
        self.invariant = invariant
        self.section_point_number = section_point_number

        assert section_point_reduction in (MEAN, ABSMAX), \
            "Valid values for section_point_reduction are 'mean' or 'absmax'."

        self.section_point_reduction = section_point_reduction


class GroupExportRequest():
    """
    Specify a group of nodes or elements that will be written to the vtk file.

    Attributes
    ----------
    See parameters

    Parameters
    ----------
    group_name : str
        Name of the set or surface in the odb
    group_type : str
        Type of the set. valid values are 'nodes' or 'elements'.
    instance_name : str, optional
        If `instance_name` is not None, look for an instance-level set
        in the odb. Otherwise look for an assembly-level set.
        Default: None.
    surface_set : bool, optional
        If `False`, export a set. If `True`, export nodes/elements of a
        surface.

    """

    def __init__(self,
                 group_name,
                 group_type,
                 instance_name=None,
                 surface_set=False):

        self.group_name = group_name
        self.group_type = group_type
        self.instance_name = instance_name
        self.surface_set = surface_set

        assert group_type in (NODES, ELEMENTS), \
            "Valid values for group_type are 'nodes' or 'elements'."

    @property
    def export_name(self):
        """Return a unique name for the surface/set that is exported."""
        export_name = ""
        if self.surface_set:
            export_name += "surface."

        if self.instance_name is not None:
            export_name += self.instance_name + "."

        export_name += self.group_name

        return export_name
