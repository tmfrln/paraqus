# -*- coding: utf-8 -*-
#
#   Paraqus - A VTK exporter for FEM results.
#
#   Copyright (C) 2022, Furlan, Stollberg and Menzel
#
#    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
"""
The main purpose of this file is to implement a model class that is
instantiated based on an Abaqus ODB.

One model instance is created for each time frame that is exported.

"""
# TODO: Looping over instances instead of set export requests makes it
# hard to check if all requests were executed. Right now, no error is
# raised when a set does not exist

import os.path
import warnings

import numpy as np
import abaqusConstants

from paraqus.paraqusmodel import ParaqusModel
from paraqus.abaqus.abaqustools import OdbObject
from paraqus.abaqus.elementlibrary import ABQ_ELEMENT_LIBRARY
from paraqus.constants import (ABAQUS, NODES, ELEMENTS,
                               SCALAR, TENSOR, VECTOR,
                               MEAN, ABSMAX)


# Lookup for invariants in field outputs
ABAQUS_INVARIANTS = {"mises": abaqusConstants.MISES,
                     "magnitude": abaqusConstants.MAGNITUDE}

# Remark: surface tensors are not yet supported
PARAQUS_FIELD_TYPES = {abaqusConstants.SCALAR: SCALAR,
                       abaqusConstants.VECTOR: VECTOR,
                       abaqusConstants.TENSOR_3D_FULL: TENSOR,
                       abaqusConstants.TENSOR_3D_PLANAR: TENSOR,
                       abaqusConstants.TENSOR_2D_PLANAR: TENSOR}


