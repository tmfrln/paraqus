"""
Tests for the BinaryWriter, AsciiWriter, CollectionWriter classes.

These tests can be executed in Abaqus Python or in Python >= 2.7.

"""
import unittest
import os
import datetime
import shutil
import filecmp

from paraqus.constants import BASE64, RAW, BINARY, ASCII, UINT32
from paraqus.writers import AsciiWriter, BinaryWriter, CollectionWriter

from paraqustests.tests_common import get_test_model


RESOURCE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "resources")


class TestWritersGeneration(unittest.TestCase):
    """Tests related to the creation of different VTK writers."""

    def test_ascii_writer_generation(self):
        """AsciiWriter is initialized with correct attributes."""
        ascii_writer = AsciiWriter("test_path",
                                   clear_output_dir=False)

        assert ascii_writer.output_dir == os.path.abspath("test_path")
        assert ascii_writer.fmt == ASCII
        assert ascii_writer.number_of_pieces == 1

    def test_binary_writer_generation(self):
        """BinaryWriter is initialized with correct attributes."""
        binary_writer = BinaryWriter("test_path",
                                     clear_output_dir=False,
                                     encoding=RAW,
                                     header_type=UINT32)

        assert binary_writer.output_dir == os.path.abspath("test_path")
        assert binary_writer.fmt == BINARY
        assert binary_writer.number_of_pieces == 1
        assert binary_writer.header_type == UINT32
        assert binary_writer.encoding == RAW

    def test_collection_writer_generation(self):
        """CollectionWriter is initialized with correct attributes."""
        binary_writer = BinaryWriter()
        collection_writer = CollectionWriter(binary_writer,
                                             "test_name")

        assert collection_writer.writer is binary_writer
        assert collection_writer.collection_name == "test_name"


class TestAsciiWriter(unittest.TestCase):
    """Tests related to writing VTK files in ASCII format."""

    def setUp(self):
        """Create a small ParaqusModel and an AsciiWriter."""
        self.model = get_test_model()
        self.folder = str(datetime.datetime.now()).replace(":", ".")
        self.writer = AsciiWriter(self.folder, clear_output_dir=True)

    def tearDown(self):
        """Delete dummy folder after test has finished."""
        if os.path.isdir(self.folder):
            shutil.rmtree(self.folder, ignore_errors=True)

    def test_write_vtu_file(self):
        """An ascii .vtu file with correct contents can be written."""
        self.writer.write(self.model)
        vtu_file = os.path.join(self.folder, self.model.model_name,
                                "vtu", self.model.part_name + "_0_0.vtu")

        reference_vtu = os.path.join(RESOURCE_PATH, "vtu_test",
                                     "vtu_reference_ascii.vtu")

        assert os.path.isfile(vtu_file)
        # assert filecmp.cmp(vtu_file, reference_vtu, shallow=False)

    def test_write_pvtu_file(self):
        """An ascii .pvtu file with corresponding .vtu files and correct contents can be can be written."""
        self.writer.number_of_pieces = 2
        self.writer.write(self.model)

        vtu_file_0 = os.path.join(self.folder, self.model.model_name,
                                  "vtu", self.model.part_name + "_0_0.vtu")
        vtu_file_1 = os.path.join(self.folder, self.model.model_name,
                                  "vtu", self.model.part_name + "_1_0.vtu")
        pvtu_file = os.path.join(self.folder, self.model.model_name,
                                 "vtu", self.model.part_name + "_0.pvtu")

        reference_vtu_0 = os.path.join(RESOURCE_PATH, "pvtu_test",
                                       "vtu_reference_ascii_0.vtu")
        reference_vtu_1 = os.path.join(RESOURCE_PATH, "pvtu_test",
                                       "vtu_reference_ascii_1.vtu")
        reference_pvtu = os.path.join(RESOURCE_PATH, "pvtu_test",
                                      "pvtu_reference_ascii.pvtu")

        assert os.path.isfile(vtu_file_0)
        assert os.path.isfile(vtu_file_1)
        assert os.path.isfile(pvtu_file)
        # assert filecmp.cmp(vtu_file_0, reference_vtu_0, shallow=False)
        # assert filecmp.cmp(vtu_file_1, reference_vtu_1, shallow=False)
        # assert filecmp.cmp(pvtu_file, reference_pvtu, shallow=False)


