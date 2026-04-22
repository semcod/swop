"""
HTML + JSON renderers for :class:`~swop.scan.report.ScanReport`.
"""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path

from swop.scan.report import ScanReport


def render_json(report: ScanReport, pretty: bool = True) -> str:
    return json.dumps(
        report.to_dict(),
        indent=2 if pretty else None,
        sort_keys=False,
        default=str,
    )


def render_html(report: ScanReport) -> str:
    kinds = report.kinds()
    via = report.via()
    ctx_rows = "\n".join(
        (
            "<tr>"
            f"<td>{html.escape(ctx.name)}</td>"
            f"<td>{ctx.files_scanned}</td>"
            f"<td>{ctx.files_cached}</td>"
            f"<td>{ctx.commands}</td>"
            f"<td>{ctx.queries}</td>"
            f"<td>{ctx.events}</td>"
            f"<td>{ctx.handlers}</td>"
            f"<td>{ctx.total}</td>"
            "</tr>"
        )
        for ctx in sorted(report.contexts.values(), key=lambda c: c.name)
    )
    detection_rows = "\n".join(
        (
            f"<tr class=\"via-{html.escape(d.via)}\">"
            f"<td>{html.escape(d.kind)}</td>"
            f"<td>{html.escape(d.context)}</td>"
            f"<td>{html.escape(d.name)}</td>"
            f"<td><code>{html.escape(d.source_file)}:{d.source_line}</code></td>"
            f"<td>{html.escape(d.via)}</td>"
            f"<td>{d.confidence:.2f}</td>"
            f"<td>{html.escape(d.reason)}</td>"
            "</tr>"
        )
        for d in report.detections
    )
    error_items = "".join(
        f"<li><code>{html.escape(err)}</code></li>" for err in report.errors[:50]
    )
    if len(report.errors) > 50:
        error_items += f"<li>… and {len(report.errors) - 50} more</li>"

    generated = datetime.now(timezone.utc).isoformat(timespec="seconds")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>swop scan — {html.escape(report.project)}</title>
<style>
body {{ font: 14px/1.4 system-ui, sans-serif; margin: 2rem auto; max-width: 72rem; color: #222; }}
h1, h2 {{ margin-top: 2rem; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border-bottom: 1px solid #ddd; padding: 0.35rem 0.6rem; text-align: left; }}
th {{ background: #f5f5f5; }}
tr.via-heuristic {{ background: #fff8e1; }}
tr.via-decorator {{ background: #e8f5e9; }}
code {{ font-family: ui-monospace, monospace; background: #f3f3f3; padding: 0 0.25rem; border-radius: 0.2rem; }}
.summary-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem 2rem; max-width: 48rem; }}
.summary-grid div strong {{ font-size: 1.5rem; display: block; }}
</style>
</head>
<body>
<h1>swop scan — {html.escape(report.project)}</h1>
<p>Generated {generated} · root: <code>{html.escape(str(report.project_root))}</code></p>

<h2>Summary</h2>
<div class="summary-grid">
  <div><strong>{kinds['command']}</strong> commands</div>
  <div><strong>{kinds['query']}</strong> queries</div>
  <div><strong>{kinds['event']}</strong> events</div>
  <div><strong>{kinds['handler']}</strong> handlers</div>
  <div><strong>{via['decorator']}</strong> via decorator</div>
  <div><strong>{via['heuristic']}</strong> via heuristic</div>
  <div><strong>{report.files_scanned}</strong> files scanned</div>
  <div><strong>{report.files_cached}</strong> files cached</div>
</div>

<h2>Contexts</h2>
<table>
<thead><tr>
  <th>Context</th><th>Files scanned</th><th>Cached</th>
  <th>Commands</th><th>Queries</th><th>Events</th><th>Handlers</th><th>Total</th>
</tr></thead>
<tbody>
{ctx_rows or '<tr><td colspan="8"><em>No contexts detected.</em></td></tr>'}
</tbody>
</table>

<h2>Detections</h2>
<table>
<thead><tr>
  <th>Kind</th><th>Context</th><th>Name</th><th>Source</th>
  <th>Via</th><th>Confidence</th><th>Reason</th>
</tr></thead>
<tbody>
{detection_rows or '<tr><td colspan="7"><em>No CQRS artifacts detected.</em></td></tr>'}
</tbody>
</table>

{f'<h2>Errors ({len(report.errors)})</h2><ul>{error_items}</ul>' if report.errors else ''}

</body>
</html>
"""


def write_report(
    report: ScanReport,
    json_path: Path | None = None,
    html_path: Path | None = None,
) -> dict:
    written: dict[str, str] = {}
    if json_path is not None:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(render_json(report), encoding="utf-8")
        written["json"] = str(json_path)
    if html_path is not None:
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(render_html(report), encoding="utf-8")
        written["html"] = str(html_path)
    return written
