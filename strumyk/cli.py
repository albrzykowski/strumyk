import argparse
import sys
import json
from .syntax_validator import SyntaxValidator
from .semantic_validator import SemanticValidator, SemanticValidationError
from .simulator import Simulator

def run_syntax_validation(yaml_path: str, schema_path: str) -> bool:

    print("\n--- Running Syntax Validation ---")
    try:
        validator = SyntaxValidator(yaml_path, schema_path)
        is_valid = validator.validate()

        if is_valid:
            print("✅ Syntax validation successful.")
            return True
        else:
            print("❌ Syntax validation failed:")
            return False
    except FileNotFoundError as e:
        print(f"❌ Error: File not found: {e.filename}")
        return False
    except Exception as e:
        print(f"❗ An unexpected error occurred during syntax validation: {e}")
        return False

def run_semantic_validation(yaml_path: str) -> bool:

    print("\n--- Running Semantic Validation ---")
    try:
        validator = SemanticValidator(yaml_path)
        is_valid = validator.validate()
        if is_valid:
            print("✅ Semantic validation successful.")
            return True
        else:
            print("❌ Semantic validation failed:")
            return False
    except SemanticValidationError as se:
        print(f"❌ Semantic validation failed: {se}")
        return False
    except FileNotFoundError:
        print(f"❌ Error: YAML file not found at '{yaml_path}'")
        return False
    except Exception as e:
        print(f"❗ An unexpected error occurred during semantic validation: {e}")
        return False

def run_simulator(yaml_path: str, raw_context: str) -> bool:

    print("\n--- Running Simulator ---")
    try:
        context_data = json.loads(raw_context)
    except json.JSONDecodeError as e:
        return False
    try:
        simulator = Simulator(yaml_path, context_data)
        is_success = simulator.simulate()
        if is_success:
            print("✅ Simulation successful.")
            return True
        else:
            print("❌ Simulation failed")
            return False
    except Exception as e:
        print(f"❗ An error occurred during simulation: {e}")
        return False        

def main():

    parser = argparse.ArgumentParser(
        description="A command-line tool to validate Strumyk YAML files.",
        epilog="Example: cli.py syntax my_net.yaml my_schema.json"
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="The validation command to run."
    )

    # Sub-parser for the "syntax" command
    parser_syntax = subparsers.add_parser(
        "validate-syntax",
        help="Perform syntax validation using a JSON schema."
    )
    parser_syntax.add_argument(
        "yaml_file",
        help="Path to the YAML file to validate."
    )
    parser_syntax.add_argument(
        "schema_file",
        help="Path to the JSON schema file for validation."
    )

    # Sub-parser for the "semantic" command
    parser_semantic = subparsers.add_parser(
        "validate-semantic",
        help="Perform semantic (WF-net) validation."
    )
    parser_semantic.add_argument(
        "yaml_file",
        help="Path to the YAML file to validate."
    )
    
    # Sub-parser for the "sumulator" command
    parser_semantic = subparsers.add_parser(
        "simulate",
        help="Perform (WF-net) simulation for given context."
    )
    parser_semantic.add_argument(
        "yaml_file",
        help="Path to the YAML file to validate."
    )
    parser_semantic.add_argument(
        "context",
        help="JSON with sample context that will try to travel the graph."
    )
    

    args = parser.parse_args()

    success = False
    
    if args.command == "validate-syntax":
        success = run_syntax_validation(args.yaml_file, args.schema_file)
    elif args.command == "validate-semantic":
        success = run_semantic_validation(args.yaml_file)
    elif args.command == "simulate":
        success = run_simulator(args.yaml_file, args.context)

    if success:
        print("\n🎉 Task finished successfully.")
        sys.exit(0)
    else:
        print("\nTask finished with errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()
