# Data feasibility and provenance evidence

## Frozen source and actual acquisition

The selected source is Tardis.dev's vendor-reconstructed top-five snapshots for
Deribit BTC-PERPETUAL. Exact dates are the first UTC day of every month,
January through December 2020. The official [download documentation](https://docs.tardis.dev/downloadable-csv-files/overview.md)
permits first-of-month downloads without a Data API key; actual HTTP responses,
not inferred URL patterns, established that all twelve files are accessible.

Acquisition requests bytes 0–524287 (512 KiB) per date and saves at most the
first 20,000 complete source records. It stops after a 64 KiB read chunk provides
sufficient complete rows. No complete daily file was downloaded.
All twelve excerpts contain exactly 20,000 rows: 240,000 records total.

- Actual retained compressed payload: **3,211,264 bytes**.
- Earlier feasibility probe: **131,072 bytes**, not retained or used for analysis.
- Accounted historical-data payload including that probe: **3,342,336 bytes**,
  below the 24 MiB hard project budget.
- Actual requested cap: 512 KiB/date, below the 2 MiB/date maximum.
- Original compressed prefixes, complete-row excerpts and acquisition manifests:
  ignored local directory data/raw/.
- Combined manifest: data/raw/manifest.json.
- Quality and coverage summary: data/raw/acquisition-quality-summary.json.

Each CSV excerpt preserves the original header and first complete rows.
Source row numbering is one-based, excluding the header. Manifests retain
canonical URLs, UTC retrieval time, response ranges/sizes, local SHA-256
for compressed prefixes and CSV excerpts, selection policy, retained counts and
the original full source-file size advertised by the HTTP response. Redirect
query strings and nonessential headers are excluded to avoid retaining signed links.

The downloaded gzip objects are **prefixes**, not whole sources. None reaches
gzip EOF. Local hashes prove integrity of retained artifacts; they do not
validate a missing whole-file gzip trailer/CRC or the provider's whole-file MD5
header. This partial-integrity description is preserved in every manifest.
Re-fetching must match the frozen excerpt checksums.

## Source semantics and units

The [CSV schema](https://docs.tardis.dev/downloadable-csv-files/data-types.md#book_snapshot_5)
has 24 columns: exchange, symbol, exchange timestamp, local receipt timestamp,
then ask price/amount and bid price/amount for each of five levels. Both
timestamps are UTC microseconds since the Unix epoch. Original row position
breaks ties. Snapshots are produced when tracked top-five levels change.

The pipeline uses local receipt time as its availability boundary, retains
exchange time separately, and preserves source order. The
[API documentation](https://docs.tardis.dev/downloadable-csv-files/api.md)
states that CSV files are partitioned by local receipt day and omit explicit
disconnect markers. A 30-second receipt gap therefore starts a new segment,
but absence of a gap is not proof of uninterrupted collection.

The vendor reconstructs snapshots and removes crossed levels upstream.
This project normalizes and validates supplied snapshots; it does not claim
to reconstruct an exchange-native incremental book. Zero observed invalid
states does not establish that the original exchange feed was clean.

[Deribit's inverse-perpetual specifications](https://support.deribit.com/hc/en-us/articles/31424954847133-Inverse-Perpetual)
identify BTC-PERPETUAL prices and order amounts as USD values, with 10 USD per
contract and a 0.5 USD minimum tick. Size/depth are vendor-native USD notional,
**not BTC**. The selected historical excerpts are consistent with half-dollar
price increments. Current documentation is not a point-in-time archival 2020
metadata certificate.

## Actual ingestion findings

Checksum-verified ingestion retained all 240,000 source records. It found 54
receipt-time ties; original row order was preserved. There were twelve file/date
segments, no observed >30-second gaps, and no rejected rows under the stated
schema/book/time checks. Synthetic tests cover malformed records, corruption,
incorrect units, missing depth, negative amounts, crossed or locked states,
level-order errors, exact duplicates, receipt-time regressions, gaps and
invalid-state segment breaks.

Each excerpt starts shortly after 00:00 UTC and covers only an opening window:

| Date | Rows | Observed duration (seconds) |
|---|---:|---:|
| 2020-01-01 | 20,000 | 1,830.118 |
| 2020-02-01 | 20,000 | 835.396 |
| 2020-03-01 | 20,000 | 299.555 |
| 2020-04-01 | 20,000 | 762.846 |
| 2020-05-01 | 20,000 | 410.816 |
| 2020-06-01 | 20,000 | 448.180 |
| 2020-07-01 | 20,000 | 638.846 |
| 2020-08-01 | 20,000 | 580.285 |
| 2020-09-01 | 20,000 | 815.169 |
| 2020-10-01 | 20,000 | 975.350 |
| 2020-11-01 | 20,000 | 226.571 |
| 2020-12-01 | 20,000 | 348.567 |

These are twelve noncontiguous observed windows, not complete days or a
continuous annual backtest. Date diversity supports the prescribed
walk-forward demonstration, but sparse, time-of-day-selected coverage limits
generalization and uncertainty estimates. Many correlated updates do not create
many independent observations. November/December schema and quality were
inspected without examining target distributions or predictive scores.

## License and publication boundary

The current [Tardis terms](https://docs.tardis.dev/legal/terms-of-service),
last modified 2026-10-28 and inspected during P0, explicitly cover free samples.
Clauses 9.1 and 9.5 allow internal research and own-model training. Clause 9.2
restricts redistribution of raw or merely sampled/filtered records. Clause 9.3
permits qualifying non-reconstructible aggregate statistics in research reports.
Clause 9.5 also restricts sharing trained models or access outside authorized
customer users.

Even the private GitHub repository therefore excludes raw data, processed
row-level samples, per-event predictions and fitted models. It contains source,
independently generated synthetic fixtures, acquisition metadata, checksums and
non-reconstructible aggregate research artifacts. Users obtain their own data
under then-current provider terms. No paid subscription, account, API key or
live exchange connection was used.

## Alternatives considered

Incremental L2 would require reset/reconstruction semantics and broader
processing scope. FI-2010 is an academic transformed benchmark and changes
ingestion/provenance claims. Neither substitution was needed: actual primary
source excerpts were accessible and inspected. No dataset was silently substituted.

## Data-module verification

Offline command:

    python -m pytest tests/test_data.py tests/test_acquisition.py -q --tb=short --maxfail=1 --basetemp=.test-tmp-data -p no:cacheprovider

Result: **30 passed**. The host's default sandboxed pytest temporary directory
was inaccessible; the passing invocation used the approved execution path and
an isolated project-local temporary directory. Tests never acquire network data.
