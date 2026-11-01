# Market Microstructure ML & Validation Pipeline
## Codex Project Package — Version 1.0

**Prepared:** 2026-10-31 (America/Los_Angeles)  
**Project type:** Standalone Python quantitative ML research and data-engineering portfolio project  
**Intended audience:** Codex implementation agent, human reviewer, hiring managers  
**Status:** Specification only; no dataset selected or experiments conducted  
**Target scope:** P0–P6, seven reviewed phases; approximately 27–39 focused hours **only if data access and processing remain straightforward**  
**Primary career target:** HFT Architecture Junior Machine Learning Engineer; also applicable to quant research engineering, quant SWE, general ML engineering and data science

---

## 1. Executive brief

### Mission

Build a defensible, reproducible Python research pipeline that tests whether **causally available limit-order-book features** predict **short-horizon mid-price movement** better than simple baselines on historical, real market data. The project must demonstrate disciplined data checks, correct temporal evaluation, leakage detection, uncertainty reporting, and an honest decision about what the evidence does and does not support.

The primary artifact is **a reliable experimental process**, not a trading bot or a promise of profitable alpha.

### Research question

> For one explicitly identified exchange, instrument, dataset, and prediction horizon, do top-of-book imbalance, spread, book depth, and recent market-state changes provide repeatable out-of-sample information about a future mid-price move beyond naive and linear baselines, after temporal leakage controls?

### Intended portfolio claim — conditional, not prewritten as fact

An acceptable final resume bullet may eventually discuss the dataset size, data checks, models compared, walk-forward folds, and measured out-of-sample result. **Never invent or imply results until independently reproduced.** A negative or inconclusive finding is an acceptable scientifically honest outcome.

### Success criteria

1. A fresh reviewer can obtain or provide the exact pinned data and run the pipeline using documented commands.
2. Every raw record's origin, schema, time unit, transformation, and exclusion reason is traceable.
3. No feature uses data later than its declared decision timestamp; labels only use future data for targets.
4. Temporal train/validation/test partitions are chronological, disjoint in effective label information, and independently audited.
5. At least one trivial baseline, logistic regression, and a small tree-boosted model run under the same data and evaluation contract.
6. Experiments record code revision, config, data manifest/checksums, preprocessing, seed, fold assignments, metrics, and warnings.
7. The write-up reports performance variability, limitations, and whether the evidence justifies further research.
8. Unit, integration, and adversarial leakage tests pass in a fully offline CI path.

### Non-goals

- No live exchange trading, order placement, brokerage integration, real-money interaction, or automated execution.
- No claim of production exchange connectivity, profitable trading strategy, executable latency, or investment performance.
- No neural networks, reinforcement learning, streaming dashboard, cloud deployment, microservices, database server, Kubernetes, distributed scheduler, or complicated frontend in the initial P0–P6 scope.
- No paid data subscription, credential collection, or large/unbounded download without explicit human approval.
- No external repo publication, pushes, account changes, or paid API requests without separate explicit authorization.

---

## 2. Why this project, and what makes it distinctive

The owner already has strong production-style engineering evidence: an asynchronous visual-inspection platform, an AI security pipeline with durable-job and evidence controls, a future adaptive training agent with strict validation gates, and a Last.fm recommender that compares multiple algorithms. This project should **complement** those strengths by filling the demonstrated gap in **market microstructure, sequential modeling, and leakage-safe quantitative research**.

HFT Architecture's published role emphasizes preparing order-book data, explaining why ordinary CV fails on time series, finding leakage, repeating someone else's results, and writing enough detail for others to repeat an experiment. Its consulting methodology also stresses out-of-sample measurements, reconstructed book assumptions, and clear research limitations. The scope below follows those competencies rather than building a general trading application.

### Priorities, in order

1. **Correctness and evidence.**
2. **Causal information boundaries and reproducibility.**
3. **Clear model comparisons and uncertainty.**
4. **Runtime/storage efficiency adequate for the selected sample.**
5. Polish and extra functionality only after the above are satisfied.

---

## 3. Research scope and decision register

All decisions here are **provisional until the P0 review**. Codex must not silently turn a provisional candidate into an irreversible commitment.

