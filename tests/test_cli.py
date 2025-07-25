import pytest
from typer.testing import CliRunner
from pathlib import Path
import json

from strumyk.cli import app

runner = CliRunner()

@pytest.fixture
def mock_files(tmp_path: Path) -> tuple[Path, Path]:
    yaml_file = tmp_path / "test.yaml"
    schema_file = tmp_path / "schema.json"
    yaml_file.touch()
    schema_file.touch()
    return yaml_file, schema_file

def test_validate_syntax_happy_path(mocker, mock_files):
    yaml_file, schema_file = mock_files
    
    mock_validator = mocker.patch('strumyk.cli.SyntaxValidator')
    mock_validator.return_value.validate.return_value = True

    result = runner.invoke(app, ["validate-syntax", str(yaml_file), str(schema_file)])

    assert result.exit_code == 0
    mock_validator.assert_called_once_with(yaml_file, schema_file)

def test_validate_semantic_happy_path(mocker, mock_files):
    yaml_file, _ = mock_files
    
    mock_validator = mocker.patch('strumyk.cli.SemanticValidator')
    mock_validator.return_value.validate.return_value = True

    result = runner.invoke(app, ["validate-semantic", str(yaml_file)])

    assert result.exit_code == 0
    mock_validator.assert_called_once_with(yaml_file)

def test_simulate_happy_path(mocker, mock_files):
    yaml_file, _ = mock_files
    context_dict = {"key": "value"}
    context_json = json.dumps(context_dict)

    mock_simulator = mocker.patch('strumyk.cli.Simulator')
    mock_simulator.return_value.simulate.return_value = True

    result = runner.invoke(app, ["simulate", str(yaml_file), context_json])

    assert result.exit_code == 0
    mock_simulator.assert_called_once_with(yaml_file, context_dict)