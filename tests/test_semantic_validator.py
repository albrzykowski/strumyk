import tempfile
import pytest
import os
from strumyk.semantic_validator import SemanticValidator, SemanticValidationError
    
@pytest.fixture
def create_yaml_file():
    created_files = []

    def _create(content: str) -> str:
        with tempfile.NamedTemporaryFile(mode='w', suffix=".yaml", delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(content)
            tmp_file.flush() 
        
        file_path = tmp_file.name
        created_files.append(file_path)
        return file_path

    yield _create

    for f_path in created_files:
        try:
            os.remove(f_path)
        except OSError as e:
            print(f"Error removing temporary file {f_path}: {e}")    
    

def test_single_start_place_axiom_valid(create_yaml_file):
    yaml_content = """
    net: Sample_Process
    version: "1.0"
    places:
      - id: p_start
      - id: p_sample
      - id: p_end
    transitions:
      - id: t1
        input: [p_start]
        output: [p_sample]
      - id: t2
        input: [p_sample]
        output: [p_end]
    """
    yaml_path = create_yaml_file(yaml_content)
    validator = SemanticValidator(yaml_path)
    
    is_valid, sources = validator.check_single_start_place_axiom()
    
    assert is_valid is True
    assert sources == {'p_start'}
    
def test_single_end_place_axiom_valid(create_yaml_file):
    yaml_content = """
    net: Sample_Process
    version: "1.0"
    places:
      - id: p_start
      - id: p_sample
      - id: p_end
    transitions:
      - id: t1
        input: [p_start]
        output: [p_sample]
      - id: t2
        input: [p_sample]
        output: [p_end]
    """
    yaml_path = create_yaml_file(yaml_content)
    validator = SemanticValidator(yaml_path)
    
    is_valid, sinks = validator.check_single_end_place_axiom()
    
    assert is_valid is True
    assert sinks == {'p_end'} 

def test_all_nodes_on_path_axiom_valid(create_yaml_file):
    yaml_content = """
    net: Sample_Process
    version: "1.0"
    places:
      - id: p_start
      - id: p_sample
      - id: p_end
    transitions:
      - id: t1
        input: [p_start]
        output: [p_sample]
      - id: t2
        input: [p_sample]
        output: [p_end]
    """
    yaml_path = create_yaml_file(yaml_content)
    validator = SemanticValidator(yaml_path)
    
    is_valid, unreachable = validator.check_all_nodes_on_path_axiom()
    
    assert is_valid is True
    assert unreachable == set()     