| Decision | Working proposal | P0 decision / verification |
|---|---|---|
| Market | One liquid cryptocurrency order book; Deribit BTC-PERPETUAL is a documented Tardis example | Confirm instrument, venue and source availability |
| Data source | Tardis downloadable normalized top-five snapshots; consider incremental L2 as alternative | Inspect sample, terms, coverage, volume, timestamp semantics |
| Model unit | One valid order-book state at a defined decision timestamp | Define snapshot sampling and equal-timestamp ordering |
| Prediction target | Three classes: up / unchanged / down future mid-price | Pin horizon type and no-change threshold using training-period rules |
| Horizon | One short fixed horizon: either **H book-state events** or **H seconds** | Choose exactly one primary definition and document tradeoffs |
| Features | Top-level and multi-level book imbalance, spread, depth, lagged state changes | Freeze a small feature list and exact calculation boundary |
| Baselines | Majority-class / persistence where appropriate, logistic regression, gradient boosting | Fix identical split and preprocessing contract |
| Validation | Chronological, date-aware walk-forward with label-interval purging; final untouched holdout | Determine feasible number of dates/folds from real coverage |
| Primary metric | Macro F1 and balanced accuracy with per-class support | Confirm target distribution and metric feasibility |
| Secondary metrics | Confusion matrix, majority baseline, per-fold dispersion, optional log loss/Brier when applicable | No hindsight metric switching |
| Runtime | Python 3.12+, uv, pytest, pandas/Polars, NumPy, scikit-learn, optional LightGBM | Check dependency compatibility and deterministic execution |
| Deployment | Offline CLI and report artifacts only | No live trading path |

### Concrete target contract

For a valid book state indexed by i:

- Best bid b_i and best ask a_i must be present and positive, with b_i < a_i.
- Mid-price m_i = (b_i + a_i) / 2.
- A candidate event-time horizon uses future state i+H **inside the same continuous session/valid segment**. A candidate clock-time horizon uses a documented forward observation selection rule; it must never silently cross a gap, session boundary, or trading outage.
- Let delta_i = m_future - m_i. The three-class target is up if delta_i > theta, down if delta_i < -theta, otherwise unchanged. Define theta in ticks or basis points and lock its value before final testing. Do not tune theta on final test results.
- Every feature X_i may depend only on records available at or before the decision-time cut-off for i. Label computation is separate and never joins back into features.
- Each sample retains feature_cutoff_time, label_end_time, session_id, source_row_position, and provenance key so temporal boundaries can be audited.

**Important:** Event-time and clock-time horizons answer different questions. Use one primary horizon for the core project and describe it unambiguously. If data gaps or sparse independent dates invalidate a credible test, **stop with a documented feasibility decision**, not a fabricated success.

---

## 4. Data-source feasibility and guardrails

### Recommended P0 candidate: Tardis normalized historical book data

Tardis documents (a) historical top-five and top-25 reconstructed book snapshots and (b) incremental level-2 book updates. Its documentation says datasets for the **first day of each month** are available without a Data API key. CSV rows include timestamps in **microseconds since epoch (UTC)**; snapshot format contains per-level bid/ask price and amount. Source row order matters when timestamps tie. This is promising, but **the free sample-date restriction is an analytical limitation**.

Useful official references:

- Tardis CSV overview: https://docs.tardis.dev/downloadable-csv-files/overview.md
- Tardis data types and timestamp/schema semantics: https://docs.tardis.dev/downloadable-csv-files/data-types.md
- Example snapshot family: https://docs.tardis.dev/downloadable-csv-files/data-types.md#book_snapshot_5
- Example L2 updates: https://docs.tardis.dev/downloadable-csv-files/data-types.md#incremental_book_l2

P0 must verify current download eligibility, available symbol/date combinations, uncompressed size, sample quality, license/redistribution terms, and usable number of independent sessions. Do not assume the example Deribit instrument is the final choice.

**Interpretation warning:** Vendor-provided reconstructed snapshots are not evidence that this project reconstructed the book. They may already have filtered crossed states, and depth truncation can alter observed spread/depth behavior. Document that provenance. If raw incremental L2 is selected, reconstruct using the feed's documented snapshot/reset and price-level semantics and test those rules explicitly; this increases scope and should be a conscious P0 tradeoff.

