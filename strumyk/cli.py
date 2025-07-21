import argparse
import sys
from typing import List

# --- Mock Objects for Demonstration ---
# In a real scenario, these would be imported from your library.
# This allows the script to run standalone for testing purposes.

class MockValidationError:
    def __init__(self, message, path):
        self.message = message
        self.path = path

class SyntaxValidator:
    def __init__(self, yaml_path: str, schema_path: str):
        print(f"-> Initializing SyntaxValidator for '{yaml_path}' with schema '{schema_path}'")
        if "bad_syntax" in yaml_path:
            self._errors = [MockValidationError("Invalid type for 'places'", ["places"])]
        else:
            self._errors = []

    def run(self) -> List[MockValidationError]:
        return self._errors

class SemanticValidationError(Exception):
    pass

class SemanticValidator:
    def __init__(self, yaml_path: str):
        print(f"-> Initializing SemanticValidator for '{yaml_path}'")
        self._path = yaml_path

    def validate(self):
        if "bad_semantic" in self._path:
            raise SemanticValidationError("Multiple source places found.")
        # If validation is successful, do nothing.

# --- Core Functions ---

def run_syntax_validation(yaml_path: str, schema_path: str) -> bool:
    """
    Performs syntax validation on a YAML file using a JSON schema.

    Args:
        yaml_path: The path to the YAML file.
        schema_path: The path to the JSON schema file.

    Returns:
        True if validation is successful, False otherwise.
    """
    print("\n--- Running Syntax Validation ---")
    try:
        validator = SyntaxValidator(yaml_path, schema_path)
        errors = validator.run()

        if not errors:
            print("✅ Syntax validation successful.")
            return True
        else:
            print("❌ Syntax validation failed:")
            for e in errors:
                path_str = ".".join(str(p) for p in e.path) if e.path else "root"
                print(f" - [{path_str}] {e.message}")
            return False
    except FileNotFoundError as e:
        print(f"❌ Error: File not found: {e.filename}")
        return False
    except Exception as e:
        print(f"❗ An unexpected error occurred during syntax validation: {e}")
        return False

def run_semantic_validation(yaml_path: str) -> bool:
    """
    Performs semantic validation for a WF-net defined in a YAML file.

    Args:
        yaml_path: The path to the YAML file.

    Returns:
        True if validation is successful, False otherwise.
    """
    print("\n--- Running Semantic Validation ---")
    try:
        validator = SemanticValidator(yaml_path)
        validator.validate()
        print("✅ Semantic validation successful.")
        return True
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
    """
    Main function to parse command-line arguments and run validators.
    """
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
        "syntax",
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
        "semantic",
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
