# Extension E0-E7 evidence index

This index separates implementation acceptance, empirical precision and external
delivery. The [completed research account](research-report.md) reports the new
measurements; [validation](../../reports/extension/validation.json) records actual
checks as observed before publication. Current repository visibility, published
revisions and hosted CI are recorded separately in the
[publication-status record](../publication-status.md). The original completed 2020 study remains
separate. Its historical P0-P6 memos do not establish extension acceptance.

| Milestone | Purpose and review entry point | Checkpoint status |
| --- | --- | --- |
| E0 - Source and research permission | [Source evidence](data-source-evidence.md), [source lock](../../data/extension-sources.lock.json), [protocol](preregistered-study.md) | PASS: accessible Bitstamp BTCUSD spot, frozen dates/windows, licensed local research boundary |
| E1 - Broader design and precision | [Research design](research-design.md), [fixed configuration](../../configs/research-extension.json), statistics tests | Design implemented; research precision NOT MET: projected half-width 0.046474 and achieved primary half-width 0.022720 exceed 0.015. Final claims remain exploratory |
| E2 - Acquisition, storage and coverage | acquisition.py, coverage.py, storage.py; [data tests](../../tests/test_extension_data.py) | PASS: 48 dates, 384 windows, 631,463 valid states, zero exclusions; 45 offline data tests |
| E3 - Causal replay and execution | [Replay/simulation tests](../../tests/test_extension_simulation.py), [accounting audit](../../reports/extension/accounting-audit.json) | PASS: 57 simulator tests; 374 integrated tests; 20 cases reproduced exactly; independent cash/fee/inventory/mark/timing reconciliation passes for all cases |
| E4 - Temporal research and simulations | [study.py](../../src/market_microstructure/extension/study.py), [research tests](../../tests/test_extension_research.py) | Completed 12 development and 24 prequential final dates; 4,244 independent numerical checks pass; all fixed trading policies have negative marked P&L under every declared scenario |
| E5 - Published-method assessment | [Method scope](research-design.md#external-published-method), replication.py | Measured development-only adaptation: 68,471 binary targets; analytic null/prior checks pass. Original paper numerical reproduction is not claimed |
| E6 - Measured scaling and parity | [Benchmark](../../reports/extension/benchmark.json), [short fit profile](../../reports/extension/fit-profile.json) | 18 independent worker measurements; exact repeated frame/batch ledger parity; native peak memory and timing boundaries recorded; no custom C++ or fully out-of-core ML claim |
| E7 - Independent verification and delivery | [Reproduction](../../reports/extension/reproduction.json), source freeze, reviews, remote verification | Local verification PASS: final clean checkout 374 tests, exact complete reproduction, independent numerical/accounting/browser audits and actual CLI fingerprint verification. Astra sign-off is recorded separately; post-push hosted CI/privacy/commit checks are not inferred from local checks |

All implementation paths above are under
[src/market_microstructure/extension](../../src/market_microstructure/extension).
The authority/interface contract is [implementation-contract.md](implementation-contract.md).

## Completed E0/E2 evidence

- Selection: first-of-month dates January 2021 through December 2024, eight
  fixed quarter-hour windows per date, two selected hours per date. Every
  observation within each window is retained before validity checks.
- Complete source gzip payload: 268,550,418 bytes. Accounted historical transfer
  including feasibility/reuse: 268,575,042 bytes. Local raw/selected/manifest
  storage: 406,304,342 bytes. Acquisition wall time approximately 163 seconds.
- Every source passed complete-gzip CRC and SHA checks; 47 freshly fetched
  objects passed provider MD5 as well. One checksum-verified feasibility gzip
  was reused and decoded/CRC-checked again.
- Normalization: 631,463 valid states, zero exclusions, 108 receipt-time ties,
  385 segments. Three exchange-time decreases remain attributable while receipt
  time and source order remain monotonic. One within-window gap adds a segment;
  fixed date/window boundaries account for the remainder.
- Every window passes the predeclared gate: 413-2,771 valid states per window,
  minimum observed span 886.338 seconds, maximum first/last edge gaps 3.920 and
  12.256 seconds. No target or model score was inspected for these checks.
- No selected price/size cells violate the research grids. BTC is base quantity;
  USD per BTC is the price unit. Current precision metadata does not certify
  every historical exchange rule.
- Normalized-state SHA-256:
  250c537888766630fc3c14f1836a2b4212ed828720ef255edce8fa60864645cb.

The data test command is:

    uv run python -m pytest tests/test_extension_data.py -q -p no:cacheprovider

On the current Windows host, the approved execution path and project-local
temporary directory were required; the passing exact invocation is recorded
in the source evidence. The tests use independent synthetic fixtures and are
offline. No actual event records are embedded in this index.

## Aggregate handoffs

| Artifact path | Required evidence before marking complete |
| --- | --- |
| reports/extension/pilot/experiment.json | Development-only results and precision estimate; reserved final targets untouched during planning |
| docs/extension/reviews/pre-empirical.json | Astra medium PASS covering the exact executable/config/data identity with no remaining complaints |
| docs/extension/freeze.json, if published | Safe source/protocol/data attestation; no historical rows, fitted assets or signals |
| reports/extension/reference/experiment.json, report.html, report.md | Frozen final predictive comparison, scenarios, method adaptation, limitations and aggregate/hash provenance |
| reports/extension/benchmark.json | Repeated synthetic timings, native peak process memory, exact frame/batch ledger parity and environment |
| reports/extension/validation.json | Clean install/tests, source/data verification, exact numerical/ledger reproduction and local/hosted CI distinctions |
| docs/extension/reviews/final.json | Final Astra medium review with all substantive complaints resolved |
| GitHub publication | See the [current publication record](../publication-status.md) for verified public visibility, remote revision and hosted CI. Original delivery authorized a private remote; that historical requirement remains in the frozen contract/review. No restricted historical or fitted assets are distributed |

Source freezes precede final scoring; reproductions repeat unchanged decisions
and are disclosed separately. Benchmark mode generates its local benchmark.json
under the selected output directory; publication copies that aggregate to the
stable path above. Review files and validation distinguish completed checks from
external publication steps. Post-push visibility, commit and hosted workflow status
must be verified separately; a pre-publication commit cannot certify its own push.

## Acceptance and interpretation

Engineering completion requires correct causal behavior and reviewable,
reproducible evidence. Research decisiveness requires the declared precision
and practical-effect criteria. Hypothetical execution uses declared assumptions
and reports all preselected scenarios. These statuses are assessed separately;
an inconclusive or negative study can be a completed engineering deliverable.

Historical rows, detailed signals/ledgers, fitted values and model assets remain
ignored/local. External reviewers obtain their own permitted provider data.
Public or private source sharing does not authorize a hosted data-backed service. No
queue-position, real-fill, profitability or continuous annual-curve claim is
part of this handoff.