### Backup source: FI-2010

The FI-2010 research benchmark provides normalized LOB data from five Nasdaq Nordic stocks over ten consecutive days and a day-based anchored validation protocol. It is credible for comparison experiments, but its transformed/benchmark-style representation changes what can be claimed about raw ingestion and book reconstruction. If the primary source fails feasibility, propose this alternative and obtain approval before changing the central dataset/claim.

Primary research reference: https://researchportal.tuni.fi/en/publications/benchmark-dataset-for-midprice-forecasting-of-limit-order-book-da/

### Do not silently substitute

Binance public candle, trade, or aggregate-depth archives are not automatically equivalent to level-by-level order-book snapshots. Verify the exact type and semantics before substituting. A trade-only or OHLCV-only project would not meet the same portfolio goal and requires a scope-change decision.

### P0 feasibility checklist

- [ ] Source, exact URL/API path, provider, exchange, instrument and exchange timezone recorded.
- [ ] Licensing/redistribution rules and whether raw data may be committed publicly recorded.
- [ ] Exact raw file schema, dtypes, units, sequence/tie behavior, snapshot frequency and update semantics verified on real rows.
- [ ] Probe is bounded and local; no credentials, paid endpoints, or bulk downloads used.
- [ ] Number of independent calendar dates/sessions, events, gaps and total byte size estimated.
- [ ] At least one defensible chronological training/validation/holdout design exists, ideally with multiple walk-forward folds; if not, record why and seek alternate data approval.
- [ ] Data split contract, horizon and target are chosen **before** model results.
- [ ] Decision memo explicitly recommends GO, CONDITIONAL GO, or NO-GO.

---

## 5. Pipeline design and module boundaries

### Logical flow

**Fetch/provide raw file -> verify source manifest -> parse and normalize -> validate book states -> construct causal features and future labels -> partition chronologically -> fit train-only preprocessing/model -> score walk-forward and final holdout -> inspect stability/uncertainty -> write reproducibility report.**

### Minimal suggested repository structure

    market-microstructure-ml/
      README.md
      pyproject.toml
      uv.lock
      .gitignore
      .github/workflows/ci.yml
      configs/
        research.yaml
      docs/
        specification.md
        decisions/
        phase-handoffs/
        data-dictionary.md
        research-report.md
        limitations.md
      src/market_microstructure/
        __init__.py
        data/
          ingest.py
          schema.py
          quality.py
        features.py
        labels.py
        splits.py
        models.py
        evaluation.py
        experiment.py
        manifests.py
        cli.py
      tests/
        unit/
        integration/
        adversarial/
        fixtures/
      data/
        README.md
        raw/                   # gitignored
        processed/             # gitignored
      reports/                 # keep small textual artifacts; large outputs gitignored

Keep structure minimal. Codex may merge modules where it improves simplicity. Do not create empty scaffolding just to match this tree.

### Data contracts

**Raw manifest:** provider, venue, symbol, date, retrieval URL, retrieval UTC time, byte length, SHA-256, original schema version/notes, license terms pointer. Download must be opt-in and bounded. Raw rows are never quietly edited.

**Normalized state:** event_time_utc, receive_time_utc (if available), source_file, original_row_number, session_id, bid/ask prices and amounts for supported depths, valid flag, exclusion reason, and a stable chronological/tie ordering. Time resolution must remain explicit.

**Quality report:** counts and rates for unparsable rows, duplicates, timestamp decreases, tied timestamps, missing/zero/negative prices and amounts, crossed/locked books, gaps, resynchronizations, depth insufficiency, and retained rows. Some conditions may be provider-normalized away; state that in the report instead of claiming to have observed none in the underlying market.

**Feature/label row:** source identifier, feature_cutoff_time, label_end_time, session_id, feature columns, target, and nullable/exclusion reason. Dropped samples must have attributable counts.

**Experiment manifest:** stable experiment ID, code revision (or dirty-tree flag), config hash, raw and processed data hashes, feature list/version, horizon, label threshold, fold boundaries, fit transformations, package versions, seed, model hyperparameters, metrics, runtime and warnings.

