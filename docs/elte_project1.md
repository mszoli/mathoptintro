# Mini-Project 1/2

## General Information

1. **Tasks**:

    - Each student must choose **exactly one** of the tasks listed below.

2. **Solution**:

    - The solution must be implemented in **Python**, using the **OR-Tools MathOpt** package.
    - A **short report** (in PDF format) must also be submitted, containing the developed formulation for the selected task and a description of the solution approach.

3. **Deadline**:

    - The files (program code and documentation) must be sent to **marko.horvath (at) sztaki (dot) hu** no later than **April 2**, 2026 (before the last supper).

4. **Presentation**:

    - The solutions will be presented **in person** (individually).
    - The presentations are scheduled to take place at the beginning of the course on **April 9**.
    - Upon prior arrangement, solutions may also be presented at another time at SZTAKI.

## Task #1: Pipes

The goal is to implement an MIP-based solution approach to puzzle [Pipes](./puzzles/puzzles.md#pipes).

Download file <a href="https://github.com/hmarko89/mathoptintro/blob/master/src/puzzles/pipes.py" target="_blank">`pipes.py`</a>.
The solution approach must be implemented into the method `solve_pipes`.
This method requires a puzzle instance encoded as a string, and must return the solution encoded as a string.

Parameters `draw_task` and `draw_solution` indicate if the task and the solution must be drawn, respectively.
For this, the `networkx` package should be used.

The file also contains a set of initial instances.
Additional instances can be obtained via <a href="https://github.com/hmarko89/mathoptintro/blob/master/src/puzzles/taskcollector.py" target="_blank">`taskcollector.py`</a>.

The method must provide a feasible solution for any valid instance (up to size 25×25) with a reasonable execution time.

## Task #2: Masyu

The goal is to implement an MIP-based solution approach to puzzle [Masyu](./puzzles/puzzles.md#masyu).

Download file <a href="https://github.com/hmarko89/mathoptintro/blob/master/src/puzzles/masyu.py" target="_blank">`masyu.py`</a>.
The solution approach must be implemented into the method `solve_masyu`.
This method requires a puzzle instance encoded as a string.

Parameters `draw_task` and `draw_solution` indicate if the task and the solution must be drawn, respectively.
For this, the `networkx` package should be used.

The file also contains a set of initial instances.
Additional instances can be obtained via <a href="https://github.com/hmarko89/mathoptintro/blob/master/src/puzzles/taskcollector.py" target="_blank">`taskcollector.py`</a>.

The method must provide a feasible solution for any valid instance (up to size 25×25) with a reasonable execution time.
