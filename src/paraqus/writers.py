# -*- coding: utf-8 -*-
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
This module keeps all writers for the different output format, e.g.
ascii and binary. Related tools like VtkFileManager should also be
stored here. Note, that currently only unstructured grids are
supported.

"""

import os
import sys
from os import path
import shutil
import itertools
from abc import ABCMeta, abstractmethod

import numpy as np
import struct
import base64

from paraqus.constants import (BYTE_ORDER_CHAR, ASCII, BINARY, BYTE_ORDER,
                               BASE64, RAW, UINT64)


# Version string for the vtk version that is supported
VTK_VERSION_MAJOR = 1
VTK_VERSION_MINOR = 0
VTK_VERSION_STRING = str(VTK_VERSION_MAJOR) + "." + str(VTK_VERSION_MINOR)

# Mapper for data types used in vtk files
VTK_TYPE_MAPPER = {"int8":    "Int8",
                   "uint8":   "UInt8",
                   "int16":   "Int16",
                   "uint16":  "UInt16",
                   "int32":   "Int32",
                   "uint32":  "UInt32",
                   "int64":   "Int64",
                   "uint64":  "UInt64",
                   "float32": "Float32",
                   "float64": "Float64",
                   }

# Mapper for binary data types
BINARY_TYPE_MAPPER = {"int8": "b",
                      "uint8": "B",
                      "int16": "h",
                      "uint16": "H",
                      "int32": "i",
                      "uint32": "I",
                      "int64": "q",
                      "uint64": "Q",
                      "float32": "f",
                      "float64": "d",
                      }

# Mapper for the header size in case of packed binary data
BINARY_HEADER_SIZE_MAPPER = {"uint32": 4,
                             "uint64": 8}


class VtkFileManager(object):
    r"""
    Context manager for VTK file reading and writing.

    Can handle all kinds of supported VTK files, i.e. .vtu, .pvtu and
    .pvd files. Files can only be opened in write mode.

    Parameters
    ----------
    file_name : str
        The name of the VTK file that will be written.
    fmt : ParaqusConstant
        Constant defining the output format of array data, i.e.
        ASCII or BINARY.

    Attributes
    ----------
    file_path : str
        The absolute path to the VTK file.
    fmt : ParaqusConstant
        Constant defining the output format of array data, i.e.
        ASCII or BINARY.

    Example
    -------
    >>> from paraqus.constants import BINARY
    >>> with VtkFileManager("my_file.vtu", BINARY) as vtu_file:
    >>>     vtu_file.write("<VTKFile>\n")
    >>>     vtu_file.write("<UnstructuredGrid>\n")
    >>>     vtu_file.write("</UnstructuredGrid>\n")
    >>>     vtu_file.write("</VTKFile>\n")

    """

    def __init__(self, file_name, fmt):

        extension = path.splitext(file_name)[1]
        if extension not in (".vtu", ".pvtu", ".pvd"):
            raise ValueError(
                "File format '{}' is not a supported VTK file format."
                .format(extension))

        self.file_path = path.abspath(file_name)
        self.fmt = fmt
        self.file = None

    def __enter__(self):
        """Open the file, in binary mode if needed."""
        # In Python 2.7 it seems to make no difference whether one is
        # iting pure string via a binary file stream or an ascii file
        # stream, thus just keep this as it is without checking the
        # version.
        if self.fmt == ASCII:
            self.file = open(self.file_path, "w")
        elif self.fmt == BINARY:
            self.file = open(self.file_path, "wb")
        else:
            raise ValueError("Format '{}' not supported.".format(self.fmt))

        return self

    def __exit__(self, type, value, traceback):
        """Close the file."""
        self.file.close()

    def write(self, output):
        """
        Write ascii or binary data into the corresponding VTK file.

        Parameters
        ----------
        output : str or binary data
            The output that will be written into the file.

        Returns
        -------
        None.

        """
        # In Python 2.7 struct.pack returns a string, that somehow
        # cannot be converted to a binary string but it makes no
        # difference anyway (see comment in methode __enter__). In
        # Python 3 binary string are obligatory.
        if sys.version_info >= (3,):
            if isinstance(output, str) and self.fmt == BINARY:
                self.file.write((output).encode("ascii"))
            elif isinstance(output, str) and self.fmt == ASCII:
                self.file.write(output)
            else:
                self.file.write(output)

        else:
            self.file.write(output)


class WriterBaseClass(object):
    """
    Base class for VTK writers.

    All writers must be derived from this class. The class contains
    methods that do not depend on the output format and, thus, will
    be the same for all writers.

    Parameters
    ----------
    output_dir : str, optional
        Directory, where all exported VTK files will be stored. The
        default is 'vtk_files'.
    clear_output_dir : bool, optional
        If this is True, the output directory will be cleared before
        exporting any files. The default is False.
    number_of_pieces : int, optional
        Number of pieces each model will be split into. The default
        is 1.

    Attributes
    ----------
    number_of_pieces : int
        Number of pieces each model will be split into.
    output_dir : str
        The path to the folder where all VTK files will be stored.
    FORMAT : ParaqusConstant
        A constant defining the type of writer, i.e. ASCII or BINARY.
        This is only for informational purposes.

    """
    __metaclass__ = ABCMeta

    def __init__(self,
                 output_dir="vtk_files",
                 clear_output_dir=False,
                 number_of_pieces=1):

        self.number_of_pieces = number_of_pieces
        self.output_dir = os.path.abspath(output_dir)
        self._part_frame_counter = {}
        self.FORMAT = None

        # Delete the output folder if requested
        if clear_output_dir and path.isdir(self.output_dir):

            # Deleting the current work directory does not make sense
            if path.abspath(self.output_dir) == os.getcwd():
                raise RuntimeError(
                    "Deleting the current directory not permitted.")

            # Catch any errors while removing the directory (e.g. open files)
            try:
                shutil.rmtree(self.output_dir)
            except PermissionError:
                raise PermissionError(
                    "Could not remove directory '" + self.output_dir + "'.")


    # Properties
    @property
    def number_of_pieces(self):
        return self._number_of_pieces

    @number_of_pieces.setter
    def number_of_pieces(self, number_of_pieces):
        if number_of_pieces < 1:
            raise ValueError("Number of pieces must be positive.")
        self._number_of_pieces = number_of_pieces


    # Methods
    @abstractmethod
    def _write_vtu_file(self, piece, piece_tag=0):
        """
        Abstract method to write a .vtu file to disk.

        The method will deliver the respective strings and array data to
        the context manager so that a .vtu file is created.
        """
        return

    def _create_folder(self, folder):
        """
        Create a new folder on the disk in case it does not exist already.

        Parameters
        ----------
        folder : str
            Path to the folder that will be created.

        Returns
        -------
        None.

        """
        abs_path = path.abspath(folder)
        if not path.isdir(abs_path):
            os.makedirs(abs_path)

    def write(self, model):
        """
        Write .vtu and .pvtu files for the model to disk.

        Export a paraqus model to .vtu file format. In case the model
        shall be split into multiple pieces, aditionally, a .pvtu file
        is created. The file names are set automatically in dependence
        on the model parameters.

        Parameters
        ----------
        model : ParaqusModel
            The model that will be exported.

        Returns
        -------
        file_path : str
            If the model is exported as one piece, this is the file path of the
            vtu file. If there are multiple pieces, it is the path to the
            corresponding pvtu file.

        """
        # Create pieces and write them to file
        vtu_files = []

        # Generator for submodels
        pieces = model.split_model(self.number_of_pieces)

        # Loop over the submodels
        for piece_tag, piece in enumerate(pieces):

            # Dump to disk
            vtu_file_path = self._write_vtu_file(piece, piece_tag)
            vtu_files.append(vtu_file_path)

        # Connect different pieces in a pvtu file
        if self.number_of_pieces == 1:
            return vtu_file_path

        if self.number_of_pieces > 1:
            pvtu_file_path = self._write_pvtu_file(model, vtu_files)
            return pvtu_file_path

    def _write_pvtu_file(self, model, vtu_files):
        """
        Write the .pvtu for multiple model pieces (and their .vtu files).

        Combine different submodels or pieces to the main model they
        are referring to by writing a .pvtu file.

        Parameters
        ----------
        model : ParaqusModel
            The main model the different pieces are referring to.
        vtu_files : list of str
            The paths to all exported .vtu files of the submodels.

        Returns
        -------
        file_path : str
            Path to the generated .pvtu file.

        """
        if len(vtu_files) <= 1:
            raise ValueError("Less than two vtu files available.")

        # Check input
        for f in vtu_files:

            if not path.splitext(f)[1] == ".vtu":
                raise ValueError("File '{}' is not a .vtu file.".format(f))

            if not path.isfile(path.join(
                    path.dirname(vtu_files[0]), path.basename(f))):
                raise ValueError("Vtu files not stored in the same folder.")

        # Create file name
        folder_name = path.dirname(vtu_files[0])
        virtual_frame = self._part_frame_counter[(model.model_name,
                                                 model.part_name, 0)]

        pvtu_file_name = model.part_name + "_{}.pvtu".format(virtual_frame - 1)
        file_path = path.join(folder_name, pvtu_file_name)

        # Since no array data will be written into the pvtu file
        # ascii format is completely fine here
        with VtkFileManager(file_path, ASCII) as pvtu_file:

            xml = XmlFactory(pvtu_file)

            # File header
            xml.add_element("VTKFile", type="PUnstructuredGrid",
                            version=VTK_VERSION_STRING, byte_order=BYTE_ORDER)
            xml.add_element("PUnstructuredGrid")

            # Add node fields
            xml.add_element("PPointData")
            for nf in model.node_fields:
                name = nf.field_name
                values = nf.get_3d_field_values()
                components = len(values[0])
                dtype = values.dtype.name
                xml.add_and_finish_element("PDataArray",
                                           type=VTK_TYPE_MAPPER[dtype],
                                           Name=name,
                                           NumberOfComponents=components)

            for group_name in model.nodes.groups:
                dtype = "uint8"
                xml.add_and_finish_element("PDataArray",
                                           type=VTK_TYPE_MAPPER[dtype],
                                           Name="_group " + group_name,
                                           NumberOfComponents=1)

            dtype = model.nodes.tags.dtype.name
            xml.add_and_finish_element("PDataArray",
                                       type=VTK_TYPE_MAPPER[dtype],
                                       Name="_node_tags",
                                       NumberOfComponents=1)

            xml.finish_element()  # Finish node fields

            # Add element fields
            xml.add_element("PCellData")
            for ef in model.element_fields:
                name = ef.field_name
                values = ef.get_3d_field_values()
                components = len(values[0])
                dtype=values.dtype.name
                xml.add_and_finish_element("PDataArray",
                                           type=VTK_TYPE_MAPPER[dtype],
                                           Name=name,
                                           NumberOfComponents=components)

            for group_name in model.elements.groups:
                dtype = "uint8"
                xml.add_and_finish_element("PDataArray",
                                           type=VTK_TYPE_MAPPER[dtype],
                                           Name="_group " + group_name,
                                           NumberOfComponents=1)

            dtype = model.elements.tags.dtype.name
            xml.add_and_finish_element("PDataArray",
                                       type=VTK_TYPE_MAPPER[dtype],
                                       Name="_element_tags",
                                       NumberOfComponents=1)

            xml.finish_element()  # Finish element fields

            # Add nodes
            xml.add_element("PPoints")
            coordinates = model.nodes.coordinates
            dtype=coordinates.dtype.name
            xml.add_and_finish_element("PDataArray",
                                       type=VTK_TYPE_MAPPER[dtype],
                                       NumberOfComponents=3)
            xml.finish_element()

            # Add pieces
            for piece_file in vtu_files:
                src = path.basename(piece_file)
                xml.add_and_finish_element("Piece", Source=src)

            xml.finish_all_elements()

        return file_path

    def _prepare_to_write_vtu_file(self, piece, piece_tag):
        """
        Prepare a ParaqusModel for the .vtu export.

        Parameters
        ----------
        piece : ParaqusModel
            The model or model piece to prepare for the export.
        piece_tag : int
            The piece identifier tag.

        Returns
        -------
        file_path : str
            The path to the resulting .vtu file.
        nel : int
            Number of elements.
        nnp : int
            Number of node points.
        element_tags : numpy.ndarray
            The original element tags.
        node_tags : numpy.ndarray
            The original node tags.
        node_coords : numpy.ndarray
            Nodal coordinates in shape (nnp,3).
        element_types : numpy.ndarray
            The VTK cell types.
        element_offsets : numpy.ndarray
            The offsets between the elements regarding the node points
            in order of the element types.
        connectivity : list of numpy.ndarray
            The connectivity list in order of the element types.

        """
        # Create a storage folder if there isn't one already
        folder_name = path.join(self.output_dir,
                                piece.model_name,
                                "vtu")
        self._create_folder(folder_name)

        # Generate a virtual frame number, so that frames are consecutive
        key = (piece.model_name, piece.part_name, piece_tag)
        virtual_frame = self._part_frame_counter.get(key, 0)

        # Define a name for the vtu file
        file_path = path.join(folder_name,
                              (piece.part_name
                               + "_{}_{}.vtu".format(piece_tag, virtual_frame))
                              )

        # Update the virtual frame
        self._part_frame_counter.update({key: virtual_frame + 1})

        # Number of elements and nodes
        nel = len(piece.elements.tags)
        nnp = len(piece.nodes.tags)

        # Extract some relevant arrays for the vtu output
        element_tags = piece.elements.tags
        node_tags = piece.nodes.tags
        node_coords = piece.nodes.coordinates
        tag_based_conn = piece.elements.connectivity
        element_types = piece.elements.types
        element_offsets = np.cumsum([len(c) for c in tag_based_conn],
                                    dtype=tag_based_conn[0].dtype)

        # Make 3d nodal coordinates
        rows, columns = node_coords.shape
        if columns == 2:
            node_coords = np.hstack((node_coords, np.zeros((rows,1))))
        elif columns == 1:
            node_coords = np.hstack((node_coords, np.zeros((rows,2))))

        # Create connectivity expressed in terms of the node indices
        node_index_mapper = piece.nodes.index_mapper
        connectivity = []
        for conn in tag_based_conn:
            connectivity.append(np.array([node_index_mapper[i] for i in conn],
                                    dtype=tag_based_conn[0].dtype))

        return (file_path, nel, nnp, element_tags, node_tags, node_coords,
                element_types, element_offsets, connectivity)


class BinaryWriter(WriterBaseClass):
    """
    Writer for the export of paraqus models to binary .vtu file format.

    Parameters
    ----------
    output_dir : str, optional
        Directory, where all exported VTK files will be stored. The
        default is 'vtk_files'.
    clear_output_dir : bool, optional
        If this is True, the output directory will be cleared before
        exporting any files. The default is False.
    number_of_pieces : int, optional
        Number of pieces each model will be split into. The default
        is 1.
    encoding : ParaqusConstant, optional
        The binary encoding used for data arrays. Currently supported
        are RAW and BASE64. The default is BASE64.
    header_type : ParaqusConstant, optional
        The data type used for the headers of the binary data blocks.
        Currently supported are UINT32 and UINT64. The default is
        UINT64.

    Attributes
    ----------
    number_of_pieces : int
        Number of pieces each model will be split into.
    output_dir : str
        The path to the folder where all VTK files will be stored.
    encoding : ParaqusConstant
        The binary encoding used for data arrays.
    header_type : ParaqusConstant
        The data type used for the headers of the binary data blocks.
    FORMAT : ParaqusConstant
        This is a constant with value BINARY and is only used for
        informational purposes.

    Example
    -------
    >>> from paraqus import BinaryWriter
    >>> from paraqus.constants import RAW
    >>> writer = BinaryWriter(number_of_pieces=2, encoding=RAW)
    >>> writer.write(random_paraqus_model)

    """
    # References:
    # https://mathema.tician.de/what-they-dont-tell-you-about-vtk-xml-binary-formats/
    # https://public.kitware.com/pipermail/paraview/2005-April/001391.html
    # https://github.com/paulo-herrera/PyEVTK
    # https://docs.python.org/2.7/library/struct.html

    # Somehow references are writing about vtk expecting fortran array ,
    # order in binary format, but in my tests this did not work and
    # c-type arrays yield the expected results. Maybe this has been
    # updated over time since the  references are quite old.

    def __init__(self,
                 output_dir="vtk_files",
                 clear_output_dir=False,
                 number_of_pieces=1,
                 encoding=BASE64,
                 header_type=UINT64):

        super(BinaryWriter, self).__init__(output_dir,
                                           clear_output_dir,
                                           number_of_pieces)
        self.header_type = header_type
        self.encoding = encoding
        self.FORMAT = BINARY


    # Properties
    @property
    def header_type(self):
        return self._header_type

    @header_type.setter
    def header_type(self, header_type):
        self._header_type = str(header_type).lower()
        self._header_size = BINARY_HEADER_SIZE_MAPPER[str(header_type).lower()]

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):

        if not encoding in (BASE64, RAW):
            raise ValueError("Invalid binary encoding.")

        self._encoding = encoding


    # Methods
    def _write_vtu_file(self, piece, piece_tag=0):
        """
        Write a .vtu file for a specified piece or submodel of a paraqus model.

        Parameters
        ----------
        piece : ParaqusModel
            The piece or submodel to export.
        piece_tag : int, optional
            The identifier of the currently processed piece. The
            default is 0.

        Returns
        -------
        file_path : str
            The path to the exported .vtu file.

        """
        (file_path,
         nel,
         nnp,
         element_tags,
         node_tags,
         node_coords,
         element_types,
         element_offsets,
         connectivity) = self._prepare_to_write_vtu_file(piece, piece_tag)

        # The connectivity is needed as one flattened array that is
        # expressed in terms of the node indices. One big 1d array
        # will be fine for binary output.
        connectivity = np.array(list(itertools.chain(*connectivity)),
                                dtype=piece.elements.connectivity[0].dtype)

        # Write the file
        with VtkFileManager(file_path, BINARY) as vtu_file:

            xml = XmlFactory(vtu_file, self.encoding,
                             self.header_type)

            # Xml attribute 'offset' breaks base64 encoded vtu files,
            # thus separate the definition of base64 encoded vtu files
            # and raw encoded vtu files.

            # Write base64 encoded file
            if self.encoding == BASE64:

                # File header
                xml.add_element("VTKFile", type="UnstructuredGrid",
                                version=VTK_VERSION_STRING,
                                byte_order=BYTE_ORDER,
                                header_type=VTK_TYPE_MAPPER[self.header_type])
                xml.add_element("UnstructuredGrid")

                # Add time data
                time_array = np.array([piece.frame_time])
                dtype = VTK_TYPE_MAPPER[time_array.dtype.name]
                xml.add_element("FieldData")
                xml.add_element("DataArray", Name="TimeValue",
                                NumberOfTuples=1, type=dtype, format="binary")
                xml.add_array_data_to_element(time_array)
                xml.finish_element()
                xml.finish_element()  # Finish definition of time data

                # Initialize model geometry
                xml.add_element("Piece", NumberOfPoints=nnp, NumberOfCells=nel)

                # Add nodes
                xml.add_element("Points")
                dtype = node_coords.dtype.name
                xml.add_element("DataArray",
                                type=VTK_TYPE_MAPPER[dtype],
                                Name="nodes", NumberOfComponents=3,
                                format="binary")
                xml.add_array_data_to_element(node_coords)
                xml.finish_element()
                xml.finish_element()  # Finish node definitions

                # Add connectivity
                xml.add_element("Cells")
                dtype = connectivity.dtype.name
                xml.add_element("DataArray",
                                type=VTK_TYPE_MAPPER[dtype],
                                Name="connectivity",
                                format="binary")
                xml.add_array_data_to_element(connectivity)
                xml.finish_element()

                # Add element offsets
                dtype = element_offsets.dtype.name
                xml.add_element("DataArray",
                                type=VTK_TYPE_MAPPER[dtype],
                                Name="offsets",
                                format="binary")
                xml.add_array_data_to_element(element_offsets)
                xml.finish_element()

                # Add element types
                dtype = element_types.dtype.name
                xml.add_element("DataArray",
                                type=VTK_TYPE_MAPPER[dtype],
                                Name="types",
                                format="binary")
                xml.add_array_data_to_element(element_types)
                xml.finish_element()
                xml.finish_element()  # Finish cell definitions

                # Add node fields
                xml.add_element("PointData")
                for nf in piece.node_fields:
                    field_vals = nf.get_3d_field_values()
                    components = len(field_vals[0])
                    dtype = field_vals.dtype.name

                    xml.add_element("DataArray",
                                    Name=nf.field_name,
                                    NumberOfComponents=components,
                                    type=VTK_TYPE_MAPPER[dtype],
                                    format="binary")

                    xml.add_array_data_to_element(field_vals)
                    xml.finish_element()

                # Add node fields based on groups
                for group_name, group_nodes in piece.nodes.groups.items():
                    field_vals = np.isin(piece.nodes.tags,
                                         group_nodes).astype(np.uint8)
                    dtype = field_vals.dtype.name

                    xml.add_element("DataArray",
                                    Name="_group " + group_name,
                                    NumberOfComponents=1,
                                    type=VTK_TYPE_MAPPER[dtype],
                                    format="binary")

                    xml.add_array_data_to_element(field_vals)
                    xml.finish_element()

                # Add node tags as field
                dtype = node_tags.dtype.name
                xml.add_element("DataArray",
                                Name="_node_tags",
                                NumberOfComponents=1,
                                type=VTK_TYPE_MAPPER[dtype],
                                format="binary")
                xml.add_array_data_to_element(node_tags)
                xml.finish_element()

                xml.finish_element()  # Finish node fields

                # Add element fields
                xml.add_element("CellData")
                for ef in piece.element_fields:
                    field_vals = ef.get_3d_field_values()
                    components = len(field_vals[0])
                    dtype=field_vals.dtype.name

                    xml.add_element("DataArray",
                                    Name=ef.field_name,
                                    NumberOfComponents=components,
                                    type=VTK_TYPE_MAPPER[dtype],
                                    format="binary")

                    xml.add_array_data_to_element(field_vals)
                    xml.finish_element()

                for group_name, group_elems in piece.elements.groups.items():
                    field_vals = np.isin(piece.elements.tags,
                                         group_elems).astype(np.uint8)
                    dtype = field_vals.dtype.name

                    xml.add_element("DataArray",
                                    Name="_group " + group_name,
                                    NumberOfComponents=1,
                                    type=VTK_TYPE_MAPPER[dtype],
                                    format="binary")

                    xml.add_array_data_to_element(field_vals)
                    xml.finish_element()

                # Add element tags as field
                dtype = element_tags.dtype.name
                xml.add_element("DataArray",
                                Name="_element_tags",
                                NumberOfComponents=1,
                                type=VTK_TYPE_MAPPER[dtype],
                                format="binary")
                xml.add_array_data_to_element(element_tags)
                xml.finish_element()

                xml.finish_all_elements()

            # Write raw encoded file
            elif self.encoding == RAW:

                # Byte offset is needed to identify data from appended list
                byte_offset = 0
                update_byte_offset = (lambda array:
                                      byte_offset
                                      + array.dtype.itemsize*array.size
                                      + self._header_size)

                # File header
                xml.add_element("VTKFile", type="UnstructuredGrid",
                                version=VTK_VERSION_STRING,
                                byte_order=BYTE_ORDER,
                                header_type=VTK_TYPE_MAPPER[self.header_type])
                xml.add_element("UnstructuredGrid")

                # Add time data
                time_array = np.array([piece.frame_time])
                dtype = time_array.dtype.name
                xml.add_element("FieldData")
                xml.add_and_finish_element("DataArray",
                                           Name="TimeValue",
                                           NumberOfTuples=1,
                                           type=VTK_TYPE_MAPPER[dtype],
                                           format="appended",
                                           offset=byte_offset)
                byte_offset = update_byte_offset(time_array)
                xml.finish_element()

                # Initialize model geometry
                xml.add_element("Piece", NumberOfPoints=nnp, NumberOfCells=nel)

                # Add nodes
                xml.add_element("Points")
                dtype = node_coords.dtype.name
                xml.add_and_finish_element("DataArray",
                                           type=VTK_TYPE_MAPPER[dtype],
                                           NumberOfComponents=3,
                                           format="appended",
                                           offset=byte_offset)
                byte_offset = update_byte_offset(node_coords)
                xml.finish_element()

                # Add connectivity
                xml.add_element("Cells")
                dtype = connectivity.dtype.name
                xml.add_and_finish_element("DataArray",
                                           type=VTK_TYPE_MAPPER[dtype],
                                           Name="connectivity",
                                           format="appended",
                                           offset=byte_offset)
                byte_offset = update_byte_offset(connectivity)

                # Add element offsets
                dtype = element_offsets.dtype.name
                xml.add_and_finish_element("DataArray",
                                           type=VTK_TYPE_MAPPER[dtype],
                                           Name="offsets",
                                           format="appended",
                                           offset=byte_offset)
                byte_offset = update_byte_offset(element_offsets)

                # Add element types
                dtype = element_types.dtype.name
                xml.add_and_finish_element("DataArray",
                                           type=VTK_TYPE_MAPPER[dtype],
                                           Name="types",
                                           format="appended",
                                           offset=byte_offset)
                byte_offset = update_byte_offset(element_types)
                xml.finish_element()

                # Add node fields
                xml.add_element("PointData")
                for nf in piece.node_fields:
                    field_vals = nf.get_3d_field_values()
                    components = len(field_vals[0])
                    dtype = field_vals.dtype.name

                    xml.add_and_finish_element("DataArray", Name=nf.field_name,
                                               NumberOfComponents=components,
                                               type=VTK_TYPE_MAPPER[dtype],
                                               format="appended",
                                               offset=byte_offset)
                    byte_offset = update_byte_offset(field_vals)

                # Node fields for groups
                for group_name, group_nodes in piece.nodes.groups.items():
                    field_vals = np.isin(piece.nodes.tags,
                                         group_nodes).astype(np.uint8)
                    dtype = field_vals.dtype.name

                    xml.add_and_finish_element("DataArray",
                                               Name="_group " + group_name,
                                               NumberOfComponents=1,
                                               type=VTK_TYPE_MAPPER[dtype],
                                               format="appended",
                                               offset=byte_offset)
                    byte_offset = update_byte_offset(field_vals)

                # Add node tags as field
                dtype = node_tags.dtype.name
                xml.add_and_finish_element("DataArray",
                                            Name="_node_tags",
                                            NumberOfComponents=1,
                                            type=VTK_TYPE_MAPPER[dtype],
                                            format="appended",
                                            offset=byte_offset)
                byte_offset = update_byte_offset(node_tags)

                xml.finish_element()  # Finish node fields

                # Add element fields
                xml.add_element("CellData")
                for ef in piece.element_fields:
                    field_vals = ef.get_3d_field_values()
                    components = len(field_vals[0])
                    dtype = field_vals.dtype.name

                    xml.add_and_finish_element("DataArray",
                                               Name=ef.field_name,
                                               NumberOfComponents=components,
                                               type=VTK_TYPE_MAPPER[dtype],
                                               format="appended",
                                               offset=byte_offset)
                    byte_offset = update_byte_offset(field_vals)

                # Element_fields for groups
                for group_name, group_elems in piece.elements.groups.items():
                    field_vals = np.isin(piece.elements.tags,
                                         group_elems).astype(np.uint8)
                    dtype = field_vals.dtype.name

                    xml.add_and_finish_element("DataArray",
                                               Name="_group " + group_name,
                                               NumberOfComponents=1,
                                               type=VTK_TYPE_MAPPER[dtype],
                                               format="appended",
                                               offset=byte_offset)
                    byte_offset = update_byte_offset(field_vals)

                # Add element tags as field
                dtype = element_tags.dtype.name
                xml.add_and_finish_element("DataArray",
                                            Name="_element_tags",
                                            NumberOfComponents=1,
                                            type=VTK_TYPE_MAPPER[dtype],
                                            format="appended",
                                            offset=byte_offset)
                byte_offset = update_byte_offset(element_tags)

                xml.finish_element()  # Finish cell data
                xml.finish_element()  # Finish piece
                xml.finish_element()  # Finish unstructured grid

                # Append geometry data
                xml.add_element("AppendedData", encoding="raw")
                xml.add_content_to_element("_", False)
                for array in [time_array, node_coords, connectivity,
                              element_offsets, element_types]:
                    xml.add_array_data_to_element(array, break_line=False)

                # Append node field data
                for nf in piece.node_fields:
                    field_vals = nf.get_3d_field_values()
                    xml.add_array_data_to_element(field_vals,
                                                  break_line=False)

                # Append node group data
                for group_name, group_nodes in piece.nodes.groups.items():
                    field_vals = np.isin(piece.nodes.tags,
                                         group_nodes).astype(np.uint8)
                    xml.add_array_data_to_element(field_vals, break_line=False)

                # Append node tags field
                xml.add_array_data_to_element(node_tags, break_line=False)

                # Append element field data
                for ef in piece.element_fields:
                    field_vals = ef.get_3d_field_values()
                    xml.add_array_data_to_element(field_vals,
                                                  break_line=False)

                # Append element group data
                for group_name, group_elems in piece.elements.groups.items():
                    field_vals = np.isin(piece.elements.tags,
                                         group_elems).astype(np.uint8)
                    xml.add_array_data_to_element(field_vals, break_line=False)

                # Add element tags field
                xml.add_array_data_to_element(element_tags)

                xml.finish_all_elements()

        return file_path


class AsciiWriter(WriterBaseClass):
    """
    Writer for the export of paraqus models to ascii .vtu file format.

    Parameters
    ----------
    output_dir : str, optional
        Directory, where all exported VTK files will be stored. The
        default is 'vtk_files'.
    clear_output_dir : bool, optional
        If this is True, the output directory will be cleared before
        exporting any files. The default is False.
    number_of_pieces : int, optional
        Number of pieces each model will be split into. The default
        is 1.

    Attributes
    ----------
    number_of_pieces : int
        Number of pieces each model will be split into.
    output_dir : str
        The path to the folder where all VTK files will be stored.
    FORMAT : ParaqusConstant
        This is a constant with value ASCII and is only used for
        informational purposes.

    Example
    -------
    >>> from paraqus import AsciiWriter
    >>> writer = AsciiWriter(number_of_pieces=2)
    >>> writer.write(random_paraqus_model)

    """

    def __init__(self,
                 output_dir="vtk_files",
                 clear_output_dir=False,
                 number_of_pieces=1):

        super(AsciiWriter, self).__init__(output_dir,
                                          clear_output_dir,
                                          number_of_pieces)
        self.FORMAT = ASCII


    # Methods
    def _write_vtu_file(self, piece, piece_tag=0):
        """
        Write a .vtu file for a specified piece or submodel of a paraqus model.

        Parameters
        ----------
        piece : ParaqusModel
            The piece or submodel to export.
        piece_tag : int, optional
            The identifier of the currently processed piece. The
            default is 0.

        Returns
        -------
        file_path : str
            The path to the exported .vtu file.

        """
        (file_path,
         nel,
         nnp,
         element_tags,
         node_tags,
         node_coords,
         element_types,
         element_offsets,
         connectivity) = self._prepare_to_write_vtu_file(piece, piece_tag)

        # Write the file
        with VtkFileManager(file_path, ASCII) as vtu_file:

            # File header
            xml = XmlFactory(vtu_file)
            xml.add_element("VTKFile", type="UnstructuredGrid",
                            version=VTK_VERSION_STRING, byte_order=BYTE_ORDER)
            xml.add_element("UnstructuredGrid")

            # Add time data
            time_array = np.array([piece.frame_time])
            xml.add_element("FieldData")
            xml.add_element("DataArray", Name="TimeValue", NumberOfTuples=1,
                            type=VTK_TYPE_MAPPER[time_array.dtype.name],
                            format="ascii")
            xml.add_array_data_to_element(time_array)
            xml.finish_element()
            xml.finish_element()  # Finish definition of time data

            # Initialize model geometry
            xml.add_element("Piece", NumberOfPoints=nnp, NumberOfCells=nel)

            # Add nodes
            xml.add_element("Points")
            xml.add_element("DataArray",
                            type=VTK_TYPE_MAPPER[node_coords.dtype.name],
                            Name="nodes", NumberOfComponents=3, format="ascii")
            xml.add_array_data_to_element(node_coords)
            xml.finish_element()
            xml.finish_element()  # Finish definition of nodes

            # Add connectivity
            xml.add_element("Cells")
            xml.add_element("DataArray",
                            type=VTK_TYPE_MAPPER[connectivity[0].dtype.name],
                            Name="connectivity", format="ascii")
            xml.add_array_data_to_element(connectivity)
            xml.finish_element()

            # Add element offsets
            xml.add_element("DataArray",
                            type=VTK_TYPE_MAPPER[element_offsets.dtype.name],
                            Name="offsets", format="ascii")
            xml.add_array_data_to_element(element_offsets)
            xml.finish_element()

            # Add element types
            xml.add_element("DataArray",
                            type=VTK_TYPE_MAPPER[element_types.dtype.name],
                            Name="types", format="ascii")
            xml.add_array_data_to_element(element_types)
            xml.finish_element()
            xml.finish_element()  # Finish definition of cells

            # Add node fields
            xml.add_element("PointData")

            for nf in piece.node_fields:
                field_vals = nf.get_3d_field_values()
                components = len(field_vals[0])
                dtype = field_vals.dtype.name

                xml.add_element("DataArray",
                                Name=nf.field_name,
                                NumberOfComponents=components,
                                type=VTK_TYPE_MAPPER[dtype],
                                format="ascii")

                xml.add_array_data_to_element(field_vals)
                xml.finish_element()

            # Add node fields based on groups
            for group_name, group_nodes in piece.nodes.groups.items():
                field_vals = np.isin(piece.nodes.tags,
                                     group_nodes).astype(np.uint8)
                dtype = field_vals.dtype.name

                xml.add_element("DataArray",
                                Name="_group " + group_name,
                                NumberOfComponents=1,
                                type=VTK_TYPE_MAPPER[dtype],
                                format="ascii")

                xml.add_array_data_to_element(field_vals)
                xml.finish_element()

            # Add node tags as field
            dtype = node_tags.dtype.name
            xml.add_element("DataArray",
                            Name="_node_tags",
                            NumberOfComponents=1,
                            type=VTK_TYPE_MAPPER[dtype],
                            format="ascii")
            xml.add_array_data_to_element(node_tags)
            xml.finish_element()

            xml.finish_element()  # Finish node fields

            # Add element fields
            xml.add_element("CellData")

            for ef in piece.element_fields:
                field_vals = ef.get_3d_field_values()
                components = len(field_vals[0])
                dtype=field_vals.dtype.name

                xml.add_element("DataArray",
                                Name=ef.field_name,
                                NumberOfComponents=components,
                                type=VTK_TYPE_MAPPER[dtype],
                                format="ascii")

                xml.add_array_data_to_element(field_vals)
                xml.finish_element()

            # Add element fields based on groups
            for group_name, group_elems in piece.elements.groups.items():
                field_vals = np.isin(piece.elements.tags,
                                     group_elems).astype(np.uint8)
                dtype = field_vals.dtype.name

                xml.add_element("DataArray",
                                Name="_goup " + group_name,
                                NumberOfComponents=1,
                                type= VTK_TYPE_MAPPER[dtype],
                                format="ascii")

                xml.add_array_data_to_element(field_vals)
                xml.finish_element()

            # Add element tags as field
            dtype = element_tags.dtype.name
            xml.add_element("DataArray",
                            Name="_element_tags",
                            NumberOfComponents=1,
                            type=VTK_TYPE_MAPPER[dtype],
                            format="ascii")
            xml.add_array_data_to_element(element_tags)
            xml.finish_element()

            xml.finish_all_elements()

        return file_path


class CollectionWriter(object):
    """
    Writer for the export of a collection of .pvtu or .vtu files.

    This writer can be used as a context manager to generate a .pvd file.

    Parameters
    ----------
    writer : BinaryWriter or AsciiWriter
        The writer that is used to generate .pvtu and .vtu files.
    collection_name : str
        The name of the collection. This is used for the .pdv file's
        name.

    Attributes
    ----------
    writer : BinaryWriter or AsciiWriter
        The writer that is used the generate .pvtu and .vtu files.
    collection_name : str
        The name of the collection.

    Example
    -------
    >>> from paraqus import BinaryWriter, CollectionWriter
    >>> vtu_writer = BinaryWriter()
    >>> with CollectionWriter(vtu_writer, "my_collection") as writer:
    >>>     writer.write(random_paraqus_model_frame_1)
    >>>     writer.write(random_paraqus_model_frame_2)
    >>>     writer.write(random_paraqus_model_frame_3)

    """
    def __init__(self, writer, collection_name):
        self.writer = writer
        self.collection_name = collection_name
        self._collection_items = None

    def __enter__(self):
        self._initialize_collection()
        return self

    def __exit__(self, type, value, traceback):
        self._finalize_collection()

    def write(self, model):
        """
        Write a ParaqusModel to a vtk file using the underlying writer.

        Parameters
        ----------
        model : ParaqusModel
            The model that will be converted to a vtk file.

        Returns
        -------
        None.

        """
        old_model_name = model.model_name
        model.model_name = self.collection_name

        vtu_file_path = self.writer.write(model)
        self._add_to_collection(model, vtu_file_path)

        model.model_name = old_model_name

    def _initialize_collection(self):
        """
        Initialize a new collection of ParaqusModels exported to .vtu files.

        A .pvd file that combines multiple .vtu or .pvtu files is
        generated from the collection when ``finalize_collection()``
        is called.

        Returns
        -------
        None.

        """
        self._collection_items = {}

    def _finalize_collection(self):
        """
        Export the .pvd file for the current collection and clear it.

        Returns
        -------
        None.

        """
        if len(self._collection_items) == 0:
            return

        self._write_pvd_file()
        self._collection_items = None

    def _add_to_collection(self, model, file_path):
        """
        Add a model to the current collection.

        Models do not need to be added in the correct order since the
        frame time is stored as a model attribute.

        Parameters
        ----------
        model : ParaqusModel
            The model that will be added to the collection.
        file_path : str
            The path to the .vtu or .pvtu file of the model to add.

        Returns
        -------
        None.

        """
        abspath = path.abspath(file_path)

        if self._collection_items is None:
            raise RuntimeError("Collection has not been initialized.")

        # Some input checking
        if path.splitext(file_path)[1] not in [".vtu", ".pvtu"]:
            raise ValueError("File is neither a .vtu file nor a .pvtu file.")
        if not path.isfile(abspath):
            raise ValueError("File '{}' does not exist.".format(abspath))

        # for each part, repo is a list of (time, file_path) tuples
        repo = self._collection_items.get(model.part_name)
        if repo is None:
            repo = self._collection_items[model.part_name] = []
        repo.append((model.frame_time, abspath))

    def _write_pvd_file(self):
        """
        Export a collection of multiple .vtu or .pvtu files.

        Returns
        -------
        None.

        """
        # Pvd files will be written into basedir/modelname/
        pvd_file_path = path.join(self.writer.output_dir,
                                  self.collection_name,
                                  self.collection_name + ".pvd")
        pvd_file_path = path.abspath(pvd_file_path)

        # Since no array data will be written into the pvd file ascii
        # format is completely fine here
        with VtkFileManager(pvd_file_path, ASCII) as pvd_file:

            xml = XmlFactory(pvd_file)

            xml.add_element("VTKFile", type="Collection",
                            version=VTK_VERSION_STRING, byte_order=BYTE_ORDER)
            xml.add_element("Collection")

            for i, part_name in enumerate(self._collection_items.keys()):

                for frame_time, file in self._collection_items[part_name]:

                    rel_path = path.relpath(file, path.dirname(pvd_file_path))
                    xml.add_and_finish_element("DataSet", timestep=frame_time,
                                               part=i, file=rel_path)

            xml.finish_all_elements()


class XmlFactory(object):
    """
    Factory to produce properly formatted XML files.

    Parameters
    ----------
    stream : VtkFileManager
        The output stream of the file that is written.
    encoding : ParaqusConstant, optional
        The binary encoding used for data arrays. Currently supported
        are RAW and BASE64. This is not needed in case of writing
        VTK ascii files. The default is None.
    header_type : ParaqusConstant, optional
        The data type used for the headers of the binary data blocks.
        Currently supported are UINT32 and UINT64. This is not needed in
        case of writing VTK ascii files. The default is None.

    """

    def __init__(self, stream, encoding=None, header_type=None):

        assert isinstance(stream, VtkFileManager)

        if stream.fmt == BINARY:
            assert encoding is not None
            assert header_type is not None

        self._stream = stream
        self._lvl = 0
        self._add_tabs = True
        self._elements = []
        self._active_element = None
        self._header_type = header_type
        self._encoding=encoding

    def add_element(self, name, break_line=True, **attributes):
        """
        Add a new element section to the XML file.

        Parameters
        ----------
        name : str
            Name of the element section.
        break_line : bool, optional
            If True, a linebreak will be inserted after the element
            section has been added. The default is True.
        **attributes : Text, Numeric
            Attributes of the element section. The keys will be the
            attribute's name, the values will be the attribute's value.

        Returns
        -------
        None.

        """
        to_write = '<{}'.format(name)
        for key, val in attributes.items():
            to_write += ' {}="{}"'.format(key, val)
        to_write += '>'

        if break_line:
            to_write += '\n'

        if self._add_tabs:
            to_write = self._lvl * '    ' + to_write
        self._stream.write(to_write)

        self._elements.append(name)
        self._active_element = name
        self._lvl += 1 if break_line else 0
        self._add_tabs = break_line

    def finish_element(self, break_line=True):
        """
        Close the active element section in the XML file.

        In case there is no active element section, nothing happens.

        Parameters
        ----------
        break_line : bool, optional
            If True, a linebreak will be inserted after the element
            section has been closed. The default is True.

        Returns
        -------
        None.

        """
        if self._active_element is None:
            return

        to_write = '</{}>'.format(self._elements.pop())

        if break_line:
            to_write += '\n'

        if self._add_tabs:
            to_write = (self._lvl - 1) * '    ' + to_write
        self._stream.write(to_write)

        self._lvl -= 1 if break_line else 0
        self._add_tabs = break_line

        if len(self._elements) > 0:
            self._active_element = self._elements[-1]
        else:
            self._active_element = None

    def finish_all_elements(self, break_line=True):
        """
        Close and finish all open element sections.

        Parameters
        ----------
        break_line : bool, optional
            If True, a linebreak will be inserted after each closed
            element section. The default is True.

        Returns
        -------
        None.

        """
        while len(self._elements) > 0:
            self.finish_element(break_line=break_line)

    def add_and_finish_element(self, name, break_line=True, **attributes):
        """
        Add an element section and close it immediately.

        Parameters
        ----------
        name : str
            Name of the element section.
        break_line : bool, optional
            If True, a linebreak will be inserted after each element
            section. The default is True.
        **attributes : Text, Numeric
            Attributes of the element section. The keys will be the
            attribute's name, the values will be the attribute's value.

        Returns
        -------
        None.

        """
        to_write = '<{}'.format(name)
        for key, val in attributes.items():
            to_write += ' {}="{}"'.format(key, val)
        to_write += '/>'

        if break_line:
            to_write += '\n'

        if self._add_tabs:
            to_write = self._lvl * '    ' + to_write
        self._stream.write(to_write)

    def add_content_to_element(self, content, break_line=True):
        """
        Add any content that is not a array-shaped to the XML file.

        Parameters
        ----------
        content : Text, Numeric
            The content to add.
        break_line : bool, optional
            If True, a linebreak will be inserted after the content hase
            been written. The default is True.

        Returns
        -------
        None.

        """
        if self._active_element is None:
            raise RuntimeError("No XML element is open.")

        if break_line:
            content += '\n'

        if self._add_tabs:
            content = self._lvl * '    ' + content
        self._stream.write(content)

    def add_array_data_to_element(self, array, break_line=True):
        """
        Add array data to the XML file.

        Parameters
        ----------
        array : numpy.ndarray
            The array data to add.
        break_line : bool, optional
            If True, a linebreak will be inserted after the array data.
            The default is True.

        Returns
        -------
        None.

        """
        if self._active_element is None:
            raise RuntimeError("No XML element is open.")

        if self._stream.fmt == BINARY:
            self._write_binary_array_data(array, break_line)

        elif self._stream.fmt == ASCII:
            self._write_ascii_array_data(array, break_line)

    def _write_binary_array_data(self, array, break_line=True):
        """
        Add binary encoded array data to the XML file.

        Parameters
        ----------
        array : numpy.ndarray
            The array to add to the output file.
        break_line : bool, optional
            If True, a linebreak will be inserted after the array data
            has been written.

        Returns
        -------
        None.

        """
        # Somehow references are writing about vtk expecting fortran array ,
        # order in binary format, but in my tests this did not work and
        # c-type arrays yield the expected results. Maybe this has been
        # updated over time since the  references are quite old.
        # binary_data = struct.pack(format_string, *np.ravel(array, order="F"))

        # Create a 32 or 64 bit length indicator of type unsigned int for
        # the header and create the header
        length_indicator = (BYTE_ORDER_CHAR
                            + BINARY_TYPE_MAPPER[self._header_type])
        block_size = array.dtype.itemsize*array.size
        header = struct.pack(length_indicator, block_size)

        # Creat a format string pack the array data
        format_string = (BYTE_ORDER_CHAR
                         + array.size
                         + BINARY_TYPE_MAPPER[array.dtype.name])
        data = struct.pack(format_string, *array.flatten())

        if self._encoding == BASE64:
            # Convert to base64
            b64_header = base64.b64encode(header)
            b64_data = base64.b64encode(data)

            if self._add_tabs:
                self._stream.write(self._lvl * '    ')
            self._stream.write(b64_header)
            self._stream.write(b64_data)

        elif self._encoding == RAW:
            self._stream.write(header)
            self._stream.write(data)

        if break_line:
            self._stream.write("\n")

        self._add_tabs = break_line

    def _write_ascii_array_data(self, array, break_line=True):
        """
        Add array data in ascii format to the XML file.

        Parameters
        ----------
        array : numpy.ndarray
            The array to add to the output file.
        line_break : bool, optional
            If True, a line break will be inserted after each line of
            the array.

        Returns
        -------
        None.

        """
        # Check if the array is 1d
        # AttributeError must be catched in case of a list as input,
        # e.g. in case of the connectivity
        try:
            if 1 in array.shape or len(array.shape) == 1:
                array = array.reshape(1,-1)
        except AttributeError:
            pass

        for i, line in enumerate(array):

            try:
                data_string = ''.join(str(val) + '    ' for val in line)[0:-4]
            except TypeError:  # In case of only one value per line
                data_string = str(line)

            if break_line:
                data_string += '\n'
            if not break_line and i == len(array):
                data_string += '    '

            if self._add_tabs:
                data_string = self._lvl * '    ' + data_string
            self._stream.write(data_string)

            self._add_tabs = break_line