**Report output:** Markdown and machine-readable JSON or CSV; never require a hosted service to view results.

### Engineering principles

- Stream or process in chunks as needed, avoid loading an enormous day's full raw history by default.
- Retain original timestamps and a stable source-order tie-breaker; never sort ties arbitrarily.
- Use UTC consistently; document the distinction between exchange time and local capture/receipt time.
- Reset lagged windows on sessions, invalid segments or feed discontinuities. Never forward-fill across unknown gaps without documenting a justified policy.
- Fit scaling, imputation, feature selection and hyperparameter tuning **only inside training folds**.
- Never random-shuffle time-indexed examples into CV folds.
- Run CI on small checked-in synthetic fixtures; large market data remains local and excluded from Git.
- Use deterministic seeds when supported; record unavoidable nondeterminism.

---

## 6. Features, models, validation and research discipline

### Minimal causal feature set

1. Best bid, best ask, mid-price and absolute/tick-normalized spread; document tick-size inference or metadata.
2. Level-one volume imbalance: (bid_size_1 - ask_size_1) / (bid_size_1 + ask_size_1), with a safe zero-denominator policy.
3. Multi-level cumulative depth imbalance across available top N levels; never assume unavailable depth.
4. Microprice or depth-weighted mid-price **only if justified and consistently defined**.
5. Trailing mid-price changes and rolling variability from prior valid states; windows cannot cross disconnections.
6. Optional recent top-of-book depth/spread changes, using only causal lagged values.

Keep the final feature count modest. Before fitting, document feature units, NaN handling, whether each is meaningful under the observed spread distribution, and the exact timestamp availability rule.

### Modeling baseline set

- **B0: Majority-class frequency** from training data only; optionally a persistence/no-change rule, if meaningful.
- **B1: Multinomial or one-vs-rest logistic regression** with train-only scaling/imputation.
- **B2: Limited-complexity gradient-boosted trees**, e.g. LightGBM if installable; otherwise scikit-learn's HistGradientBoosting with documented reason.

Avoid a hyperparameter search large enough to overfit the small number of dates. Use a modest predeclared grid or fixed reasonable configurations; reserve one validation process for selection and a genuinely untouched final holdout.

### Split contract — critical

1. Order sessions/dates chronologically. A split must not mix observations from the same forward-looking label interval across train and validation/test.
2. Each sample has [feature_cutoff_time, label_end_time]. Exclude a training example if its future label interval reaches a later evaluation boundary. Apply a documented purge; add an embargo only where justified by the information/feature policy.
3. No features that look beyond the decision timestamp; no interpolation or global preprocessing trained on validation/test rows.
4. Select model/threshold/hyperparameters on chronological training/validation folds, never on the final holdout. Refit on permitted pre-holdout data after freezing settings and then evaluate the untouched holdout once.
5. Treat calendar sessions and feed gaps as boundaries. If free Tardis samples fall on noncontiguous first-of-month dates, they are independent observed samples, **not** a continuous backtest of the intervening month.
6. State the actual number of independent dates and walk-forward folds. Millions of correlated updates do not equal millions of independent experimental observations.

### Evaluation contract

**Primary:** macro F1, balanced accuracy, class-wise precision/recall/support, confusion matrix, compared to B0 on exactly the same eligible test rows.

**Secondary:** per-fold score dispersion, calibration or log-loss/Brier where valid, prediction frequency, class imbalance, inference runtime only if methodologically fair, descriptive performance by defined periods. For autocorrelated observations, use session/block-aware intervals or a clearly labeled descriptive range, not naive IID row-level standard errors.

**Research interpretation:** Report whether apparent improvement persists across held-out periods, how much depends on class imbalance/label definition, where features degenerate, and the most important unresolved data limitations. No profitability or trading alpha claim from a classification score alone.

### Essential adversarial tests

