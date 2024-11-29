Starting point for the Statecharts assignment of MoSIS in the academic year 2024-2025.

Clone this repository, and import the `StartingPoint` directory as an Itemis CREATE project (without copying the files). This way, you can still do a `git pull` in case of a bug fix in the Python code.


## Dependencies

To run the Python scripts, you need the following:

  - **Python 3.?** (tested with 3.12)
  - **TkInter** library (included in most Python distributions)


## Contents

### Exercises

Files related to the exercises:
  - **`StartingPoint/exercises/`**: (DO NOT EDIT) directory that contains the exercises. Each exercise is a Statechart model that you can run/debug in ITEMIS.
  - **`StartingPoint/runner_exercises_tests.py`**: (FEEL FREE TO EDIT) runs automated tests on (generated code from) the exercise models. Feel free to edit and run this file to understand the exercises better.

### Assignment

Files related to the assignment:
  - **`StartingPoint/Statechart.ysc`**: (MUST EDIT THIS) this is the Statechart model.
  - **`StartingPoint/runner_tests.py`**: (ADD ONE TEST) runs automated tests on your Statechart. It already includes 3 test scenarios, which your solution **must pass**! You are not allowed to modify the existing tests. You must however **add one test** to it.
  - **`StartingPoint/runner_gui.py`**: (DO NOT EDIT) this script runs a TkInter GUI that allows you to interact with your Statechart.

When running the GUI, you can pass an additional `time_scale` parameter, as such:
```
cd StartingPoint
python runner_gui.py 0.5 # run simulation at half-speed
python runner_gui.py 2   # run simulation at double-speed
```

### Background

Other files:
  - **`StartingPoint/PythonGenerator.sgen`**: (DO NOT EDIT) specifies how ITEMIS should generate Python code from the models.
  - **`StartingPoint/srcgen/`**: (DO NOT EDIT BY HAND) This directory contains Python code generated from the models. Each time you change a model, code will be re-generated, overwriting the files in this directory.
  - **`StartingPoint/lib/`**: (DO NOT EDIT) A Statecharts run-time library, for running the generated code in (scaled) real-time while integrating with TkInter's event loop (for the GUI), and for running the Python tests (simulating as-fast-as-possible).
