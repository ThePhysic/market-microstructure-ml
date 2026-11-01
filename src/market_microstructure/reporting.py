"""Offline aggregate reports: no services, model execution or remote assets.

The supplied experiment result must contain aggregate evidence only. Raw market
rows, individual predictions and fitted weights do not belong in that result.
"""

from __future__ import annotations

import html
import json
import math
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

MODEL_NAMES = {
    "majority": "Simple majority baseline",
    "logistic": "Logistic regression",
    "boosted": "Small boosted trees",
}
MODEL_ORDER = ("majority", "logistic", "boosted")
NAVIGATION = (
    ("overview", "Overview"), ("models", "Model results"),
    ("validation", "Time-split audit"), ("quality", "Data quality"),
    ("research-note", "Research note"), ("provenance", "Provenance"),
)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> list[Any] | tuple[Any, ...]:
    return value if isinstance(value, (list, tuple)) else []


def _h(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _number(value: Any, digits: int = 3) -> str:
    if isinstance(value, bool):
        return "Not recorded"
    try:
        converted = float(value)
    except (TypeError, ValueError, OverflowError):
        return "Not recorded"
    return f"{converted:.{digits}f}" if math.isfinite(converted) else "Not recorded"


def _count(value: Any) -> str:
    if isinstance(value, bool):
        return "Not recorded"
    try:
        converted = float(value)
    except (TypeError, ValueError, OverflowError):
        return "Not recorded"
    if not math.isfinite(converted) or converted < 0 or not converted.is_integer():
        return "Not recorded"
    return f"{int(converted):,}"


def _dates(value: Any) -> str:
    dates = [str(item) for item in _sequence(value)]
    return ", ".join(dates) if dates else "Not recorded"


def _md(value: Any) -> str:
    value = html.escape(str(value), quote=False).replace("\\", "\\\\")
    for character in "|" + chr(96) + "[]()!*_":
        value = value.replace(character, "\\" + character)
    return value.replace("\r", " ").replace("\n", " ")


def _code_block(value: str) -> str:
    tick = chr(96)
    longest = max((len(match) for match in re.findall(tick + "+", value)), default=0)
    fence = tick * max(3, longest + 1)
    return f"{fence}text\n{value}\n{fence}"


def _source_link(value: Any) -> str:
    text = str(value or "Not recorded")
    try:
        parsed = urlsplit(text)
        allowed = (
            parsed.scheme in {"https", "http"} and bool(parsed.netloc)
            and parsed.username is None and parsed.password is None
        )
    except ValueError:
        allowed = False
    return f'<a href="{_h(text)}" rel="noreferrer">{_h(text)}</a>' if allowed else _h(text)


def _table(headers: list[str], rows: list[list[str]], label: str) -> str:
    if not rows:
        return '<p class="empty">No records were supplied for this section.</p>'
    return (
        '<p class="scroll-hint">On a narrow screen, swipe this table sideways. '
        'With a keyboard, focus the table and use the left/right arrow keys.</p>'
        f'<div class="table-wrap" tabindex="0" role="region" aria-label="{_h(label)}">'
        '<table><thead><tr>'
        + "".join(f'<th scope="col">{_h(header)}</th>' for header in headers)
        + "</tr></thead><tbody>"
        + "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
        + "</tbody></table></div>"
    )


def _markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        return "No records were supplied for this section."
    return "\n".join(
        ["| " + " | ".join(_md(item) for item in headers) + " |",
         "| " + " | ".join("---" for _ in headers) + " |"]
        + ["| " + " | ".join(_md(cell) for cell in row) + " |" for row in rows]
    )


def _model_rows(result: Mapping[str, Any]) -> list[list[str]]:
    summary = _mapping(_mapping(result.get("development")).get("summary"))
    final = _mapping(_mapping(result.get("holdout")).get("models"))
    keys = set(summary) | set(final)
    models = [name for name in MODEL_ORDER if name in keys] + sorted(keys - set(MODEL_ORDER))
    rows = []
    for name in models:
        earlier, later = _mapping(summary.get(name)), _mapping(final.get(name))
        rows.append([
            MODEL_NAMES.get(name, name), _number(earlier.get("macro_f1_mean")),
            _number(earlier.get("macro_f1_std")), _number(earlier.get("balanced_accuracy_mean")),
            _number(later.get("macro_f1")), _number(later.get("balanced_accuracy")),
            _count(later.get("support")),
        ])
    return rows


def _fold_rows(result: Mapping[str, Any]) -> list[list[str]]:
    rows = []
    folds = [(item, "Development") for item in _sequence(_mapping(result.get("development")).get("folds"))]
    final = _mapping(result.get("holdout"))
    if final:
        folds.append((final, "Final holdout"))
    for value, purpose in folds:
        fold = _mapping(value)
        rows.append([
            str(fold.get("name", purpose)), purpose, _dates(fold.get("train_dates")),
            _dates(fold.get("test_dates")), _count(fold.get("train_count")),
            _count(fold.get("test_count")), _count(fold.get("purged_count")),
        ])
    return rows


def _quality_rows(quality: Any, prefix: str = "") -> list[list[str]]:
    """Display scalar aggregate fields, never per-record diagnostic lists."""
    rows: list[list[str]] = []
    for key, value in _mapping(quality).items():
        if key in {"exclusions", "per_file", "rows", "records", "predictions"}:
            continue
        label = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, Mapping):
            rows.extend(_quality_rows(value, label))
        elif value is None or isinstance(value, (str, int, float, bool)):
            rows.append([label, str(value)])
    return rows