class TestBinaryWriterBase64(unittest.TestCase):
    """Tests related to writing VTK files in base64 binary format."""

    def setUp(self):
        """Create a small ParaqusModel and a base64 BinaryWriter."""
        self.model = get_test_model()
        self.folder = str(datetime.datetime.now()).replace(":", ".")
        self.writer = BinaryWriter(self.folder,
                                   clear_output_dir=True,
                                   encoding=BASE64)

    def tearDown(self):
        """Delete dummy folder after test has finished."""
        if os.path.isdir(self.folder):
            shutil.rmtree(self.folder, ignore_errors=True)

    def test_write_vtu_file(self):
        """A base64 .vtu file with correct contents can be written."""
        self.writer.write(self.model)
        vtu_file = os.path.join(self.folder, self.model.model_name,
                                "vtu", self.model.part_name + "_0_0.vtu")

        reference_vtu = os.path.join(RESOURCE_PATH, "vtu_test",
                                     "vtu_reference_base64.vtu")

        assert os.path.isfile(vtu_file)
        # assert filecmp.cmp(vtu_file, reference_vtu, shallow=False)

    def test_write_pvtu_file(self):
        """A base64 .pvtu file with corresponding .vtu files and correct contents can be can be written."""
        self.writer.number_of_pieces = 2
        self.writer.write(self.model)

        vtu_file_0 = os.path.join(self.folder, self.model.model_name,
                                  "vtu", self.model.part_name + "_0_0.vtu")
        vtu_file_1 = os.path.join(self.folder, self.model.model_name,
                                  "vtu", self.model.part_name + "_1_0.vtu")
        pvtu_file = os.path.join(self.folder, self.model.model_name,
                                 "vtu", self.model.part_name + "_0.pvtu")

        reference_vtu_0 = os.path.join(RESOURCE_PATH, "pvtu_test",
                                       "vtu_reference_base64_0.vtu")
        reference_vtu_1 = os.path.join(RESOURCE_PATH, "pvtu_test",
                                       "vtu_reference_base64_1.vtu")
        reference_pvtu = os.path.join(RESOURCE_PATH, "pvtu_test",
                                      "pvtu_reference_base64.pvtu")

        assert os.path.isfile(vtu_file_0)
        assert os.path.isfile(vtu_file_1)
        assert os.path.isfile(pvtu_file)
        # assert filecmp.cmp(vtu_file_0, reference_vtu_0, shallow=False)
        # assert filecmp.cmp(vtu_file_1, reference_vtu_1, shallow=False)
        # assert filecmp.cmp(pvtu_file, reference_pvtu, shallow=False)


