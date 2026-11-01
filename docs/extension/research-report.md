# Broader spot study and hypothetical execution

**Research status: exploratory; the predeclared planning precision gate was not met.**

The implemented platform is assessed separately from predictive decisiveness and hypothetical profitability. A narrow conditional interval does not waive the failed planning gate. The original 2020 Deribit result is preserved unchanged.

## Data and frozen information boundary

The new study uses Bitstamp BTCUSD spot on 48 first-of-month dates in 2021–2024. Eight fixed 15-minute windows spread across each UTC day provide 96 selected hours in total. Complete daily gzip sources contain 7,470,173 records; normalization retained all 631,463 selected observations with zero exclusions. All 384 windows pass the predeclared availability gate. One observed gap creates an additional segment, for 385 independent segments.

These observations are sparse calendar sampling, not uninterrupted four-year coverage or proof of feed completeness. Sizes are BTC, prices USD per BTC. Research cent/base-quantity grids agree with selected source values; current exchange metadata is not a point-in-time certificate of every historical trading rule.

2021 supplies initial training, 2022 supplies twelve development evaluation dates, and 2023–2024 supplies twenty-four final dates. The frozen prequential schedule refits before each final date using strictly earlier eligible labels, including past final dates when available. Settings never change from intermediate final results. Label-end purging, train-only preprocessing and timestamp/source-order audits apply to every fit.

The primary three-class target is the exact midpoint change ten valid states later within the same segment: up above one cent, down below minus one cent, unchanged otherwise. Exact integer half-ticks determine labels. Execution signals cover every causal feature-valid observation after warm-up, including the last ten observations without available forward labels.

## Predictive comparisons

The primary comparison is full-book logistic minus history-only logistic. The latter uses only past midpoint changes and volatility. Boosted minus book-logistic is secondary. Macro F1 always uses the fixed three classes. Both development and final values below average per-date scores; they are not pooled F1.

| Model | Development date-mean macro F1 | Final date-mean macro F1 | Final balanced accuracy |
| --- | ---: | ---: | ---: |
| majority | 0.204842 | 0.177399 | 0.333333 |
| history_logistic | 0.296870 | 0.405650 | 0.428128 |
| book_logistic | 0.347730 | 0.458722 | 0.459688 |
| boosted | 0.372856 | 0.488190 | 0.485960 |

| Comparison | Final mean difference | Conditional 95% interval | Raw practical-effect classification |
| --- | ---: | --- | --- |
| Primary: book minus history | 0.053071 | [0.023520, 0.068959] | positive_practical_gain |
| Secondary: boosted minus book | 0.029468 | [0.017966, 0.044688] | positive_practical_gain |

The practical threshold was fixed at 0.01 macro F1. The paired non-circular moving-block bootstrap uses three adjacent observed dates, 2,000 resamples and a 95% percentile interval. Twenty-four final dates provide eight nonoverlapping block equivalents. Stationarity and appropriate dependence coverage are assumptions, not established properties; sparse dates and overlapping training histories may introduce dependence beyond three months. Secondary and adaptation results remain exploratory.

Book minus history is positive on 22 of 24 final dates, with date differences
from -0.081521 to +0.268961. Mean class-F1 changes decompose the macro gain into
down +0.043858, unchanged +0.025549 and up -0.016336 after dividing each class
change by three. Down-class improvement contributes more than unchanged-class
detection; up-class F1 declines. This is an arithmetic decomposition, not a
causal explanation. The long/flat execution policy acts on up predictions, so
its purpose and outcome must not be inferred from overall macro F1 alone.

Final unchanged-label shares range from 6.9% to 74.9%. Non-circular moving blocks
also sample edge dates less often: with the large early-period gains, the
expected resampled primary mean is approximately 0.044418 versus the observed
unweighted mean 0.053071. This is behavior of the frozen method, not a reason to
replace it after seeing outcomes. It reinforces the heterogeneity, stationarity
and exploratory-inference limitations.

