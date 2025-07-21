import tempfile
import pytest
from strumyk.semantic_validator import SemanticValidator, SemanticValidationError
 
def write_temp_yaml(content):
    """Creates a temporary YAML file and returns its path."""
    # We use delete=False so the file is not removed after closing the handle.
    # The file will be automatically deleted by pytest.
    tmp = tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding='utf-8')
    tmp.write(content)
    tmp.flush()
    tmp.close()
    return tmp.name 

def test_unique_place_ids_valid_yaml():
    yaml_definition = """
    net: example_process
    version: "1.0"
    places:
      - id: p1
        label: Start
      - id: p2
        label: In_Progress
      - id: p3
        label: End
    transitions: []
    """
    yaml_path = write_temp_yaml(yaml_definition)
    validator = SemanticValidator(yaml_path)
    assert validator.validate_unique_place_ids() is True
    
def test_unique_place_ids_duplicate_yaml():
    yaml_definition = """
    net: error_process
    version: "1.0"
    places:
      - id: p1
        label: Step_A
      - id: p2
        label: Step_B
      - id: p1 # Duplicate ID
        label: Step_C_duplicate
    transitions: []
    """
    path = write_temp_yaml(yaml_definition)
    validator = SemanticValidator(path)
    
    assert validator.validate_unique_place_ids() is False

def test_unique_transition_ids_valid_yaml():
    yaml_definition = """
    net: example_process
    version: "1.0"
    places:
      - id: p1
      - id: p2
    transitions:
      - id: t1
        input: [p1]
        output: [p2]
      - id: t2
        input: [p2]
        output: [p1]
      - id: t3
        input: [p1]
        output: [p2]
    """
    yaml_path = write_temp_yaml(yaml_definition)
    validator = SemanticValidator(yaml_path)
    assert validator.validate_unique_transition_ids() is True    

def test_unique_transition_ids_duplicate_yaml():
    yaml_definition = """
    net: error_process
    version: "1.0"
    places:
      - id: p1
      - id: p2
    transitions:
      - id: t1
        input: [p1]
        output: [p2]
      - id: t2
        input: [p2]
        output: [p1]
      - id: t1 # Duplicate ID
        input: [p1]
        output: [p2]
    """
    yaml_path = write_temp_yaml(yaml_definition)
    validator = SemanticValidator(yaml_path)
    
    with pytest.raises(SemanticValidationError) as excinfo:
        validator.validate_unique_transition_ids()
    assert "Duplicate transition ID found: 't1'" in str(excinfo.value)

def test_disjoint_ids_valid_yaml():
    yaml_definition = """
    net: disjoint_ids_net
    version: "1.0"
    places:
      - id: p1
      - id: p2
    transitions:
      - id: t1
      - id: t2
    """
    yaml_path = write_temp_yaml(yaml_definition)
    validator = SemanticValidator(yaml_path)
    assert validator.validate_disjoint_place_and_transition_ids() is True

def test_disjoint_ids_with_conflict_yaml():
    yaml_definition = """
    net: conflicting_ids_net
    version: "1.0"
    places:
      - id: p1
      - id: common_id # Conflict here
    transitions:
      - id: t1
      - id: common_id # Conflict here
    """
    yaml_path = write_temp_yaml(yaml_definition)
    validator = SemanticValidator(yaml_path)
    
    with pytest.raises(SemanticValidationError) as excinfo:
        validator.validate_disjoint_place_and_transition_ids()
    assert "Conflicting IDs found: IDs ['common_id'] are used for both places and transitions." in str(excinfo.value)

def test_single_start_place_valid_yaml():
    """
    Tests the scenario with exactly one valid start place.
    """
    yaml_definition_correct_start = """
    net: correct_start_net
    version: "1.0"
    places:
      - id: p_start # This is the unique start place
      - id: p_middle
      - id: p_end
    transitions:
      - id: t1
        input: [p_start] # p_start is an input
        output: [p_middle]
      - id: t2
        input: [p_middle]
        output: [p_end]
    """
    yaml_path = write_temp_yaml(yaml_definition_correct_start)
    validator = SemanticValidator(yaml_path)
    assert validator.validate_single_start_place() is True

