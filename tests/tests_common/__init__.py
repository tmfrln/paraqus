"""
This init file is required to guarantee that unittest can import the
folder as a package to discover the tests.

"""
from paraqus.paraqusmodel import ParaqusModel
from paraqus.constants import SCALAR, VECTOR, TENSOR, NODES, ELEMENTS

def get_test_mesh():
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
    element_types = [9, 9, 5, 5, 5]
    connectivity = [[1, 2, 5, 4],
                    [2, 3, 6, 5],
                    [4, 5, 7],
                    [5, 6, 8],
                    [5, 8, 7]]

    return node_tags, node_coords, element_tags, element_types, connectivity

def get_test_model():
    (node_tags,
     node_coords,
     element_tags,
     element_types,
     connectivity) = get_test_mesh()

    # Create four element base model
    model_name = "TEST_MODEL"
    part_name = "TEST_PART"
    step_name = "TEST_STEP"
    model = ParaqusModel(element_tags,
                         connectivity,
                         element_types,
                         node_tags,
                         node_coords,
                         model_name=model_name,
                         part_name=part_name,
                         step_name=step_name)

    return model

def get_test_field_data(field_position, field_type):
    field_map = {"scalar": [1, 2, 3, 4, 5, 6, 7, 8],
                 "vector": [[11, 12],
                            [21, 22],
                            [31, 32],
                            [41, 42],
                            [51, 52],
                            [61, 62],
                            [71, 72],
                            [81, 82]],
                 "tensor": [[11, 12, 13, 14],
                            [21, 22, 23, 24],
                            [31, 32, 33, 34],
                            [41, 42, 43, 44],
                            [51, 52, 53, 54],
                            [61, 62, 63, 64],
                            [71, 72, 73, 74],
                            [81, 82, 83, 84]]}

    field_values = field_map[str(field_type).lower()]

    if field_position == NODES:
        field_tags = get_test_mesh()[0]
    elif field_position == ELEMENTS:
        field_tags = get_test_mesh()[2]
    else:
        raise ValueError("Invalid field position.")

    return field_tags, field_values[0:len(field_tags)]
