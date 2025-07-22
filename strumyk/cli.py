import argparse
import sys
from .syntax_validator import SyntaxValidator
from .semantic_validator import SemanticValidator, SemanticValidationError

def run_syntax_validation(yaml_path: str, schema_path: str) -> bool:

    print("\n--- Running Syntax Validation ---")
    try:
        validator = SyntaxValidator(yaml_path, schema_path)
        is_valid = validator.validate()

        if not is_valid:
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
        if not is_valid:
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

    args = parser.parse_args()

    success = False
    if args.command == "syntax":
        success = run_syntax_validation(args.yaml_file, args.schema_file)
    elif args.command == "semantic":
        success = run_semantic_validation(args.yaml_file)

    if success:
        print("\n🎉 Validation finished successfully.")
        sys.exit(0)
    else:
        print("\nValidation finished with errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()
