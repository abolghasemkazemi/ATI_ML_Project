# Element-property references

These CSV files are intentionally empty templates. Add only traceable values,
one documented source per row. `binary_mixing_enthalpies.csv` stores the
pairwise value used in `H_mix = 4 sum(H_ij x_i x_j)`. Conflicting sources must
not be averaged silently. Missing constants remain NA and therefore produce NA
derived features. The pipeline never estimates stacking-fault energy (SFE).
