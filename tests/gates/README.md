# Driving the gates to a known positive

A gate that has never been made to fail has not been shown to be able to fail.
Both scripts here take the tree as it stands, break exactly one thing, and check
that the refusal arrives — then put it back.

```sh
python3 tests/gates/plant_violations.py    # 37 planted violations + a control
node    tests/gates/gate_c_refusals.mjs    # every gate (c) refusal + a control
```

Each exits non-zero if any planted violation goes uncaught **or if the control
build is refused**. The control matters as much as the plants: a verifier that
refuses everything catches every violation and is useless.

Neither script writes to `dist/`, `docs/` or `src/`. `plant_violations.py`
copies the artifact and the source into a temporary directory and mutates the
copy.

When you add a gate, add a plant for it in the same change. The eight labelled
`NEW` were added because a real defect got past the gates that existed:
reader-visible text injected through CSS `content:`, a foreign syntax palette
arriving with a Shiki theme, a colour Expressive Code derived on its own,
unreachable JavaScript in the served directory, the banned status grade
returning to a machine record, and the on-page snippet drifting from the file it
claims to reproduce byte for byte.
