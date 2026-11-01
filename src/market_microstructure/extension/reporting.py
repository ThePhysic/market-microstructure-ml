"""Small offline evidence report; no live data service or simulated controls."""
from __future__ import annotations

from html import escape
import json
from pathlib import Path
from typing import Any

from ..manifests import write_json


def _text(value: Any) -> str:
    if value is None:
        return "Not reported"
    if isinstance(value, float):
        return f"{value:.6f}"
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    return str(value)


def _table(headers: list[str], rows: list[list[Any]], caption: str) -> str:
    return '<div class="table" role="region" tabindex="0" aria-label="' + escape(caption, quote=True) + '"><table><caption>' + escape(caption) + '</caption><thead><tr>' + ''.join('<th scope="col">' + escape(h) + '</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + escape(_text(v)) + '</td>' for v in row) + '</tr>' for row in rows) + '</tbody></table></div>'


def _details(title: str, value: Any) -> str:
    return '<details><summary>' + escape(title) + '</summary><pre tabindex="0">' + escape(json.dumps(value, indent=2, ensure_ascii=False)) + '</pre></details>'


def write_report(result: dict[str, Any], output: str | Path) -> dict[str, str]:
    target = Path(output)
    target.mkdir(parents=True, exist_ok=True)
    synthetic = result.get("kind") == "synthetic_fixture"
    banner = "SYNTHETIC DEMONSTRATION — no market evidence" if synthetic else "HISTORICAL RESEARCH — hypothetical execution only"
    research = result.get("research", {})
    rows = []
    for scenario, models in result.get("simulations", {}).items():
        for model, record in models.items():
            metrics = record["aggregate"]
            rows.append([scenario, model, metrics.get("net_pnl_quote", metrics.get("net_pnl")),
                         metrics.get("gross_pnl_quote", metrics.get("gross_pnl")),
                         metrics.get("fees_quote", metrics.get("fees")),
                         metrics.get("fill_count", metrics.get("fills")),
                         metrics.get("unresolved_position_segments")])
    simulation_table = _table(["Scenario", "Signal", "Net P&L (USD)", "Gross P&L (USD)", "Fees (USD)", "Fills", "Unresolved segments"], rows, "Independent-segment simulation totals") if rows else '<p>No execution results in this development-only artifact.</p>'
    limitations = result.get("limitations", [])
    body = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(result.get('experiment_id', 'Development'))} · Quantitative research</title>
