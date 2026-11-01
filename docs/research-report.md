# Frozen historical research result

The result is **inconclusive evidence of improvement beyond the linear
comparison**. Boosted trees outperform logistic regression across the seven
development dates, but logistic regression wins on each of the two final dates
and on the pooled final holdout. The predeclared rule therefore does not support
a repeatable gain beyond the linear comparison. This is a classification study;
it establishes neither trading profitability nor an executable trading strategy.

The authoritative aggregate record is
[reports/reference/experiment.json](../reports/reference/experiment.json), with
an [HTML report](../reports/reference/report.html). The original empirical run is
exp-f6aab567f4de3706, created 2026-11-01 UTC from scientific code committed before
fitting. A later formatting-only report refresh may have a different artifact
identity; the scientific inputs and numerical results must remain identical.

## Data and frozen design

The source is Tardis.dev's vendor-reconstructed top-five Deribit BTC-PERPETUAL
book snapshots, using the first 20,000 complete records on the first day of each
month in 2020. These are twelve short opening excerpts, approximately 227 to
1,830 seconds each, rather than full days or continuous annual coverage.
The [source evidence](data-source-evidence.md) records acquisition limits,
checksums, upstream crossed-book filtering and legal restrictions. Tardis
documents the [snapshot schema](https://docs.tardis.dev/downloadable-csv-files/data-types.md#book_snapshot_5)
and [sample access](https://docs.tardis.dev/downloadable-csv-files/overview.md).

Ingestion retained 240,000 states in twelve file/date segments with no excluded
records, 54 tied receipt timestamps and no observed receipt gaps over 30 seconds.
This does not establish that the upstream feed contains every exchange event.
Twenty trailing warm-up states and ten unavailable future-label states per date
leave 239,640 primary labeled samples. Depth amounts are USD notional for this
inverse instrument, following the [Deribit specification](https://support.deribit.com/hc/en-us/articles/31424954847133-Inverse-Perpetual).

The target is the mid-price change ten valid states later within the same
segment: up above +0.5 USD, down below -0.5 USD, otherwise unchanged. A ten-state
horizon has variable elapsed duration. Ten causal spread, imbalance, depth and
trailing-change features use information available by local receipt time.
Tied receipt times retain source order; features and labels never cross a
file/date or invalid/gap boundary.

The [predeclared contract](decisions/001-predeclared-research-contract.md) fixed
the data, features, models, target, split, robustness checks and conclusion rule
before scores were inspected. January through March are initial training dates;
April through October supply seven expanding walk-forward validation dates.
The frozen models are then trained on January through October, with 199,700
samples, and evaluated on November and December, with 39,940 samples total.
Preprocessing is fitted inside each training fold. Label-end purging and
independent order/time audits protect the evaluation boundary. The observed
date-separated folds require zero purges; synthetic boundary tests exercise
cases requiring positive purging.

## Primary comparisons

All scores are on a 0 to 1 scale; higher is better. Development values below
are the arithmetic mean of seven per-date scores. Final values are computed
from predictions pooled across two final dates. Macro F1 is nonlinear, so these
two aggregation methods must not be treated as interchangeable.

| Model | Development date-mean macro F1 | Development date-mean balanced accuracy | Final pooled macro F1 | Final pooled balanced accuracy |
| --- | ---: | ---: | ---: | ---: |
| Training-majority rule | 0.326678 | 0.333333 | 0.272051 | 0.333333 |
| Logistic regression | 0.434971 | 0.395790 | **0.497672** | **0.480496** |
| Boosted trees | **0.460571** | **0.413220** | 0.457272 | 0.441951 |

Boosted minus logistic development macro F1 averages +0.025600. The descriptive
95% paired date-bootstrap percentile interval is [+0.015060, +0.039279], using
seven date units, 2,000 resamples and seed 42. Each development date favors
boosting, but shared expanding training sets, within-date temporal dependence
and only seven validation dates limit the interpretation. Treat this interval
as exploratory: calendar dates are not proven independent or exchangeable,
and 239,640 correlated labeled states are not 239,640 independent experiments.

The final pooled boosted-minus-logistic difference is **-0.040401** macro F1.
Both fitted models beat the majority rule, while the more demanding comparison
against logistic regression reverses. The final dates separately show the same
ranking:

| Final observed date | Samples | Majority macro F1 | Logistic macro F1 | Boosted macro F1 | Down / unchanged / up support |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2020-11-01 | 19,970 | 0.295149 | **0.486050** | 0.462406 | 2,107 / 15,865 / 1,998 |
| 2020-12-01 | 19,970 | 0.245891 | **0.487543** | 0.439136 | 4,358 / 11,670 / 3,942 |

No holdout confidence interval is promoted: two held-out date units are too few
for credible broad uncertainty claims. The report's JSON contains all
per-date/class metrics, confusion matrices, warnings and fold audit details.

## Imbalance and robustness

Unchanged labels comprise approximately 93.16% to 98.17% of individual
development-date targets, compared with 79.44% in November and 58.44% in December.
This is a substantial change in target composition across the observed
excerpts. The fixed USD threshold, variable elapsed event-count horizon and
different short opening windows provide plausible context for limited
transfer; the experiment does not identify a causal explanation. All three true classes
are present on both final dates. The majority rule predicts unchanged only and
has zero recall for down and up, so its superficially high accuracy on quiet
development excerpts is not evidence of directional skill.

Final pooled down/up recall is 0.209745 / 0.313131 for logistic regression and
0.228152 / 0.153704 for boosting. Minority-class detection remains limited;
an aggregate F1 gain must not be read as reliable identification of every move.

The two robustness checks were fixed in advance and run on development data
only. They neither redefine the primary target nor select a final-holdout
configuration:

| Development-only check | Majority date-mean macro F1 | Logistic date-mean macro F1 | Boosted date-mean macro F1 |
| --- | ---: | ---: | ---: |
| Primary ten-state horizon, all features | 0.326678 | 0.434971 | 0.460571 |
| Remove imbalance inputs | 0.326678 | 0.431848 | 0.461691 |
| Twenty-state horizon | 0.319577 | 0.398270 | 0.411241 |

Removing imbalance does not reduce the boosted score in this study. The
comparison therefore does not isolate imbalance as the cause of the observed
development gain. At twenty states, boosted minus logistic averages +0.012970,
with a descriptive 95% paired date-bootstrap interval of [+0.004975, +0.020693].
The same seven-date and dependence caveats apply. No robustness variant is
evaluated against the reserved final dates to choose a new winner.

## Reproducibility and provenance

The original empirical record identifies commit
8e645136152197f1d9a4afb3eab5f3df61f77d12 and scientific-source SHA-256
102a74ceb1a60cbab08d167138ea954696e8bc1cedfde4bab21aff82471caa45.
It records Python 3.12.15 and the exact dependency lock. Full identifiers are
machine-readable in the reference rather than inferred from this narrative.

| Invariant | SHA-256 |
| --- | --- |
| Research contract | 1d2edfa071abd75d344fa9a244e296132ada743018803cdacca6d3ffd6c679ee |
| Raw source metadata | 3db6d6e29797bbabbb79ea04f582a05f4993fb7a6192a2d4b654738534ed82ec |
| Normalized states | d286808c5692bc3783be222f5dfad5e6807fa64f093d43c0dc3a34a00b9ad9c4 |
| Primary samples | 2df42787c1c2e716b825e690233bd6b5e9a8f6e211ff07c4569ca2db74d166c5 |
| Split assignments | 458cce745c77994b2942a2ebf42b4fc8341c2bb7591af7629702de6712771e5f |

The original frozen run passed independent clean-checkout verification of its
source, locked dependencies, runtime versions, raw data, normalized states,
features and split assignments. The clean checkout passed all 221 tests and
re-executed the study with exact equality of all compared metrics. Final
formatter-revision evidence belongs in [P6](phase-handoffs/P6.md) and the
published validation record. Frozen reproduction repeats previously fixed
decisions and is distinct from new model selection.

Provider [terms](https://docs.tardis.dev/legal/terms-of-service) allow the
internal research workflow while restricting data and model redistribution.
The repository therefore publishes code, synthetic fixtures, metadata,
fingerprints and non-reconstructible aggregate findings only. Raw/processed
historical rows, per-event predictions and fitted model weights remain local.

## Interpretation and next test

This project demonstrates a traceable research and validation pipeline and an
honest inconclusive finding. It does not establish persistent market signal,
causal value of imbalance, performance on other instruments/periods, latency
feasibility, net returns, execution quality or capacity. Spread costs, fees,
slippage, queue position and trading decisions were not modeled.

The next empirical step requires a newly predeclared set of broader intraday
dates and a new untouched holdout before further model selection. The current
final dates must not become a tuning set. See the full
[limitations](limitations.md) and [interview discussion](interview-notes.md).