## Why the research claim remains qualified

Development book-minus-history gain was +0.050860, positive on all twelve dates, but heterogeneous. The four three-month means were approximately 0.007193, 0.009305, 0.037665 and 0.149278. October–December supplied most of the aggregate gain alongside a changing target composition; that observation does not identify a causal explanation.

Development-only planning projected a 0.046474 interval half-width for the fixed final coverage, exceeding the 0.015 target. The extrapolation of 77 blocks / 231 dates comes from only four development blocks and is highly uncertain. It is a planning estimate, not a certified sample-size requirement. Dates, models, margins and scenarios were retained, and final evaluation proceeded explicitly as exploratory. Neither a favorable conditional final interval nor software test success restores confirmatory status.

Final achieved interval half-width: 0.022720; precision_target_met=False; research_decisiveness_met=False; claim_status=exploratory_precision_unmet.

## Hypothetical execution

Every scenario uses the same fixed prediction-to-long/flat policy, an unlevered maximum of 0.001 BTC and independent segment starting cash of 10,000 USD. A cap on consecutive long decisions is a signal rule, not a guarantee of executed holding time. Marketable IOC attempts occur only on later observed books. One pending order is retained; later signals while pending are recorded as ignored. Displayed depth, affordable fee-inclusive quantity, adverse tick rounding, quote age and clock-skew rejection are explicit.

The fee/slippage/action-delay settings are research scenarios, not verified historical account tiers or measured inference latency. No passive queue position, market-impact feedback or exchange-realistic fills are claimed. The `zero_cost_diagnostic` has zero added fees and slippage and zero action delay; it still buys at observed ask and sells or marks at bid, so spread-crossing costs remain. All declared scenarios are reported without selecting the most favorable one.

| Scenario | Signal | Net marked P&L USD | Fees USD | Level fills | Completed round trips | Turnover USD | Worst segment drawdown USD | Unresolved segments |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| zero_cost_diagnostic | no_trade | 0.00 | 0.00 | 0 | 0 | 0.00 | 0.00 | 0 |
| zero_cost_diagnostic | majority | -149.09 | 0.00 | 63195 | 30217 | 3,041,872.65 | 6.65 | 176 |
| zero_cost_diagnostic | history_logistic | -122.29 | 0.00 | 50377 | 24063 | 2,422,676.87 | 4.86 | 119 |
| zero_cost_diagnostic | book_logistic | -209.00 | 0.00 | 69085 | 33031 | 3,468,653.02 | 10.94 | 52 |
| zero_cost_diagnostic | boosted | -244.13 | 0.00 | 83929 | 40281 | 4,149,186.49 | 12.69 | 52 |
| optimistic | no_trade | 0.00 | 0.00 | 0 | 0 | 0.00 | 0.00 | 0 |
| optimistic | majority | -1,670.03 | 1,520.94 | 63195 | 30217 | 3,041,872.65 | 23.51 | 176 |
| optimistic | history_logistic | -1,333.63 | 1,211.34 | 50377 | 24063 | 2,422,676.87 | 24.32 | 119 |
| optimistic | book_logistic | -1,943.33 | 1,734.33 | 69085 | 33031 | 3,468,653.02 | 40.77 | 52 |
| optimistic | boosted | -2,318.72 | 2,074.59 | 83929 | 40281 | 4,149,186.49 | 47.61 | 52 |
| base | no_trade | 0.00 | 0.00 | 0 | 0 | 0.00 | 0.00 | 0 |
| base | majority | -3,495.46 | 3,041.87 | 63195 | 30217 | 3,041,873.46 | 50.53 | 176 |
| base | history_logistic | -2,787.48 | 2,422.68 | 50377 | 24063 | 2,422,677.39 | 52.15 | 119 |
| base | book_logistic | -4,024.85 | 3,468.65 | 69085 | 33031 | 3,468,653.30 | 77.96 | 52 |
| base | boosted | -4,808.63 | 4,149.19 | 83929 | 40281 | 4,149,186.77 | 91.55 | 52 |
| stress | no_trade | 0.00 | 0.00 | 0 | 0 | 0.00 | 0.00 | 0 |
| stress | majority | -9,261.05 | 7,593.42 | 63082 | 30192 | 3,037,367.32 | 136.12 | 140 |
| stress | history_logistic | -6,597.59 | 5,407.23 | 45676 | 21815 | 2,162,891.52 | 121.00 | 92 |
| stress | book_logistic | -7,034.24 | 5,754.86 | 47255 | 22579 | 2,301,945.55 | 113.85 | 55 |
| stress | boosted | -7,778.76 | 6,363.76 | 53415 | 25574 | 2,545,505.46 | 132.23 | 56 |

