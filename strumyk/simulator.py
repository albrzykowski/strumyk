import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class Simulator:
    def __init__(self, yaml_path: Path, context: Dict[str, Any]):
        net_definition = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        self.places: Dict[str, int] = {p["id"]: 0 for p in net_definition.get("places", [])}
        self.transitions: List[Dict[str, Any]] = net_definition.get("transitions", [])
        self.context: Dict[str, Any] = context
        self.trace: List[str] = []

    def _evaluate_condition(self, condition: str) -> bool:
        try:
            return bool(eval(condition, {}, self.context))
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False

    def get_enabled_transitions(self) -> List[Dict[str, Any]]:
        return [
            t for t in self.transitions
            if all(self.places.get(p, 0) > 0 for p in t.get("input", []))
            and (t.get("condition") is None or self._evaluate_condition(t.get("condition")))
        ]

    def fire_transition(self, transition: Dict[str, Any]) -> None:
        transition_id = transition.get("id", "Unnamed Transition")
        logger.debug(f"→ Firing transition: {transition_id}")
        self.trace.append(transition_id)
        
        for p in transition.get("input", []):
            self.places[p] -= 1
        for p in transition.get("output", []):
            self.places[p] += 1
            
        logger.debug(f"  New marking: {self.places}")

    def run(self, start_place: str = 'p_start', end_place: str = 'p_end', max_steps: int = 1000) -> bool:
        if start_place not in self.places or end_place not in self.places:
            logger.error(f"Error: Start ('{start_place}') or end ('{end_place}') place not found in the net.")
            return False

        self.places[start_place] = 1
        logger.debug(f"Initial marking: {self.places}")

        for step in range(max_steps):
            if self.places.get(end_place, 0) > 0:
                logger.info(f"✅ Simulation successful. Reached end place '{end_place}' in {step} steps.")
                return True

            enabled_transitions = self.get_enabled_transitions()
            
            if not enabled_transitions:
                logger.error("✖ Deadlock: No enabled transitions found.")
                return False
                
            self.fire_transition(enabled_transitions[0])

        logger.error(f"✖ Simulation failed: Exceeded maximum of {max_steps} steps.")
        return False