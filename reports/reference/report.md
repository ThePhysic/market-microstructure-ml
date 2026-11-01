# Market Microstructure ML & Validation Pipeline

**REAL HISTORICAL DATA — BOUNDED EXCERPTS**

Experiment: exp-13c5f0856ef3a87a  
Created: 2026-11-01T06:40:40.462477+00:00

## Purpose and interpretation

Test whether causal order-book inputs improve short-horizon mid-price direction predictions beyond a majority rule and a linear baseline. A book state is one snapshot of waiting orders. Mid-price is halfway between the best buy and sell prices. The unchanged class includes moves inside the frozen no-change threshold, not only identical prices. This is prediction research, not evidence of executable or profitable trading.

Observed dates: 2020-01-01, 2020-02-01, 2020-03-01, 2020-04-01, 2020-05-01, 2020-06-01, 2020-07-01, 2020-08-01, 2020-09-01, 2020-10-01, 2020-11-01, 2020-12-01. Eligible labeled samples: 239,640. Development evaluation dates: 7. Final holdout dates: 2020-11-01, 2020-12-01.

The real-data design uses noncontiguous opening excerpts from month-start files, not full trading days or a continuous backtest. Correlated updates are not independent observations.

## Model comparison

Both metrics range from 0 to 1; higher is better. Macro F1 assigns equal weight to the three declared classes. Balanced accuracy averages recalls of true classes present in each evaluation period; missing classes are explicitly warned about. Development scores are date-level means; final scores summarize the reserved later-date holdout.

| Method | Development macro F1 | Across-date SD | Development balanced accuracy | Final macro F1 | Final balanced accuracy | Final support |
| --- | --- | --- | --- | --- | --- | --- |
| Simple majority baseline | 0.327 | 0.003 | 0.333 | 0.272 | 0.333 | 39,940 |
| Logistic regression | 0.435 | 0.037 | 0.396 | 0.498 | 0.480 | 39,940 |
| Small boosted trees | 0.461 | 0.047 | 0.413 | 0.457 | 0.442 | 39,940 |

## Temporal evaluation

Expanding training folds use earlier observed dates and evaluate on later dates. Label-overlap purging removes training targets that reach the evaluation boundary. Final holdout dates are excluded from selection.

| Split | Purpose | Training dates | Evaluation dates | Train count | Evaluation count | Purged |
| --- | --- | --- | --- | --- | --- | --- |
| walk\_forward\_01 | Development | 2020-01-01, 2020-02-01, 2020-03-01 | 2020-04-01 | 59,910 | 19,970 | 0 |
| walk\_forward\_02 | Development | 2020-01-01, 2020-02-01, 2020-03-01, 2020-04-01 | 2020-05-01 | 79,880 | 19,970 | 0 |
| walk\_forward\_03 | Development | 2020-01-01, 2020-02-01, 2020-03-01, 2020-04-01, 2020-05-01 | 2020-06-01 | 99,850 | 19,970 | 0 |
| walk\_forward\_04 | Development | 2020-01-01, 2020-02-01, 2020-03-01, 2020-04-01, 2020-05-01, 2020-06-01 | 2020-07-01 | 119,820 | 19,970 | 0 |
| walk\_forward\_05 | Development | 2020-01-01, 2020-02-01, 2020-03-01, 2020-04-01, 2020-05-01, 2020-06-01, 2020-07-01 | 2020-08-01 | 139,790 | 19,970 | 0 |
| walk\_forward\_06 | Development | 2020-01-01, 2020-02-01, 2020-03-01, 2020-04-01, 2020-05-01, 2020-06-01, 2020-07-01, 2020-08-01 | 2020-09-01 | 159,760 | 19,970 | 0 |
| walk\_forward\_07 | Development | 2020-01-01, 2020-02-01, 2020-03-01, 2020-04-01, 2020-05-01, 2020-06-01, 2020-07-01, 2020-08-01, 2020-09-01 | 2020-10-01 | 179,730 | 19,970 | 0 |
| final\_holdout | Final holdout | 2020-01-01, 2020-02-01, 2020-03-01, 2020-04-01, 2020-05-01, 2020-06-01, 2020-07-01, 2020-08-01, 2020-09-01, 2020-10-01 | 2020-11-01, 2020-12-01 | 199,700 | 39,940 | 0 |

