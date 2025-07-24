import yaml
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class Simulator:
    def __init__(self, yaml_path: str, context: dict):
        yaml_text = self._load_file(yaml_path)
        self.net = yaml.safe_load(yaml_text)
        self.places = {p['id']: 0 for p in self.net['places']}
        self.transitions = self.net['transitions']
        self.context = context
        self.trace = []

    def set_token(self, place_id: str, count: int = 1):
        self.places[place_id] = count

    def evaluate_condition(self, condition: str) -> bool:
        try:
            return bool(eval(condition, {}, self.context))
        except Exception as e:
            logger.error(f"Condition error: {e} -> '{condition}'")
            return False

    def enabled_transitions(self):
        enabled = []
        for t in self.transitions:
            if all(self.places.get(p, 0) > 0 for p in t['input']):
                cond = t.get('condition')
                if cond is None or self.evaluate_condition(cond):
                    enabled.append(t)
        return enabled

    def fire_transition(self, t: dict):
        logger.debug(f"→ Transition: {t['id']}")
        self.trace.append(t['id'])
        for p in t['input']:
            self.places[p] -= 1
        for p in t['output']:
            self.places[p] += 1
        logger.debug(f"   Places: {self.places}")

    def simulate(self, start_place='p_start', end_place='p_end'):
        self.set_token(start_place)
        logger.debug(f"Initial: {self.places}")
        while self.places[end_place] == 0:
            enabled = self.enabled_transitions()
            if not enabled:
                logger.error("✖ Deadlock – no enabled transitions.")
                return False
            self.fire_transition(enabled[0])
        return True

    def _load_file(self, filepath: str) -> str:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
