## What you write: a Python controller

Write a Python module that defines

    def act(obs):
        ...
        return [a_1, ..., a_{{ACT_DIM}}]

`obs` is a list of {{OBS_DIM}} floats (the observation above). `act` must return a sequence of {{ACT_DIM}} floats
(the action above; out-of-range values are clipped). You may use the Python standard library and numpy. You may
keep state between calls in module-level variables; if you do, also define `def reset():` which is called at the
start of every episode. The code gets no other information about the simulation, and no files or network.

Output format: reply with the complete module in a single ```python code block. You may write any explanation
outside the code block. If the reply has no valid block, or `act` raises an error or returns the wrong shape,
the controller scores as a failure.
