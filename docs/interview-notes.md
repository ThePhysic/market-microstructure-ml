# Discussing the project accurately

## A short introduction

I built a reproducible research pipeline to test whether order-book features
improve short-horizon price-move classification beyond simple baselines.
I used bounded historical Deribit BTC perpetual top-five snapshots, causal
features and date-aware validation. Boosted trees led during development, but
logistic regression won on both reserved final dates. I reported the result as
inconclusive and retained the negative comparison rather than tuning the
holdout into a positive result.

## What the result actually says

The seven development dates give date-mean macro F1 of 0.460571 for boosted
trees and 0.434971 for logistic regression. On the two final dates pooled
together, logistic reaches 0.497672 and boosting reaches 0.457272; logistic
also wins on each date separately. Development and final scores use different
aggregation rules, so I identify them explicitly. The
[research report](research-report.md) and
[machine-readable reference](../reports/reference/experiment.json) contain
the complete comparison, including the majority baseline.

Both learned models beat the majority rule on final macro F1. That is weaker
evidence than a consistent gain beyond the linear comparison. It does not
justify selecting boosted trees as a reliable improvement or claiming a
profitable trading signal.

## Decisions worth explaining

- **Data feasibility before fitting.** I verified accessible historical
  schemas, receipt-time semantics, depth units, tick alignment, coverage and
  provider permissions. Each of twelve dates contains a short opening excerpt,
  approximately 227-1,830 seconds; I do not call these full-day backtests.
- **Availability and lineage.** Features stop at local receipt time. Source
  order resolves tied times, while every retained sample points back to a
  source hash and original row. Exchange time alone does not prove that a
  feature was available to a local decision maker.
- **Temporal validation.** Labels use ten subsequent valid states within a
  segment. Training labels touching an evaluation cutoff are purged, feature
  transformations fit only training data, and a reserved final block is
  excluded from selection. Independent order/time checks supplement fold code.
- **Small baselines first.** A majority rule exposes class imbalance; logistic
  regression tests whether extra model complexity contributes. Fixed small
  boosted trees avoid a broad optimization exercise on a tiny date sample.
- **Ablation without a causal claim.** Removing imbalance inputs yields boosted
  development macro F1 0.461691, versus 0.460571 with all inputs. The observed
  development advantage cannot be uniquely attributed to imbalance.
- **Reproduction with an audit trail.** Source/excerpt, normalized-state,
  sample, split, configuration, dependency and code hashes make the experiment
  reviewable. Verification checks inputs without fitting; reproduction repeats
  frozen decisions rather than starting a new search.

## A concrete defect caught before empirical evaluation

Adversarial review identified a holdout date-shift defect: a date that lost all
usable labeled samples could cause observed-sample-based splitting to select a
different final block. The fix requires the exact predeclared dates for both
the primary and alternate horizon, failing before fitting when coverage is
missing. Regression tests now exercise the missing-date case. No real model
score was inspected to choose that repair. This illustrates why a chronological
split alone is not sufficient without checking which dates actually survived
the feature/label pipeline.

The local holdout registry also binds the contract, scientific source,
dependency lock and environment. It guards ordinary workflow mistakes; it is
not a tamper-proof global enforcement system.

## Limits that matter

The unchanged class dominates development targets, approximately 93.2-98.2%
per date, and becomes 79.4% and 58.4% on the final dates. I can describe this
observed composition shift without claiming to know its cause. Directional
recall remains limited. Seven development date units and two final date units
do not establish generalization across market regimes; correlated updates are
not independent trials. Date-bootstrap intervals are exploratory because
exchangeability is uncertain and expanding folds share training data.

These are vendor-reconstructed snapshots, including upstream crossed-level
filtering, rather than my own reconstruction from raw exchange messages.
There is no explicit disconnect marker in this CSV, so a thirty-second gap
rule cannot certify complete feed continuity. A ten-state horizon varies in
elapsed time and is not an assumed executable latency budget.

No fees, slippage, queue position, fills or capital constraints are modeled.
There is no P&L claim, live trading integration or demonstration that the
features could be acted on economically. The
[provider terms](https://docs.tardis.dev/legal/terms-of-service) also restrict
redistribution: the repository contains permitted aggregates and metadata,
not historical rows, per-event predictions or fitted model weights.

## A defensible next step

I would predeclare broader intraday observations, clearer coverage requirements
and a new untouched holdout before changing models. If the research question
became trading profitability, I would separately specify available information,
latency, actions, execution assumptions and costs. I would not reuse the current
final dates to choose a winning configuration.

Clean-checkout reproduction, final review and publication status should be
described only using their completed evidence in
[P6](phase-handoffs/P6.md); this interview note does not assert those pending
checks have already passed.
