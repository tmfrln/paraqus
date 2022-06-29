"""
Small example modes for unit testing.

These models will be imported by the actual tests

"""

def create_example_model():
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

    # Add some field outputs
    tensor_field_vals = [[1,1,1,1],[2,2,2,2],[3,3,3,3],[4,4,4,4],[5,5,5,5]]
    vector_field_vals = [[1,1,1],[2,2,2],[3,3,3],[4,4,4],[5,5,5]]
    model_1.add_field_output("tensor_field", [1,2,3,4,5], tensor_field_vals,
                             "elements", "tensor")
    model_1.add_field_output("vector_field", [1,2,3,4,5], vector_field_vals,
                             "elements", "vector")