def _source_rows(result: Mapping[str, Any]) -> list[list[str]]:
    rows = []
    for value in _sequence(result.get("source_manifest")):
        item = _mapping(value)
        rows.append([
            str(item.get("date", "Not recorded")),
            str(item.get("retrieval_url", item.get("source_url", "Not recorded"))),
            _count(item.get("retained_rows")), _count(item.get("bytes_received")),
            _count(item.get("excerpt_bytes")),
            str(item.get("excerpt_sha256", item.get("sha256", "Not recorded"))),
            str(item.get("compressed_sha256", "Not recorded")),
        ])
    return rows


def _comparison_rows(result: Mapping[str, Any]) -> list[list[str]]:
    comparisons = _mapping(_mapping(result.get("development")).get("paired_comparisons"))
    rows = []
    for name, value in comparisons.items():
        comparison = _mapping(value)
        lower, upper = comparison.get("ci_lower"), comparison.get("ci_upper")
        try:
            confidence = float(comparison.get("confidence"))
        except (TypeError, ValueError, OverflowError):
            confidence = None
        confidence_label = (
            f"{100 * confidence:g}%"
            if confidence is not None and math.isfinite(confidence) and 0 < confidence < 1
            else "Confidence level not recorded"
        )
        interval = (
            f"{confidence_label} [{_number(lower)}, {_number(upper)}]"
            if lower is not None and upper is not None else
            f"{confidence_label}: interval not reported; insufficient evaluation dates"
        )
        rows.append([
            str(name).replace("_vs_", " minus ").replace("_", " "),
            _count(comparison.get("n_units")), _number(comparison.get("mean_difference")),
            interval, str(comparison.get("status", "Not recorded")),
        ])
    return rows


def _robustness_rows(result: Mapping[str, Any]) -> list[list[str]]:
    rows = []
    for change, value in _mapping(result.get("robustness")).items():
        for model, scores in _mapping(_mapping(value).get("summary")).items():
            scores = _mapping(scores)
            rows.append([
                str(change).replace("_", " "), MODEL_NAMES.get(model, model),
                _number(scores.get("macro_f1_mean")), _number(scores.get("balanced_accuracy_mean")),
            ])
    return rows


def _class_rows(result: Mapping[str, Any]) -> list[list[str]]:
    rows = []
    for model, value in _mapping(_mapping(result.get("holdout")).get("models")).items():
        for item in _sequence(_mapping(value).get("per_class")):
            item = _mapping(item)
            rows.append([
                MODEL_NAMES.get(model, model), str(item.get("name", item.get("label", "Not recorded"))),
                _number(item.get("precision")), _number(item.get("recall")),
                _number(item.get("f1")), _count(item.get("support")),
            ])
    return rows


def _warnings(result: Mapping[str, Any]) -> list[str]:
    warnings = [str(value) for value in _sequence(result.get("warnings"))]
    for model, metrics in _mapping(_mapping(result.get("holdout")).get("models")).items():
        warnings.extend(
            f"{MODEL_NAMES.get(model, model)}: {warning}"
            for warning in _sequence(_mapping(metrics).get("warnings"))
        )
    for name, comparison in _mapping(_mapping(result.get("development")).get("paired_comparisons")).items():
        warnings.extend(f"{name}: {warning}" for warning in _sequence(_mapping(comparison).get("warnings")))
    return list(dict.fromkeys(warnings))


