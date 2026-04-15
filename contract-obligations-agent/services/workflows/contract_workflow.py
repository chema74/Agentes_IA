from __future__ import annotations

import json
import re
from pathlib import Path

from connectors.files.loaders import load_bytes
from core.config.settings import settings
from core.logging.logger import configure_logging
from core.security.redaction import redact_sensitive_text
from domain.clauses.models import Clause, EvidenceRef
from domain.contracts.models import ContractAnalysis, ExecutiveSummary, ParsedDocument
from domain.obligations.models import Obligation
from domain.risk_flags.models import Alert, RiskAssessment, RiskLevel
from services.llm.gateway import LiteLLMGateway
from services.parsing.parser import parse_loaded_file
from services.retrieval.retriever import EvidenceRetriever
from services.vectorstore.chroma_store import ChromaVectorStore
from services.vectorstore.qdrant_store import QdrantVectorStore


configure_logging()

CLAUSE_PATTERNS = {
    "penalty": r"\b(penalty|penalties|liquidated damages|default|late fee)\b",
    "payment": r"\b(payment|fee|invoice|amount|price)\b",
    "renewal": r"\b(renewal|automatic renewal|renews|extension)\b",
    "termination": r"\b(terminate|termination|rescission|cancel)\b",
    "confidentiality": r"\b(confidential|nda|non-disclosure)\b",
    "data": r"\b(data protection|privacy|gdpr|personal data)\b",
    "obligation": r"\b(shall|must|will|is required to|undertakes to)\b",
}

DATE_RE = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b")


def _vectorstore():
    if settings.vectorstore_backend == "qdrant":
        return QdrantVectorStore(settings.qdrant_url, settings.qdrant_collection)
    return ChromaVectorStore(str(settings.chroma_path))


