# Extension implementation contract (E0-E7)

The owner authorizes the agreed extension, parallel agents, feature/milestone
commits, repeated Astra medium review and final push to the existing private
repository. Preserve the original study/artifacts and original source modules
where possible. New modules live under market_microstructure.extension.

## Initial division and interfaces

- Root: integration CLI, configuration, provenance, benchmarks, reports, review,
  commits and publication. Agents must not commit or push concurrently.
- Data owner: new acquisition/coverage/storage modules and tests plus E0 source
  evidence. Propose one spot instrument to avoid unsupported inverse/funding
  accounting. No Coinbase data obtained via Tardis. Source must permit internal
  ML and local simulation. Never publish historical rows or trained assets.
- Simulation owner: replay.py, simulation.py, analytics.py and their tests.
- Research owner: study.py, statistics.py, replication.py and their tests.

No new scores or final target distributions may be examined before a frozen
research protocol and required review. Schema/time/coverage inspection is allowed.
Initial free feasibility budget: 8 MiB compressed total; extension acquisition
hard ceiling 1 GiB compressed, 5 GiB local historical storage, at most 64 dates,
20 minutes acquisition wall time. These are limits, not a requirement to spend
them. Fix the actual dates/selection and tighter bounds before bulk acquisition.
Stop if suitable lawful coverage cannot support the declared study.

## Simulator input contract

Reuse normalized states from data.ingest_files. Replay adapters accept normalized
DataFrames (also batches) with existing receive_time_us, source_order, segment_id,
session_date, provenance_key and five bid/ask price/size columns. Prices are quote
currency per base unit; spot depth sizes are base quantity. Retain exchange time.
Reject nonmonotonic receipt/order, duplicate provenance and malformed books.
Timestamp ties retain strict source order; never reorder ties.

Signal records have source_order, available_time_us, target_position (base
quantity; long/flat only initially), model_id, train_label_end_time_us and
feature_cutoff_time_us. Reject signals with training labels ending at/after
availability, features later than availability or an unmatched source event.
Detailed historical signals stay local.

SimulationConfig: initial_cash (quote), max_position (base), quantity_step,
price_tick, fee_bps, slippage_bps, latency_us, max_quote_age_us. Decimal via string
conversion for accounting/rounding; JSON monetary values are strings. Validate
finite positive cash/caps/steps/tick and nonnegative costs/latency. Currency names
and dataset/model identities enter manifests.

At each market observation: (1) cancel orders at segment boundaries, (2) execute
eligible older pending orders using current observed side/depth, (3) receive
signals and submit new orders. New orders cannot execute on their originating
observation, even at zero latency. No passive fills or queue claims. Marketable
IOC orders consume displayed liquidity once per current observation; cancel
remainder. Reject stale quotes, insufficient cash and exposure violations. One
pending-order policy prevents accidental stacking. Segment-end orders cancel;
inventory is marked at best bid and reported as unresolved. No fabricated gap
liquidation or continuous cross-gap holdings. Sessions are independent with
starting cash reset; never aggregate as a continuously investable annual curve.

Provide simulate(states, signals, config) -> JSON-safe result with local ledger,
orders, fills, per-segment summaries, aggregate metrics and assumptions. Include
a canonical ledger hash. Report exports aggregate metrics/hashes only.

## Research integration contract

Study consumes normalized states and a strict versioned config; reuse existing
features.build_samples and temporal split/model components. Primary comparison:
logistic with book features versus logistic with only past midpoint changes and
volatility. Secondary boosted versus full logistic. Majority is descriptive.
One horizon/threshold, fixed models, no search. Predict only later dates, fit
earlier dates with label-end purging; signals retain training-label maximum and
decision availability. No final fit/tuning before protocol/data/precision gates.

Statistics operate on paired date/block differences, never row IID. Predeclare
practical effect delta and block-bootstrap procedure. Positive if lower bound
exceeds delta; rule out improvement of delta if upper bound is below delta;
otherwise indeterminate. Equivalence requires the whole interval within
[-delta, delta]. No annualized Sharpe from excerpts.

Define run_study(states, config) -> aggregate study plus local signals per model;
root will wire exact interfaces before integration. External queue-imbalance
logistic adaptation is separate from a claim to reproduce published numerical
results. Use an accessible reference when exact external replication is feasible;
label scope and differences precisely.