def _development_dates(result: Mapping[str, Any]) -> list[str]:
    dates: set[str] = set()
    for fold in _sequence(_mapping(result.get("development")).get("folds")):
        dates.update(str(value) for value in _sequence(_mapping(fold).get("test_dates")))
    return sorted(dates)


CSS = """
:root{--ink:#20362a;--muted:#4e6651;--line:#dce5d8;--green:#2e7250;--lime:#d5ef98;--paper:#f4f6f0;--mono:Consolas,monospace}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.75 "Segoe UI",Arial,sans-serif}
a{color:#286342;text-underline-offset:3px}a:focus-visible,summary:focus-visible,.table-wrap:focus-visible,pre:focus-visible{outline:3px solid #34784f;outline-offset:3px}
.skip{position:absolute;left:20px;top:-80px;z-index:20;background:var(--lime);padding:10px 16px}.skip:focus{top:12px}
.sidebar{position:fixed;inset:0 auto 0 0;width:224px;overflow-y:auto;background:#19271f;color:#dfeadc;padding:32px 23px;display:flex;flex-direction:column}
.brand{font-size:27px;font-weight:650;letter-spacing:-1.2px}.brand span{color:var(--lime)}.brand small{font:11px var(--mono);display:block;letter-spacing:1.2px;color:#a1b79c;margin-top:5px}
.sidebar nav{display:grid;gap:8px;margin-top:42px}.sidebar nav a{font-size:14px;color:#c7d6c2;text-decoration:none;border-radius:6px;padding:10px 12px}.sidebar nav a:hover{background:#2b4030;color:var(--lime)}.sidebar nav a:focus-visible{outline-color:var(--lime)}
.sidebar-note{margin-top:auto;padding-top:40px;color:#a6bda0;font-size:14px}.sidebar-note strong{display:block;font:23px Georgia,serif;color:#e1eadb;margin-bottom:10px}
.workspace{margin-left:224px}.topbar{display:flex;gap:20px;align-items:center;justify-content:space-between;padding:22px 38px;background:#fff;border-bottom:1px solid var(--line);font-size:14px}
.topbar-links{display:flex;gap:11px;flex-wrap:wrap}.button{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:8px 14px;border:1px solid #ccd9c4;border-radius:6px;background:#fff;text-decoration:none;font-size:14px;color:#36582c}
.button:hover{background:#edf3e6}.button.primary{background:#243f2b;color:#f2f6ed;border-color:#243f2b}.notice{padding:15px 38px;background:#e9f0e0;border-bottom:1px solid #ceddc0;color:#3d5e30;font-size:14px}.notice.synthetic{background:#fbf0d8;color:#75551e;border-color:#e6d3a9}.notice strong{margin-right:7px}
main{max-width:1520px;margin:auto;padding:34px 38px;outline:none}section{scroll-margin-top:20px;margin-bottom:30px}.eyebrow{font:12px var(--mono);letter-spacing:1.5px;color:#526b45;text-transform:uppercase}
h1{font:44px/1.15 Georgia,serif;letter-spacing:-1.1px;max-width:900px;margin:13px 0 18px}h2{font-size:24px;letter-spacing:-.5px;line-height:1.3;margin:0 0 13px}h3{font-size:17px;line-height:1.5;margin:18px 0 8px}p{margin:0 0 15px;max-width:980px}.intro{font-size:17px;color:#48633d;max-width:850px;line-height:1.8}.meta{display:flex;gap:12px 22px;flex-wrap:wrap;font:12px/1.8 var(--mono);color:#4c6840;overflow-wrap:anywhere;margin-bottom:24px}
.reading-guide{border:1px solid #d6e1cc;border-radius:8px;background:#eef4e6;padding:21px 24px;margin:24px 0}.reading-guide h2{font-size:19px}.reading-guide ol{margin:10px 0 0;padding-left:23px}.reading-guide li{padding:4px 0;color:#455f38}
.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:15px;margin:24px 0}.metric-card{background:#fff;border:1px solid var(--line);border-radius:8px;padding:19px}.metric-card span{display:block;font-size:14px;color:#4a653e}.metric-card strong{display:block;font:31px/1.5 var(--mono);letter-spacing:-1px;color:#2e5030;overflow-wrap:anywhere}.metric-card p{font-size:14px;margin:3px 0 0;color:#58714b}
.panel{background:#fff;border:1px solid var(--line);border-radius:8px;padding:24px;margin:20px 0}.panel h2{font-size:22px}.panel h3:first-child{margin-top:0}.callout{background:#edf3e5;border-left:4px solid #82a464;border-radius:0 6px 6px 0;padding:18px 20px;margin:18px 0;color:#405e32}.callout.warning{background:#faf0dc;border-color:#c7a15b;color:#74571f}.callout p:last-child{margin-bottom:0}
.table-wrap{overflow-x:auto;max-width:100%;border:1px solid var(--line);border-radius:6px;scrollbar-width:thin;overscroll-behavior-x:contain}.table-wrap:focus-visible{outline-offset:-3px}table{border-collapse:collapse;width:100%;min-width:660px;font-size:14px}th,td{text-align:left;vertical-align:top;border-bottom:1px solid #e6ece1;padding:12px 14px}th{background:#f1f5ec;color:#3c5d2f;font-weight:600;font-size:14px}td{color:#49623c}tbody tr:last-child td{border-bottom:0}.scroll-hint{font-size:14px;color:#566e47;margin:15px 0 9px}.wide table{min-width:960px}.hash{font:12px/1.7 var(--mono);overflow-wrap:anywhere;max-width:230px;display:block}.source-url{overflow-wrap:anywhere;min-width:240px;display:block}
.legend{font-size:14px;color:#49643c;background:#f2f6ed;padding:16px 18px;border-radius:6px;margin:18px 0}.legend p:last-child{margin-bottom:0}.warning-list{padding-left:23px;color:#70552c;overflow-wrap:anywhere}.warning-list li{margin:7px 0}.empty{padding:16px;background:#f4f5f0;border:1px dashed #cfd8c7;color:#627455;border-radius:6px}
details{border:1px solid var(--line);border-radius:7px;background:#fff;margin:18px 0}summary{cursor:pointer;min-height:46px;padding:13px 17px;font-size:15px;font-weight:600;color:#3b602d}details>.details-body{padding:0 18px 18px}pre{background:#1e3023;color:#deebd1;padding:20px;border-radius:6px;white-space:pre-wrap;overflow-wrap:anywhere;max-height:440px;overflow:auto;font:13px/1.8 var(--mono);max-width:100%}code{font-family:var(--mono);font-size:.92em}
.note{color:#516b43;font-size:14px}.research-text{white-space:pre-line}.footer{padding:12px 0 5px;font:12px/1.8 var(--mono);letter-spacing:.4px;color:#5d7350;border-top:1px solid var(--line)}
@media(max-width:1100px){.cards{grid-template-columns:repeat(2,minmax(0,1fr))}h1{font-size:39px}}
@media(max-width:900px){.sidebar{position:static;width:auto;display:block;padding:22px 24px}.sidebar nav{display:flex;flex-wrap:wrap;gap:6px 12px;margin-top:20px}.sidebar nav a{padding:8px 10px}.sidebar-note{display:none}.workspace{margin-left:0}.topbar{padding:18px 24px;flex-wrap:wrap}.notice{padding:15px 24px}main{padding:27px 24px}}
@media(max-width:500px){.sidebar{padding:20px}.sidebar nav{gap:5px}.sidebar nav a{font-size:14px}.brand{font-size:25px}.topbar{padding:17px 20px}.topbar-links{width:100%}.topbar-links .button{flex:1 1 140px}.notice{padding:15px 20px}main{padding:25px 20px}h1{font-size:35px;line-height:1.18}h2{font-size:22px}.intro{font-size:16px}.panel{padding:20px 17px}.cards{gap:12px}.metric-card{padding:17px 13px}.metric-card strong{font-size:26px}.metric-card p,.metric-card span{font-size:14px}.reading-guide{padding:19px 17px}.callout{padding:17px 15px}.meta{gap:8px 14px}.hash{font-size:12px}pre{padding:17px;font-size:13px}.scroll-hint{font-size:14px}}
@media(max-width:360px){.cards{grid-template-columns:minmax(0,1fr)}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{.sidebar,.topbar-links,.skip,.scroll-hint{display:none}.workspace{margin-left:0}main{padding:0}.topbar,.notice{padding-left:0;padding-right:0}.panel{break-inside:avoid}.table-wrap{overflow:visible}table,.wide table{min-width:0;font-size:10px}th,td{padding:6px;font-size:10px}.cards{grid-template-columns:repeat(4,1fr)}pre{max-height:none}}
"""