def _extract_clauses(doc: ParsedDocument) -> list[Clause]:
    clauses: list[Clause] = []
    lines = [line.strip() for line in doc.normalized_text.splitlines() if line.strip()]
    for idx, line in enumerate(lines, start=1):
        line_lower = line.lower()
        for clause_type, pattern in CLAUSE_PATTERNS.items():
            if re.search(pattern, line_lower):
                chunk = doc.chunks[min(len(doc.chunks) - 1, (idx - 1) // 3)] if doc.chunks else None
                clauses.append(
                    Clause(
                        clause_id=f"{doc.document_id}-cl-{idx}",
                        title=line[:120],
                        clause_type=clause_type,
                        text=line,
                        confidence=0.72 if clause_type != "obligation" else 0.66,
                        evidence=[
                            EvidenceRef(
                                source_id=doc.document_id,
                                source_label=doc.filename,
                                chunk_id=chunk.chunk_id if chunk else f"{doc.filename}-chunk-1",
                                source_excerpt=line[:240],
                                confidence=0.72,
                            )
                        ],
                    )
                )
                break
    return clauses


def _extract_dates(doc: ParsedDocument) -> list[dict]:
    items = []
    for match in DATE_RE.finditer(doc.normalized_text):
        items.append({"date": match.group(1), "context": doc.normalized_text[max(0, match.start() - 40) : match.end() + 40]})
    return items


def _extract_obligations(doc: ParsedDocument, clauses: list[Clause]) -> list[Obligation]:
    obligations: list[Obligation] = []
    for idx, clause in enumerate(clauses, start=1):
        if clause.clause_type in {"obligation", "payment", "termination", "penalty"}:
            obligations.append(
                Obligation(
                    obligation_id=f"{doc.document_id}-ob-{idx}",
                    description=clause.text,
                    responsible_party=None,
                    due_date=None,
                    dependency=None,
                    observations=f"Inferred from {clause.clause_type} clause.",
                    confidence=clause.confidence,
                    evidence=clause.evidence,
                )
            )
    return obligations


def _validate_findings(doc: ParsedDocument, clauses: list[Clause]) -> RiskAssessment:
    alerts: list[Alert] = []
    if not clauses:
        alerts.append(
            Alert(
                alert_id=f"{doc.document_id}-al-1",
                title="No relevant clauses detected",
                message="The parser did not detect clauses that match the current rule set.",
                severity=RiskLevel.medium,
                human_review_required=True,
                rationale="This may indicate an unusual document structure or weak extraction coverage.",
            )
        )
    if any(c.clause_type == "penalty" for c in clauses):
        alerts.append(
            Alert(
                alert_id=f"{doc.document_id}-al-2",
                title="Penalty language detected",
                message="Potential penalty or default language found.",
                severity=RiskLevel.high,
                human_review_required=True,
                rationale="Penalty language can have material legal and operational consequences.",
                evidence=clauses[0].evidence if clauses else [],
            )
        )
    level = RiskLevel.low
    if any(a.severity == RiskLevel.high for a in alerts):
        level = RiskLevel.high
    elif alerts:
        level = RiskLevel.medium
    return RiskAssessment(overall_level=level, alerts=alerts)


def _summarize(doc: ParsedDocument, clauses: list[Clause], obligations: list[Obligation], risk: RiskAssessment) -> ExecutiveSummary:
    gw = LiteLLMGateway(settings.litellm_model, settings.litellm_fallback_model)
    summary = gw.summarize(f"Contract review for {doc.filename}", doc.normalized_text[:4000])
    points = [
        f"{len(clauses)} relevant clauses detected",
        f"{len(obligations)} obligations extracted",
        f"Overall risk: {risk.overall_level.value}",
    ]
    return ExecutiveSummary(
        executive_summary=summary,
        key_points=points,
        human_review_note="Review required for any high-risk alert or ambiguous extraction.",
    )


def _comparison(checklist_json: str | None, text: str) -> dict:
    if not checklist_json:
        return {"status": "not_provided", "missing": []}
    try:
        payload = json.loads(checklist_json)
    except Exception:
        return {"status": "invalid_json", "missing": []}
    if isinstance(payload, dict):
        items = payload.get("items", [])
    elif isinstance(payload, list):
        items = payload
    else:
        items = []
    missing = [item for item in items if str(item).lower() not in text.lower()]
    return {"status": "ok", "missing": missing}


def analyze_contract_file(
    filename: str,
    content: bytes,
    suffix: str,
    checklist_json: str | None = None,
) -> ContractAnalysis:
    loaded = load_bytes(filename, suffix, content)
    parsed = parse_loaded_file(loaded)
    normalized = redact_sensitive_text(parsed.normalized_text) if settings.redaction_enabled else parsed.normalized_text
    parsed = parsed.model_copy(update={"normalized_text": normalized})

    store = _vectorstore()
    store.upsert(parsed.document_id, parsed.chunks)
    retriever = EvidenceRetriever(store)
    retrieval_hits = [
        hit.__dict__
        for hit in retriever.search("payment renewal penalty confidentiality obligation", top_k=5)
    ]

    clauses = _extract_clauses(parsed)
    obligations = _extract_obligations(parsed, clauses)
    risk = _validate_findings(parsed, clauses)
    summary = _summarize(parsed, clauses, obligations, risk)
    alerts = list(risk.alerts)
    comparison = _comparison(checklist_json, parsed.normalized_text)
    if comparison.get("missing"):
        alerts.append(
            Alert(
                alert_id=f"{parsed.document_id}-al-checklist",
                title="Checklist gap detected",
                message=f"Missing items: {', '.join(map(str, comparison['missing']))}",
                severity=RiskLevel.medium,
                human_review_required=True,
                rationale="Checklist items may represent expected obligations or clauses.",
            )
        )
    dates = _extract_dates(parsed)
    metadata = {**parsed.metadata, "comparison": comparison, "dates": dates, "risk_level": risk.overall_level.value}
    return ContractAnalysis(
        document_id=parsed.document_id,
        filename=parsed.filename,
        document_type=parsed.document_type,
        metadata=metadata,
        raw_text=parsed.raw_text,
        normalized_text=parsed.normalized_text,
        chunks=parsed.chunks,
        clauses=clauses,
        obligations=obligations,
        alerts=alerts,
        risk_assessment=risk,
        summary=summary,
        comparison=comparison,
        evidences=[ref for clause in clauses for ref in clause.evidence],
        retrieval_hits=retrieval_hits,
    )