- Insert a future-only signal into a held-out period; ensure no feature or fitted transformer can use it.
- A rolling feature at time t does not change when records after t are modified.
- Purge/exclusion removes samples whose label_end_time crosses a fold boundary.
- Tied timestamps retain provider/source order deterministically.
- No labels cross session boundaries, outages or gaps.
- Train-only preprocessing statistics are unchanged when validation/test distribution is perturbed.
- Time unit confusion (milliseconds vs microseconds), duplicate rows, malformed depth, crossed/locked states, missing price/amount and negative volume all produce deterministic errors or recorded exclusions.
- Experiment rerun on pinned fixture/config yields matching splits and metrics within specified numerical tolerance.
- Deliberately leaky synthetic pipeline is flagged or rejected by an explicit test; tests are not satisfied merely by returning an empty dataset.

---

## 7. Detailed phase contracts

### P0 — Scope, data feasibility and research contract (2–3h)

**Goal:** Decide exactly what can be measured with accessible real data; stop early if the data cannot support a defensible result.

**Tasks:**

1. Review this package and inspect the environment and existing repository without mutating unrelated files.
2. Compare the primary Tardis reconstructed-snapshot candidate against incremental L2 and FI-2010 backup, describing scope/risk differences.
3. Propose one instrument and several chronological dates, with a bounded dataset probe and storage estimate; actually inspect a tiny real sample **only if explicitly authorized and accessible**.
4. Lock one horizon, label threshold, feature availability timestamp, session/gap rule, training/validation/final holdout design, metrics and baseline set.
5. Create a brief data-source decision, risk register and acceptance test plan.

**Deliverables:** P0 specification; source/license/provenance note; schema sample; estimated runtime/storage; GO/CONDITIONAL GO/NO-GO decision; phase scope lock.

**Acceptance gate:** Every decision in Section 3 is resolved or explicitly flagged; real schema has been checked or P0 remains conditional; no model result was used to pick horizon, labels, or splits.

**Stop conditions:** Need to pay, authenticate, download large data, unclear redistribution terms, insufficient session diversity, timestamps without credible ordering, or inability to define leakage-safe evaluation. Present options; request human decision.

### P1 — Data ingestion and integrity (4–6h)

**Goal:** Transform reproducible source inputs into normalized, auditable book states.

**Tasks:**

1. Build checksum-verified manifest, streaming/chunked parsing, explicit schema validation and microsecond UTC conversion.
2. Preserve source order within tied timestamps and correctly handle snapshot representations, book depth, negative/zero amounts, and missing values.
3. Produce immutable normalized Parquet or equivalent artifact and the quality/exclusion report.
4. Add tests for malformed/tied/out-of-order records, corruption and deterministic processing.

**Deliverables:** CLI ingestion command, normalized schema, data dictionary, quality report, fixture-based tests.

**Acceptance gate:** The real sample yields inspectable audited records; no silent drops; offline CI tests pass; source is traceable back to a checksum. If L2 reconstruction was explicitly selected, add reset and update semantics tests.

### P2 — Causal features and labels (4–6h)

**Goal:** Build a feature matrix with provable decision-time boundaries and correctly separated future labels.

**Tasks:**

1. Implement mid-price, spread, top-level and multilevel imbalance, rolling lagged change and variation features.
2. Implement the chosen horizon and three-class target in a separate module.
3. Record decision timestamps, future label endpoint, segment identifiers and missing reasons per sample.
4. Add synthetic tests for zero denominator, equal timestamp ordering, no cross-gap windows, future mutation invariance and end-of-segment exclusion.

**Deliverables:** Versioned feature specification; feature/label artifacts; causal availability report; adversarial tests.

**Acceptance gate:** Future-row perturbations leave earlier features unchanged; labels are computed only from permitted future observations and never leak into features.

### P3 — Baseline models and experiment runner (4–5h)

**Goal:** Obtain a repeatable, unambiguous baseline experiment with no optimistic result claims.

**Tasks:**

1. Fit B0, B1 and B2 under identical eligible data partitions.
2. Build a config-controlled CLI for training and scoring, including immutable split IDs.
3. Record model config, training-only transforms, seed, hashes, package versions and metrics.
4. Export class distribution, confusion matrix, primary/secondary scores and warnings.

**Deliverables:** Minimal experiment runner, baseline comparison report, stable result schema, reproducibility tests.

**Acceptance gate:** A fresh local rerun with the same fixture/config reproduces results; all preprocessing is trained exclusively on training rows. Any early real-data score is labeled **preliminary** until P4/P5 pass.

