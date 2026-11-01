# E0-E1 predeclared extension study

These choices are recorded before fitting new historical models or inspecting
reserved target distributions. The original 2020 Deribit study and its results
remain unchanged. The new spot instrument is a documented scope decision to
avoid applying spot accounting to an inverse perpetual without funding inputs.

## Data and acquisition

- Tardis Bitstamp BTCUSD top-five spot snapshots, first UTC day of each month
  January 2021 through December 2024: 48 dates, all distinct from original dates.
- Fetch complete daily gzip objects; verify whole-gzip CRC and SHA-256. Select all
  observations in eight fixed half-open 15-minute windows beginning 00:00,
  03:00, 06:00, 09:00, 12:00, 15:00, 18:00 and 21:00 UTC. Two sampled hours per
  date, not continuous market coverage; first-of-month selection remains a limit.
- Every window and invalid/gap boundary starts a new segment. Receipt time and
  original source order determine information availability; no interpolation.
- Probed aggregate compressed full-source size: 268,550,418 bytes; maximum single
  source 9,256,742 bytes. Feasibility probes consumed 1,436,943 bytes, tracked
  separately. Caps: 16 MiB compressed/date, 160 MiB decompressed/date, 1 GiB total
  compressed, 5 GiB historical storage, 64 dates, 20 minutes acquisition. No paid
  data, credentials or live exchange connection.
- Data quality and all date/window coverage must pass before fitting. An exact
  source lock pins downloaded content. No silent source/date substitution.
- Before bulk acquisition, freeze objective availability gates: each of 384
  windows has at least 100 valid states, observed span at least 840 of 900
  seconds, first/last observation within 60 seconds of its window edge, and
  excluded fraction at most 1% per date. All 48 dates and eight windows/date
  must qualify. These are coverage checks, not target/score checks; they cannot
  certify the absence of short unrecorded disconnects.

## Prediction and evaluation

- One target: midpoint change ten later valid states, within the same segment.
  Up above +0.01 USD, down below -0.01 USD, otherwise unchanged. Research price
  grid 0.01 USD; spot depth is BTC; quantity accounting grid 0.00000001 BTC.
  Source units and historical grid consistency require independent verification.
- Reuse ten existing causal book/change features and fixed original model
  factories. History-only logistic uses midpoint change one/trailing-window and
  trailing volatility. Primary comparison full-book logistic minus history-only
  logistic. Secondary boosted minus full-book logistic. Majority descriptive.
- Initial training dates: 2021 (12). Development evaluation dates: 2022 (12).
  Expanding chronological fits with label-end purging and train-only transforms.
- Final evaluation dates: 2023-2024 (24). Predeclared prequential evaluation:
  scheduled expanding refits before each date may use strictly earlier labels,
  including earlier final dates. Settings never change. No intermediate final
  score is used for a human or automated choice; release all final scores only
  after completing the fixed evaluation. This is not a single frozen two-year fit.
- Primary metric: date-mean macro F1; report balanced accuracy, class supports,
  per-class metrics and confusion matrices. Do not mix date means with pooled F1.
- Practical gain delta: 0.01 macro F1. Paired moving-block date bootstrap, block
  length three adjacent observed months, 2,000 resamples, seed 42, 95% interval.
  Positive practical gain requires lower bound > delta; upper bound < delta
  rules out that declared gain under assumptions. Equivalence requires the whole
  interval inside [-delta,+delta]. Otherwise evidence is indeterminate.
- Development-only precision plan estimates required final date coverage from
  observed variability and dependence, targeting interval half-width <=0.015.
  At least eight length-three final blocks. This estimate is approximate and
  cannot guarantee future precision or independence. If inadequate, explicitly
  downgrade research decisiveness; do not change delta or data after final scores.
- Final scoring requires completed protocol/source freeze, coverage checks and
  independent safety review. Record every unchanged reproduction separately.

## Simulation assumptions

- Unlevered long/flat spot, initial quote cash 10,000 USD per independent segment,
  maximum base inventory 0.001 BTC. No borrowing, shorts, funding or derivatives.
- Same fixed mapping for model signals: up requests long, other classes request
  flat; maximum-holding policy, if supported, is exactly ten observations and
  must be documented as a signal rule, not guaranteed execution. No threshold
  search or strategy selection using final returns. No-trade baseline included.
- Signals are available at the current receipt timestamp; no measured inference
  latency claim. Scenario action delays apply after signal availability.
- Marketable IOC only, displayed depth bounds, one pending order, no own impact,
  maker queue or exchange-realistic fill claim. New orders execute only on later
  source observations; exchange-clock skew/stale quote handling is explicit.
- Cost/action-delay scenarios fixed in configs/research-extension.json. Costs
  are research assumptions, not verified historical account-specific fee tiers.
  Zero-cost run is diagnostic; base and stress results are reported regardless
  of sign. Never select the most profitable assumption as the headline result.
- Each segment starts independently. Cancel pending orders at boundaries, mark
  unresolved inventory at best bid, disclose it, and invent no unseen liquidation
  or gap returns. Sum scenario P&L across independent equal-capital trials only;
  do not claim compounding, annualized Sharpe or a continuous annual equity curve.
- Historical signals, orders, fills, ledgers and fitted values stay ignored/local.
  Shared results contain only permitted non-reconstructible aggregate statistics.

## Reproduction, engineering and acceptance

External queue-imbalance logistic study is a separately labeled methodological
adaptation unless the original data/protocol support numerical reproduction.
Do not imply published equity results were replicated by a crypto experiment.
Measure repeatable wall time and native peak process memory with exact data-size
and environment metadata; optimize only measured bottlenecks and require result
parity. No C++ requirement. Offline synthetic fixtures support all CI checks.

Platform acceptance, predictive practical-gain decision and hypothetical trading
outcome are separate statuses. Completion never means forcing profitable returns
or relabeling an imprecise result. A supported negative decision is acceptable;
remaining precision/coverage limits stay explicit. Final Astra medium review and
verified push to the existing private repository are required delivery gates.