## Date-level uncertainty

Paired bootstrap intervals resample whole date/session score differences, not order-book rows. They assume exchangeable independent evaluation dates and remain exploratory; fewer than three units gives no interval. Overlapping training folds do not supply extra independent evidence.

| Comparison A minus B | Dates | Mean macro F1 difference | Exploratory macro F1 interval | Status |
| --- | --- | --- | --- | --- |
| boosted minus logistic | 7 | 0.026 | 95% \[0.015, 0.039\] | exploratory |
| boosted minus majority | 7 | 0.134 | 95% \[0.102, 0.166\] | exploratory |

## Predeclared development-only robustness

These sensitivity checks do not retune against the final holdout.

| Change | Method | Development macro F1 | Development balanced accuracy |
| --- | --- | --- | --- |
| remove imbalance | Simple majority baseline | 0.327 | 0.333 |
| remove imbalance | Logistic regression | 0.432 | 0.395 |
| remove imbalance | Small boosted trees | 0.462 | 0.414 |
| horizon 20 | Simple majority baseline | 0.320 | 0.333 |
| horizon 20 | Logistic regression | 0.398 | 0.377 |
| horizon 20 | Small boosted trees | 0.411 | 0.384 |

## Final class-wise evaluation

| Method | Class | Precision | Recall | F1 | Support |
| --- | --- | --- | --- | --- | --- |
| Simple majority baseline | down | 0.000 | 0.000 | 0.000 | 6,465 |
| Simple majority baseline | unchanged | 0.689 | 1.000 | 0.816 | 27,535 |
| Simple majority baseline | up | 0.000 | 0.000 | 0.000 | 5,940 |
| Logistic regression | down | 0.483 | 0.210 | 0.292 | 6,465 |
| Logistic regression | unchanged | 0.771 | 0.919 | 0.838 | 27,535 |
| Logistic regression | up | 0.429 | 0.313 | 0.362 | 5,940 |
| Small boosted trees | down | 0.473 | 0.228 | 0.308 | 6,465 |
| Small boosted trees | unchanged | 0.746 | 0.944 | 0.833 | 27,535 |
| Small boosted trees | up | 0.461 | 0.154 | 0.230 | 5,940 |

## Aggregate quality

Only aggregate diagnostics are displayed. Vendor-reconstructed snapshots do not establish that this project reconstructed exchange books.

| Field | Value |
| --- | --- |
| ingestion.schema\_version | 1 |
| ingestion.total\_rows | 240000 |
| ingestion.retained\_rows | 240000 |
| ingestion.excluded\_rows | 0 |
| ingestion.counts.total\_rows | 240000 |
| ingestion.counts.retained\_rows | 240000 |
| ingestion.counts.tied\_receive\_timestamps | 54 |
| ingestion.segments | 12 |
| ingestion.timestamp\_unit | microseconds since Unix epoch UTC |
| ingestion.availability\_policy | local receipt timestamp; original source position breaks ties |
| ingestion.gap\_seconds | 30.0 |
| features.input\_rows | 240000 |
| features.retained\_samples | 239640 |
| features.excluded\_samples | 360 |
| features.segments | 12 |
| features.horizon\_events | 10 |
| features.threshold\_ticks | 1.0 |
| features.tick\_size | 0.5 |
| features.trailing\_window | 20 |
| features.zero\_l1\_denominator\_states | 0 |
| features.zero\_depth\_denominator\_states | 0 |
| features.zero\_denominator\_policy | Use zero imbalance when both opposing sizes/depths are zero. |
| features.information\_time | receive\_time\_us; ties retain ascending source\_order |
| features.volatility\_definition | Population std\(ddof=0\) of the last trailing\_window one-state mid-price changes in ticks. |

## Research conclusion

### Inconclusive evidence of improvement beyond the linear comparison

