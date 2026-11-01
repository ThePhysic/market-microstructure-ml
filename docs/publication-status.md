# Publication status

Verified **2026-11-01 (UTC)** against GitHub's authenticated repository, commit,
workflow and languages APIs. This is a publication snapshot, separate from the
frozen research manifests and historical acceptance memos.

## Verified repository and hosted checks

| Item | Observed status |
| --- | --- |
| Repository | [ThePhysic/market-microstructure-ml](https://github.com/ThePhysic/market-microstructure-ml) |
| Visibility | **Public** (`visibility=PUBLIC`, `isPrivate=false`); no visibility change was made by this polish task |
| Git remote / branch | `https://github.com/ThePhysic/market-microstructure-ml.git`, `main` |
| Published revision verified before polish | [`5acd9579db5605386284b88e76b41cd325661207`](https://github.com/ThePhysic/market-microstructure-ml/commit/5acd9579db5605386284b88e76b41cd325661207) |
| Hosted CI for that revision | [Offline research checks, run 41348148399](https://github.com/ThePhysic/market-microstructure-ml/actions/runs/41348148399): completed, **success** |
| Tested hosted platforms | `offline (ubuntu-latest)` and `offline (windows-latest)`, both success |
| Hosted check scope | Locked installation, offline tests, both synthetic CLI demos, synthetic frame/batch benchmark parity; no licensed historical data is fetched |
| Code license | No license file or GitHub-detected license; choosing one remains an owner decision |

**Polish revision:** at this record's initial creation, the documentation and
attribute changes are local and have not passed a new hosted run. The successful
run above applies only to the exact prior revision. A post-push verification
snapshot will identify any subsequently verified polish revision separately.
For later changes, inspect the [workflow history](https://github.com/ThePhysic/market-microstructure-ml/actions/workflows/ci.yml)
and its exact `headSha`; a prior green run is not proof for a later commit.

## Earlier private-publication plans

The original completion instructions authorized creation and publication of a
**private** repository. The historical
[authority decision](decisions/000-authority-and-scope.md),
[extension contract](extension/implementation-contract.md),
[preregistered protocol](extension/preregistered-study.md),
[original review](reviews/final.json),
[extension final review](extension/reviews/final.json) and
[extension validation record](../reports/extension/validation.json) retain that
pre-publication context. Their private-release approval and pending-push wording
are historical evidence, not a description of today's visibility.

The current repository is independently verified public, as described in the
owner-supplied polish handoff. This task does not establish who changed
visibility or when, and does not imply that public release was originally
authorized. It makes no visibility change and grants no additional data rights.

## Available artifacts and exclusions

The public repository contains Python implementation and tests, independently
generated synthetic fixtures, frozen research configurations, acquisition
metadata/checksums, review records and qualifying aggregate research reports.
Entry points include the [README](../README.md),
[original report](research-report.md),
[extension report](extension/research-report.md),
[aggregate reference](../reports/extension/reference/experiment.json),
[reproduction proof](../reports/extension/reproduction.json),
[accounting audit](../reports/extension/accounting-audit.json) and
[measured benchmark](../reports/extension/benchmark.json).
The [report screenshot](extension/assets/research-report.png) is an actual
aggregate output; the [HTML proposal](../proposal/index.html) is synthetic.

Historical market records, sampled/processed event rows, individual
predictions/signals, detailed order/fill/portfolio or per-segment ledgers,
fitted preprocessing, trained model assets, credentials and local caches remain
excluded. Source locks record metadata and hashes, not order-book price/size
rows. Reviewers obtain their own permitted inputs to reproduce historical work.

The [source evidence](extension/data-source-evidence.md#permission-and-publication-boundary)
and [Tardis terms, clauses 9.2-9.5](https://docs.tardis.dev/legal/terms-of-service#9-licence)
define the provider boundary: qualifying research aggregates do not authorize
raw-data/model redistribution or a hosted data-backed analytics/backtesting
service. The terms were rechecked during this polish task; no broader
redistribution license is inferred from public GitHub access.

## Language classification and discoverability

Before polish, GitHub's languages API reported 1,909,272 HTML bytes and 477,881
Python bytes (approximately 80% / 20%). The
[attributes](../.gitattributes) mark `reports/**/*.html` as `linguist-generated`
and `proposal/index.html` as `linguist-documentation`. Report contents and Python
sources are unchanged; the files remain available. These exclusions follow
[Linguist's documented overrides](https://github.com/github-linguist/linguist/blob/main/docs/overrides.md).

Local `git check-attr` must confirm every tracked HTML report matches its rule
and that Python files remain unmarked. GitHub recalculates language statistics
after publication; verify the languages API and repository language bar after
the push rather than treating local attributes as a hosted result.

The repository description was applied and read back from GitHub:

> Python market-microstructure research: causal ML validation, deterministic backtesting, exact accounting and reproducible experiments.

Topics: `python`, `machine-learning`, `quantitative-finance`,
`market-microstructure`, `time-series`, `backtesting`, `algorithmic-trading`.
All seven topics were applied and verified against GitHub. Metadata edits are
separate from Git commits; visibility remained public.

## Local polish validation

- Existing offline suite: **374 passed in 56.07 seconds** on Windows with the
  pinned environment; no test or implementation changes were needed.
- The README's extension demo completed offline on independently generated
  synthetic inputs, producing `ext-0a7a4138dacb1397` and its local HTML report
  across all 20 declared scenario/policy cases. No historical inputs were used.
- All **102** local Markdown links/anchors in the eight revised/new Markdown
  documents resolve. GitHub's GFM API rendered the README, including its report
  image, comparison table, code block and reviewer navigation.
- Attributes match all three tracked HTML reports and the proposal. All **47**
  tracked Python implementation/test files remain unmarked by the Linguist
  overrides. This is local attribute verification, not a hosted language result.
- **86** protected source/test/configuration/build/CI, empirical artifact and
  historical review/decision files remain unchanged against `5acd957`.
  The frozen executable identity is still
  `4c0da99b0b5406670b2e120fa63d74d401ccb8b72bc84eb5e867be0103e4c08f`.
- The tracked/candidate inventory contains **112** files. Path checks, structured
  JSON-key checks, known credential-pattern scanning and manual inventory/diff
  review found no restricted-data/model/ledger or secret candidates. Reachable
  Git history also contains no restricted-path candidates. These bounded checks
  do not prove the absence of every possible encoded secret or provide legal
  clearance. Historical-data permissions remain unchanged.
- Frozen experiment results, source locks, reports, screenshots, hyperparameters,
  splits and review memos were preserved; no models were refitted or empirical
  reports regenerated.

## Remaining limits and owner decisions

- A public repository without a code license is not a generally licensed
  open-source release. No license was automatically added. Any future code
  license must remain separate from provider-data rights.
- The public visibility transition's actor/time is not established by this
  snapshot. Historical approvals are preserved instead of being rewritten.
- Historical replication depends on independently permitted provider access
  and the pinned environment. Hosted synthetic CI does not rerun the historical
  experiment or replace its archived independent reproduction.
- Research remains exploratory with unmet precision; every tested trading
  policy/scenario case has negative hypothetical marked P&L. Portfolio polish
  adds no scientific evidence, real-fill validity or live/profitable-trading claim.
- Prior AI review and assistance are documented. Applicant understanding and
  independent ability must be demonstrated by the applicant; see the
  [reviewer exercises](extension/applicant-guide.md#independent-exercises-before-an-interview).
