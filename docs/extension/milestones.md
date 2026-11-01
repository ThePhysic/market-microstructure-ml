# Extension E0-E7 evidence index

This checkpoint records completed data evidence and the remaining delivery
gates. It does not announce empirical findings, a clean final review, hosted CI
success or an extension push before those events occur. The original completed
2020 study remains separate; its historical P0-P6 memos are not evidence that
the new extension has passed the corresponding gates.

| Milestone | Purpose and review entry point | Checkpoint status |
| --- | --- | --- |
| E0 - Source and research permission | [Source evidence](data-source-evidence.md), [source lock](../../data/extension-sources.lock.json), [protocol](preregistered-study.md) | PASS: accessible Bitstamp BTCUSD spot, frozen dates/windows, licensed local research boundary |
| E1 - Broader design and precision | [Research design](research-design.md), [fixed configuration](../../configs/research-extension.json), statistics tests | Protocol recorded before fitting; development planning and final precision evidence pending |
| E2 - Acquisition, storage and coverage | acquisition.py, coverage.py, storage.py; [data tests](../../tests/test_extension_data.py) | PASS: 48 dates, 384 windows, 631,463 valid states, zero exclusions; 45 offline data tests |
| E3 - Causal replay and execution | [Replay/simulation tests](../../tests/test_extension_simulation.py), declared scenario configuration | Implementation and synthetic adversarial tests present; final integrated acceptance pending |
| E4 - Temporal research and simulations | [study.py](../../src/market_microstructure/extension/study.py), [research tests](../../tests/test_extension_research.py) | Fixed primary/secondary comparisons implemented; historical pilot/final measurements pending |
| E5 - Published-method assessment | [Method scope](research-design.md#external-published-method), replication.py | Development-only methodological adaptation implemented; numerical reproduction of the paper is not claimed; measured adaptation result pending |
| E6 - Measured scaling and parity | benchmark.py; synthetic frame/batch replay with native peak memory | Harness implemented; repeatable measured benchmark evidence pending |
| E7 - Independent verification and delivery | Source freeze, clean checkout, exact numerical/ledger reproduction, Astra medium review, private remote verification | Pending final evidence; new hosted CI and push not yet claimed |

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

## Intended aggregate handoffs

| Artifact path | Required evidence before marking complete |
| --- | --- |
| reports/extension/pilot/experiment.json | Development-only results and precision estimate; reserved final targets untouched during planning |
| docs/extension/reviews/pre-empirical.json | Astra medium PASS covering the exact executable/config/data identity with no remaining complaints |
| docs/extension/freeze.json, if published | Safe source/protocol/data attestation; no historical rows, fitted assets or signals |
| reports/extension/reference/experiment.json, report.html, report.md | Frozen final predictive comparison, scenarios, method adaptation, limitations and aggregate/hash provenance |
| reports/extension/benchmark.json | Repeated synthetic timings, native peak process memory, exact frame/batch ledger parity and environment |
| reports/extension/validation.json | Clean install/tests, source/data verification, exact numerical/ledger reproduction and local/hosted CI distinctions |
| docs/extension/reviews/final.json | Final Astra medium review with all substantive complaints resolved |
| Existing private GitHub remote | Verified privacy, expected branch/commit and successful final push; no restricted historical or fitted assets |

These are intended delivery paths, not a statement that every file already
exists. Source freezes precede final scoring; reproductions repeat unchanged
decisions and are disclosed separately. Benchmark mode generates its local
benchmark.json under the selected output directory; publication may copy that
aggregate to the stable path above.

## Acceptance and interpretation

Engineering completion requires correct causal behavior and reviewable,
reproducible evidence. Research decisiveness requires the declared precision
and practical-effect criteria. Hypothetical execution uses declared assumptions
and reports all preselected scenarios. These statuses are assessed separately;
an inconclusive or negative study can be a completed engineering deliverable.

Historical rows, detailed signals/ledgers, fitted values and model assets remain
ignored/local. External reviewers obtain their own permitted provider data.
Private source sharing does not authorize a hosted data-backed service. No
queue-position, real-fill, profitability or continuous annual-curve claim is
part of this handoff.
