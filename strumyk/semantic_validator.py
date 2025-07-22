import yaml
from collections import deque

class SemanticValidationError(Exception):
    pass

class SemanticValidator:
    def __init__(self, yaml_path):
        self.net_definition = self.load_yaml(yaml_path)
        
    def validate(self):
        self.validate_unique_place_ids
        self.validate_unique_transition_ids()
        self.validate_disjoint_place_and_transition_ids()
        self.validate_single_start_place()
        self.validate_single_end_place()
        self.validate_all_nodes_on_path_from_start_to_end()
    
    def load_yaml(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f)
            
    def check_single_start_place_axiom(self):
        all_places = {p['id'] for p in self.net_definition['places']}
        places_with_input_arcs = set()
        for t in self.net_definition['transitions']:
            places_with_input_arcs.update(t.get('output', []))
        source_places = all_places - places_with_input_arcs
        is_valid = len(source_places) == 1
        
        return is_valid, source_places
        
    def check_single_end_place_axiom(self):
        all_places = {p['id'] for p in self.net_definition['places']}
        places_with_output_arcs = set()
        for t in self.net_definition['transitions']:
            places_with_output_arcs.update(t.get('input', []))
        end_places = all_places - places_with_output_arcs
        is_valid = len(end_places) == 1

        return is_valid, end_places    
