from srcgen import a, b, c, d, e
from lib.test import run_scenarios

SCENARIOS_A = [
    {
        "name": "A",
        "input_events": [],
        "output_events": [
            (1000000000, "x", None),
            (2000000000, "x", None),
            (3000000000, "x", None),
        ],
    },
]
SCENARIOS_B = [
    {
        "name": "B",
        "input_events": [],
        "output_events": [
            (2000000000, "inner", None),
            (3000000000, "outer", None),
            (5000000000, "inner", None),
            (6000000000, "outer", None),
            (8000000000, "inner", None),
            (9000000000, "outer", None),
        ],
    },
]
SCENARIOS_C = [
    {
        "name": "C",
        "input_events": [],
        "output_events": [],
    },
]
SCENARIOS_D = [
    {
        "name": "D",
        "input_events": [],
        "output_events": [],
    },
]
SCENARIOS_E = [
    {
        "name": "E",
        "input_events": [],
        "output_events": [
            (1000000000, "x", None),
            (1000000000, "y", None),
            (2000000000, "x", None),
            (2000000000, "y", None),
            (3000000000, "x", None),
            (3000000000, "y", None),
        ],
    },
]

if __name__ == "__main__":
    run_scenarios(SCENARIOS_A, a.A, [], [], verbose=True)
    run_scenarios(SCENARIOS_B, b.B, [], [], verbose=True)
    run_scenarios(SCENARIOS_C, c.C, [], [], verbose=True)
    run_scenarios(SCENARIOS_D, d.D, [], [], verbose=True)
    run_scenarios(SCENARIOS_E, e.E, [], [], verbose=True)