The frozen comparisons do not jointly support a repeatable improvement beyond logistic regression. Any observed advantage is limited by variation across dates, a small independent sample, or missing-class coverage.

**Next test:** Predeclare a new set of broader intraday dates and a new untouched holdout before further model selection.

## Warnings

- Only noncontiguous monthly opening excerpts are observed; these are not full trading days.
- Millions of correlated rows are not millions of independent experimental observations.
- Date bootstrap intervals are exploratory; overlapping training windows and few dates limit inference.
- Vendor snapshots were reconstructed and may have crossed levels removed upstream.
- CSV disconnect events are unavailable; a 30-second gap rule is only a discontinuity heuristic.
- Order sizes are vendor-native USD notional for this inverse instrument, not BTC quantities.
- Prediction scores do not establish executable, fee-adjusted trading profitability.
- No fitted models, row-level predictions or historical records are redistributed.
- Exploratory session/date bootstrap: assumes exchangeable independent evaluation units; overlapping training folds do not create independent observations.
- Fewer than 10 session/date units; the percentile interval may be unstable and must not be read as proof of generalization.
- primary/walk\_forward\_01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- primary/walk\_forward\_01/2020-04-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- primary/walk\_forward\_02/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- primary/walk\_forward\_02/2020-05-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- primary/walk\_forward\_03/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- primary/walk\_forward\_03/2020-06-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- primary/walk\_forward\_04/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- primary/walk\_forward\_04/2020-07-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- primary/walk\_forward\_05/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- primary/walk\_forward\_05/2020-08-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- primary/walk\_forward\_06/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- primary/walk\_forward\_06/2020-09-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- primary/walk\_forward\_07/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- primary/walk\_forward\_07/2020-10-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- remove\_imbalance/walk\_forward\_01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- remove\_imbalance/walk\_forward\_01/2020-04-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- remove\_imbalance/walk\_forward\_02/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- remove\_imbalance/walk\_forward\_02/2020-05-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- remove\_imbalance/walk\_forward\_03/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- remove\_imbalance/walk\_forward\_03/2020-06-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- remove\_imbalance/walk\_forward\_04/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- remove\_imbalance/walk\_forward\_04/2020-07-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- remove\_imbalance/walk\_forward\_05/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- remove\_imbalance/walk\_forward\_05/2020-08-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- remove\_imbalance/walk\_forward\_06/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- remove\_imbalance/walk\_forward\_06/2020-09-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- remove\_imbalance/walk\_forward\_07/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- remove\_imbalance/walk\_forward\_07/2020-10-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- horizon\_20/walk\_forward\_01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- horizon\_20/walk\_forward\_01/2020-04-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- horizon\_20/walk\_forward\_02/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- horizon\_20/walk\_forward\_02/2020-05-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- horizon\_20/walk\_forward\_03/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- horizon\_20/walk\_forward\_03/2020-06-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- horizon\_20/walk\_forward\_04/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- horizon\_20/walk\_forward\_04/2020-07-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- horizon\_20/walk\_forward\_05/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- horizon\_20/walk\_forward\_05/2020-08-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- horizon\_20/walk\_forward\_06/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- horizon\_20/walk\_forward\_06/2020-09-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- horizon\_20/walk\_forward\_07/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- horizon\_20/walk\_forward\_07/2020-10-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- final\_holdout/final\_holdout/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- final\_holdout/final\_holdout/2020-11-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- final\_holdout/final\_holdout/2020-12-01/majority: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- Simple majority baseline: No predictions for classes: -1, 1. Undefined precision/F1 components use zero.
- boosted\_vs\_logistic: Exploratory session/date bootstrap: assumes exchangeable independent evaluation units; overlapping training folds do not create independent observations.
- boosted\_vs\_logistic: Fewer than 10 session/date units; the percentile interval may be unstable and must not be read as proof of generalization.
- boosted\_vs\_majority: Exploratory session/date bootstrap: assumes exchangeable independent evaluation units; overlapping training folds do not create independent observations.
- boosted\_vs\_majority: Fewer than 10 session/date units; the percentile interval may be unstable and must not be read as proof of generalization.

