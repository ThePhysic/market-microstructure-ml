# Implementation contract

Implement P0–P6 of the supplied Market Microstructure ML & Validation Pipeline specification. The owner's latest instruction authorizes end-to-end completion, parallel implementation, repeated Astra medium adversarial review, and private GitHub publication. Phase evidence and scientific acceptance gates remain required; the earlier P0-only execution limit is superseded by that instruction.

## Research boundaries

One historical venue/instrument, top-five vendor-reconstructed order-book snapshots, causal inputs at local receipt time, one primary event-count horizon, three target classes, chronological purged walk-forward comparison, and a final untouched holdout. No live trading, paid access, proprietary-data redistribution, or synthetic empirical claims.

P0 pins the exact dataset and research configuration before any model score is inspected. Free real-data probing is bounded to 12 dates, at most 2 MiB compressed bytes/date, 20,000 retained rows/date and 24 MiB transferred overall; stop before exceeding any cap. These are excerpts rather than complete trading days and must be described that way. No later evidence-based change to these choices without a dated decision.

## Shared Python interfaces

Normalized valid-state DataFrame:
- exchange, symbol, session_date (YYYY-MM-DD), segment_id, source_file, source_row_position (1-based source record index), provenance_key.
- event_time_us and receive_time_us as signed int64 UTC microseconds. Receipt time defines information availability.
- bid_price_1..5, ask_price_1..5, bid_size_1..5, ask_size_1..5 as float64.
- source_order as a global, stable, ascending int64 across date-ordered source files. Preserve timestamp ties.

features.build_samples(states, *, horizon_events=10, threshold_ticks=1, tick_size=0.5, trailing_window=20) -> (samples DataFrame, feature_columns list[str], quality dict).
Samples retain provenance plus feature_cutoff_time (int64 microseconds), label_end_time (int64), feature_order, label_end_order, target (-1/0/1). Features and labels never cross segment_id. Every unusable sample has an attributable exclusion count.

splits.walk_forward(samples, *, min_train_dates=3, holdout_dates=2) -> (folds list[Fold], holdout Fold, audit dict).
Fold is a dataclass with name, train_indices and test_indices (positional numpy arrays), train_dates, test_dates, purged_count and audit metadata. Expanding folds use one later date for validation. Final holdout is the last two observed dates and excluded from selection. Train labels ending at or after the first evaluation decision timestamp are purged conservatively.

models.model_factories(seed=42) -> dict[str, callable producing unfitted sklearn estimators].
Keys majority, logistic, boosted. Preprocessing is inside each model Pipeline and fit exclusively on training rows. Fixed modest settings, no final-holdout tuning.

evaluation.evaluate_predictions(y_true, y_pred) -> dict containing macro_f1, balanced_accuracy, per_class, confusion_matrix, support. Fixed class order [-1,0,1]; report absent classes explicitly.

Root integrates experiment.run_experiment and manifest/report formats. Result distinguishes development folds, predeclared robustness, and once-only final holdout. Manifests retain data/config/code/package/split hashes and warnings.

## Ownership

- Root: setup/configuration, CLI, experiment integration, reports, documentation, real runs, review integration, GitHub.
- Data agent: acquisition.py, data.py, tests/test_data.py, tests/test_acquisition.py and data feasibility notes.
- Temporal agent: features.py, splits.py, tests/test_features.py, tests/test_splits.py.
- Model agent: models.py, evaluation.py, statistical helpers, tests/test_models.py, tests/test_evaluation.py.

Use src/market_microstructure/. Do not modify another owner's files without coordination. Never track raw historical records in Git. A small fixture generator may be duplicated within independent test modules until integration; do not create a shared conftest.py owned by multiple agents.