class OdbReader():
    """
    Reads an .odb file and exports selected results to a ParaqusModel.

    Parameters
    ----------
    odb_path : str
        Name of the underlying ODB.
    model_name : str, optional
        Name of the model returned by the reader. When ``model_name`` is
        omitted, it is set based on ``odb_path``. Default: ``None``.
    instance_names : Sequence[str], optional
        Instances that will be exported to individual models. If
        ``instance_names`` is omitted, all instances in the ODB will be
        exported. Default: ``None``.
    time_offset : float, optional
        Assume the simulation started at this time when exporting.
        Useful to create files in VTK format that are ordered in time
        from multiple ODBs. Default: ``0.0``.

    Attributes
    ----------
    odb_path : str
        Path to the underlying ODB.
    model_name : str
        Name of the model returned by the reader.
    field_export_requests : list[FieldExportRequest]
        Contains one request per field that will be exported to VTK
        format.
    group_export_requests : list[GroupExportRequest]
        Contains one request per node or element set that will be
        exported.
    instance_names : list[str]
        Instances that will be exported to individual models.
    time_offset : float
        Assume the simulation started at this time when exporting.
        Useful to create files in VTK format that are ordered in time
        from multiple ODBs.

    Examples
    --------
    >>> from paraqus.abaqus import OdbReader
    >>> # Define the odb/model/instances that will be read
    >>> reader = OdbReader(odb_path="example.odb",
    >>>                    model_name="example model",
    >>>                    instance_names=["instance-1", "instance-2"],
    >>>                    )
    >>> # Export the node field 'U' (displacements)
    >>> reader.add_field_export_request("U", field_position="nodes")
    >>> # Export the element set 'element set name' for 'instance-1'
    >>> reader.add_set_export_request("element set name",
    >>>                               set_type="elements",
    >>>                               instance_name="instance-1")
    >>> # Store the models for both instances in a list
    >>> instance_models = list(reader.read_instances(step_name="Step-1",
    >>>                                              frame_index=-1)
    >>>                        )

    """

    def __init__(self,
                 odb_path,
                 model_name=None,
                 instance_names=None,
                 time_offset=0.0):

        self._odb_path = odb_path
        self._odb = OdbObject(odb_path)
        self.model_name = model_name
        self.field_export_requests = []
        self.group_export_requests = []
        self.instance_names = instance_names
        self.time_offset = time_offset

    @property
    def odb_path(self):
        return self._odb_path

    @odb_path.setter
    def odb_path(self, odb_path):
        self._odb_path = odb_path
        self._odb = OdbObject(self._odb_path)

    def get_number_of_frames(self, step_name):
        """
        Return the number of frames for a step in the underlying ODB.

        The reader does NOT check that all output is available in each
        frame.

        Parameters
        ----------
        step_name : str
            Name of the step in the ODB.

        Returns
        -------
        number_of_frames : int
            Number of frames in the step, including the initial (0th)
            frame.

        """
        with self._odb as odb:
            step = odb.steps[step_name]
            return len(step.frames)

    def get_frame_indices(self, step_name, how='all'):
        """
        Return the indices of frames with at least one requested field.

        Parameters
        ----------
        step_name : str
            Name of the step in the ODB.
        how : str
            Whether to get frame indices where ``'any'`` or ``'all'``
            fields have values. Default: ``'all'``.

        Returns
        -------
        frame_indices : list[int]
            Indices of the frames with at least one requested field.

        """
        if len(self.field_export_requests) == 0:
            raise RuntimeError(
                "Can not check for frame indices when no field export "
                "requests are registered.")

        # Names of the fields
        field_names = [
            er.field_name for er in self.field_export_requests]

        # Function to check if at least one field is present in a frame
        if how == 'all':
            reduction = all
        elif how == 'any':
            reduction = any
        else:
            raise ValueError("'how' argument must be 'any' or 'all'.")

        def has_data(f):
            return reduction([n in f.fieldOutputs for n in field_names])

        with OdbObject(self.odb_path) as odb:
            step = odb.steps[step_name]
            frames = step.frames

            frame_indices = [
                i for (i, f) in enumerate(frames) if has_data(f)]

        return frame_indices

    def add_field_export_request(self,
                                 field_name,
                                 **kwargs):
        """
        Request export of an output field.

        Parameters
        ----------
        field_name : str
            Abaqus identifier for the field, e.g. ``'S'`` for stress.
        **kwargs : dict[str, str or int]
            Additional parameters that will be passed to the underlying
            FieldExportRequest. See the documentation of class
            ``FieldExportRequest`` for possible options.

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
            Name of the set in the ODB.
        set_type : str
            Type of the set. Valid values are ``'nodes'`` or
            ``'elements'``.
        instance_name : str, optional
            If ``instance_name`` is not None, look for an instance-level
            set in the ODB. Otherwise look for an assembly-level set.
            Default: ``None``.

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
            Name of the surface in the ODB.
        surface_type : str
            Type of the surface. Valid values are ``'nodes'`` or
            ``'elements'``.
        instance_name : str, optional
            If ``instance_name`` is not None, look for an instance-level
            surface in the ODB. Otherwise look for an assembly-level
            surface. Default: ``None``.

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
        Get the highest time value of any frame in the ODB.

        The ``time_offset`` attribute specified for the reader is added
        to the value.

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
        with self._odb as odb:
            step = odb.steps[step_name]
            frame = step.frames[frame_index]
            frame_time = self.time_offset + step.totalTime + frame.frameValue

        return frame_time

    def read_instances(self, step_name, frame_index):
        """
        Read a frame from the underlying ODB.

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
            Model representing the geometry and output for one part
            instance at the step/frame.

        """
        if self.model_name is None:
            model_name = os.path.splitext(
                os.path.basename(self.odb_path))[0]
        else:
            model_name = self.model_name

        with self._odb as odb:
            if step_name not in odb.steps.keys():
                raise KeyError("Step '{}' not found.".format(step_name))
            step = odb.steps[step_name]

            if (frame_index >= len(step.frames)
                    or frame_index < -len(step.frames)):
                raise IndexError("Frame index '{}' out of range"
                                 .format(frame_index))
            frame = step.frames[frame_index]

            frame_time = self.time_offset + step.totalTime + frame.frameValue

            # If no instances are specified, export all of them
            if self.instance_names is None:
                instance_names = list(odb.rootAssembly.instances.keys())
            else:
                instance_names = self.instance_names

            # Loop over the requested instances
            for instance_name in instance_names:

                instance = odb.rootAssembly.instances[instance_name]

                # Extract nodes/elements and instance-level sets
                mesh = InstanceMesh(instance)

                # Create a model object based on the mesh info
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

                # Loop to add field outputs
                for request in self.field_export_requests:
                    self._add_odb_field_to_model(request,
                                                 model,
                                                 mesh,
                                                 instance,
                                                 frame)

                # Loop to export node/element sets
                for request in self.group_export_requests:
                    self._add_odb_groups_to_model(request,
                                                  model,
                                                  odb,
                                                  instance)

                yield model

    def _add_odb_field_to_model(self, request, model, mesh, instance, frame):
        """
        Add a field output to the Paraqus version of an ODB model.

        Parameters
        ----------
        request : FieldExportRequest
            Specifies which field will be read from the ODB.
        model : ParaqusModel
            The Paraqus representation of the ODB model.
        instance_mesh : InstanceMesh
            Mesh representation of the instance the output is requested
            for, used to extract the correct values.
        instance : Abaqus OdbInstance
            The part instance that is currently exported.
        frame : Abaqus OdbFrame
            Frame of which the field output is requested.

        Returns
        -------
        None.

        """
        fo = self._get_field_output(request, frame, instance=instance)

        if fo is None:
            # Skip empty outputs when exporting
            msg = ("Field output {} ".format(request.field_name)
                   + "not available in instance "
                   + "{}. ".format(instance.name)
                   + "Export skipped.")
            warnings.warn(msg)
            return

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

    def _add_odb_groups_to_model(self, request, model, odb, instance):
        """
        Add a node/element group to the Paraqus version of an ODB model.

        Parameters
        ----------
        request : GroupExportRequest
            Describes a set or surface that will be exported.
        model : ParaqusModel
            The Paraqus representation of the ODB model.
        odb : Abaqus Odb
            The open ODB.
        instance : Abaqus OdbInstance
            The part instance that is currently exported.

        Returns
        -------
        None.

        """
        group_tags = self._get_group_tags(request, odb, instance)

        # Do nothing if the request is not for this instance
        if group_tags is None:
            return

        # Add the actual groups to the model
        if request.group_type == NODES:
            model.nodes.add_group(request.export_name,
                                  group_tags)
        elif request.group_type == ELEMENTS:
            model.elements.add_group(request.export_name,
                                     group_tags)
        else:
            raise ValueError(
                "Request type must be 'nodes' or 'elements'.")

    def _get_group_tags(self, request, odb, instance):
        """
        Return the node/element tags for a node/element set.

        Parameters
        ----------
        request : GroupExportRequest
            Describes a set or surface that will be exported.
        odb : Abaqus Odb
            The open ODB.
        instance : Abaqus OdbInstance
            The part instance that is currently exported.

        Returns
        -------
        tags : ArrayLike[int] or None
            Node/element numbers in the surface or set. If the export
            request is for another instance, None is returned.

        """
        # We will read the attributes based on the group type
        if request.group_type == NODES:
            group_type = "nodes"
            set_type = "nodeSets"
        else:  # request.group_type == ELEMENTS:
            group_type = "elements"
            set_type = "elementSets"

        if request.instance_name is None:
            # Assembly-level set/surface

            # Extract an odbSet representing the surface or set
            if request.surface_set:
                # The surface returns as an odbSet directly
                set_object = odb.rootAssembly.surfaces[request.group_name]
            else:
                # For node/element sets, we need to take one more step
                set_repository = odb.rootAssembly.__getattribute__(
                    set_type)
                set_object = set_repository[request.group_name]

            # For assembly-level sets or surfaces, the nodes/elements
            # are stored per instance, so we extract the index for the
            # current instance
            try:
                index = set_object.instances.index(instance)
            except ValueError:
                # Instance has no nodes/elements in the set
                return np.array([], dtype=int)

            # Extract the nodes/elements as an odbMeshNodeArray or
            # odbMeshElementArray. This array has only nodes/elements of
            # the instance under consideration
            array_object = set_object.__getattribute__(group_type)[
                index]

            labels = np.array([o.label for o in array_object])

            # Sort the array
            labels.sort()

            # Remove duplicates (these do actually occur)
            return np.unique(labels)

        if request.instance_name == instance.name:
            # Instance-level set/surface

            # Extract an odbSet representing the surface or set
            if request.surface_set:
                # The surface returns as an odbSet directly
                set_object = instance.surfaces[request.group_name]
            else:
                # For node/element sets, we need to take one more step
                set_repository = instance.__getattribute__(set_type)
                set_object = set_repository[request.group_name]

            # Extract the nodes/elements as an odbMeshNodeArray or
            # odbMeshElementArray
            array_object = set_object.__getattribute__(group_type)

            # Return an array of node or element labels
            labels = np.array([o.label for o in array_object])

            # Sort the array
            labels.sort()

            # Remove duplicates (these do actually occur)
            return np.unique(labels)

        # The request was not for this instance
        return None

    def _get_field_output(self,
                          request,
                          frame,
                          instance=None):
        """Get a field output object for the requested field."""
        field_name = request.field_name
        invariant = request.invariant

        # Get the field output for the current field
        field_out = frame.fieldOutputs[field_name]

        # Reduce to the instance
        if instance is not None:
            field_out = field_out.getSubset(region=instance)

        # If an invariant is specified, apply the reduction
        if invariant is not None:
            abq_invar = ABAQUS_INVARIANTS[invariant.lower().strip()]
            field_out = field_out.getScalarField(invariant=abq_invar)

        # If a field position is specified, reduce the output
        # correspondingly
        if request.field_position is not None:
            if request.field_position == NODES:
                field_out = field_out.getSubset(
                    position=abaqusConstants.NODAL)
            elif request.field_position == ELEMENTS:
                field_out = field_out.getSubset(
                    position=abaqusConstants.CENTROID)
            else:
                raise ValueError("Position not implemented.")

        if len(field_out.values) == 0:
            # No data for the field at this position
            return None

        return field_out

    def _read_field_output(self, request, field_out, instance_mesh):
        """
        Read the data for one field output.

        Parameters
        ----------
        request : FieldExportRequest
            Specifies which field will be read from the ODB.
        field_out : Abaqus FieldOutput
            Field output corresponding to the request (may still have
            values at other points than requested etc).
        instance_mesh : InstanceMesh
            Mesh representation of the instance the output is requested
            for, used to extract the correct values.

        Returns
        -------
        labels : ArrayLike[int]
            Node or element labels.
        data : ArrayLike[float]
            Field values in the same order as ``labels``.
        paraqus_position : ParaqusConstant
            Specifies where the output is evaluated (``NODES`` or
            ``'ELEMENTS'``).
        field_type : ParaqusConstant
            What type of field (``SCALAR``/``VECTOR``/``TENSOR``).

        """
        blocks = field_out.bulkDataBlocks

        position = blocks[0].position

        assert all(b.position == position for b in blocks), \
            "All data for one field must exist at the same output position."

        # Make sure element output is actually per element
        if position in (abaqusConstants.INTEGRATION_POINT,
                        abaqusConstants.ELEMENT_NODAL):
            field_out = field_out.getSubset(
                position=abaqusConstants.CENTROID)

            blocks = field_out.bulkDataBlocks
            position = blocks[0].position

        # Possible values for the position at this point:
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

        # Change 5th and 6th component to be compatible to vtk element
        # order
        if field_type == TENSOR and data.shape[1] == 6:
            data = data[:, [0, 1, 2, 3, 5, 4]]

        return labels, data, paraqus_position, field_type, field_description

    def _get_node_data(self, request, field_out, instance_mesh):
        """Extract node values from an Abaqus FieldOutput."""
        instance_nodes = instance_mesh.node_labels

        blocks = field_out.bulkDataBlocks
        dtype = blocks[0].data.dtype
        ncomponents = blocks[0].data.shape[1]
        field_type = PARAQUS_FIELD_TYPES[blocks[0].type]

        # Initialize data as NaNs
        data = np.ones((len(instance_nodes), ncomponents),
                       dtype=dtype)*np.nan

        # Create a description for the field
        description_str = request.field_name

        if request.invariant is not None:
            description_str += "_{}".format(request.invariant)

        # For each node there is only a single value
        for block in blocks:
            block_nodes = block.nodeLabels
            block_data = block.data

            # Indices of the block nodes in instance_nodes
            # this assumes that instance_nodes is sorted!
            indices = np.searchsorted(instance_nodes, block_nodes)

            data[indices, :] = block_data

        return instance_nodes, data, field_type, description_str

    def _get_element_data(self, request, field_out, instance_mesh):
        """Extract element values from an Abaqus FieldOutput."""
        instance_elements = instance_mesh.element_labels

        blocks = field_out.bulkDataBlocks
        dtype = blocks[0].data.dtype
        ncomponents = blocks[0].data.shape[1]
        field_type = PARAQUS_FIELD_TYPES[blocks[0].type]

        # Section point number for every block
        # Since abaqus numbers section points from 1, we use 0 for None
        # values
        section_points = np.zeros(len(blocks), dtype=int)

        for ib, block in enumerate(blocks):
            if block.sectionPoint is not None:
                section_points[ib] = block.sectionPoint.number

        # Mapping section point number -> index in data array
        section_point_indices = {n: i
                                 for (i, n) in enumerate(np.unique(section_points))}

        # Assume there is only one data value for each
        # (element, sectionPoint)
        nel = len(instance_elements)
        nsp = len(section_point_indices)

        # Initialize data as NaNs
        data = np.ones((nel, nsp, ncomponents), dtype=dtype)*np.nan

        # Create a description for the field
        description_str = self._create_element_data_description_string(
            request, section_point_indices)

        # Extract the data by looping over the data blocks
        for block, sp_number in zip(blocks, section_points):
            sp_index = section_point_indices[sp_number]

            block_elements = block.elementLabels
            block_data = block.data

            assert len(np.setdiff1d(block_elements, instance_elements)) == 0, \
                "Not all block element labels are part of the instance."

            # Indices iof the block elements in instance_elements
            # this assumes that instance_elements is sorted!
            el_indices = np.searchsorted(
                instance_elements, block_elements)

            data[el_indices, sp_index, :] = block_data

        data = self._get_section_point_element_data(request, data,
                                                    section_point_indices)
        return (instance_elements, data, field_type, description_str)

    def _create_element_data_description_string(self, request,
                                                section_point_indices):
        """Create a description for the exported element data."""
        # Create a description for the field
        description_str = request.field_name

        if request.invariant is not None:
            description_str += "_{}".format(request.invariant)

        if request.section_point_number is not None:
            description_str += "_sp{}".format(
                request.section_point_number)
        elif len(section_point_indices) > 1:
            # Triggers only if there is no explicit specification of the
            # section point
            description_str += "_{}".format(
                request.section_point_reduction)

        return description_str

    def _get_section_point_element_data(self, request, data,
                                        section_point_indices):
        """Handle element data at section points during export."""
        # If a specific section point was requested:
        if request.section_point_number is not None:
            assert request.section_point_number in section_point_indices, \
                "Requested section point number not in output."

            sp_index = section_point_indices[request.section_point_number]
            return data[:, sp_index, :]

        # Standard case where there are not section points (or only 1)
        if len(section_point_indices) == 1:
            return data[:, 0, :]

        # Reductions for multiple section points
        if request.section_point_reduction == MEAN:
            # Average data ignoring nans
            return np.nanmean(data, axis=1)
        if request.section_point_reduction == ABSMAX:
            return np.nanmax(np.abs(data), axis=1)

        raise ValueError("Reduction method invalid.")


class InstanceMesh():
    """
    Represent the mesh for one part instance.

    Parameters
    ----------
    instance : Abaqus OdbInstance
        The instance the mesh is extracted from.
    sort_values : bool, optional
        Whether the nodes and elements are sorted by label. Default:
        ``True``.

    Attributes
    ----------
    node_labels : ArrayLike[int]
        Node numbers for the part instance.
    node_coords : ArrayLike[float]
        Coordinates of the nodes.
    element_labels : ArrayLike[int]
        Element number for each element in the instance.
    element_types : ArrayLike[int]
        VTK element type for each element, in the same order as
        ``element_labels``.
    element_connectivities : list[tuple[int]]
        Nodes in each element, in the same order as ``element_labels``.

    """

    def __init__(self, instance, sort_values=True):

        self._instance = instance
        self._read_nodes(sort=sort_values)
        self._read_elements(sort=sort_values)
        self._read_node_sets()
        self._read_element_sets()

    def _read_nodes(self, sort=True):
        """
        Extract node info.

        Sets the attributes ``node_tags`` and ``node_coords``.

        Parameters
        ----------
        sort : bool, optional
            Whether to sort the return by node label. Default: ``True``.

        Returns
        -------
        None.

        """
        instance = self._instance

        labels, coords = zip(*[(n.label, n.coordinates)
                               for n in instance.nodes])

        labels = np.array(labels, dtype=int)
        coords = np.array(coords)

        # Sort output by node label
        if sort:
            sorter = np.argsort(labels)
            labels = labels[sorter]
            coords = coords[sorter]

        self.node_labels = labels
        self.node_coords = coords

    def _read_elements(self, sort=True):
        """
        Extract element info.

        Sets the attributes ``element_tags`` , ``element_types`` and
        ``element_connectivities``.

        Parameters
        ----------
        sort : bool, optional
            Whether to sort the return by element label. Default:
            ``True``.

        Returns
        -------
        None.

        """
        instance = self._instance

        # Using zip as its own inverse is faster than multiple
        # comprehensions
        labels, types, connectivities = zip(*[(e.label, e.type, e.connectivity)
                                              for e in instance.elements])

        labels = np.array(labels)

        # Conversion to integer vtk element codes
        types = np.array([ABQ_ELEMENT_LIBRARY[str(el_type)]
                          for el_type in types],
                         dtype=int)

        # Since connectivities are tuples of possibly different lengths,
        # we do not convert these to arrays

        # Sort output by element label
        if sort:
            sorter = np.argsort(labels)

            labels = labels[sorter]
            types = types[sorter]

            # Convert back to tuples so return type stays the same
            # types = tuple([types[i] for i in sorter])

            connectivities = [tuple(connectivities[i]) for i in sorter]

        self.element_labels = labels
        self.element_types = types
        self.element_connectivities = connectivities

    def _read_node_sets(self):
        """
        Extract instance-level node sets as indicator arrays.

        Sets the attribute ``node_sets``.

        Returns
        -------
        None.

        """
        instance = self._instance
        self.node_sets = {}

        for set_name, nset in instance.nodeSets.items():
            set_labels = np.array([n.label for n in nset.nodes])
            set_indicators = np.array([label in set_labels
                                       for label in self.node_labels])

            self.node_sets[set_name] = set_indicators.astype(int)

    def _read_element_sets(self):
        """
        Extract instance-level element sets as indicator arrays.

        Sets the attribute ``element_sets``.

        Returns
        -------
        None.

        """
        instance = self._instance
        self.element_sets = {}

        for set_name, eset in instance.elementSets.items():
            set_labels = np.array([e.label for e in eset.elements])
            set_indicators = np.array([label in set_labels
                                       for label in self.element_labels])

            self.element_sets[set_name] = set_indicators.astype(int)


class FieldExportRequest():
    """
    Specify a field output that will be exported.

    Parameters
    ----------
    field_name : str
        Abaqus identifier for the field, e.g. ``'S'`` for stress.
    field_position : str, optional
        What type of field. valid values: ``'nodes'`` or ``'elements'``.
    invariant : str, optional
        Invariant of the field, if applicable, e.g. ``'mises'`` or
        ``'magnitude'``. Default: ``None``.
    section_point_number : int, optional
        Section point for shell elements. If no section point number is
        specified, the section point values are reduced according to
        ``section_point_reduction``. Default: ``None``.
    section_point_reduction : str, optional
        How to reduce values of multiple section points for the same
        node or element. Valid values are ``'mean'`` or ``'absmax'``.
        Default: ``'absmax'``.

    Attributes
    ----------
    field_name : str
        Abaqus identifier for the field, e.g. ``'S'`` for stress.
    field_position : str, optional
        What type of field. valid values: ``'nodes'`` or ``'elements'``.
    invariant : str
        Invariant of the field, if applicable, e.g. ``'mises'`` or
        ``'magnitude'``.
    section_point_number : int
        Section point for shell elements. If no section point number is
        specified, the section point values are reduced according to
        ``section_point_reduction``.
    section_point_reduction : str
        How to reduce values of multiple section points for the same
        node or element. Valid values are ``'mean'`` or ``'absmax'``.

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
    Specify a nodes/elements group that will be written to VTK format.

    Parameters
    ----------
    group_name : str
        Name of the set or surface in the ODB.
    group_type : str
        Type of the set. Valid values are ``'nodes'`` or ``'elements'``.
    instance_name : str, optional
        If ``instance_name`` is not None, look for an instance-level set
        in the ODB. Otherwise look for an assembly-level set.
        Default: ``None``.
    surface_set : bool, optional
        If ``False``, export a set. If ``True``, export nodes/elements
        of a surface. Default: ``False``.

    Attributes
    ----------
    group_name : str
        Name of the set or surface in the ODB.
    group_type : str
        Type of the set. Valid values are ``'nodes'`` or ``'elements'``.
    instance_name : str
        If `instance_name` is not None, look for an instance-level set
        in the ODB. Otherwise look for an assembly-level set.
    surface_set : bool
        If ``False``, export a set. If ``True``, export nodes/elements
        of a surface.

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
