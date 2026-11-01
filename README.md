# Market Microstructure ML & Validation Pipeline

A reproducible Python research pipeline for one question: do order-book
measurements help predict a short-horizon mid-price move beyond a simple
majority rule and logistic regression?

The project combines auditable historical-data ingestion, causal features,
chronological evaluation, explicit leakage checks and portable research reports.
It supports honest positive, negative and inconclusive findings. Classification
scores alone do not establish trading profitability.

## Start here

1. Install the locked Python environment.
2. Run the synthetic demonstration to learn the workflow without obtaining data.
3. Fetch the exact bounded historical excerpts, then run or reproduce the study.
4. Open the generated HTML report directly in a browser. No server is required.

The frozen reference experiment is
[reports/reference/experiment.json](reports/reference/experiment.json), with its
[readable HTML report](reports/reference/report.html). Consult those artifacts
for measured results, warnings and the exact code/config/data fingerprints.
The [research contract](docs/decisions/001-predeclared-research-contract.md)
defines choices made before model scores were inspected.

## Install and try the workflow

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and clone
this repository. The project pins Python 3.12.15 and exact dependencies in uv.lock.
Initial environment installation requires access to the Python/package sources.

    uv sync --frozen --extra dev
    uv run python -m pytest -p no:cacheprovider
    uv run microstructure demo --output artifacts/demo

The demo uses independently generated **synthetic** order books and labels its
reports accordingly. It does not download historical data and provides no
empirical market evidence. After installation, the test suite is fully offline.

On Windows hosts where the default pytest temporary directory is restricted,
use an accessible, disposable project-local directory:

    uv run python -m pytest -p no:cacheprovider --basetemp=artifacts/pytest-local

Pytest owns and may replace the directory supplied to --basetemp; do not point
it at a directory containing work you want to keep.

## Obtain the pinned historical data

Review the [data instructions](data/README.md) and
[source/license evidence](docs/data-source-evidence.md) first.
Data acquisition is explicit; analysis commands consume local files.

    uv run microstructure fetch --config configs/research.json --raw-dir data/raw --source-lock data/sources.lock.json

The source is Tardis.dev's vendor-reconstructed top-five snapshots for Deribit
BTC-PERPETUAL. The study uses the first 20,000 complete source records on the
first day of each month in 2020. Each requested compressed range is capped at
512 KiB; the total project ceiling is 24 MiB. No subscription, API key, paid
endpoint or live exchange connection is required for these documented samples.

These are **twelve short opening windows**, approximately 227–1,830 seconds
each, rather than complete trading days. The reference acquisition retained
240,000 records. The local compressed objects are partial gzip prefixes, so
whole-source gzip CRC/MD5 is not claimed. Reproduction checks the pinned local
excerpt checksums and selection contract in
[data/sources.lock.json](data/sources.lock.json).

Raw and sampled records remain local and ignored. Provider terms also restrict
sharing trained models. This repository contains source, synthetic test
fixtures, metadata and aggregate research artifacts; it does not distribute raw
data, processed rows, per-event predictions or fitted model weights.

## Run, verify and reproduce

Run the reviewed contract against the local, checksum-verified sources:

    uv run microstructure run --config configs/research.json --raw-dir data/raw --output reports/runs

Each run has a stable identity and records its configuration, source hashes,
code/package fingerprints, feature names, fold assignments, metrics and warnings.
Open reports/runs/&lt;experiment-id&gt;/report.html in a browser; the command
prints the actual artifact location. An existing immutable completed run is
reused rather than silently overwritten.

Check the reference and local inputs without fitting models:

    uv run microstructure verify --reference reports/reference/experiment.json --raw-dir data/raw

Re-execute the frozen reference and compare its numerical results:

    uv run microstructure reproduce --reference reports/reference/experiment.json --raw-dir data/raw --output artifacts/reproduction

Reproduction repeats frozen decisions; it is not a new tuning exercise. A
different source, horizon, target, feature set or split contract requires a
dated reviewed decision and, where necessary, a new untouched holdout.

## What is measured?

- **Target:** the mid-price ten later book states within the same valid segment.
  A move strictly greater than +0.5 USD is up, strictly below -0.5 USD is down,
  and all remaining moves are unchanged. This is an event-count horizon, not
  a fixed number of seconds.
- **Inputs:** ten modest spread, imbalance, depth and trailing-change features.
  Inputs stop at local receipt time; original row order resolves tied times.
  [The data dictionary](docs/data-dictionary.md) specifies formulas and units.
- **Models:** a training-majority baseline, logistic regression and
  limited-complexity boosted trees. Preprocessing is fitted inside each
  training fold.
- **Development:** expanding chronological training, starting with January–March,
  followed by seven one-date validation folds, April–October.
- **Final evaluation:** November and December are excluded from selection.
  Training samples whose forward labels touch an evaluation boundary are purged.
- **Scores:** macro F1 and balanced accuracy on a 0–1 scale, higher is better;
  per-class counts/precision/recall and confusion matrices provide context.
  Date-level variability is reported rather than assuming every update is
  an independent observation.

The predeclared robustness checks remove imbalance features and examine a
20-state horizon on development data only. They do not select settings from
final-holdout performance.

## Measured result

The frozen historical study is **inconclusive about improvement beyond logistic
regression**. Boosted trees lead on the seven development dates, but logistic
regression wins on each of the two final dates and on their pooled predictions.

| Model | Development date-mean macro F1 | Final pooled macro F1 |
| --- | ---: | ---: |
| Training-majority rule | 0.326678 | 0.272051 |
| Logistic regression | 0.434971 | **0.497672** |
| Boosted trees | **0.460571** | 0.457272 |

The primary pipeline produces 239,640 labeled samples from twelve short opening
excerpts. Correlated states are not independent trials. The development
boosted-minus-logistic difference is +0.025600, with a descriptive 95% paired
date-bootstrap interval [+0.015060, +0.039279] based on only seven date units.
The final pooled difference reverses to -0.040401. Removing imbalance inputs
does not reduce the boosted development score, so this study does not isolate
imbalance as the cause of its development advantage. There is no profitability
claim or modeled execution/cost strategy.

See the [research report](docs/research-report.md) for per-date results,
class imbalance, robustness checks, fingerprints and uncertainty limits, and
[interview notes](docs/interview-notes.md) for a concise discussion of the work.

## Scope and evidence

The work follows P0 source feasibility, P1 ingestion, P2 causal features,
P3 baseline experiments, P4 temporal validation, P5 robustness and P6
reproducibility/review. Phase evidence is under
[docs/phase-handoffs](docs/phase-handoffs), and
[limitations](docs/limitations.md) explain the boundaries on interpretation.

The final clean checkout passes 226 tests and reproduces the reference metrics
exactly. The [validation record](reports/validation.json) and
[P6 handoff](docs/phase-handoffs/P6.md) distinguish the initial frozen study,
report-format corrections and unchanged reproduction runs.

The reviewed synthetic HTML proposal is a design reference, separate from
measured research outputs. The implementation's core interface is the offline
CLI and generated report artifacts.
