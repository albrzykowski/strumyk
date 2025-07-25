import typer
import logging
import json
from pathlib import Path

from .syntax_validator import SyntaxValidator
from .semantic_validator import SemanticValidator, SemanticValidationError
from .simulator import Simulator

app = typer.Typer(
    help="Tool for validating and simulating Strumyk YAML files.",
    add_completion=False,
    pretty_exceptions_show_locals=False,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler()],
)


def _execute_task(task_func, success_msg: str, task_name: str):
    logging.info(f"--- Executing: {task_name} ---")
    try:
        task_func()
        logging.info(f"✅ {success_msg}")
    except (SemanticValidationError, json.JSONDecodeError, ValueError) as e:
        logging.error(f"❌ Validation failed: {e}")
        raise typer.Exit(code=1)
    except FileNotFoundError as e:
        logging.error(f"❌ Error: File not found: {e.filename}")
        raise typer.Exit(code=1)
    except Exception:
        logging.exception(f"❗ An unexpected error occurred during: {task_name}.")
        raise typer.Exit(code=1)


@app.command("validate-syntax", help="Validates the YAML file syntax against a JSON schema.")
def validate_syntax(
    yaml_file: Path = typer.Argument(..., exists=True, readable=True, help="Path to the YAML file."),
    schema_file: Path = typer.Argument(..., exists=True, readable=True, help="Path to the JSON schema file."),
):
    def task():
        validator = SyntaxValidator(yaml_file, schema_file)
        if not validator.validate():
            raise ValueError("YAML syntax is invalid according to the schema.")

    _execute_task(task, "Syntax validation completed successfully.", "Syntax Validation")


@app.command("validate-semantic", help="Performs semantic validation (WF-net).")
def validate_semantic(
    yaml_file: Path = typer.Argument(..., exists=True, readable=True, help="Path to the YAML file."),
):
    def task():
        validator = SemanticValidator(yaml_file)
        if not validator.validate():
            raise SemanticValidationError("Semantic validation failed.")
            
    _execute_task(task, "Semantic validation completed successfully.", "Semantic Validation")


@app.command("simulate", help="Runs WF-net simulation using provided context.")
def simulate(
    yaml_file: Path = typer.Argument(..., exists=True, readable=True, help="Path to the YAML file."),
    context: str = typer.Argument(..., help="JSON-formatted context to simulate the network."),
):
    def task():
        context_data = json.loads(context)
        simulator = Simulator(yaml_file, context_data)
        if not simulator.simulate():
            raise Exception("Simulation failed.")

    _execute_task(task, "Simulation completed successfully.", "Simulation")


def main():
    app()


if __name__ == "__main__":
    main()