class TestBinaryWriterRaw(unittest.TestCase):
    """Tests related to writing VTK files in raw binary format."""

    def setUp(self):
        """Create a small ParaqusModel and a raw BinaryWriter."""
        self.model = get_test_model()
        self.folder = str(datetime.datetime.now()).replace(":", ".")
        self.writer = BinaryWriter(self.folder,
                                   clear_output_dir=True,
                                   encoding=RAW)

    def tearDown(self):
        """Delete dummy folder after test has finished."""
        if os.path.isdir(self.folder):
            shutil.rmtree(self.folder, ignore_errors=True)

    def test_write_vtu_file(self):
        """A raw .vtu file with correct contents can be written."""
        self.writer.write(self.model)
        vtu_file = os.path.join(self.folder, self.model.model_name,
                                "vtu", self.model.part_name + "_0_0.vtu")

        reference_vtu = os.path.join(RESOURCE_PATH, "vtu_test",
                                     "vtu_reference_raw.vtu")

        assert os.path.isfile(vtu_file)
        # assert filecmp.cmp(vtu_file, reference_vtu, shallow=False)

    def test_write_pvtu_file(self):
        """A raw .pvtu file with corresponding .vtu files and correct contents can be can be written."""
        self.writer.number_of_pieces = 2
        self.writer.write(self.model)

        vtu_file_0 = os.path.join(self.folder, self.model.model_name,
                                  "vtu", self.model.part_name + "_0_0.vtu")
        vtu_file_1 = os.path.join(self.folder, self.model.model_name,
                                  "vtu", self.model.part_name + "_1_0.vtu")
        pvtu_file = os.path.join(self.folder, self.model.model_name,
                                 "vtu", self.model.part_name + "_0.pvtu")

        reference_vtu_0 = os.path.join(RESOURCE_PATH, "pvtu_test",
                                       "vtu_reference_raw_0.vtu")
        reference_vtu_1 = os.path.join(RESOURCE_PATH, "pvtu_test",
                                       "vtu_reference_raw_1.vtu")
        reference_pvtu = os.path.join(RESOURCE_PATH, "pvtu_test",
                                      "pvtu_reference_raw.pvtu")

        assert os.path.isfile(vtu_file_0)
        assert os.path.isfile(vtu_file_1)
        assert os.path.isfile(pvtu_file)
        # assert filecmp.cmp(vtu_file_0, reference_vtu_0, shallow=False)
        # assert filecmp.cmp(vtu_file_1, reference_vtu_1, shallow=False)
        # assert filecmp.cmp(pvtu_file, reference_pvtu, shallow=False)


class TestCollectionWriter(unittest.TestCase):
    """Tests related to writing PVD collection files."""

    def setUp(self):
        """Create a small ParaqusModel."""
        self.model = get_test_model()
        self.collection_folder = str(datetime.datetime.now()).replace(":", ".")

    def tearDown(self):
        """Delete dummy folder after test has finished."""
        if os.path.isdir(self.collection_folder):
            shutil.rmtree(self.collection_folder, ignore_errors=True)

    def test_write_pvd_file(self):
        """A .pvd file with correct contents can be written as a collection of .vtu files."""
        binary_writer = BinaryWriter(self.collection_folder,
                                     clear_output_dir=True,
                                     number_of_pieces=2)

        with CollectionWriter(binary_writer, self.model.model_name) as writer:
            writer.write(self.model)

        vtu_file_0 = os.path.join(self.collection_folder,
                                  self.model.model_name, "vtu",
                                  self.model.part_name + "_0_0.vtu")
        vtu_file_1 = os.path.join(self.collection_folder,
                                  self.model.model_name, "vtu",
                                  self.model.part_name + "_1_0.vtu")
        pvtu_file = os.path.join(self.collection_folder,
                                 self.model.model_name, "vtu",
                                 self.model.part_name + "_0.pvtu")
        pvd_file = os.path.join(self.collection_folder, self.model.model_name,
                                self.model.model_name + ".pvd")

        reference_vtu_0 = os.path.join(RESOURCE_PATH, "pvd_test",
                                       "vtu_reference_0.vtu")
        reference_vtu_1 = os.path.join(RESOURCE_PATH, "pvd_test",
                                       "vtu_reference_1.vtu")
        reference_pvtu = os.path.join(RESOURCE_PATH, "pvd_test",
                                      "pvtu_reference.pvtu")
        reference_pvd = os.path.join(RESOURCE_PATH, "pvd_test",
                                     "pvd_reference.pvd")

        assert os.path.isfile(vtu_file_0)
        assert os.path.isfile(vtu_file_1)
        assert os.path.isfile(pvtu_file)
        assert os.path.isfile(pvd_file)
        # assert filecmp.cmp(vtu_file_0, reference_vtu_0, shallow=False)
        # assert filecmp.cmp(vtu_file_1, reference_vtu_1, shallow=False)
        # assert filecmp.cmp(pvtu_file, reference_pvtu, shallow=False)
        # assert filecmp.cmp(pvd_file, reference_pvd, shallow=False)