def test_single_start_place_no_start_place_found_yaml():
    """
    Tests the scenario where all places have incoming arcs, so no start place exists.
    Expects a SemanticValidationError.
    """
    yaml_definition = """
    net: no_start_place_net
    version: "1.0"
    places:
      - id: p1
      - id: p2
    transitions:
      - id: t1
        input: [p2] # p1 has incoming from t2
        output: [p1]
      - id: t2
        input: [p1] # p2 has incoming from t1
        output: [p2]
    """
    yaml_path = write_temp_yaml(yaml_definition)
    validator = SemanticValidator(yaml_path)
    
    with pytest.raises(SemanticValidationError) as excinfo:
        validator.validate_single_start_place()
    assert "No start place found: All places have incoming arcs." in str(excinfo.value)

def test_single_start_place_multiple_start_places_yaml():
    """
    Tests the scenario with multiple start places. Expects a SemanticValidationError.
    """
    yaml_definition = """
    net: multiple_starts_net
    version: "1.0"
    places:
      - id: p_start1 # Start place 1
      - id: p_start2 # Start place 2
      - id: p1
    transitions:
      - id: t1
        input: [p_start1]
        output: [p1]
      - id: t2
        input: [p_start2]
        output: [p1]
    """
    yaml_path = write_temp_yaml(yaml_definition)
    validator = SemanticValidator(yaml_path)
    
    with pytest.raises(SemanticValidationError) as excinfo:
        validator.validate_single_start_place()
    assert "Expected exactly one start place, but found 2: ['p_start1', 'p_start2']" in str(excinfo.value)

def test_single_end_place_valid_yaml():
    """
    Tests the scenario with exactly one valid end place.
    """
    yaml_definition_correct_end = """
    net: correct_end_net
    version: "1.0"
    places:
      - id: p_start
      - id: p_middle
      - id: p_end # This is the unique end place
    transitions:
      - id: t1
        input: [p_start]
        output: [p_middle]
      - id: t2
        input: [p_middle]
        output: [p_end] # p_end is an output, but not an input to any transition
    """
    yaml_path = write_temp_yaml(yaml_definition_correct_end)
    validator = SemanticValidator(yaml_path)
    assert validator.validate_single_end_place() is True

def test_single_end_place_no_end_place_found_yaml():
    """
    Tests the scenario where all places have outgoing arcs (are inputs to transitions),
    so no end place exists. Expects a SemanticValidationError.
    """
    yaml_definition = """
    net: no_end_place_net
    version: "1.0"
    places:
      - id: p1
      - id: p2
    transitions:
      - id: t1
        input: [p1] # p1 has outgoing to t1
        output: [p2]
      - id: t2
        input: [p2] # p2 has outgoing to t2
        output: [p1]
    """
    yaml_path = write_temp_yaml(yaml_definition)
    validator = SemanticValidator(yaml_path)
    
    with pytest.raises(SemanticValidationError) as excinfo:
        validator.validate_single_end_place()
    assert "No end place found: All places have outgoing arcs." in str(excinfo.value)

def test_single_end_place_multiple_end_places_yaml():
    """
    Tests the scenario with multiple end places. Expects a SemanticValidationError.
    """
    yaml_definition = """
    net: multiple_ends_net
    version: "1.0"
    places:
      - id: p1
      - id: p_end1 # End place 1
      - id: p_end2 # End place 2
    transitions:
      - id: t1
        input: [p1]
        output: [p_end1] # p_end1 is an output, not an input to anything
      - id: t2
        input: [p1]
        output: [p_end2] # p_end2 is an output, not an input to anything
    """
    yaml_path = write_temp_yaml(yaml_definition)
    validator = SemanticValidator(yaml_path)
    
    with pytest.raises(SemanticValidationError) as excinfo:
        validator.validate_single_end_place()
    assert "Expected exactly one end place, but found 2: ['p_end1', 'p_end2']" in str(excinfo.value)
    