## Reproduction

```text
uv sync --frozen --extra dev
uv run microstructure fetch --config configs/research.json --raw-dir data/raw --source-lock data/sources.lock.json
uv run microstructure run --config configs/research.json --raw-dir data/raw --output reports/runs
uv run microstructure reproduce --reference reports/reference/experiment.json --raw-dir data/raw --output artifacts/reproduction
```

Acquisition is opt-in and bounded. Raw or sampled historical records, row predictions and trained weights are excluded from the repository. Keep report.html, report.md and experiment.json together.

## Source URLs, excerpt hashes and byte sizes

| Date | Exact source URL | Retained rows | Compressed bytes received | Excerpt bytes | Excerpt SHA-256 | Compressed-prefix SHA-256 |
| --- | --- | --- | --- | --- | --- | --- |
| 2020-01-01 | https://datasets.tardis.dev/v1/deribit/book\_snapshot\_5/2020/01/01/BTC-PERPETUAL.csv.gz | 20,000 | 262,144 | 3,439,565 | bc3b40f249060bda9411402bd2e704a3e861d5cfc691b3f3500ec71ebc4768c0 | f9f6c3a666eeeeb1c1b1695ad1170a8d39b9a8cfb0cb47343bd51a5f719d80d2 |
| 2020-02-01 | https://datasets.tardis.dev/v1/deribit/book\_snapshot\_5/2020/02/01/BTC-PERPETUAL.csv.gz | 20,000 | 262,144 | 3,368,696 | 77daf543d84f82a913dc1b96dfe16d325acfda5fea148d2c7136679916a7373e | 67ad21c12bc76762cd910c5ec3bcfbe9c04d2a7b15648a847d74b42ef0c22a66 |
| 2020-03-01 | https://datasets.tardis.dev/v1/deribit/book\_snapshot\_5/2020/03/01/BTC-PERPETUAL.csv.gz | 20,000 | 262,144 | 3,364,177 | c61f294010cf0e47a88ba61ab5f0999423f2dcff51cabb94931a800a2ed1009c | f8fd5d6cc3d3fbace8bebd1fed0a82bfb31832f253aaf9bb38b54bd3a76a3205 |
| 2020-04-01 | https://datasets.tardis.dev/v1/deribit/book\_snapshot\_5/2020/04/01/BTC-PERPETUAL.csv.gz | 20,000 | 262,144 | 3,392,083 | c433c782937192cf921a6f07b759fe7af46aee3af467843bc4a90e8c14a9598c | 563770548fa58aba2dca62d3a2387ec7fee4cdc095f8abf86022e1c1bacc758a |
| 2020-05-01 | https://datasets.tardis.dev/v1/deribit/book\_snapshot\_5/2020/05/01/BTC-PERPETUAL.csv.gz | 20,000 | 262,144 | 3,343,265 | 45a882f68fcb1024d8e6d9a771d88f344afdb6806a2f38fa9e0906d66216df1a | 357afd13193cd67c714b3985df0e3c9d2325be2641b0d506c14620adb1c332fd |
| 2020-06-01 | https://datasets.tardis.dev/v1/deribit/book\_snapshot\_5/2020/06/01/BTC-PERPETUAL.csv.gz | 20,000 | 262,144 | 3,359,647 | ca493f79f62df095f5b740de036aa714cbc685dc17dba1f678090ececebd4d72 | 9a4bd7d9f0af243d0fb594d03212aba157149b14156825e80f7c2956effddd01 |
| 2020-07-01 | https://datasets.tardis.dev/v1/deribit/book\_snapshot\_5/2020/07/01/BTC-PERPETUAL.csv.gz | 20,000 | 262,144 | 3,400,181 | e5cf751bffef6f5fcf125dd5a903be272829c848bb930b2be4c14b3d8975f66a | 1d23cd0901c337c88ff4096041ed7bafeb83797e48d999832f9bc48472225728 |
| 2020-08-01 | https://datasets.tardis.dev/v1/deribit/book\_snapshot\_5/2020/08/01/BTC-PERPETUAL.csv.gz | 20,000 | 262,144 | 3,593,337 | 973f501e7dc3e77710181b4dff3313140e0538de1f74172e79696369cc6d3b40 | 8e31a02cacb131ea8d8af6d3a1671839e43ad774be24483253b5d0725e72f0b9 |
| 2020-09-01 | https://datasets.tardis.dev/v1/deribit/book\_snapshot\_5/2020/09/01/BTC-PERPETUAL.csv.gz | 20,000 | 262,144 | 3,595,975 | ac68993a914f14e4d00ecf555fd23fd93266dfecfea3c081ff97a862eb395758 | 22d61d3a37bbc8804eeb395c97f8ec87d47820ac9b1fffc462a656aabfc243d1 |
| 2020-10-01 | https://datasets.tardis.dev/v1/deribit/book\_snapshot\_5/2020/10/01/BTC-PERPETUAL.csv.gz | 20,000 | 262,144 | 3,569,483 | ab069d54c1784e06dcc3365a70346b122aa13dfd04a1b12338176635832792ba | 0385cc62a8e16f54249bfb25ff0be5e747a38127140dd5b0541a08549fdb496e |
| 2020-11-01 | https://datasets.tardis.dev/v1/deribit/book\_snapshot\_5/2020/11/01/BTC-PERPETUAL.csv.gz | 20,000 | 262,144 | 3,489,820 | 0a19d76e829a8ed9edae86a2197e815e2352208831e6d4075bd1f3803240a62e | 0150ed5420bb48a8a0c966f7bdcc671406ce46e0b4e8673d82eed1fad1115a25 |
| 2020-12-01 | https://datasets.tardis.dev/v1/deribit/book\_snapshot\_5/2020/12/01/BTC-PERPETUAL.csv.gz | 20,000 | 327,680 | 3,490,158 | bc6a4a8d20c6cc70ef2e4b893cc0afc1fe5a4a82e03e754b1f4bf5bacd580150 | 7d686720d79b46a2d13ad3cdb738911a6796d10cb5d67b2c4f9c0f7932023cd8 |

