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
            
    def validate_unique_place_ids(self):
        place_ids = set()
        places = self.net_definition.get('places', [])
        if not places:
            return False
        for place in places:
            place_id = place.get('id')
            if place_id is None:
                raise  SemanticValidationError(f"Missing 'id' property for place: {place}")
            if place_id in place_ids:
                return False
            place_ids.add(place_id)
        return True
        
    def validate_unique_transition_ids(self):
        seen_transition_ids = set()
        transitions = self.net_definition.get('transitions', [])

        if not transitions:
            return False

        for transition in transitions:
            transition_id = transition.get('id')
            if transition_id is None:
                raise SemanticValidationError(f"Missing 'id' property for transition: {transition}")
            if transition_id in seen_transition_ids:
                raise SemanticValidationError(f"Duplicate transition ID found: '{transition_id}'")
            seen_transition_ids.add(transition_id)
            
        return True

    def validate_disjoint_place_and_transition_ids(self):
        """
        Validates that place IDs and transition IDs are disjoint (no ID is used for both a place and a transition).
        Raises SemanticValidationError if a common ID is found.
        """
        place_ids = set()
        for place in self.net_definition.get('places', []):
            # We assume unique_place_ids validation has passed, so 'id' exists and is unique.
            # If not, this method should be called AFTER unique_place_ids/transitions_ids.
            if 'id' in place and place['id'] is not None:
                place_ids.add(place['id'])

        transition_ids = set()
        for transition in self.net_definition.get('transitions', []):
            # Similarly, assume unique_transition_ids validation has passed.
            if 'id' in transition and transition['id'] is not None:
                transition_ids.add(transition['id'])

        # Find the intersection of the two sets of IDs
        common_ids = place_ids.intersection(transition_ids)

        if common_ids:
            # If there are any common IDs, raise a validation error
            raise SemanticValidationError(
                f"Conflicting IDs found: IDs {list(common_ids)} are used for both places and transitions."
            )
        
        return True # IDs are disjoint
        
    def validate_single_start_place(self):
        """
        Validates that there is exactly one start place (a place with no incoming arcs).
        A place has no incoming arcs if its ID does not appear in the 'output' list of any transition.
        Raises SemanticValidationError if there isn't exactly one such place.
        """
        all_places_ids = {place['id'] for place in self.net_definition.get('places', [])
                          if isinstance(place, dict) and 'id' in place and place['id'] is not None}
        
        # Collect all place IDs that are outputs of *any* transition
        places_that_are_outputs = set()
        for transition in self.net_definition.get('transitions', []):
            if isinstance(transition, dict) and 'output' in transition and isinstance(transition['output'], list):
                for output_place_id in transition['output']:
                    # Ensure output_place_id is not None if we're using it in a set
                    if output_place_id is not None:
                        places_that_are_outputs.add(output_place_id)
        
        # A start place is any place that exists in all_places_ids but is NOT an output of any transition
        start_places = all_places_ids - places_that_are_outputs

        if len(start_places) != 1:
            if not all_places_ids: # Case: No places defined at all
                raise SemanticValidationError("WF-net must contain at least one place to define a start place.")
            elif not start_places and all_places_ids: # Case: All places have incoming arcs
                raise SemanticValidationError("No start place found: All places have incoming arcs.")
            else: # Case: More than one start place
                raise SemanticValidationError(
                    f"Expected exactly one start place, but found {len(start_places)}: {sorted(list(start_places))}"
                )
        
        return True # Exactly one start place found
        
    def validate_single_end_place(self):
        """
        Validates that there is exactly one end place (a place with no outgoing arcs).
        A place has no outgoing arcs if its ID does not appear in the 'input' list of any transition.
        Raises SemanticValidationError if there isn't exactly one such place.
        """
        all_places_ids = {place['id'] for place in self.net_definition.get('places', [])
                          if isinstance(place, dict) and 'id' in place and place['id'] is not None}
        
        # Collect all place IDs that are inputs of *any* transition
        places_that_are_inputs = set()
        for transition in self.net_definition.get('transitions', []):
            if isinstance(transition, dict) and 'input' in transition and isinstance(transition['input'], list):
                for input_place_id in transition['input']:
                    # Ensure input_place_id is not None if we're using it in a set
                    if input_place_id is not None:
                        places_that_are_inputs.add(input_place_id)
        
        # An end place is any place that exists in all_places_ids but is NOT an input of any transition
        end_places = all_places_ids - places_that_are_inputs

        if len(end_places) != 1:
            if not all_places_ids: # Case: No places defined at all
                raise SemanticValidationError("WF-net must contain at least one place to define an end place.")
            elif not end_places and all_places_ids: # Case: All places have outgoing arcs
                raise SemanticValidationError("No end place found: All places have outgoing arcs.")
            else: # Case: More than one end place
                raise SemanticValidationError(
                    f"Expected exactly one end place, but found {len(end_places)}: {sorted(list(end_places))}"
                )
        
        return True # Exactly one end place found

    def validate_all_nodes_on_path_from_start_to_end(self):
        """
        Validates that all places and transitions are on a path from the unique start place
        to the unique end place. This implies two checks:
        1. All nodes are reachable from the start place.
        2. The end place is reachable from all nodes (or, all nodes can reach the end place).
        Raises SemanticValidationError if any node is isolated or not on such a path.
        """
        # Przed uruchomieniem tej walidacji, powinniśmy upewnić się,
        # że istnieją dokładnie jedno miejsce początkowe i jedno końcowe.
        # W praktyce, metody te byłyby wywoływane sekwencyjnie.
        try:
            self.validate_single_start_place()
            self.validate_single_end_place()
        except SemanticValidationError as e:
            raise SemanticValidationError(f"Prerequisite failed for reachability check: {e}")

        # Znajdź unikalne miejsce początkowe i końcowe
        all_places_ids = {p['id'] for p in self.net_definition.get('places', []) if 'id' in p and p['id'] is not None}
        places_that_are_outputs = {out_id for t in self.net_definition.get('transitions', [])
                                    if isinstance(t, dict) and 'output' in t and isinstance(t['output'], list)
                                    for out_id in t['output'] if out_id is not None}
        start_place_id = (all_places_ids - places_that_are_outputs).pop() # Safe due to validate_single_start_place

        places_that_are_inputs = {in_id for t in self.net_definition.get('transitions', [])
                                   if isinstance(t, dict) and 'input' in t and isinstance(t['input'], list)
                                   for in_id in t['input'] if in_id is not None}
        end_place_id = (all_places_ids - places_that_are_inputs).pop() # Safe due to validate_single_end_place


        # Stwórz reprezentację grafu dla łatwiejszego przeszukiwania
        # Użyjemy wspólnej przestrzeni nazw dla miejsc i przejść w grafie
        # p_id -> t_id (dla input)
        # t_id -> p_id (dla output)
        graph_forward = {} # Używane do sprawdzania osiągalności OD źródła
        graph_backward = {} # Używane do sprawdzania osiągalności DO ujścia (czyli od ujścia "do tyłu")

        all_node_ids = all_places_ids.union({t['id'] for t in self.net_definition.get('transitions', [])
                                              if isinstance(t, dict) and 'id' in t and t['id'] is not None})
        
        # Inicjalizuj grafy
        for node_id in all_node_ids:
            graph_forward[node_id] = set()
            graph_backward[node_id] = set() # Odwrotny graf

        for transition in self.net_definition.get('transitions', []):
            if not isinstance(transition, dict) or 'id' not in transition:
                continue # Pomiń wadliwe przejścia, zakładając, że walidacja unikalności i struktury już je wyłapała
            t_id = transition['id']

            inputs = transition.get('input', [])
            outputs = transition.get('output', [])

            if not isinstance(inputs, list) or not isinstance(outputs, list):
                 continue # Pomiń, zakładając, że walidacja struktury już je wyłapała

            for p_in_id in inputs:
                if p_in_id is not None:
                    graph_forward[p_in_id].add(t_id)
                    graph_backward[t_id].add(p_in_id) # W odwrotnym grafie łuk od t do p_in
            for p_out_id in outputs:
                if p_out_id is not None:
                    graph_forward[t_id].add(p_out_id)
                    graph_backward[p_out_id].add(t_id) # W odwrotnym grafie łuk od p_out do t

        # Funkcja pomocnicza do przeszukiwania grafu (BFS)
        def bfs_reachable_nodes(start_node, graph, all_nodes):
            visited = {start_node}
            queue = deque([start_node])
            while queue:
                current_node = queue.popleft()
                for neighbor in graph.get(current_node, set()):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            return visited

        # 1. Sprawdź osiągalność wszystkich węzłów ze źródła (i)
        reachable_from_start = bfs_reachable_nodes(start_place_id, graph_forward, all_node_ids)
        
        unreachable_from_start = all_node_ids - reachable_from_start
        if unreachable_from_start:
            raise SemanticValidationError(
                f"Nodes unreachable from start place '{start_place_id}': {sorted(list(unreachable_from_start))}"
            )

        # 2. Sprawdź osiągalność ujścia (o) ze wszystkich węzłów (lub równoważnie, czy wszystkie węzły mogą 'dojść' do ujścia)
        # Robimy to poprzez przeszukanie ODWRÓCONEGO grafu, zaczynając od ujścia.
        reachable_from_end_in_reverse_graph = bfs_reachable_nodes(end_place_id, graph_backward, all_node_ids)

        # Jeśli jakiś węzeł nie jest osiągalny z ujścia w odwrotnym grafie,
        # oznacza to, że ujście nie jest osiągalne z tego węzła w oryginalnym grafie.
        unreachable_to_end = all_node_ids - reachable_from_end_in_reverse_graph
        if unreachable_to_end:
            raise SemanticValidationError(
                f"Nodes from which end place '{end_place_id}' is unreachable: {sorted(list(unreachable_to_end))}"
            )

        return True
