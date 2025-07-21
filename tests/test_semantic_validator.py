import tempfile
import pytest
from strumyk.semantic_validator import SemanticValidator, SemanticValidationError

# --- Sample YAML data for tests ---

valid_wfnet_yaml = """
net: ExampleNet
version: "1.0"
places:
  - id: p1
    label: Start
  - id: p2
    label: Middle
  - id: p3
    label: End
transitions:
  - id: t1
    input: [p1]
    output: [p2]
    label: "First"
  - id: t2
    input: [p2]
    output: [p3]
    label: "Second"
"""

multiple_sources_yaml = """
net: MultipleSourcesNet
version: "1.0"
places:
  - id: p1
    label: Start1
  - id: p2
    label: Start2
  - id: p3
    label: End
transitions:
  - id: t1
    input: [p3]
    output: [p1]
    label: "Loop"
"""

missing_sink_yaml = """
net: MissingSinkNet
version: "1.0"
places:
  - id: p1
    label: Start
  - id: p2
    label: Middle
transitions:
  - id: t1
    input: [p1]
    output: [p2]
    label: "Transition"
  - id: t2
    input: [p2]
    output: [p1]
    label: "Back"
"""

not_strongly_connected_yaml = """
net: NotConnectedNet
version: "1.0"
places:
  - id: p1 # Source
    label: Start
  - id: p2 # Sink
    label: End
  - id: p3 # Isolated place
    label: IsolatedPlace
transitions:
  - id: t1
    input: [p1]
    output: [p2]
    label: "Connects source to sink"
  - id: t2 # Isolated transition
    input: [p3]
    output: [p3]
    label: "Isolated Transition"
"""

# --- Helper function ---

def write_temp_yaml(content):
    """Creates a temporary YAML file and returns its path."""
    # We use delete=False so the file is not removed after closing the handle.
    # The file will be automatically deleted by pytest.
    tmp = tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding='utf-8')
    tmp.write(content)
    tmp.flush()
    tmp.close()
    return tmp.name

# --- Tests ---

def test_valid_wfnet():
    """Tests a valid WF-net which should pass validation without errors."""
    path = write_temp_yaml(valid_wfnet_yaml)
    validator = SemanticValidator(path)
    validator.validate()  # Should not raise exception

def test_multiple_sources():
    """Tests a net with multiple sources."""
    path = write_temp_yaml(multiple_sources_yaml)
    validator = SemanticValidator(path)
    with pytest.raises(SemanticValidationError) as e:
        validator.validate_unique_source()
    assert "Multiple source places" in str(e.value)

def test_missing_sink():
    """Tests a net without a sink."""
    path = write_temp_yaml(missing_sink_yaml)
    validator = SemanticValidator(path)
    with pytest.raises(SemanticValidationError) as e:
        validator.validate_unique_sink()
    assert "No sink place" in str(e.value)

def test_not_strongly_connected():
    """
    Tests a net that is not strongly connected.
    The net has a valid source and sink but contains elements (place p3 and transition t2)
    that are not on any path from source to sink.
    """
    path = write_temp_yaml(not_strongly_connected_yaml)
    validator = SemanticValidator(path)
    with pytest.raises(SemanticValidationError) as e:
        validator.validate_strongly_connected()
    
    # Verify the error message contains info about missing elements
    error_message = str(e.value)
    assert "Not all elements are on a path from source to sink" in error_message
    # Verify the missing elements are mentioned in the message
    assert 'p3' in error_message
    assert 't2' in error_message