def _html_report(result: Mapping[str, Any]) -> str:
    experiment_id = result.get("experiment_id", "Unrecorded experiment")
    kind = result.get("kind")
    synthetic = kind == "synthetic_fixture"
    if synthetic:
        evidence_label = "SYNTHETIC FIXTURE — DEMONSTRATION ONLY"
        evidence_note = "No empirical market findings. These values exercise the software and report format."
    elif kind == "real_historical":
        evidence_label = "REAL HISTORICAL DATA — BOUNDED EXCERPTS"
        evidence_note = "Historical classification scores do not establish trading profitability."
    else:
        evidence_label = "EVIDENCE TYPE NOT RECORDED"
        evidence_note = "Do not treat this artifact as validated market research until its provenance is established."
    config = _mapping(result.get("config"))
    horizon = config.get("horizon_events", _mapping(config.get("research")).get("horizon_events"))
    horizon_text = f"{_count(horizon)} observed book states later" if horizon is not None else "at the recorded prediction horizon"
    observed = _sequence(result.get("observed_dates"))
    development_dates = _development_dates(result)
    final, conclusion = _mapping(result.get("holdout")), _mapping(result.get("conclusion"))
    cards = [
        ("Observed dates", _count(len(observed)), "Separate observed excerpts, not a continuous history."),
        ("Eligible labeled samples", _count(result.get("sample_count")), "Correlated book updates are not independent evidence."),
        ("Development test dates", _count(len(development_dates)), "Earlier-period evaluation; settings fixed before final testing."),
        ("Final holdout dates", _count(len(_sequence(final.get("test_dates")))), "Later dates reserved outside model selection."),
    ]
    score_table = _table(
        ["Method", "Development macro F1", "Across-date SD", "Development balanced accuracy", "Final macro F1", "Final balanced accuracy", "Final sample count"],
        [[_h(cell) for cell in row] for row in _model_rows(result)], "Model score comparison",
    )
    fold_table = _table(
        ["Split", "Purpose", "Training dates", "Evaluation dates", "Training samples", "Evaluation samples", "Purged"],
        [[_h(cell) for cell in row] for row in _fold_rows(result)], "Chronological training and evaluation splits",
    )
    comparisons = _table(
        ["Comparison (A minus B)", "Evaluation dates", "Mean macro F1 difference", "Exploratory macro F1 interval", "Status"],
        [[_h(cell) for cell in row] for row in _comparison_rows(result)], "Paired development-date comparisons",
    )
    robustness = _table(
        ["Predeclared change", "Method", "Development macro F1", "Development balanced accuracy"],
        [[_h(cell) for cell in row] for row in _robustness_rows(result)], "Development-only robustness checks",
    )
    class_table = _table(
        ["Method", "Actual class", "Precision", "Recall", "F1", "Actual sample count"],
        [[_h(cell) for cell in row] for row in _class_rows(result)], "Final holdout performance by outcome class",
    )
    source_rows = [
        [_h(row[0]), f'<span class="source-url">{_source_link(row[1])}</span>']
        + [_h(value) for value in row[2:5]]
        + [f'<code class="hash">{_h(value)}</code>' for value in row[5:]]
        for row in _source_rows(result)
    ]
    sources = _table(
        ["Date", "Exact source URL", "Retained rows", "Compressed bytes received", "CSV excerpt bytes", "Excerpt SHA-256", "Compressed-prefix SHA-256"],
        source_rows, "Source URLs, local excerpt checksums and byte sizes",
    )
    quality_table = _table(
        ["Aggregate quality field", "Recorded value"],
        [[_h(cell) for cell in row] for row in _quality_rows(result.get("quality"))], "Aggregate ingestion and feature quality",
    )
    warnings = _warnings(result)
    warning_html = (
        '<ul class="warning-list">' + "".join(f"<li>{_h(value)}</li>" for value in warnings) + "</ul>"
        if warnings else '<p class="note">No additional warnings were supplied in the experiment record.</p>'
    )
    commands = [str(value) for value in _sequence(result.get("reproduction_commands"))]
    reproduction = (
        f'<pre tabindex="0" aria-label="Exact reproduction commands">{_h(chr(10).join(commands))}</pre>'
        if commands else '<p class="empty">Exact reproduction commands were not recorded. Consult the project README and configuration before attempting a rerun.</p>'
    )
    audit = _h(json.dumps(result.get("split_audit", {}), indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))
    fingerprints = _h(json.dumps(
        {"code": result.get("code", {}), "fingerprints": result.get("fingerprints", {}), "config": config, "feature_columns": result.get("feature_columns", [])},
        indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False,
    ))
    nav = "".join(f'<a href="#{identifier}">{_h(label)}</a>' for identifier, label in NAVIGATION)
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{_h(experiment_id)} · Micro / Lab research report</title><style>{CSS}</style></head><body>'
        '<a class="skip" href="#main">Skip to research report</a><aside class="sidebar" aria-label="Report navigation">'
        '<div class="brand">micro<span> / </span>lab<small>RESEARCH EVIDENCE</small></div><nav aria-label="Report sections">'
        + nav + '</nav><div class="sidebar-note"><strong>Built for scrutiny.</strong>Every result should have a trail you can follow.</div></aside>'
        '<div class="workspace"><header class="topbar"><span>Market microstructure / Research report</span><div class="topbar-links">'
        '<a class="button" href="#reading-guide">How to read this</a><a class="button" href="report.md">Technical Markdown</a>'
        '<a class="button primary" href="experiment.json">Open JSON evidence</a></div></header>'
        f'<div class="notice{" synthetic" if synthetic or kind != "real_historical" else ""}"><strong>{_h(evidence_label)}</strong> {_h(evidence_note)}</div>'
        '<main id="main" tabindex="-1"><section id="overview"><div class="eyebrow">A reproducible research process</div>'
        '<h1>Order-book prediction,<br>with an evidence trail.</h1>'
        f'<p class="intro">Can orders waiting to buy and sell help predict whether the mid-price moves down, stays within a no-change band or moves up, {_h(horizon_text)}? This offline report compares simple methods and records how the evidence was checked.</p>'
        '<p class="note">An order book lists waiting buy and sell orders; a book state is one snapshot of that list. Mid-price means halfway between the best buy and sell prices. “Unchanged” includes small moves inside the frozen target threshold, not only identical prices. Exact threshold and tick-size settings appear in the configuration record. This report places no orders.</p>'
        f'<div class="meta"><span>EXPERIMENT {_h(experiment_id)}</span><span>CREATED {_h(result.get("created_at", "Not recorded"))}</span></div>'
        '<div class="reading-guide" id="reading-guide"><h2>Start here: three things to check</h2><ol>'
        '<li><a href="#models">Compare the methods.</a> Read earlier-date results separately from the final later-date holdout.</li>'
        '<li><a href="#validation">Inspect the time boundaries.</a> Inputs must be available when each prediction is made.</li>'
        '<li><a href="#research-note">Read the conclusion and limitations.</a> A negative or uncertain result is a valid outcome.</li></ol></div>'
        '<div class="cards">'
        + "".join(f'<div class="metric-card"><span>{_h(label)}</span><strong>{_h(value)}</strong><p>{_h(note)}</p></div>' for label, value, note in cards)
        + '</div><div class="callout"><strong>What the data covers</strong>'
        f'<p>This record contains {_count(len(observed))} observed dates and {_count(len(development_dates))} development evaluation dates. The intended real-data study uses noncontiguous opening excerpts from month-start files, not complete trading days or a continuous backtest. Many correlated updates do not create many independent dates.</p></div></section>'
        '<section id="models"><div class="eyebrow">Comparison / same eligible samples</div><h2>How did the methods compare?</h2>'
        '<div class="legend"><p><strong>Both scores range from 0 to 1; higher is better.</strong> Macro F1 balances false alarms and missed outcomes, giving down, unchanged and up equal weight. Balanced accuracy averages the fraction correctly recognized in each actual class present in that evaluation period. Missing classes are disclosed in warnings.</p>'
        '<p>The majority baseline always predicts the most common training outcome. Logistic regression is the simple linear comparison. Small boosted trees model more flexible relationships. A score improvement is not a return or profit estimate.</p></div>'
        + score_table
        + '<p class="note">Development values are date-level means; SD is their descriptive standard deviation. Final values are the recorded scores on the reserved later dates. These are different summaries and should not be pooled into a single selection score.</p>'
        '<details><summary>Inspect final results for each outcome class</summary><div class="details-body">'
        + class_table + '<p class="note">Precision asks how often predictions of a class were correct. Recall asks how many actual examples of that class were recognized. Support is the actual example count.</p></div></details></section>'
        '<section id="validation"><div class="eyebrow">Causal inputs / chronological evaluation</div><h2>Was future information kept out?</h2>'
        '<p>Each development fold trains on earlier dates and evaluates on a later date. “Purged” samples are removed because their future target interval reaches an evaluation boundary. The final holdout is reserved outside model selection. Overlapping training sets do not make their evaluation dates extra independent observations.</p>'
        + fold_table
        + '<details><summary>Inspect the recorded split audit</summary><div class="details-body">'
        f'<pre tabindex="0" aria-label="Recorded time-split audit">{audit}</pre></div></details>'
        '<div class="panel"><h3>Uncertainty belongs to dates, not individual updates</h3><p>The paired comparisons resample whole evaluation-date scores. Intervals are exploratory and assume the dates are exchangeable independent units. Fewer than three units produces no interval; a small number of dates remains a substantial limitation.</p>'
        + comparisons
        + '</div><details><summary>Inspect predeclared development-only robustness checks</summary><div class="details-body">'
        '<p>These sensitivity checks use development periods only. They do not provide permission to retune against the final holdout.</p>'
        + robustness
        + '</div></details></section><section id="quality"><div class="eyebrow">Data integrity / exclusions</div><h2>What was retained or excluded?</h2>'
        '<p>Counts below describe the supplied excerpts and feature construction. Vendor snapshots were reconstructed upstream; this project does not claim to have reconstructed the exchange book. Raw market records, individual predictions and model weights are not displayed here.</p>'
        + quality_table + '<div class="panel"><h3>Warnings and qualifications</h3>' + warning_html
        + '</div></section><section id="research-note"><div class="eyebrow">Research note / evidence before claims</div><h2>'
        + _h(conclusion.get("title", "No research conclusion was supplied"))
        + '</h2><div class="callout warning"><p class="research-text">'
        + _h(conclusion.get("text", "The available record is insufficient to support a research conclusion."))
        + '</p></div><h3>Next test</h3><p class="research-text">'
        + _h(conclusion.get("next_test", "Review the missing evidence before proposing another experiment."))
        + '</p><p>Research findings are conditional on the observed instrument, dates, excerpt selection, target definition and data transformations. Classification scores alone establish neither executable latency nor fee-adjusted trading profitability.</p></section>'
        '<section id="provenance"><div class="eyebrow">Reproduction / exact recorded evidence</div><h2>Follow the evidence trail.</h2>'
        '<p>The sibling <a href="experiment.json">experiment.json</a> contains the aggregate evidence behind these tables. The <a href="report.md">Markdown report</a> is a portable technical summary. Keep all three files together when moving this report.</p><h3>Reproduce the recorded experiment</h3>'
        + reproduction
        + '<p class="note">Data acquisition is a separate opt-in command with fixed byte/row limits. Obtain permitted data from its source; raw or sampled market rows and trained weights are excluded from the repository.</p>'
        '<details><summary>Inspect code, configuration and feature fingerprints</summary><div class="details-body">'
        f'<pre tabindex="0" aria-label="Code and configuration metadata">{fingerprints}</pre></div></details>'
        f'<details><summary>Inspect source URLs and excerpt checksums ({_count(len(source_rows))} files)</summary><div class="details-body wide">'
        + sources
        + '<p class="note">Excerpt SHA-256 identifies the local complete-row CSV excerpt. Compressed-prefix SHA-256 identifies downloaded bytes. A prefix does not verify the complete vendor archive or its whole-file gzip CRC. Source files are not redistributed with this report.</p></div></details></section>'
        '<footer class="footer">MARKET MICROSTRUCTURE ML &amp; VALIDATION PIPELINE · OFFLINE AGGREGATE EVIDENCE</footer></main></div></body></html>'
    )


