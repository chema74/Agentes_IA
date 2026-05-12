from __future__ import annotations

from pathlib import Path
from tempfile import mkdtemp

from services.exports.exporter import export_bundle
from services.workflows.contract_workflow import analyze_contract_file


def _format_clauses(result) -> str:
    if not result.clauses:
        return "No clauses detected."
    return "\n\n".join(
        f"[{clause.clause_type}] {clause.title}\n{clause.text}\nEvidence: {clause.evidence[0].source_excerpt if clause.evidence else ''}"
        for clause in result.clauses
    )


def _format_obligations(result) -> str:
    if not result.obligations:
        return "No obligations detected."
    lines = []
    for obligation in result.obligations:
        lines.append(
            "\n".join(
                [
                    f"- {obligation.description}",
                    f"  Responsible party: {obligation.responsible_party or 'not verified'}",
                    f"  Due date: {obligation.due_date or 'not verified'}",
                    f"  Dependency: {obligation.dependency or 'none detected'}",
                    f"  Risk: {obligation.risk_level}",
                    f"  Human review: {'yes' if obligation.human_review_required else 'no'}",
                    f"  Explanation: {obligation.explanation}",
                ]
            )
        )
    return "\n\n".join(lines)


def _format_alerts(result) -> str:
    if not result.alerts:
        return "No alerts detected."
    return "\n\n".join(
        "\n".join(
            [
                f"- [{alert.severity.value}] {alert.title}",
                f"  Message: {alert.message}",
                f"  Human review: {'yes' if alert.human_review_required else 'no'}",
                f"  Explanation: {alert.explanation or alert.rationale}",
            ]
        )
        for alert in result.alerts
    )


def _format_evidence(result) -> str:
    if not result.retrieval_hits:
        return "No retrieval hits available."
    return "\n\n".join(
        "\n".join(
            [
                f"- [{hit.rank}] {hit.source_label}",
                f"  Chunk: {hit.chunk_id}",
                f"  Excerpt: {hit.source_excerpt}",
                f"  Score: {hit.score:.3f}",
                f"  Span: {hit.source_start}-{hit.source_end}",
            ]
        )
        for hit in result.retrieval_hits
    )


def _format_dates(result) -> str:
    if not result.dates:
        return "No dates detected."
    return "\n\n".join(
        f"- {item.date} [{item.category}]\n  Context: {item.context}\n  Confidence: {item.confidence:.2f}" for item in result.dates
    )


def _format_comparison(result) -> str:
    comparison = result.comparison or {}
    lines = [f"Status: {comparison.get('status', '')}"]
    for key in ("matched", "missing", "unverifiable"):
        items = comparison.get(key, [])
        lines.append(f"{key.title()}: {', '.join(items) if items else 'none'}")
    return "\n".join(lines)


def _run_analysis(file_obj, checklist_json: str = ""):
    if file_obj is None:
        empty = "Upload a file first."
        return empty, empty, empty, empty, empty, empty, empty, empty, None, None, None, None

    path = Path(file_obj.name)
    result = analyze_contract_file(path.name, path.read_bytes(), path.suffix.lower(), checklist_json or None)

    export_dir = Path(mkdtemp(prefix="agente-obligaciones-contractuales-"))
    exports = export_bundle(result.model_dump(mode="json"), export_dir)
    summary = result.summary.executive_summary
    overview = "\n".join(
        [
            f"Document: {result.filename}",
            f"Type: {result.document_type.value}",
            f"Risk: {result.risk_assessment.overall_level.value if result.risk_assessment else 'unknown'}",
            f"Human review required: {'yes' if result.risk_assessment and result.risk_assessment.human_review_required else 'no'}",
            "",
            result.summary.human_review_note,
        ]
    )
    clauses = _format_clauses(result)
    obligations = _format_obligations(result)
    alerts = _format_alerts(result)
    evidence = _format_evidence(result)
    dates = _format_dates(result)
    comparison = _format_comparison(result)
    return (
        summary,
        overview,
        clauses,
        obligations,
        alerts,
        evidence,
        dates,
        comparison,
        str(exports["json"]),
        str(exports["markdown"]),
        str(exports["csv"]),
        str(exports["docx"]),
    )


def launch_demo() -> None:
    import gradio as gr

    with gr.Blocks(title="agente-obligaciones-contractuales", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # agente-obligaciones-contractuales

            Demo de revisión contractual con trazabilidad documental.
            No sustituye asesoría legal.
            """
        )
        with gr.Row():
            file_input = gr.File(label="Contract, annex, or email", file_types=[".pdf", ".docx", ".eml", ".txt"])
            checklist_input = gr.Textbox(label="Optional checklist/template JSON", lines=8, placeholder='{"items": ["payment terms", "renewal"]}')
        run_btn = gr.Button("Analyze", variant="primary")

        with gr.Tabs():
            with gr.Tab("Overview"):
                summary = gr.Textbox(label="Executive summary", lines=6)
                overview = gr.Textbox(label="Review status", lines=6)
            with gr.Tab("Clauses"):
                clauses = gr.Textbox(label="Detected clauses", lines=16)
            with gr.Tab("Obligations"):
                obligations = gr.Textbox(label="Obligation matrix", lines=18)
            with gr.Tab("Alerts"):
                alerts = gr.Textbox(label="Risk alerts", lines=14)
            with gr.Tab("Evidence"):
                evidence = gr.Textbox(label="Retrieval hits", lines=16)
                dates = gr.Textbox(label="Date mentions", lines=12)
                comparison = gr.Textbox(label="Checklist comparison", lines=8)
            with gr.Tab("Exports"):
                export_json_file = gr.File(label="JSON export")
                export_md_file = gr.File(label="Markdown export")
                export_csv_file = gr.File(label="CSV export")
                export_docx_file = gr.File(label="DOCX export")

        run_btn.click(
            _run_analysis,
            [file_input, checklist_input],
            [
                summary,
                overview,
                clauses,
                obligations,
                alerts,
                evidence,
                dates,
                comparison,
                export_json_file,
                export_md_file,
                export_csv_file,
                export_docx_file,
            ],
        )
    demo.launch()
