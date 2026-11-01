# Historical data is obtained locally

No market-data rows are distributed in this repository. The frozen source list
and excerpt hashes are in sources.lock.json. Obtain your own copies under the
provider's then-current [terms](https://docs.tardis.dev/legal/terms-of-service).
The terms apply to free samples as well as paid data.

From the project root:

    uv sync --frozen --extra dev
    uv run microstructure fetch --config configs/research.json --raw-dir data/raw --source-lock data/sources.lock.json

The fetch command performs explicit bounded historical downloads; run, verify
and reproduce consume existing local files. The acquisition contract is:

| Item | Pinned choice |
|---|---|
| Provider | Tardis.dev |
| Venue/instrument | Deribit BTC-PERPETUAL |
| Representation | Vendor-reconstructed top-five book snapshots |
| Dates | First day of every month in 2020 |
| Selection | First 20,000 complete source rows/date |
| Requested compressed range | Bytes 0–524287, at most 512 KiB/date |
| Aggregate hard ceiling | 24 MiB historical payload |
| Timestamp units | UTC microseconds since the Unix epoch |
| Availability time | Local receipt timestamp, source order breaks ties |
| Prices | USD |
| Amounts/depth | USD notional in the source's native amount field; not BTC |

The [source documentation](https://docs.tardis.dev/downloadable-csv-files/overview.md)
identifies first-of-month files as available without a Data API key. The command
does not acquire credentials or purchase access. Stop and investigate any
authentication or eligibility error rather than substituting another dataset.

## Files saved under raw/

Each date has a complete-row CSV excerpt, an original compressed gzip prefix,
and an acquisition manifest. The combined manifest is raw/manifest.json.
Manifests identify original URLs, response range/source size, retrieval time,
requested caps, actual received bytes, selected row counts and SHA-256 values.
Existing matching files are reused only after both local hashes are checked.
Corrupt, mismatched or unmanifested artifacts produce explicit errors.

A prefix is not a full daily gzip object: its full-source CRC and advertised
whole-file MD5 cannot be verified. The CSV excerpt contains complete original
rows from that prefix, and its own SHA-256 is pinned. It is not a complete day.

Actual reference coverage is 240,000 rows in twelve opening windows of roughly
227–1,830 seconds each. Noncontiguous dates must not be joined into a continuous
backtest. See [the full evidence note](../docs/data-source-evidence.md).

## What stays out of Git

Raw CSV excerpts, gzip prefixes, normalized/feature rows, per-event predictions
and fitted model weights remain local. These are excluded even from the private
repository. Synthetic test fixtures are generated independently; they are not
sampled historical records. Published research artifacts contain only metadata
and qualifying aggregate results.

The terms distinguish internal research/own-model training from redistribution
of raw or merely sampled/filtered data and trained models. A source-code license
does not grant rights to the provider's data.
