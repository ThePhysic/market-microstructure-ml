# P0 research contract, frozen before model scores

## Decision

CONDITIONAL GO based on actual 2020-01-01 Deribit BTC-PERPETUAL top-five data inspection: its CSV has the documented 24-column schema, microsecond UTC exchange/receipt times, tick size 0.5 USD and HTTP Range support. GO becomes effective only after all twelve preselected excerpts and legal/source evidence pass the feasibility audit. No predictive score has been inspected at the time this contract is recorded.

## Predeclared choices

- Source: Tardis vendor-reconstructed top-five snapshots, Deribit BTC-PERPETUAL.
- Dates: first day of every month January–December 2020, selected for bounded independent observed-date coverage rather than outcomes.
- Sample: first 20,000 complete records/date, requested with a fixed 512 KiB compressed-prefix cap/date (tightened from the initial 2 MiB ceiling before any score), and 24 MiB transferred overall including feasibility probes. A compressed prefix may end before 20,000 records; record actual coverage. Prefixes do not establish full-gzip integrity or represent full trading days.
- Time: local receipt UTC microseconds define decision availability; exchange timestamps are retained. Original source row order breaks timestamp ties.
- Continuous segments break at a new source/date, invalid state, local timestamp decrease or receipt gap over 30 seconds. Missing disconnect events remain a source limitation.
- Primary target: mid-price change ten valid book states later in the same segment. Up if change > 0.5 USD, down if change < -0.5 USD, otherwise unchanged. This is one synthetic-tick-width no-change band on each side, with actual tick metadata verified on the selected sample.
- Inputs: spread in ticks, level-one/top-five imbalance, bid/ask top-five depth, trailing midpoint changes/volatility and past spread/imbalance changes. Twenty past increments for the trailing window. No future-derived inputs.
- Models: training-majority baseline; median-imputed, standardized logistic regression; median-imputed small histogram gradient boosting. Fixed settings and seed 42; no broad search.
- Development: expanding walk-forward training with at least three earlier dates, one later validation date per fold. April–October are seven validation dates when all twelve dates qualify.
- Final holdout: November and December, entirely excluded from selection and robustness evaluation. Refit frozen models on permissible January–October samples, purge training target intervals at the holdout boundary, then score the final holdout once.
- Purge: remove every training sample whose label endpoint is at or after the first evaluation cutoff time. Record times, source ordering and sample-index hashes for independent audit.
- Primary metrics: fixed-class macro F1 and standard present-true-class balanced accuracy; also report fixed-three-class macro recall, confusion matrix, per-class support and missing-class warnings.
- Predeclared robustness: remove imbalance inputs and separately change horizon to twenty book states on development folds only. These are descriptive stress tests, not a search that can redefine the primary contract.
- Uncertainty: paired bootstrap of per-date model-score differences, with seven development dates an explicitly small exploratory sample. Never treat correlated rows as IID observations.
- Conclusion rule, frozen before scores: describe a result as promising only on these limited excerpts if the development date-bootstrap lower bound for boosted-minus-linear macro F1 exceeds zero, boosted improves on the trivial baseline, and the final aggregate holdout improves beyond both. Otherwise classify as inconclusive, or no added value beyond the linear comparison when development and holdout deltas are both nonpositive. Every category remains exploratory; no global market generalization or profitability claim.

## Interpretation and stop conditions

These are twelve monthly opening excerpts. They cannot support statements about uninterrupted monthly trading, other exchanges/instruments, all intraday regimes or profitability. The outcome may be negative or inconclusive.

Stop before empirical fitting if source eligibility, legal research permission, timestamp/order semantics, required independent dates or three-class feasibility cannot be verified. The holdout is not a source of configuration changes. Any subsequent material research change requires a dated note and a new clean evaluation design where necessary.

## Source pointers

- https://docs.tardis.dev/downloadable-csv-files/overview.md
- https://docs.tardis.dev/downloadable-csv-files/data-types.md
- https://docs.tardis.dev/downloadable-csv-files/api.md
- https://docs.tardis.dev/legal/terms-of-service

Current terms permit internal research but restrict raw/processed row redistribution and external sharing of trained models. Only non-reconstructible aggregate statistics, checksums/manifests, code and synthetic test fixtures will be committed; no trained weights or row-level predictions.
