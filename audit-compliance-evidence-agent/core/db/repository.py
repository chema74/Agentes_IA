from __future__ import annotations

from dataclasses import dataclass, field

from domain.controls.models import Control
from domain.evidence.models import Evidence
from domain.findings.models import Finding
from domain.gaps.models import Gap
from domain.mappings.models import ControlEvidenceMapping, CoverageEvaluation
from domain.packages.models import AuditPackage
from domain.remediation.models import Remediation
from domain.scopes.models import AuditScope


@dataclass
class InMemoryStore:
    scopes: dict[str, AuditScope] = field(default_factory=dict)
    controls: dict[str, Control] = field(default_factory=dict)
    evidence: dict[str, Evidence] = field(default_factory=dict)
    mappings: dict[str, ControlEvidenceMapping] = field(default_factory=dict)
    coverage: dict[str, CoverageEvaluation] = field(default_factory=dict)
    gaps: dict[str, Gap] = field(default_factory=dict)
    findings: dict[str, Finding] = field(default_factory=dict)
    remediations: dict[str, Remediation] = field(default_factory=dict)
    packages: dict[str, AuditPackage] = field(default_factory=dict)


STORE = InMemoryStore()