def _markdown_report(result: Mapping[str, Any]) -> str:
    kind = result.get("kind")
    status = (
        "REAL HISTORICAL DATA — BOUNDED EXCERPTS" if kind == "real_historical" else
        "SYNTHETIC FIXTURE — DEMONSTRATION ONLY; NO EMPIRICAL MARKET FINDINGS" if kind == "synthetic_fixture" else
        "EVIDENCE TYPE NOT RECORDED — DO NOT INFER VALIDATED MARKET FINDINGS"
    )
    conclusion, final = _mapping(result.get("conclusion")), _mapping(result.get("holdout"))
    commands = [str(value) for value in _sequence(result.get("reproduction_commands"))]
    observed, development = _sequence(result.get("observed_dates")), _development_dates(result)
    sections = [
        "# Market Microstructure ML & Validation Pipeline", f"**{status}**",
        f"Experiment: {_md(result.get('experiment_id', 'Not recorded'))}  \nCreated: {_md(result.get('created_at', 'Not recorded'))}",
        "## Purpose and interpretation",
        "Test whether causal order-book inputs improve short-horizon mid-price direction predictions beyond a majority rule and a linear baseline. A book state is one snapshot of waiting orders. Mid-price is halfway between the best buy and sell prices. The unchanged class includes moves inside the frozen no-change threshold, not only identical prices. This is prediction research, not evidence of executable or profitable trading.",
        f"Observed dates: {_md(_dates(observed))}. Eligible labeled samples: {_count(result.get('sample_count'))}. Development evaluation dates: {len(development)}. Final holdout dates: {_md(_dates(final.get('test_dates')))}.",
        "The real-data design uses noncontiguous opening excerpts from month-start files, not full trading days or a continuous backtest. Correlated updates are not independent observations.",
        "## Model comparison",
        "Both metrics range from 0 to 1; higher is better. Macro F1 assigns equal weight to the three declared classes. Balanced accuracy averages recalls of true classes present in each evaluation period; missing classes are explicitly warned about. Development scores are date-level means; final scores summarize the reserved later-date holdout.",
        _markdown_table(
            ["Method", "Development macro F1", "Across-date SD", "Development balanced accuracy", "Final macro F1", "Final balanced accuracy", "Final support"],
            _model_rows(result)),
        "## Temporal evaluation",
        "Expanding training folds use earlier observed dates and evaluate on later dates. Label-overlap purging removes training targets that reach the evaluation boundary. Final holdout dates are excluded from selection.",
        _markdown_table(
            ["Split", "Purpose", "Training dates", "Evaluation dates", "Train count", "Evaluation count", "Purged"],
            _fold_rows(result)),
        "## Date-level uncertainty",
        "Paired bootstrap intervals resample whole date/session score differences, not order-book rows. They assume exchangeable independent evaluation dates and remain exploratory; fewer than three units gives no interval. Overlapping training folds do not supply extra independent evidence.",
        _markdown_table(
            ["Comparison A minus B", "Dates", "Mean macro F1 difference", "Exploratory macro F1 interval", "Status"],
            _comparison_rows(result)),
        "## Predeclared development-only robustness",
        "These sensitivity checks do not retune against the final holdout.",
        _markdown_table(["Change", "Method", "Development macro F1", "Development balanced accuracy"], _robustness_rows(result)),
        "## Final class-wise evaluation",
        _markdown_table(["Method", "Class", "Precision", "Recall", "F1", "Support"], _class_rows(result)),
        "## Aggregate quality",
        "Only aggregate diagnostics are displayed. Vendor-reconstructed snapshots do not establish that this project reconstructed exchange books.",
        _markdown_table(["Field", "Value"], _quality_rows(result.get("quality"))),
        "## Research conclusion", f"### {_md(conclusion.get('title', 'No conclusion supplied'))}",
        _md(conclusion.get("text", "The supplied record does not support a research conclusion.")),
        "**Next test:** " + _md(conclusion.get("next_test", "Review missing evidence before another experiment.")),
        "## Warnings",
        "\n".join("- " + _md(value) for value in _warnings(result)) or "No additional warnings were supplied in the experiment record.",
        "## Reproduction",
        _code_block("\n".join(commands)) if commands else "Exact commands were not recorded; consult the project README and configuration before rerunning.",
        "Acquisition is opt-in and bounded. Raw or sampled historical records, row predictions and trained weights are excluded from the repository. Keep report.html, report.md and experiment.json together.",
        "## Source URLs, excerpt hashes and byte sizes",
        _markdown_table(
            ["Date", "Exact source URL", "Retained rows", "Compressed bytes received", "Excerpt bytes", "Excerpt SHA-256", "Compressed-prefix SHA-256"],
            _source_rows(result)),
        "Local prefix/excerpt hashes do not verify the complete vendor archive or whole-file gzip CRC. Obtain permitted data from the source; this report does not redistribute it.",
        "## Recorded configuration and code fingerprints",
        _code_block(json.dumps(
            {"code": result.get("code", {}), "fingerprints": result.get("fingerprints", {}), "config": result.get("config", {}), "feature_columns": result.get("feature_columns", [])},
            indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)),
        "The sibling experiment.json is the machine-readable aggregate evidence for all figures and tables above.",
    ]
    return "\n\n".join(sections) + "\n"


def write_reports(result: dict[str, Any], output_dir: Path) -> dict[str, str]:
    """Write JSON/HTML/Markdown; missing optional fields are not fabricated.

    Non-JSON or nonfinite values fail before any output is written.
    """
    if not isinstance(result, dict):
        raise ValueError("result must be an aggregate experiment dictionary")
    serialized = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    rendered_html, rendered_markdown = _html_report(result), _markdown_report(result)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "html": output_dir / "report.html", "markdown": output_dir / "report.md",
        "json": output_dir / "experiment.json",
    }
    paths["json"].write_text(serialized, encoding="utf-8")
    paths["html"].write_text(rendered_html, encoding="utf-8")
    paths["markdown"].write_text(rendered_markdown, encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}
