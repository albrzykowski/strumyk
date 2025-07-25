import pytest
from pathlib import Path

from strumyk.simulator import Simulator 

@pytest.fixture
def happy_path_simulator(tmp_path: Path) -> Simulator:
    yaml_content = """
    places:
      - id: p_start
      - id: p_middle
      - id: p_end
    transitions:
      - id: t1
        input: [p_start]
        output: [p_middle]
      - id: t2
        input: [p_middle]
        output: [p_end]
        condition: "user_is_approved == True"
    """
    net_file = tmp_path / "net.yaml"
    net_file.write_text(yaml_content, encoding="utf-8")
    
    context = {"user_is_approved": True}
    
    return Simulator(yaml_path=net_file, context=context)


def test_simulation_happy_path(happy_path_simulator: Simulator):
    """
    GIVEN a valid Petri net and a context that satisfies all conditions.
    WHEN the simulation is run.
    THEN it should return True, the end place should have a token,
    and the trace should be correct.
    """
    # GIVEN
    simulator = happy_path_simulator
    start_place = 'p_start'
    end_place = 'p_end'
    
    # WHEN
    result = simulator.run(start_place=start_place, end_place=end_place)
    
    # THEN
    assert result is True, "Simulation should succeed for a valid net."
    
    assert simulator.places[end_place] == 1, "End place should have one token."
    
    assert simulator.places[start_place] == 0, "Start place should be empty."
    assert simulator.places['p_middle'] == 0, "Intermediate places should be empty."
    
    expected_trace = ['t1', 't2']
    assert simulator.trace == expected_trace, f"Execution trace should be {expected_trace}."