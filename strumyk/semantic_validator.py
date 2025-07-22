import yaml
import networkx as nx

class SemanticValidationError(Exception):
    pass

class SemanticValidator:
    def __init__(self, yaml_path):
        self.net_definition = self._load_yaml(yaml_path)
        self._build_graph()
        
    def validate(self):
        self.check_single_start_place_axiom()
        self.check_single_end_place_axiom()
        self.check_all_nodes_on_path_axiom()
            
    def check_single_start_place_axiom(self):
        all_places = {p['id'] for p in self.net_definition['places']}
        places_with_input_arcs = {v for u, v in self.graph.edges()}
        source_places = all_places - places_with_input_arcs
        is_valid = len(source_places) == 1

        return is_valid, source_places

        
    def check_single_end_place_axiom(self):
        all_places = {p['id'] for p in self.net_definition['places']}
        places_with_output_arcs = {u for u, v in self.graph.edges()}
        end_places = all_places - places_with_output_arcs
        is_valid = len(end_places) == 1

        return is_valid, end_places

    def check_all_nodes_on_path_axiom(self):
        _, source_places = self.check_single_start_place_axiom()
        _, end_places = self.check_single_end_place_axiom()
        start = next(iter(source_places))
        end = next(iter(end_places))
        reachable_from_start = nx.descendants(self.graph, start) | {start}
        reversed_graph = self.graph.reverse(copy=True)
        reachable_to_end = nx.descendants(reversed_graph, end) | {end}
        on_path = reachable_from_start & reachable_to_end
        all_nodes = set(self.graph.nodes)
        unreachable = all_nodes - on_path
        is_valid = len(unreachable) == 0
        
        return is_valid, unreachable
    
    def _load_yaml(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f)    
    
    def _build_graph(self):
        self.graph = nx.DiGraph()
        for place in self.net_definition['places']:
            self.graph.add_node(place['id'], type='place')
        for transition in self.net_definition['transitions']:
            self.graph.add_node(transition['id'], type='transition')
            for p_in in transition.get('input', []):
                self.graph.add_edge(p_in, transition['id'])
            for p_out in transition.get('output', []):
                self.graph.add_edge(transition['id'], p_out)   