### P4 — Temporal evaluation and leakage safety (6–8h) **Highest-priority technical phase**

**Goal:** Make the out-of-sample comparison defensible for time-dependent data.

**Tasks:**

1. Implement explicit chronological, session-aware walk-forward folds.
2. Purge training examples with labels that overlap later validation/test periods; document any necessary embargo.
3. Hold the final period entirely outside model/parameter selection.
4. Add boundary audits and adversarial leak tests, including train/test shift and transformer contamination checks.
5. Ensure no tuning step is informed by final holdout metrics.

**Deliverables:** Fold manifest, split audit, leakage test suite, walk-forward comparison report.

**Acceptance gate:** Every split has a machine-checkable temporal proof and reproducible manifest; adversarial tests fail under a known leakage injection and pass under corrected logic.

### P5 — Statistical robustness and research conclusion (4–6h)

**Goal:** Interpret the experiment conservatively and decide whether further work is justified.

**Tasks:**

1. Summarize results per fold/date and report class counts, distribution shifts, score dispersion and supported uncertainty estimates.
2. Run a small predeclared robustness grid (e.g., feature ablation and one target/period sensitivity) **without tuning on the final holdout**.
3. Investigate anomalous gains or failure modes with evidence.
4. Distinguish statistical prediction from executable, fee-adjusted trading returns.
5. Write the decision: promising, inconclusive, or no evidence of generalization; specify a concrete next test.

**Deliverables:** Analysis table/plots where useful, limitations section, final research note, results backed by experiment hashes.

**Acceptance gate:** Claims have matching evidence; no final-test cherry-picking; uncertainty and data coverage restrictions are explicit; a negative result is acceptable.

### P6 — Reproducibility, portfolio and independent review (3–5h)

**Goal:** Turn validated work into a coherent public-facing technical portfolio artifact.

**Tasks:**

1. Document installation, data acquisition/license, exact reproduction commands, resource requirements, data dictionary and model decisions.
2. Clean up CLI ergonomics, errors, static typing where reasonable, lint/format, and offline CI.
3. Link every reported figure to a small tracked manifest; exclude raw licensed datasets, credentials, large models and caches.
4. Have Codex perform a separate read-only adversarial review of provenance, data leakage, conclusion wording, and reproducibility.
5. Draft interview talking points: research question, why chronological CV, one discovered issue, model comparisons, limits, and what to change next.

**Deliverables:** Polished README, technical research report, stable artifact schema, CI, independent review memo, truthful resume-bullet candidates.

**Acceptance gate:** From a clean checkout with allowable data supplied, commands work as documented; offline tests pass; reviewer signs off or lists residual blockers; no unsupported market performance claims.

---

## 8. Phase budget and quality checkpoints

| Phase | Time estimate | Cumulative estimate | Core exit question |
|---|---:|---:|---|
| P0 — Scope & source | 2–3h | 2–3h | Is a defensible dataset/experiment possible? |
| P1 — Ingestion & QA | 4–6h | 6–9h | Can data be reproduced and audited? |
| P2 — Features & labels | 4–6h | 10–15h | Are all features causal and labels valid? |
| P3 — Baselines & runner | 4–5h | 14–20h | Are models and numbers reproducible? |
| P4 — Temporal validation | 6–8h | 20–28h | Has leakage been prevented and tested? |
| P5 — Robustness & findings | 4–6h | 24–34h | Does the result survive cautious scrutiny? |
| P6 — Portfolio review | 3–5h | 27–39h | Can a third party understand and repeat it? |

These are **planning estimates, not delivery guarantees**. In particular, data access, disk/CPU constraints, unexpected exchange feed semantics, insufficient independent sessions, and low-coverage periods can materially extend P0/P1. Do not suppress correctness requirements to stay within a stated hour budget.

### Checkpoints

- **After P0:** Explicit feasibility approval required to begin implementation.
- **After P3:** Functional prototype only; **not** yet validated portfolio research.
- **After P4:** Core leakage-safe validation complete.
- **After P5:** Research-ready, contingent on full test evidence.
- **After P6:** Publication-ready only after review and provenance checks.

