import yaml

class SemanticValidationError(Exception):
    pass

class SemanticValidator:
    def __init__(self, yaml_path):
        self.net = self.load_yaml(yaml_path)
        self.places = {p['id'] for p in self.net.get('places', [])}
        self.transitions = self.net.get('transitions', [])
        self.place_inputs = self._build_place_inputs()
        self.place_outputs = self._build_place_outputs()

    def load_yaml(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def _build_place_inputs(self):
        """Places that appear as output of transitions (have incoming arcs)."""
        inputs = set()
        for t in self.transitions:
            inputs.update(t.get('output', []))
        return inputs

    def _build_place_outputs(self):
        """Places that appear as input of transitions (have outgoing arcs)."""
        outputs = set()
        for t in self.transitions:
            outputs.update(t.get('input', []))
        return outputs

    def validate_unique_source(self):
        # Source: place with no incoming arcs
        source_places = self.places - self.place_inputs
        if len(source_places) == 0:
            raise SemanticValidationError("No source place found (place with no incoming arcs).")
        if len(source_places) > 1:
            raise SemanticValidationError(f"Multiple source places found: {source_places}")
        return source_places.pop()

    def validate_unique_sink(self):
        # Sink: place with no outgoing arcs
        sink_places = self.places - self.place_outputs
        if len(sink_places) == 0:
            raise SemanticValidationError("No sink place found (place with no outgoing arcs).")
        if len(sink_places) > 1:
            raise SemanticValidationError(f"Multiple sink places found: {sink_places}")
        return sink_places.pop()

    def validate_strongly_connected(self):
        # Validate unique source and sink places
        source = self.validate_unique_source()
        sink = self.validate_unique_sink()

        # Build graph: place->transition edges and transition->place edges
        graph = {}

        for t in self.transitions:
            for p_in in t.get('input', []):
                graph.setdefault(p_in, set()).add(t['id'])
            for p_out in t.get('output', []):
                graph.setdefault(t['id'], set()).add(p_out)

        # BFS from source to find reachable nodes
        def bfs(start, graph):
            visited = set()
            queue = [start]
            while queue:
                node = queue.pop(0)
                if node not in visited:
                    visited.add(node)
                    queue.extend(graph.get(node, []))
            return visited

        reachable_from_source = bfs(source, graph)

        # Build reversed graph for reverse BFS
        reversed_graph = {}
        for node, neighbors in graph.items():
            for nbr in neighbors:
                reversed_graph.setdefault(nbr, set()).add(node)

        reachable_to_sink = bfs(sink, reversed_graph)

        # All places and transitions
        expected_nodes = self.places.union({t['id'] for t in self.transitions})

        # Nodes reachable both from source and to sink
        strongly_connected_nodes = reachable_from_source.intersection(reachable_to_sink)

        missing = expected_nodes - strongly_connected_nodes
        if missing:
            raise SemanticValidationError(f"Not all elements are on a path from source to sink. Missing: {missing}")

    def validate(self):
        self.validate_unique_source()
        self.validate_unique_sink()
        self.validate_strongly_connected()
        # Additional axioms can be added here
