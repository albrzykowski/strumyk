import yaml
import json
from jsonschema import Draft202012Validator

class SyntaxValidator:
    def __init__(self, yaml_path: str, schema_path: str):
        self.yaml_path = yaml_path
        self.schema_path = schema_path
        self.data = None
        self.schema = None
        self.validator = None

    def load_yaml(self):
        with open(self.yaml_path, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f)

    def load_json_schema(self):
        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

    def prepare_validator(self):
        if self.schema is None:
            raise ValueError("JSON schema not loaded")
        self.validator = Draft202012Validator(self.schema)

    def validate(self):
        if self.data is None:
            raise ValueError("YAML data not loaded")
        if self.validator is None:
            self.prepare_validator()
        errors = sorted(self.validator.iter_errors(self.data), key=lambda e: e.path)
        return errors

    def run(self):
        self.load_yaml()
        self.load_json_schema()
        self.prepare_validator()
        return self.validate()
