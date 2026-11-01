# Broader research design

The frozen protocol is [preregistered-study.md](preregistered-study.md). This
implementation compares full book logistic with a history-only logistic on
identical eligible observations. The primary score is the unweighted mean of
date-level macro F1 with the fixed down/unchanged/up class set. Boosted versus
full book logistic is secondary. Majority is descriptive. These are fixed
comparisons without hyperparameter search.

## Information and evaluation

All 48 selected dates must be present and match the frozen market before any
fit. Schema, book validity and coverage are checked without constructing final
targets. In pilot mode, final dates are removed before both feature and target
construction. Warm-up and forward horizon reset at every date, segment and
source boundary. Folds use strictly earlier dates; training label endpoints
must precede the first evaluation decision in both timestamp and source order.
Every scheduled fold is checked before fitting begins.

The extension reuses original sample selection and causal feature formulas,
then constructs targets from exact price-grid integers. A midpoint is expressed
in half ticks as best-bid ticks plus best-ask ticks. Its endpoint change is
compared exactly with twice the declared threshold. Exact one-cent changes in
either direction are unchanged; one-and-a-half-cent changes are directional.
Off-grid or unsafe-size prices fail validation rather than receiving a tolerance.
Original study source and artifacts remain untouched.

Development evaluates the 12 dates in 2022. The authorized final stage follows
the predeclared prequential schedule: refit before each of the 24 dates in
2023–2024 using all earlier eligible dates, including prior final labels.
No intermediate final score may guide settings, stopping or selection. This is
a scheduled sequence of fits, rather than a single model held unchanged for two
years. Outer CLI provenance binds the frozen protocol/source attestation to the
actual files; the research engine rejects missing attestations or authorization.

## Uncertainty and stopping

The paired score difference is full book logistic minus history-only logistic.
The frozen practical margin is 0.01 macro F1. A non-circular moving-block
bootstrap samples overlapping blocks of three chronological observed dates,
concatenates blocks, truncates to the original number of dates and computes the
paired mean. It uses 2,000 resamples, seed 42 and a 95% percentile interval.
Blocks do not wrap from the last observed date to the first. At least eight
nonoverlapping block equivalents are required for a final interval.

For pilot precision planning, split development date differences into complete
nonoverlapping three-date blocks. Estimate the sample standard deviation of
their means. With z = 1.95996 and target half-width 0.015, the estimated required
block count is max(8, ceil((z × block SD / 0.015)^2)). The planned final interval
half-width is approximated by z × block SD / sqrt(8). These normal-approximation
estimates from four pilot blocks are uncertain, including when observed
variance is zero. They are planning diagnostics, not power guarantees.

Use the fixed final selection once; do not add dates or stop based on final
scores. Inadequate projected precision requires explicit exploratory
acknowledgment before final evaluation. Research decisiveness also requires the
achieved primary interval half-width to be at most 0.015. Otherwise report that
the precision goal was unmet. Conditional practical gain requires the lower
bound to exceed 0.01; an upper bound below 0.01 rules out that gain under the
declared assumptions. Equivalence requires the whole interval within
[-0.01, 0.01]. Boundary contact alone does not establish a strictly greater gain.

Blocks assume sufficiently stable and exchangeable local behavior. Month-start
excerpts are separated by unsampled days; overlapping expanding fits can cause
dependence beyond three observed dates. Eight block equivalents do not prove
independence. No book update is an IID uncertainty unit, and these results do
not establish a continuous investable return curve or market profitability.

## Local signals

Each eligible out-of-sample decision requests 0.001 BTC when the model predicts
up and zero otherwise. Ten consecutive long target decisions force one flat
target before another long request. The count resets per segment. This caps
consecutive eligible target decisions; it does not guarantee execution holding
time, exit fills or gap liquidation. The simulator accounts for action latency,
IOC orders and unresolved segment-end inventory.
Signals carry source order, original receive-time availability, feature cutoff,
training-label maximum and model identity. Inference delay is zero. Detailed
signals, row-level probabilities and fitted estimators remain local.

Execution decisions use a separate causal feature frame that includes every
state after warm-up, including the last ten states without future targets.
Future label availability only restricts model training and classification
metrics. It never removes otherwise available trading decisions before a gap
or a segment endpoint.

## External published method

The accessible primary reference is Gould and Bonart,
[Queue Imbalance as a One-Tick-Ahead Price Predictor in a Limit Order Book,
arXiv:1512.03492v1](https://arxiv.org/abs/1512.03492). It studies ten Nasdaq stocks
using 2014 LOBSTER data and fits a logistic probability of the next nonzero
midpoint direction from best-queue imbalance. Its constant probability 0.5
baseline has Brier score 0.25.

Our separate development-only adaptation uses the same imbalance formula and
binary next-move idea. A decision occurs on arrival of the first state in each
constant-midpoint run. Its endpoint is the next midpoint change within the same
segment. The last run is excluded; no label crosses a gap. This causal sampling
rule is different from the paper's within-run random clock-time sampling.
The adapter validates the price grid and compares integer half-tick midpoints,
so floating-point addition cannot fabricate a nonzero move at an unchanged
midpoint.
Fits expand across earlier dates and reuse the fixed C=1 logistic pipeline.
The empirical training-frequency probability baseline is evaluated alongside
the paper's 0.5 null using Brier score, log loss, ROC AUC when defined and binary
accuracy. Zero queue denominator maps to zero imbalance and is counted.

The original equity dataset, randomized split and unpenalized fitting protocol
are not reproduced. There is no local-logistic variant or claim to match the
paper's reported numbers. The aggregate explicitly labels this a methodological
adaptation; it cannot substitute for the untouched final study.