Local prefix/excerpt hashes do not verify the complete vendor archive or whole-file gzip CRC. Obtain permitted data from the source; this report does not redistribute it.

## Recorded configuration and code fingerprints

```text
{
  "code": {
    "build_files": {
      ".python-version": "845c494b4a7e1a741db19fd42eda239d3ee03b65f08276008943349a3055c9cc",
      "pyproject.toml": "1a08561b036753e792af5ede22844b650152d23c4bd00598c948e5928f433432",
      "uv.lock": "7bf3f1be22ce1d335ba525f84200653c1e589242e6227255bdc4830638850b1c"
    },
    "build_sha256": "0a2e77fbe11f3a35f8b4206afa83a73e24ec8d6f548b6c2e0c363bed700ce8df",
    "dirty_tree": false,
    "provenance_note": "Source hashes identify executable code even when report/docs commits follow.",
    "revision": "9376319ce6db429b42d9ef0a670ab7e8994c4e23",
    "scientific_sha256": "102a74ceb1a60cbab08d167138ea954696e8bc1cedfde4bab21aff82471caa45",
    "source_files": {
      "src/market_microstructure/__init__.py": "2394a7f0c3da5e1455a2d4a3d37fd7df11197dcc3a6c5e6a2959aea7c5e4cc17",
      "src/market_microstructure/__main__.py": "935a1c1166b0c1ea35a82256345000bf2c73ded718d77773bc27a71ecce28f7d",
      "src/market_microstructure/acquisition.py": "11e2f4f893f8164ae998b903f8aa3b95d14f07c528571fe0bc989ed91515dbf9",
      "src/market_microstructure/cli.py": "4c72eb4b343be11c07ab1f2b5f39e9405b90513b445543d92a60c85384e5301d",
      "src/market_microstructure/config.py": "9004845bbd37199a3bf8ac5e64cd797cfa9bf2c3fdbd75b0164b3d4d9154bbc9",
      "src/market_microstructure/data.py": "3176a42d0884f2dfb23473f7252a8da641912d72241584b4fb4d634c0a66378c",
      "src/market_microstructure/evaluation.py": "85c4544a7b389df16490f2283c9fa355f4496ff0830e640b89c0cc2b2d550d36",
      "src/market_microstructure/experiment.py": "afd5d9e47959cf22a2b262716baddb6ff65a7ed1b1d79f4a0fe418486d658e29",
      "src/market_microstructure/features.py": "ef889426d15894b5cd3fc0c43269ab8835b4d21e9d47e6ac9a7065c3e6867192",
      "src/market_microstructure/manifests.py": "20f6f2be9c4f47210fbbca3916ad98847b5f4cdeb87460b00f0629f3d0f6c757",
      "src/market_microstructure/models.py": "79d822dd8a9c0af3e7c41e449a552d0c9aacebd6e4f4ae190f1445d2d88eaa0c",
      "src/market_microstructure/reporting.py": "8f8d7969c4f22faa6d575052889153181af5570c228d741d906101739881543d",
      "src/market_microstructure/splits.py": "0c3bcabf9bf44653abd3a3a2bb60d12f05a49d2aaa8a5e408b8aa0b1a5e7ab7a",
      "src/market_microstructure/synthetic.py": "82569f37b6ca0d54491866521ccb8472411501471ff38e798144e7add43bca1a"
    },
    "source_sha256": "d1cb5db3fb97bc2b63400e5e7ee07b4b3e5415501c00cdd36f53bc4147bfe316"
  },
  "config": {
    "data_type": "book_snapshot_5",
    "dates": [
      "2020-01-01",
      "2020-02-01",
      "2020-03-01",
      "2020-04-01",
      "2020-05-01",
      "2020-06-01",
      "2020-07-01",
      "2020-08-01",
      "2020-09-01",
      "2020-10-01",
      "2020-11-01",
      "2020-12-01"
    ],
    "exchange": "deribit",
    "gap_seconds": 30.0,
    "holdout_dates": 2,
    "horizon_events": 10,
    "max_compressed_bytes_per_date": 524288,
    "max_total_transfer_bytes": 25165824,
    "min_train_dates": 3,
    "robustness": {
      "alternate_horizon_events": 20,
      "development_only": true,
      "feature_ablation": "remove_imbalance"
    },
    "rows_per_date": 20000,
    "schema_version": 1,
    "seed": 42,
    "symbol": "BTC-PERPETUAL",
    "threshold_ticks": 1.0,
    "tick_size": 0.5,
    "trailing_window": 20
  },
  "feature_columns": [
    "spread_ticks",
    "level1_imbalance",
    "depth5_imbalance",
    "bid_depth5",
    "ask_depth5",
    "mid_change_1_ticks",
    "mid_change_window_ticks",
    "mid_volatility_ticks",
    "spread_change_1_ticks",
    "imbalance_change_1"
  ],
  "fingerprints": {
    "build": "0a2e77fbe11f3a35f8b4206afa83a73e24ec8d6f548b6c2e0c363bed700ce8df",
    "config": "5d4059c9419831831dee184cdd148c60c75425288006471f0c6523790d0aec63",
    "environment": "1671a55e4d9564cee99d041a218a77a0a732638946d2b9e32e5332dbdefe58a3",
    "feature_columns": "cdfe32dc77d4b494eed529d4dce7aa0284a3493f3f5a3928ac2e653ab3768736",
    "normalized_states": "d286808c5692bc3783be222f5dfad5e6807fa64f093d43c0dc3a34a00b9ad9c4",
    "raw_sources": "3db6d6e29797bbabbb79ea04f582a05f4993fb7a6192a2d4b654738534ed82ec",
    "samples": "2df42787c1c2e716b825e690233bd6b5e9a8f6e211ff07c4569ca2db74d166c5",
    "split_assignments": "458cce745c77994b2942a2ebf42b4fc8341c2bb7591af7629702de6712771e5f"
  }
}
```

The sibling experiment.json is the machine-readable aggregate evidence for all figures and tables above.
