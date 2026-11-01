# Interpretation and operational limits

## Sampling and generalization

The reference data consists of 20,000 opening snapshots on the first UTC day of
each month in 2020 for one exchange/instrument. The twelve windows cover roughly
227–1,830 seconds each, not full days, a continuous year or current markets.
Time-of-day selection, first-of-month selection, one historical regime and one
instrument all limit generalization.

Twelve dates are twelve observed date units, not proof of statistical
independence. Updates within a window are strongly dependent. The development
design has seven validation dates; the final holdout has only two dates.
Row-level IID standard errors would create false precision. Date-aware
resampling or descriptive dispersion is useful context but cannot overcome
limited coverage or establish a stable market edge.

## Source and book assumptions

Tardis reconstructed the top-five snapshots. Crossed levels may have been
removed upstream, so clean supplied rows do not prove clean exchange-native
events. The pipeline does not reconstruct an incremental book. Truncated depth
also omits liquidity beyond the visible five levels.

CSV files omit explicit disconnect markers. Date/file boundaries and observed
receipt gaps greater than 30 seconds reset windows, but undetected short
disconnects and upstream capture/filtering cannot be ruled out. Receipt time
provides a conservative information boundary, not a guarantee of realistic
trading-system latency. Current instrument documentation is not an archival
metadata record for every historical date.

Compressed acquisitions are bounded source prefixes. Local SHA-256 values
verify those saved prefixes and complete-row excerpts. They do not validate a
missing whole-day gzip CRC or the provider's full-file MD5, and they do not
establish that the unobserved remainder of the day is intact.

## Modeling and evaluation

The primary event-count horizon advances ten valid snapshots; its elapsed
clock time varies with activity. A 0.5 USD no-change threshold is a declared
research choice. Results depend on that target and do not describe every
possible horizon or economically actionable move.

Model settings are intentionally modest. A majority rule, logistic regression
and limited-complexity boosted trees demonstrate comparison discipline rather
than an exhaustive model search. Predeclared ablation and horizon sensitivity
use development data only. Favorable robustness cells are not permission to
replace the frozen primary result.

The final holdout must remain outside selection. Exact reproduction of frozen
decisions is distinct from repeatedly changing decisions after inspecting the
holdout. Material post-result changes require a dated reviewed contract and,
where necessary, new untouched observations.

## Prediction is not execution

Classification quality does not establish net profit. The study does not model
fees, queue position, fills, spread crossing, slippage, inventory constraints,
funding, risk limits or executable latency. It places no orders and connects to
no live exchange or broker.

## Reproduction and distribution

The locked Python environment, immutable run metadata and data hashes support
repeatability. Providers can change availability or files; any checksum mismatch
must be reported rather than silently accepted. Numerical behavior may differ
outside the pinned environment. The CLI requires exact canonical metric equality
in the recorded runtime; a different numerical result fails explicitly rather
than being silently accepted under an undocumented tolerance.

Provider terms cover free samples. Raw/processed event-level data, per-event
predictions and fitted models remain local and are excluded from GitHub,
under either public or private visibility. Research reports contain qualifying aggregate
outputs rather than substituting for the underlying data service.
See the [publication-status record](publication-status.md) for current visibility.

The synthetic HTML design proposal and demo make no empirical claim. Their
usability review does not validate market predictability. Consult the actual
reference experiment and independent research review for evidence-backed claims.
