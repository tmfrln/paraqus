"""
Tests for the BinaryWriter, AsciiWriter, CollectionWriter classes.

These tests can be executed in Abaqus python or in standard python 2.7+.

"""

import unittest
import numpy as np
import os
import datetime
import shutil

from paraqus.paraqusmodel import ParaqusModel
from paraqus.writers import AsciiWriter, BinaryWriter, CollectionWriter


class TestWritersGeneration(unittest.TestCase):
    
    def test_ascii_writer_generation(self):
        """AsciiWriter is initialized with correct attributes."""
        ascii_writer = AsciiWriter("test_path", 
                                   clear_output_dir=False, 
                                   number_of_pieces=2)
        
        assert ascii_writer.output_dir == os.path.abspath("test_path")
        assert ascii_writer.FORMAT == "ASCII"
        
    def test_binary_writer_generation(self):
        """BinaryWriter is initialized with correct attributes."""
        binary_writer = BinaryWriter("test_path", 
                                     clear_output_dir=False, 
                                     number_of_pieces=2)
        
        assert binary_writer.output_dir == os.path.abspath("test_path")
        assert binary_writer.FORMAT == "BINARY"
        
    def test_collection_writer_generation(self):
        """CollectionWriter is initialized with correct attributes."""
        binary_writer = BinaryWriter()
        collection_writer = CollectionWriter(binary_writer,
                                             "test_name")
        
        assert collection_writer.writer is binary_writer
        assert collection_writer.collection_name == "test_name"


class TestAsciiWriter(unittest.TestCase):
    
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
        
        self.ascii_folder = str(datetime.datetime.now()).replace(":", ".")
        
    def tearDown(self):
        """Delete dummy folder after test has finished."""
        if os.path.isdir(self.ascii_folder):
            shutil.rmtree(self.ascii_folder, ignore_errors=True)
        
    def test_write_vtu_file(self):
        """An ascii .vtu file can be written based on a ParaqusModel."""
        # Initialize writer
        ascii_writer = AsciiWriter(self.ascii_folder, 
                                   clear_output_dir=True, 
                                   number_of_pieces=1)
        
        # Export model
        ascii_writer.write(self.model)
        vtu_file = os.path.join(self.ascii_folder, "2D_TEST_MODEL", 
                                "vtu", "2D_TEST_PART_0_0.vtu")
        
        assert os.path.isfile(vtu_file)
        
    def test_write_pvtu_file(self):
        """Multiple ascii .vtu files can be written based on a ParaqusModel."""
        # Initialize writer
        ascii_writer = AsciiWriter(self.ascii_folder, 
                                   clear_output_dir=True, 
                                   number_of_pieces=2)
        
        # Export model
        ascii_writer.write(self.model)
        vtu_file_1 = os.path.join(self.ascii_folder, "2D_TEST_MODEL",
                                  "vtu", "2D_TEST_PART_0_0.vtu")
        vtu_file_2 = os.path.join(self.ascii_folder, "2D_TEST_MODEL",
                                  "vtu", "2D_TEST_PART_1_0.vtu")
        pvtu_file = os.path.join(self.ascii_folder, "2D_TEST_MODEL",
                                 "vtu", "2D_TEST_PART_0.pvtu")
        
        assert os.path.isfile(vtu_file_1)
        assert os.path.isfile(vtu_file_2)
        assert os.path.isfile(pvtu_file)
        