---

## 9. Testing and verification policy

### Test layers

1. **Unit:** parsing, data schema, time conversion, book math, features, labels, fold inclusion, metrics.
2. **Property/adversarial:** future perturbation invariance, boundary crossing, duplicate or corrupted event handling, tie stability.
3. **Integration:** tiny fixture raw -> features -> folds -> model -> report; rerun produces identical split and comparable numerical metrics.
4. **Real-data smoke:** small authorized slice for input sanity and performance; no proprietary data in Git or CI.
5. **Independent review:** reviewer checks invariants and skeptical alternative explanations, not merely a green test count.

### Definition of done per phase

A phase is not complete because code exists. Completion requires:

- Requirements and assumptions documented.
- Relevant tests run and their exact command/count/status reported.
- Source files and generated outputs enumerated.
- Known failures, tradeoffs, unverified claims, and proposed follow-ups disclosed.
- No unrelated user work overwritten.
- No automated declaration of **GO** when the gate requires human review.

Use structured error reporting and deterministic failure exits. Prefer precise explicit fixture coverage over artificially inflated test counts.

---

## 10. Key risks, mitigations and change control

| Risk | Impact | Mitigation / decision |
|---|---|---|
| Free dataset lacks sufficiently many independent sessions | Fragile out-of-sample inference | P0 coverage audit; alternate source or narrower claims; stop if not credible |
| Very large compressed/uncompressed sample | Runtime or disk surprises | Probe schema/size first; bounded chunks; hard local download budget |
| Vendor snapshots already filtered invalid states | Quality report may overstate cleanliness | State preprocessing performed upstream; no claim of observed raw feed validity |
| Event time vs exchange/receipt time confusion | Temporal leakage or impossible causality | Time semantics in schema; use availability timestamp conservatively |
| Multiple rows at same timestamp | Silent unstable ordering | Preserve source row position; deterministic tie tests |
| Overlapping target horizons | Inflated validation score | Label-end aware purge and fold audit |
| Preprocessing fitted globally | Data leakage | Fold-local fit/test adversarial fixture |
| Too many knobs on few dates | Overfitting research decisions | Predeclare one market/horizon, modest models, fixed final holdout |
| Correlated updates misread as independent samples | False certainty | Session/block-aware uncertainty; report days/folds |
| No predictive signal | Temptation to inflate performance | Treat as valid conclusion; report baselines, limits and next test |
| Scope creep into execution system | Delays meaningful evidence | Reject bot/backtester/infra extensions during P0–P6 |

### Change-control rules

Changes to source, instrument, horizon, class threshold, split policy, feature set, primary metrics, or final holdout after model results are observed require:

1. A dated change-request note explaining the reason and whether prior results influenced it.
2. Reinstatement of clean model selection / new untouched holdout if necessary.
3. Human approval when materially changing the project objective.

Never retroactively rewrite the experiment registry or overwrite a frozen result.

---

## 11. Optional post-P6 extensions — not included in core estimate

**P7 Multi-market / multi-horizon transfer:** Compare generalization across a deliberately selected second market or horizon. Keep each market/horizon result separately versioned; do not cherry-pick.

**P8 Execution-cost-aware simulation:** Only after a validated forecast, explore fee, spread, slippage, queue and fill assumptions in an explicitly hypothetical backtest. Never call hypothetical profitability realized trading profit.

**P9 Scale and systems optimization:** Benchmark chunked ingestion or Parquet processing on a larger permitted dataset, profile bottlenecks and memory ceiling, verify correctness parity with the reference pipeline.

Each extension needs a new scoped contract and time estimate. Do not implement opportunistically.

---

## 12. Codex operating agreement

**Agent role:** Implementer and evidence collector. Human/ChatGPT acts as reviewer and phase gatekeeper. Codex may propose design alternatives but does not independently expand scope.

**Initial scope:** **P0 only.** Do not implement P1–P6 until P0's explicit GO is reviewed and the next-phase instruction is issued.

### On every milestone

