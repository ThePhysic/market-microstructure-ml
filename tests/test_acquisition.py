"""Offline transport fixtures exercise bounds and partial-source integrity."""
import gzip
import hashlib
import io
import csv
import json

import pytest

from market_microstructure.acquisition import (
    AcquisitionError, HEADER_FIELDS, download_excerpt, download_many,
)


class Response(io.BytesIO):
    def __init__(self, body, *, status=206, source_length=None, headers=None):
        super().__init__(body)
        self.status = status
        self.headers = {
            "Content-Length": str(len(body)),
            "Content-Range": f"bytes 0-{len(body)-1}/{source_length or len(body)}",
            "Set-Cookie": "DO_NOT_RECORD",
        }
        self.headers.update(headers or {})
        self.read_calls = 0

    def read(self, size=-1):
        self.read_calls += 1
        assert size >= 0, "Unbounded reads are forbidden"
        return super().read(size)

    def geturl(self):
        return "https://storage.example/object?secret=DO_NOT_RECORD"


def csv_bytes(rows=8):
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(HEADER_FIELDS)
    for i in range(rows):
        writer.writerow(["deribit", "BTC-PERPETUAL", str(1577836800000000+i), str(1577836800000100+i)] + [
            item for level in range(5) for item in (100.5+level*.5, 10+i, 100-level*.5, 20+i)
        ])
    return output.getvalue().encode()


def test_complete_rows_row_cap_hashes_and_reuse(tmp_path):
    raw = csv_bytes()
    compressed = gzip.compress(raw, mtime=0)
    requests = []

    def opener(request, timeout):
        requests.append(request)
        return Response(compressed)

    manifest = download_excerpt("2020-01-01", tmp_path, max_rows=3, opener=opener)
    excerpt = (tmp_path / manifest["path"]).read_bytes()
    assert excerpt == b"".join(raw.splitlines(keepends=True)[:4])
    assert manifest["retained_rows"] == 3
    assert manifest["excerpt_sha256"] == hashlib.sha256(excerpt).hexdigest()
    assert manifest["compressed_sha256"] == hashlib.sha256(compressed).hexdigest()
    assert manifest["complete_source_gzip"] is True
    assert "DO_NOT_RECORD" not in json.dumps(manifest)
    assert requests[0].get_header("Range") == "bytes=0-2097151"
    assert not requests[0].has_header("Authorization")
    again = download_excerpt("2020-01-01", tmp_path, max_rows=3, opener=lambda *_args, **_kw: pytest.fail("reuse must stay offline"))
    assert again == manifest
    (tmp_path / manifest["path"]).write_bytes(b"corrupt")
    with pytest.raises(AcquisitionError, match="checksum"):
        download_excerpt("2020-01-01", tmp_path, max_rows=3, opener=opener)


def test_partial_gzip_does_not_claim_whole_source_integrity(tmp_path):
    compressed = gzip.compress(csv_bytes(), mtime=0)
    partial = compressed[:-8]
    manifest = download_excerpt(
        "2020-01-01", tmp_path,
        opener=lambda *_args, **_kw: Response(partial, source_length=len(compressed)),
    )
    assert manifest["complete_source_gzip"] is False
    assert "NOT verified" in manifest["integrity_scope"]
    assert manifest["bytes_received"] == len(partial)
    assert manifest["retained_rows"] == 8


def test_ignored_range_large_response_is_rejected_without_read(tmp_path):
    response = Response(b"", status=200, headers={"Content-Length": "999999999"})
    with pytest.raises(AcquisitionError, match="ignored Range"):
        download_excerpt("2020-01-01", tmp_path, opener=lambda *_args, **_kw: response)
    assert response.read_calls == 0
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("date", ["2020-01-02", "2020-2-01", "2020-13-01", "bad"])
def test_only_free_calendar_dates_are_permitted(date, tmp_path):
    with pytest.raises(AcquisitionError):
        download_excerpt(date, tmp_path, opener=lambda *_args, **_kw: pytest.fail("no network"))


def test_bad_range_schema_and_zip_bomb_are_rejected(tmp_path):
    data = gzip.compress(csv_bytes())
    with pytest.raises(AcquisitionError, match="starting at byte zero"):
        download_excerpt("2020-01-01", tmp_path, opener=lambda *_args, **_kw: Response(data, headers={"Content-Range": f"bytes 1-{len(data)}/{len(data)+1}"}))
    with pytest.raises(AcquisitionError, match="schema"):
        download_excerpt("2020-01-01", tmp_path, opener=lambda *_args, **_kw: Response(gzip.compress(b"wrong,columns\n1,2\n")))
    with pytest.raises(AcquisitionError, match="Decompression budget"):
        download_excerpt("2020-01-01", tmp_path, max_decompressed_bytes=32, opener=lambda *_args, **_kw: Response(data))


def test_contract_or_aggregate_budget_mismatch_is_rejected(tmp_path):
    with pytest.raises(AcquisitionError, match="aggregate budget"):
        download_many(["2020-01-01", "2020-02-01"], tmp_path, max_compressed_bytes=512, max_total_compressed_bytes=1000)
    with pytest.raises(AcquisitionError, match="distinct"):
        download_many(["2020-01-01", "2020-01-01"], tmp_path)
    with pytest.raises(AcquisitionError, match="supports"):
        download_excerpt("2020-01-01", tmp_path, exchange="other")
    compressed = gzip.compress(csv_bytes())
    download_excerpt("2020-01-01", tmp_path, max_rows=3, opener=lambda *_args, **_kw: Response(compressed))
    with pytest.raises(AcquisitionError, match="different acquisition contract"):
        download_excerpt("2020-01-01", tmp_path, max_rows=4)


@pytest.mark.parametrize("kwargs", [
    {"max_compressed_bytes":0}, {"max_compressed_bytes":2*1024**2+1},
    {"max_rows":20001}, {"max_rows":True}, {"timeout":0},
])
def test_bounds_are_checked_before_network(kwargs, tmp_path):
    with pytest.raises(AcquisitionError):
        download_excerpt("2020-01-01", tmp_path, opener=lambda *_args, **_kw: pytest.fail("no network"), **kwargs)
