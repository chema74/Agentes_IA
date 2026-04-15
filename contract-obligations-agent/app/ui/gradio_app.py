from pathlib import Path

from services.workflows.contract_workflow import analyze_contract_file


def _run_analysis(file_obj, checklist_json: str = ""):
    if file_obj is None:
        return "Upload a file first.", "", "", ""
    path = Path(file_obj.name)
    result = analyze_contract_file(path.name, path.read_bytes(), path.suffix.lower(), checklist_json or None)
    summary = result.summary.executive_summary
    clauses = "\n\n".join(f"- {c.title}: {c.text}" for c in result.clauses)
    obligations = "\n".join(f"- {o.description}" for o in result.obligations)
    alerts = "\n".join(f"- [{a.severity}] {a.title}: {a.message}" for a in result.alerts)
    return summary, clauses, obligations, alerts


def launch_demo() -> None:
    import gradio as gr

    with gr.Blocks(title="contract-obligations-agent") as demo:
        gr.Markdown("# contract-obligations-agent")
        file_input = gr.File(label="Contract, annex, or email", file_types=[".pdf", ".docx", ".eml"])
        checklist_input = gr.Textbox(label="Optional checklist/template JSON", lines=8)
        run_btn = gr.Button("Analyze")
        summary = gr.Textbox(label="Executive summary", lines=8)
        clauses = gr.Textbox(label="Clauses", lines=12)
        obligations = gr.Textbox(label="Obligations", lines=12)
        alerts = gr.Textbox(label="Alerts", lines=10)
        run_btn.click(_run_analysis, [file_input, checklist_input], [summary, clauses, obligations, alerts])
    demo.launch()