P&L sums independent equal-capital segment trials. Open inventory is marked at the final observed best bid and disclosed as unresolved; no unseen terminal liquidation, exit fee or gap return is fabricated. Gross P&L adds fees back to net marked P&L while retaining adverse execution effects. Full aggregates retain realized/unrealized components, adverse slippage, order rejections and exposure. There is no continuously investable equity curve, compounded annual return or annualized Sharpe claim.

Every trading policy has negative marked P&L in every declared scenario;
no-trade is zero. Losses already occur without added fees or slippage, where
spread crossing and later-observation execution still apply. Additional costs
increase losses, but this is not a one-factor causal sensitivity experiment:
the scenario bundles also change delay and therefore execution timing, ignored
pending signals and turnover. No conclusion about passive market-making fills,
an optimized policy or real profitability follows from this fixed taker policy.

## External method and engineering evidence

The development-only next-midpoint-change queue-imbalance study is a methodological adaptation of Gould and Bonart, not numerical reproduction of their equity results. It uses causal first observations of constant-midpoint runs, chronological fitting and a different instrument/data/sampling scheme. Empirical training-frequency and constant-half probability baselines accompany Brier score, log loss, AUC and binary confusion counts. Differences and aggregate measurements are in the reference JSON.

Across twelve development dates and 68,471 binary targets, queue-logistic
date-mean Brier score is 0.248882, log loss 0.690908 and AUC 0.543522. The
training-frequency baseline gives Brier 0.249979 and log loss 0.693105; the
constant-half null gives Brier 0.25, log loss ln(2) and AUC 0.5. These are modest
development-only comparisons, not a reproduced published numerical result or
a selected final-holdout trading model.

The original study code and dependency lock remain unchanged. The original reference can be reproduced at revision 2ebb818. Extension provenance binds actual source/build/runtime bytes, fixed configuration, full-source and selected-excerpt checksums, normalized observations, fold audits, signal hashes and detailed simulation hashes. Repeated frozen executions are reproduction checks, not additional independent evidence or opportunities for selection.

Repeated synthetic benchmarks measure native peak process memory and engine wall time, including exact frame/batch ledger parity. At 50,000 observations the recorded median engine times were 5.40 seconds for a frame and 5.69 seconds for batches, with peak process memory about 255 MiB. Input generation/import time is excluded from engine time but included in peak process memory. Retained signals/ledgers still grow with event count; fully out-of-core ML and exchange latency are not claimed. No bespoke C++ acceleration is justified by these measurements.

See [validation](../../reports/extension/validation.json), [review evidence](reviews/final.json), [milestone index](milestones.md), [source evidence](data-source-evidence.md) and [applicant guide](applicant-guide.md). Historical records, signals, orders, fills, detailed ledgers and fitted assets remain local. Reviewers acquire their own data under the applicable provider terms.

## Next empirical decision

A confirmatory claim needs a separately predeclared study with feasible representative observations, a credible dependence/precision plan and a fresh reserved evaluation. The already-consumed final dates cannot be relabeled untouched or used to select a winner. Broader data access and the research question should be settled before more model complexity. This completed bounded experiment must retain its explicit precision limitation.