class TestBinaryWriter(unittest.TestCase):
    
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
        
        self.binary_folder = str(datetime.datetime.now()).replace(":", ".")
        
    def tearDown(self):
        """Delete dummy folder after test has finished."""
        if os.path.isdir(self.binary_folder):
            shutil.rmtree(self.binary_folder, ignore_errors=True)
        
    def test_write_vtu_file_base64(self):
        """A base64 .vtu file can be written based on a ParaqusModel."""
        # Initialize writer
        binary_writer = BinaryWriter(self.binary_folder, 
                                     clear_output_dir=True, 
                                     number_of_pieces=1)
        
        # Export model
        binary_writer.write(self.model)
        vtu_file = os.path.join(self.binary_folder, "2D_TEST_MODEL", 
                                "vtu", "2D_TEST_PART_0_0.vtu")
        
        assert os.path.isfile(vtu_file)
        
    def test_write_pvtu_file_base64(self):
        """Multiple base64 .vtu files can be written based on a ParaqusModel."""
        # Initialize writer
        binary_writer = BinaryWriter(self.binary_folder, 
                                     clear_output_dir=True, 
                                     number_of_pieces=2)
        
        # Export model
        binary_writer.write(self.model)
        vtu_file_1 = os.path.join(self.binary_folder, "2D_TEST_MODEL",
                                  "vtu", "2D_TEST_PART_0_0.vtu")
        vtu_file_2 = os.path.join(self.binary_folder, "2D_TEST_MODEL",
                                  "vtu", "2D_TEST_PART_1_0.vtu")
        pvtu_file = os.path.join(self.binary_folder, "2D_TEST_MODEL",
                                 "vtu", "2D_TEST_PART_0.pvtu")
        
        assert os.path.isfile(vtu_file_1)
        assert os.path.isfile(vtu_file_2)
        assert os.path.isfile(pvtu_file)
        
    def test_write_vtu_file_raw(self):
        """A raw .vtu file can be written based on a ParaqusModel."""
        # Initialize writer
        binary_writer = BinaryWriter(self.binary_folder, 
                                     clear_output_dir=True, 
                                     number_of_pieces=1,
                                     encoding="raw")
        
        # Export model
        binary_writer.write(self.model)
        vtu_file = os.path.join(self.binary_folder, "2D_TEST_MODEL", 
                                "vtu", "2D_TEST_PART_0_0.vtu")
        
        assert os.path.isfile(vtu_file)
        
    def test_write_pvtu_file_raw(self):
        """Multiple raw .vtu files can be written based on a ParaqusModel."""
        # Initialize writer
        binary_writer = BinaryWriter(self.binary_folder, 
                                     clear_output_dir=True, 
                                     number_of_pieces=2,
                                     encoding="raw")
        
        # Export model
        binary_writer.write(self.model)
        vtu_file_1 = os.path.join(self.binary_folder, "2D_TEST_MODEL",
                                  "vtu", "2D_TEST_PART_0_0.vtu")
        vtu_file_2 = os.path.join(self.binary_folder, "2D_TEST_MODEL",
                                  "vtu", "2D_TEST_PART_1_0.vtu")
        pvtu_file = os.path.join(self.binary_folder, "2D_TEST_MODEL",
                                 "vtu", "2D_TEST_PART_0.pvtu")
        
        assert os.path.isfile(vtu_file_1)
        assert os.path.isfile(vtu_file_2)
        assert os.path.isfile(pvtu_file)


class TestCollectionWriter(unittest.TestCase):
    
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
        
        self.collection_folder = str(datetime.datetime.now()).replace(":", ".")
        
    def tearDown(self):
        """Delete dummy folder after test has finished."""
        if os.path.isdir(self.collection_folder):
            shutil.rmtree(self.collection_folder, ignore_errors=True)
            
    def test_write_pvd_file(self):
        """A .pvd file can be written as a collection of .vtu files."""
        # Initialize writer
        binary_writer = BinaryWriter(self.collection_folder, 
                                     clear_output_dir=True, 
                                     number_of_pieces=2)
        
        # Make pvd file
        with CollectionWriter(binary_writer, "2D_TEST_MODEL") as writer:
            writer.write(self.model)
            
        vtu_file_1 = os.path.join(self.collection_folder, "2D_TEST_MODEL",
                                  "vtu", "2D_TEST_PART_0_0.vtu")
        vtu_file_2 = os.path.join(self.collection_folder, "2D_TEST_MODEL",
                                  "vtu", "2D_TEST_PART_1_0.vtu")
        pvtu_file = os.path.join(self.collection_folder, "2D_TEST_MODEL",
                                 "vtu", "2D_TEST_PART_0.pvtu")
        pvd_file = os.path.join(self.collection_folder, "2D_TEST_MODEL",
                                "2D_TEST_MODEL.pvd")
        
        assert os.path.isfile(vtu_file_1)
        assert os.path.isfile(vtu_file_2)
        assert os.path.isfile(pvtu_file)
        assert os.path.isfile(pvd_file)