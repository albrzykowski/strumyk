# Strumyk DSL

[![Build](https://github.com/albrzykowski/strumyk/actions/workflows/tests.yaml/badge.svg)](https://github.com/albrzykowski/strumyk/actions/workflows/tests.yaml)
[![Last Commit](https://img.shields.io/github/last-commit/albrzykowski/strumyk)](https://github.com/albrzykowski/strumyk/commits/main)
![License](https://img.shields.io/github/license/albrzykowski/strumyk)
[![Lint: ruff](https://img.shields.io/badge/lint%20%3A-ruff-green)](https://github.com/albrzykowski/strumyk)

Strumyk is a lightweight YAML-based domain-specific language (DSL) for modeling business processes using the formalism of workflow nets (WF-nets). It provides a human-readable syntax to describe states (places) and transitions.

### What is a WF-net?

A **WF-net** also called [Workflow net](https://en.wikipedia.org/wiki/Petri_net) is a specialized type of Petri net designed to model business processes or workflows. It is a formal graphical tool that helps represent the states and transitions within a process, enabling analysis and verification of process correctness.

WF-nets consist mainly of two types of elements:

- **Places**: These represent conditions or states in the process. For example, a place can indicate a specific step is ready to start, or a resource is available. Places are typically depicted as circles.

- **Transitions**: These represent events or actions that can change the state of the process. For example, a transition may represent the execution of a task, a decision point, or the completion of an activity. Transitions are usually depicted as rectangles or bars.

In a WF-net, places and transitions are connected by directed arcs showing the flow from one state to another, defining how the process progresses.

The Strumyk DSL allows you to define WF-nets in a YAML format, specifying places and transitions clearly, including conditions on transitions that express business logic using Python expressions.


### Syntax Overview

```yaml
net: <net_name>            # Required: name of the WF-net
version: "<version>"       # Required: format version string

places:
  - id: <place_id>         # Unique identifier of the place
    label: <label>         # Optional human-readable label

transitions:
  - id: <transition_id>    # Unique identifier of the transition
    input: [<place_id>]    # List of input places
    output: [<place_id>]   # List of output places
    condition: "<expr>"    # Optional condition syntax
    label: <label>         # Optional label
```

[See JSON Schema](https://github.com/albrzykowski/strumyk/blob/main/data/schema.json)
 

### Example (Inspired by Stanisław Lem's novel [*The Investigation*](https://en.wikipedia.org/wiki/The_Investigation)) 

```yaml
net: The_Investigation
version: "1.0"

places:
  - id: morgue
    label: "Morgue Incident"
  - id: hypothesis
    label: "Competing Hypotheses"
  - id: resolution
    label: "Uncertain Conclusion"

transitions:
  - id: discover_disappearance
    input: []
    output: [morgue]
    label: "Body Disappears from Morgue"

  - id: explore_explanations
    input: [morgue]
    output: [hypothesis]
    condition: "user['open_mindedness'] >= 40"
    label: "Analyze Statistical & Rational Hypotheses"

  - id: accept_uncertainty
    input: [hypothesis]
    output: [resolution]
    condition: "user['need_for_closure'] <= 30"
    label: "Accept Lack of Closure"
```

## CLI Usage

### Validators Overview

- **SyntaxValidator** checks whether a YAML file conforms to a given JSON Schema. It verifies the structural correctness of the file (e.g., required fields, value types, object structure).

- **SemanticValidator** performs domain-specific validation of a WF-net (Workflow net) encoded in YAML. It checks formal properties: unique source/sink places and strong connectivity.

Validate YAML models from the command line:

### Syntax validation (validates structure against JSON Schema)

`python -m strumyk.cli validate-syntax data/example.yaml data/schema.json`

### Semantic validation (validates WF-net semantics)

`python -m strumyk.cli validate-semantic data/example.yaml`

### Simulator Overview

- **Simulator** loads a workflow net from a YAML file and simulates its execution by firing transitions based on context.

Simulate process from the command line:

### Process simulation (for given context)

`python -m strumyk.cli data/example.yaml '{"user": {"open_mindedness": 55, "need_for_closure": 25}}'`

## Python API Usage

How to use the validators in your Python code:

```
from strumyk.syntax_validator import SyntaxValidator
from strumyk.semantic_validator import SemanticValidator

yaml_file = "data/example.yaml"
schema_file = "data/schema.json"

# --- Syntax Validation ---
syntax_validator = SyntaxValidator(yaml_file, schema_file)
is_valid = syntax_validator.validate()

# --- Semantic Validation ---
semantic_validator = SemanticValidator(yaml_file)
is_valid = semantic_validator.validate()
```

How to use the simulator in your Python code:

```
from strumyk.simulator import Simulator

yaml_file = "data/example.yaml"
context = '{"user": {"open_mindedness": 55, "need_for_closure": 25}}'

# --- Process simulation ---
simulator = Simulator(yaml_file, context)
is_valid = simulator.simulate()
```

## Installation

You can install the module directly from GitHub using pip:

`pip install git+https://github.com/albrzykowski/strumyk.git`