def test_all_nodes_on_path_valid_linear_yaml():
    """
    Tests a simple linear WF-net where all nodes are on the path from start to end.
    """
    yaml_definition = """
    net: linear_process
    version: "1.0"
    places:
      - id: i # Start
      - id: p1
      - id: p2
      - id: o # End
    transitions:
      - id: t1
        input: [i]
        output: [p1]
      - id: t2
        input: [p1]
        output: [p2]
      - id: t3
        input: [p2]
        output: [o]
    """
    yaml_path = write_temp_yaml(yaml_definition)
    validator = SemanticValidator(yaml_path)
    assert validator.validate_all_nodes_on_path_from_start_to_end() is True

def test_all_nodes_on_path_with_branching_yaml():
    """
    Tests a WF-net with branching where all nodes are still on the path.
    """
    yaml_definition = """
    net: branching_process
    version: "1.0"
    places:
      - id: i
      - id: p1
      - id: p2
      - id: p3
      - id: o
    transitions:
      - id: t1
        input: [i]
        output: [p1]
      - id: t2 # Branch 1
        input: [p1]
        output: [p2]
      - id: t3 # Branch 2
        input: [p1]
        output: [p3]
      - id: t4
        input: [p2, p3] # Join
        output: [o]
    """
    yaml_path = write_temp_yaml(yaml_definition)
    validator = SemanticValidator(yaml_path)
    assert validator.validate_all_nodes_on_path_from_start_to_end() is True

def test_all_nodes_on_path_isolated_place_yaml():
        """
        Tests a WF-net with an isolated place.
        The isolated place is not reachable from the start, and the end is not reachable from it.
        It does NOT violate the single start/end place axiom.
        Expects a SemanticValidationError for unreachable nodes.
        """
        yaml_definition_correct_isolated_test = """
        net: isolated_place_net_correct_test
        version: "1.0"
        places:
          - id: i
          - id: p1
          - id: o
          - id: isolated_p # This place should be detected as not on path
        transitions:
          - id: t1
            input: [i]
            output: [p1]
          - id: t2
            input: [p1]
            output: [o]
          # To ensure isolated_p is NOT a start place and NOT an end place,
          # but IS isolated from the main flow, we give it a self-loop transition.
          - id: t_self_loop
            input: [isolated_p]
            output: [isolated_p]
        """
        yaml_path = write_temp_yaml(yaml_definition_correct_isolated_test)
        validator = SemanticValidator(yaml_path)
        
        with pytest.raises(SemanticValidationError) as excinfo:
            validator.validate_all_nodes_on_path_from_start_to_end()
        
        # Now, 'isolated_p' is neither a start nor an end place, but it's unreachable
        # from 'i' and 'o' is unreachable from it.
        # The error message should now correctly point to 'isolated_p'.
        # It should appear in BOTH unreachable lists, depending on the traversal order.
        assert "Nodes unreachable from start place 'i': ['isolated_p', 't_self_loop']" in str(excinfo.value) or \
               "Nodes from which end place 'o' is unreachable: ['isolated_p', 't_self_loop']" in str(excinfo.value)