<style>
:root{{color-scheme:light;--ink:#19392d;--muted:#456355;--line:#d4dfd7}}*{{box-sizing:border-box}}body{{margin:0;background:#f4f6f1;color:var(--ink);font:16px/1.65 "Segoe UI",Arial,sans-serif}}header{{background:#18372b;color:#f3f8ec;padding:30px max(20px,calc((100vw - 1150px)/2));overflow-wrap:anywhere}}main{{max-width:1190px;margin:auto;padding:24px 20px}}section{{background:white;border:1px solid var(--line);border-radius:10px;padding:24px;margin-bottom:22px;min-width:0}}h1{{font:38px/1.2 Georgia,serif;max-width:850px}}h2{{font-size:24px;margin:0 0 14px}}h3{{font-size:19px}}a{{color:#246344;text-underline-offset:3px}}header a{{color:#d2ef9a}}nav{{display:flex;gap:18px;flex-wrap:wrap}}.banner{{font-weight:700;letter-spacing:.06em;font-size:14px;color:#d2ef9a}}.lead{{font-size:18px}}.table{{overflow:auto;max-width:100%;border:1px solid var(--line);border-radius:6px}}table{{border-collapse:collapse;min-width:780px;width:100%;font-size:15px}}caption{{text-align:left;padding:14px;font-weight:600}}th,td{{padding:11px 14px;border-top:1px solid var(--line);text-align:left;vertical-align:top}}th{{background:#edf3e6}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#f1f5ef;padding:16px;max-height:500px;overflow:auto;font-size:14px}}details{{margin:15px 0}}summary{{cursor:pointer;font-weight:600}}:focus-visible{{outline:3px solid #518635;outline-offset:3px}}.muted{{color:var(--muted)}}li{{margin:8px 0}}code,.identity{{overflow-wrap:anywhere}}@media(max-width:500px){{h1{{font-size:30px}}section{{padding:18px}}main{{padding:18px 12px}}}}
</style></head><body><header><div class="banner">{banner}</div><h1>From order-book evidence to explicit simulation assumptions</h1><p class="identity">{escape(result.get('experiment_id', 'Development planning'))}</p><nav aria-label="Report sections"><a href="#research">Research</a><a href="#execution">Execution</a><a href="#limits">Limits</a><a href="#reproduce">Reproduce</a></nav></header><main>
<section><h2>How to read this report</h2><p class="lead">Prediction quality, hypothetical trading performance and software correctness are separate assessments.</p><p>Read the research decision first, compare all declared execution scenarios, then inspect the assumptions and provenance. A positive classification comparison does not establish profitable trading.</p><p><a href="experiment.json">Machine-readable aggregate evidence</a> · <a href="report.md">Plain-text report</a></p></section>
<section id="research"><h2>Research comparison</h2><p>Primary: book-feature logistic regression versus price-history-only logistic regression. Secondary: boosted trees versus book-feature logistic regression. The practical improvement threshold is declared before final evaluation.</p>{_details('Research decisions, uncertainty and model metrics', research)}{_details('Development-only precision plan', research.get('precision_plan', {}))}</section>
<section id="execution"><h2>Hypothetical execution</h2><p>Long/flat, unlevered spot; marketable IOC orders execute only on later observed books. Fees, adverse slippage and action delays are research assumptions. Queue position, market impact and exchange-realistic fills are not established.</p>{simulation_table}<p class="muted">Totals sum independent segment trials with capital reset. Unclosed inventory is marked at the segment’s observed best bid; it is not an executed liquidation. These totals are not a continuously investable equity curve.</p>{_details('Declared scenarios and accounting configuration', {'simulation': result.get('config', {}).get('simulation'), 'scenarios': result.get('config', {}).get('scenarios')})}{_details('Full aggregate execution metrics', result.get('simulations', {}))}</section>
<section id="limits"><h2>What the evidence does and does not support</h2><ul>{''.join('<li>'+escape(str(x))+'</li>' for x in limitations)}</ul>{_details('External method adaptation, not numerical reproduction', result.get('replication', {}))}{_details('Coverage and validation evidence', result.get('coverage', {}))}</section>
<section id="reproduce"><h2>Reproduce the evidence</h2><p>Use the locked Python environment and obtain your own checksum-matching data under the provider terms. Detailed historical signals, orders, fills, ledgers and models remain local.</p><pre tabindex="0">uv sync --frozen --extra dev\nuv run --offline python -m market_microstructure.extension reproduce --reference reports/extension/reference/experiment.json --raw-dir data/extension/raw --output artifacts/extension/reproduction</pre><p>The synthetic demo runs offline and requires no historical data. See the project README for the complete acquisition and experiment workflow.</p>{_details('Content identities and runtime provenance', {key: result.get(key) for key in ('protocol_identity', 'dataset_identity', 'source_identity', 'provenance', 'freeze')})}</section>
</main></body></html>'''
    write_json(target / "experiment.json", result)
    (target / "report.html").write_text(body, encoding="utf-8", newline="\n")
    markdown = f"# Quantitative research and simulation\n\n{banner}\n\nExperiment: {result.get('experiment_id', 'Development')}\n\n## Research\n\n```json\n{json.dumps(research, indent=2)}\n```\n\n## Execution\n\nIndependent-segment hypothetical trials; unresolved inventory marked at bid, not executed.\n\n```json\n{json.dumps(result.get('simulations', {}), indent=2)}\n```\n\n## Limitations\n\n" + '\n'.join('- '+str(x) for x in limitations) + '\n'
    (target / "report.md").write_text(markdown, encoding="utf-8", newline="\n")
    return {"json": str(target / "experiment.json"), "html": str(target / "report.html"), "markdown": str(target / "report.md")}
