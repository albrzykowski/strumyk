import tempfile
import pytest
import json
from strumyk.syntax_validator import SyntaxValidator  # adjust import as needed

valid_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["net", "version", "places", "transitions"],
    "properties": {
        "net": {"type": "string"},
        "version": {"type": "string"},
        "places": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "label"],
                "properties": {
                    "id": {"type": "string"},
                    "label": {"type": "string"}
                }
            }
        },
        "transitions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "input", "output", "condition", "label"],
                "properties": {
                    "id": {"type": "string"},
                    "input": {"type": "array", "items": {"type": "string"}},
                    "output": {"type": "array", "items": {"type": "string"}},
                    "condition": {"type": "string"},
                    "label": {"type": "string"}
                }
            }
        }
    }
}

@pytest.fixture
def create_temp_file():
    files = []
    def _create(content, suffix):
        f = tempfile.NamedTemporaryFile(mode='w+', suffix=suffix, delete=False)
        f.write(content)
        f.flush()
        files.append(f.name)
        return f.name
    yield _create
    import os
    for file in files:
        try:
            os.remove(file)
        except FileNotFoundError:
            pass

def test_valid_yaml_and_schema(create_temp_file):
    valid_yaml_content = """
        net: ExampleNet
        version: "1.0"
        places:
          - id: p1
            label: Start
        transitions:
          - id: t1
            input: [p1]
            output: [p1]
            condition: "True"
            label: "Test transition"
        """
    yaml_path = create_temp_file(valid_yaml_content, ".yaml")
    schema_path = create_temp_file(json.dumps(valid_schema), ".json")

    validator = SyntaxValidator(yaml_path, schema_path)
    is_valid = validator.validate()

    assert is_valid

def test_invalid_yaml_schema(create_temp_file):
    invalid_yaml_content = """
        net: ExampleNet
        version: "1.0"
        places:
          - id: p1
        transitions: []
        """
    yaml_path = create_temp_file(invalid_yaml_content, ".yaml")
    schema_path = create_temp_file(json.dumps(valid_schema), ".json")
    validator = SyntaxValidator(yaml_path, schema_path)
    is_valid = validator.validate()

    assert not is_valid
    """
    messages = [e.message for e in errors]
    assert any("label" in msg for msg in messages)
    """