def test_all_nodes_on_path_isolated_transition_yaml():
    """
    Tests a WF-net with an isolated transition and its connected places.
    These nodes are not reachable from the start, and the end is not reachable from them.
    It does NOT violate the single start/end place axiom.
    Expects a SemanticValidationError for unreachable nodes.
    """
    yaml_definition = """
    net: isolated_transition_net_fixed
    version: "1.0"
    places:
      - id: i
      - id: p1
      - id: o
      - id: p_isolated_A # Part of isolated sub-net
      - id: p_isolated_B # Part of isolated sub-net
    transitions:
      - id: t1
        input: [i]
        output: [p1]
      - id: t2
        input: [p1]
        output: [o]
      # --- Isolated sub-net (a disconnected cycle) ---
      - id: t_isolated_cycle_1 
        input: [p_isolated_A]
        output: [p_isolated_B]
      - id: t_isolated_cycle_2
        input: [p_isolated_B]
        output: [p_isolated_A] # Forms a loop: p_isolated_A -> t_isolated_cycle_1 -> p_isolated_B -> t_isolated_cycle_2 -> p_isolated_A
    """
    yaml_path = write_temp_yaml(yaml_definition)
    validator = SemanticValidator(yaml_path)
    
    with pytest.raises(SemanticValidationError) as excinfo:
        validator.validate_all_nodes_on_path_from_start_to_end()
    
    # Now, 'p_isolated_A' has an incoming arc (from t_isolated_cycle_2)
    # and 'p_isolated_B' has an incoming arc (from t_isolated_cycle_1).
    # Neither are detected as a second start place.
    # The entire isolated cycle (p_isolated_A, p_isolated_B, t_isolated_cycle_1, t_isolated_cycle_2)
    # will be detected as unreachable from 'i' and unable to reach 'o'.
    
    expected_unreachable_nodes = sorted(['p_isolated_A', 'p_isolated_B', 't_isolated_cycle_1', 't_isolated_cycle_2'])
    
    # The error message should now correctly point to these nodes.
    # It should appear in BOTH unreachable lists, depending on the traversal order.
    # Using 'in' and checking for sorted list conversion to handle exact string match.
    assert f"Nodes unreachable from start place 'i': {expected_unreachable_nodes}" in str(excinfo.value) or \
           f"Nodes from which end place 'o' is unreachable: {expected_unreachable_nodes}" in str(excinfo.value)

def test_all_nodes_on_path_node_cannot_reach_end_yaml():
    """
    Tests a WF-net where some nodes can be reached from start, but cannot reach the end.
    Expects a SemanticValidationError.
    """
    yaml_definition = """
    net: unreachable_end_net
    version: "1.0"
    places:
      - id: i
      - id: p1
      - id: p_deadend # A place that cannot reach 'o'
      - id: o
    transitions:
      - id: t1
        input: [i]
        output: [p1, p_deadend] # Both p1 and p_deadend are reachable from start
      - id: t2
        input: [p1]
        output: [o]
      - id: t_dead # Leads to nowhere from p_deadend
        input: [p_deadend]
        output: [] # No output, or output to another isolated part
    """
    yaml_path = write_temp_yaml(yaml_definition)
    validator = SemanticValidator(yaml_path)
    
    with pytest.raises(SemanticValidationError) as excinfo:
        validator.validate_all_nodes_on_path_from_start_to_end()
    assert "Nodes from which end place 'o' is unreachable: ['p_deadend', 't_dead']" in str(excinfo.value)


def test_all_nodes_on_path_multiple_start_places_prereq_fail():
    """
    Tests that if multiple start places exist, the reachability check fails due to prerequisite.
    """
    yaml_definition = """
    net: multiple_starts_reachability_fail
    version: "1.0"
    places:
      - id: i1
      - id: i2
      - id: o
    transitions:
      - id: t1
        input: [i1]
        output: [o]
      - id: t2
        input: [i2]
        output: [o]
    """
    yaml_path = write_temp_yaml(yaml_definition)
    validator = SemanticValidator(yaml_path)

    with pytest.raises(SemanticValidationError) as excinfo:
        validator.validate_all_nodes_on_path_from_start_to_end()
    assert "Prerequisite failed for reachability check: Expected exactly one start place, but found 2: ['i1', 'i2']" in str(excinfo.value)

def test_all_nodes_on_path_multiple_end_places_prereq_fail():
    """
    Tests that if multiple end places exist, the reachability check fails due to prerequisite.
    """
    yaml_definition = """
    net: multiple_ends_reachability_fail
    version: "1.0"
    places:
      - id: i
      - id: o1
      - id: o2
    transitions:
      - id: t1
        input: [i]
        output: [o1]
      - id: t2
        input: [i]
        output: [o2]
    """
    yaml_path = write_temp_yaml(yaml_definition)
    validator = SemanticValidator(yaml_path)

    with pytest.raises(SemanticValidationError) as excinfo:
        validator.validate_all_nodes_on_path_from_start_to_end()
    assert "Prerequisite failed for reachability check: Expected exactly one end place, but found 2: ['o1', 'o2']" in str(excinfo.value)  