# Data dictionary and information boundaries

## Raw source representation

The pinned Tardis book_snapshot_5 CSV schema has 24 fields: exchange, symbol,
timestamp, local_timestamp and twenty price/amount fields. For each level 0–4,
the raw ordering is ask price, ask amount, bid price, bid amount. The
[official schema](https://docs.tardis.dev/downloadable-csv-files/data-types.md#book_snapshot_5)
defines timestamps as UTC microseconds since the Unix epoch and the snapshot
as the tracked top-five levels. The vendor performed reconstruction and may
have removed crossed levels upstream.

The normalized schema numbers levels from **1 to 5**. Level 1 is the highest
bid or lowest ask. Bid prices strictly decrease with depth; ask prices strictly
increase. A valid state requires positive finite prices, nonnegative finite
amounts, all five levels and best bid below best ask.

## Normalized state fields

| Field | Type / meaning |
|---|---|
| exchange, symbol | Strings identifying the one selected market |
| session_date | Canonical YYYY-MM-DD UTC date of receipt |
| segment_id | Identifier reset for each source file/date, invalid state or >30-second receipt gap |
| source_file | Portable original CSV basename |
| source_row_position | Int64, one-based record number excluding the header |
| source_order | Int64, one-based global original-record position across date-ordered files; excluded rows still consume positions |
| provenance_key | Excerpt SHA-256 plus original record position |
| event_time_us | Int64 exchange timestamp, UTC microseconds |
| receive_time_us | Int64 local receipt timestamp; the information-availability boundary |
| bid_price_1..5, ask_price_1..5 | Float64 prices in USD |
| bid_size_1..5, ask_size_1..5 | Float64 source-native USD notional amounts |

Original capture order is retained for tied receipt times. Receive-time
regressions are excluded against the last valid high-water mark; the data is
not sorted into a deceptively clean order. Exchange-time decreases are counted
separately because receipt time controls causal availability. Exact duplicate
source rows are excluded. Identical book payloads at different timestamps are
counted and retained as distinct source records.

The quality report partitions all source rows into retained and excluded rows,
with attributable source/row/reason records and counts. Zero amounts are
retained and counted. Missing depth, invalid units, malformed numerical fields,
negative amounts, crossed/locked books, bad level ordering and market mismatches
are deterministic exclusions or explicit file-level errors.

## Ten causal features

Let mid be (best bid + best ask) / 2, tick be 0.5 USD, and window be 20 states.
All inputs use the current received state and earlier states in the same
contiguous segment. They never use target endpoints.

| Feature | Formula / units |
|---|---|
| spread_ticks | (best ask - best bid) / tick |
| level1_imbalance | (bid size at level 1 - ask size at level 1) / their sum; dimensionless |
| depth5_imbalance | (sum of five bid sizes - sum of five ask sizes) / combined depth; dimensionless |
| bid_depth5 | Sum of five bid amounts, USD notional |
| ask_depth5 | Sum of five ask amounts, USD notional |
| mid_change_1_ticks | (current mid - preceding state mid) / tick |
| mid_change_window_ticks | (current mid - mid 20 states earlier) / tick |
| mid_volatility_ticks | Population standard deviation, ddof=0, of the last 20 one-state mid-price changes in ticks |
| spread_change_1_ticks | Current spread minus preceding spread, both in ticks |
| imbalance_change_1 | Current top-five imbalance minus preceding top-five imbalance |

When opposing total size/depth is zero, imbalance is defined as zero and the
condition is counted. No future interpolation or cross-gap forward fill is
performed. The first 20 states of a segment lack the required trailing history
and are excluded with a recorded reason.

The [Deribit inverse-perpetual specifications](https://support.deribit.com/hc/en-us/articles/31424954847133-Inverse-Perpetual)
describe order amounts as USD exposure, not BTC. The current specification and
the observed historical half-dollar grid support the declared units/tick; this
is not a point-in-time 2020 metadata certificate.

## Targets and audit metadata

The primary horizon is exactly ten subsequent supplied valid book states in
the same segment/file/date. It is not ten seconds. Let delta be future mid
minus current mid, measured in USD:

- target +1: delta > +0.5;
- target -1: delta < -0.5;
- target 0: all other moves, including exactly +/-0.5.

The final ten states of a segment lack a permitted endpoint and are excluded.
Warm-up exclusion takes precedence so every input state has one attributable
retained/excluded outcome.

| Field | Meaning |
|---|---|
| feature_cutoff_time | Int64 current receipt time in UTC microseconds |
| label_end_time | Int64 receipt time of the exact future endpoint |
| feature_order, label_end_order | Original event-order boundaries, including ties |
| label_end_source_row_position | Endpoint's one-based source record position |
| label_provenance_key | Endpoint's excerpt hash and record position |
| label_segment_id, label_session_date, label_source_file | Proof that the endpoint stays within the permitted boundary |
| target | Int8 class -1, 0 or +1 |

Target construction is separate from feature calculation. Only the explicit
ten-feature list is passed to estimators; target/audit/provenance columns are
never automatically selected as model inputs.

## Folds, metrics and reports

January–March are the initial training dates. Expanding one-date validation
folds use April through October; November–December are reserved for the final
evaluation. Training examples are purged if their label endpoint reaches the
first evaluation decision time. Final-holdout outcomes do not select model
settings, features, labels or robustness variants.

Metrics use fixed class order [-1, 0, +1]. Macro F1 averages class F1 scores;
balanced accuracy averages class recalls. Both range from 0 to 1, higher is
better. Reports include class support and explicit absent-class warnings,
confusion matrices, date/fold dispersion and supported date-aware uncertainty.
Row counts are not treated as counts of statistically independent observations.

Experiment JSON records the frozen configuration, hashes, package/code
identity, feature definitions, split audit, model settings, metrics and
warnings. Portable HTML is a readable presentation of those artifacts.
