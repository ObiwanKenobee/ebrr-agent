# Notebooks

Use notebooks for transparent analysis and visualization, not as the sole source of core implementation logic. Keep reusable code in `src/ebrr/` and import it from notebooks.

Every notebook should state its data source/version, expected inputs, environment, random seed, and whether it uses training, validation, or held-out test data. Clear outputs containing private paths, tokens, or hidden evaluation information before publication.