1. Inspect repository status and existing instructions; preserve user changes.
2. State planned edits, decisions, and acceptance evidence before work.
3. Implement only the authorized phase. Prefer small reviewable changes.
4. Run smallest relevant checks first, then complete permitted regression suite.
5. Do not create synthetic market results that could be confused with real empirical conclusions.
6. Record assumptions and provenance in versioned docs and machine-readable metadata.
7. Never commit raw market data, secrets, tokens, paid sample content, or large binary model artifacts.
8. Do not push, publish, create remote resources, subscribe, execute live exchange calls, or acquire paid data without explicit authorization.
9. If permission, license, data access, missing scope decision or safety gate blocks work, **STOP** and request direction. Do not switch datasets silently.
10. Finish with the handoff template below and **wait** for review before the next phase.

### Required per-phase handoff format

    Phase: Pn — title
    Outcome: PASS | CONDITIONAL | BLOCKED | FAIL
    Scope performed:
      - ...
    Files changed:
      - ...
    Dataset/provenance:
      - source/date/size/checksum or "not used"
    Tests/checks:
      - exact command: result
    Measured results:
      - actual numbers with method and artifact paths, or "none"
    Acceptance-gate mapping:
      - requirement -> proof
    Limitations / unresolved questions:
      - ...
    Security/permissions/external actions:
      - ...
    Git status:
      - branch, dirty state, commits (if any); no claim of push unless verified
    Recommended next action:
      - request review / specific approval; do not auto-start P(n+1)

### Suggested review questions for ChatGPT after each phase

- Are the deliverables supported by actual files and test outputs?
- Which claims are verified versus assumed?
- Is the amount of complexity proportionate to the role?
- Are data provenance, time cut-offs and splitting invariants tested adversarially?
- Is the next phase safe and justified, or should we revise scope?

---

## 13. Initial Codex prompt (copy/paste as first message)

**Project:** Market Microstructure ML & Validation Pipeline

You are the implementation agent for the attached **Market Microstructure ML & Validation Pipeline — Codex Project Package v1.0**. Treat its explicit phase contracts, quality gates, data provenance rules, and non-goals as the project specification. The human owner and ChatGPT will review milestones. Do not pretend any experiments or data inspections have already happened.

**Your authorization for this turn is P0 only.**

1. Read the entire package and inspect current working directory, repo status, existing AGENTS.md/instructions, Python tooling and available resources.
2. Prepare a bounded P0 project/research contract. Evaluate exact historical order-book data options, preferring one market/instrument/horizon, with Tardis reconstructed top-five snapshots as the primary *candidate*, not as a foregone decision.
3. Verify dataset schema, license/redistribution, timestamps, estimated raw/uncompressed size, independent dates, and viability of honest chronological walk-forward plus untouched final holdout. Do not claim availability based solely on URL patterns. If network access or a data download needs approval, stop and ask for it. Do not pay, use credentials or fetch large files without explicit permission.
4. Propose and justify exact data availability timestamp, target/horizon, class threshold, causal features, chronological split, label-overlap purge, modest baselines, primary metrics, run manifest, and P1 acceptance tests. Mark anything unverified explicitly.
5. Produce a P0 decision report with GO / CONDITIONAL GO / NO-GO and bounded next steps. If the data cannot support a credible evaluation, propose alternatives but do not silently change the project's claim.
6. Do not implement P1+, train models, report empirical performance, commit/push/publish, download large datasets, install heavyweight tooling unnecessarily, or perform any live trading operation.
7. Conclude using the package's per-phase handoff format, enumerate exact evidence and blockers, and wait for my review before further work.

Optimize for a scientifically defensible **junior ML research portfolio** project, not maximum infrastructure complexity.

---

## 14. Source notes and integrity disclaimer

The research scope was tailored to HFT Architecture's publicly posted Junior Machine Learning Engineer responsibilities and consulting methodology:

- Role: https://hftarchitecture.com/careers/junior-machine-learning-engineer
- Methodology: https://hftarchitecture.com/consulting

Data source claims in this specification reflect official Tardis documentation and the FI-2010 original research publication as inspected during preparation. They do **not** establish that any particular future file can be downloaded or that a dataset is licensed for redistribution; P0 must verify those operational details.

**This package is a specification, not an implementation. No code, model, backtest or dataset was created or validated as part of writing it.**
