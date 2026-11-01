# Extension spot-source feasibility and selection

The reviewed source is Tardis.dev's vendor-reconstructed top-five **Bitstamp
BTCUSD spot** book snapshots. It is distinct from the original Deribit inverse
perpetual and requires no funding or inverse-contract accounting. No Coinbase
source is used. Tardis documents [Bitstamp spot coverage](https://docs.tardis.dev/historical-data-details/bitstamp)
from 2019 and [free first-of-month CSV access](https://docs.tardis.dev/downloadable-csv-files/overview).

## Frozen observation design

All first-of-month dates January 2021 through December 2024 are fixed: 48 dates,
none used in the original study. All observations are retained in eight
half-open 15-minute receipt-time windows beginning 00:00, 03:00, 06:00, 09:00,
12:00, 15:00, 18:00 and 21:00 UTC. This samples two hours per date across the
clock, rather than selecting additional opening prefixes. It remains sparse
first-of-month coverage, not a continuous four-year backtest.

The complete daily gzip is streamed and retained locally. Its CRC/trailer is
validated and SHA-256 recorded. The selected CSV preserves original complete
records; its own checksum and compact original-source row ranges are pinned.
No complete decompressed daily CSV is materialized. A source exceeding a cap,
missing date/window, schema change or failed checksum causes an explicit stop;
there is no fallback to a prefix or another date/source.

All 48 one-byte HTTP ranges returned 206 with a complete advertised source size.
Their total is **268,550,418 compressed bytes**, with a maximum single daily
object of **9,256,742 bytes**. The feasibility budget consumed **1,436,943 bytes**,
including six 4 KiB Bitstamp/Kraken comparisons, the 48 one-byte ranges and one
complete 1,412,319-byte Bitstamp day. That complete 2023-01-01 object is reused
under its verified checksum during bulk acquisition; no repeated download is
needed. Source URLs, advertised sizes and the frozen selection are in
[the extension source lock](../../data/extension-sources.lock.json).

The feasibility full day contains 58,923 observations spanning approximately
86,397 seconds. Each fixed window contains 414-890 observations and spans
approximately 895-900 seconds. Inspection was limited to schema, receipt-time
coverage, units and price/amount precision, without deriving targets or scores.

The frozen ceilings are 16 MiB compressed/date, 160 MiB decompressed/date,
1 GiB compressed overall including probes, 5 GiB local historical storage,
64 dates and 20 minutes acquisition wall time. The actual selected dates number
48. Transfer is explicit and bounded; no paid endpoint, API key, subscription
or live exchange connection is required.

## Schema, units and lineage

The [top-five schema](https://docs.tardis.dev/downloadable-csv-files/data-types#book_snapshot_5)
is the same 24-column normalized CSV used by the original parser: exchange,
symbol, exchange/receipt timestamps and five ask/bid price/amount levels.
Timestamps are integer UTC microseconds. Source order resolves tied times;
normalization retains the full-day source row number, and global source order
counts unselected events too. Provenance is full-source gzip SHA-256 plus that
original row number, not a newly numbered filtered stream.

Bitstamp's [official pair metadata](https://www.bitstamp.net/api/v2/trading-pairs-info/)
identifies BTC/USD with eight base decimals and two quote decimals. Price is
USD per BTC and displayed depth quantity is BTC. The study/accounting grids
are explicitly **research grids**, 0.01 USD and 0.00000001 BTC, consistent with
current official precision and the inspected historical values. Current
metadata is not a point-in-time certificate of every historical exchange
rule, fee tier or minimum order size. Selected historical cells are checked
against these grids; their aggregate findings are recorded separately.

This is vendor reconstruction, including upstream crossed-level removal,
not our reconstruction of the incremental exchange feed. The
[CSV API documentation](https://docs.tardis.dev/downloadable-csv-files/api)
partitions files by local receipt day and omits explicit disconnect markers.
Invalid records, receipt regressions, gaps over 30 seconds, new files/dates and
every predeclared intraday window create segment boundaries. No feature,
forward label, order or simulated holding period may bridge those boundaries.

## Objective availability gate

These gates were recorded before bulk acquisition and before fitting: every
date and every one of its eight windows must contain at least 100 valid
observations, span at least 840 of 900 seconds, and have observations within
60 seconds of each window edge. Excluded rows may comprise at most 1% of a
date's selected observations. The gate reports valid state counts, spans and
segments without computing targets or model scores. An observed span alone
does not establish uninterrupted feed collection or guarantee enough usable
labels in every segment. The exact thresholds live in the
[preregistered study](preregistered-study.md) and frozen configuration.

## Permission and publication boundary

The [Tardis terms](https://docs.tardis.dev/legal/terms-of-service), modified
2026-10-28 and checked during E0, cover samples. Clauses 9.1/9.5 permit internal
analysis and own-model training; 9.2 restricts raw/filtered record redistribution;
9.3 permits qualifying non-reconstructible research aggregates; 9.5 restricts
external model sharing. Clause 23 separately bars Coinbase ML use, which this
Bitstamp selection avoids. Only code, synthetic fixtures, metadata, hashes and
qualifying aggregate reports are published. Historical rows, signals, fills,
ledgers, fitted preprocessing values and trained models remain ignored/local,
including in the private repository. The local simulator does not expose a
provider-data service to third parties.

## Verification checkpoint

The offline acquisition/storage/coverage suite passes **45 tests** using
independent synthetic books. It exercises complete-gzip CRC/MD5, corruption and
truncation, transfer/decoded/disk/deadline caps, cache checks, exact half-open
selection, original source/global ordering, tied times, invalid-state segment
breaks, chunked versus unchunked parity and checked local storage round trips.
The frozen bulk acquisition completed all 48 dates in approximately 163 seconds.
The actual accounted historical transfer, including feasibility and reuse, is
**268,575,042 bytes**; local raw/selected/manifest storage is **406,304,342 bytes**.
Every complete gzip passed CRC and SHA checks; 47 fresh downloads also passed
the advertised whole-file MD5 check. The reused feasibility object retains its
verified checksum and is decoded/CRC-checked again.

Normalization retained **631,463 states**, with **zero excluded rows**, **108
tied receipt timestamps** and **385 segments**. All 48 dates and all 384 fixed
windows pass the predeclared objective gate. Each window contains **413-2,771
valid observations**; the minimum observed span is **886.338 seconds**, the
largest first-edge gap **3.920 seconds**, and largest last-edge gap **12.256
seconds**. One additional within-window gap over 30 seconds creates an extra
segment; the other segment boundaries follow the fixed date/window selection.
These are observed timing facts, not proof of exchange-feed completeness.
Three exchange-timestamp decreases and six repeated book payloads are counted
and retained under the declared receipt-time/source-order policy. Neither is
silently recast as a receipt-time regression or a duplicate source record.

No selected price cell is off the 0.01 USD research grid, and no selected size
cell is off the 0.00000001 BTC research grid. These checks do not certify every
historical exchange rule. Normalized-state SHA-256 is
250c537888766630fc3c14f1836a2b4212ed828720ef255edce8fa60864645cb.
The source lock contains per-date/window aggregate coverage and source hashes;
detailed local quality records live under ignored data/extension/processed/.
No target distribution, model score, historical signal, row prediction or
simulation result was derived or inspected during this acquisition checkpoint.

The passing offline command is:

    .venv\\Scripts\\python.exe -m pytest tests/test_extension_data.py -q --tb=short --maxfail=1 --basetemp=artifacts/pytest-extension-data-release -p no:cacheprovider

The host required the approved execution path because default sandboxed pytest
temporary-directory access failed. Tests themselves never access the network.
