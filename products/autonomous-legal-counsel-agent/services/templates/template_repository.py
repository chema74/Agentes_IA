from __future__ import annotations

from domain.templates.models import ContractTemplate


class TemplateRepository:
    def __init__(self) -> None:
        self.templates = {
            "nda": ContractTemplate(
                template_id="tmpl-nda",
                contract_type="NDA",
                allowed_jurisdictions=["Spain", "EU", "Ireland"],
                fallback_positions={"liability": "Mutual direct damages cap limited to fees paid.", "jurisdiction": "Madrid courts or EU venue."},
                prohibited_terms=["unlimited liability", "perpetual non-mutual confidentiality"],
                liability_cap_policy="limited-mutual",
                required_clauses=["confidentiality", "jurisdiction", "termination"],
            ),
            "msa": ContractTemplate(
                template_id="tmpl-msa",
                contract_type="MSA",
                allowed_jurisdictions=["Spain", "EU", "Ireland"],
                fallback_positions={"liability": "Cap liability to 12 months fees.", "data_transfer": "EU-only transfer or SCC fallback."},
                prohibited_terms=["unlimited liability", "exclusive foreign jurisdiction"],
                liability_cap_policy="fees-12-months",
                required_clauses=["liability", "jurisdiction", "data", "termination"],
            ),
            "dpa": ContractTemplate(
                template_id="tmpl-dpa",
                contract_type="DPA",
                allowed_jurisdictions=["EU", "Spain", "Ireland"],
                fallback_positions={"data_transfer": "EU processing or SCC-approved transfer mechanism."},
                prohibited_terms=["non-eu unrestricted transfer"],
                liability_cap_policy="policy-driven",
                required_clauses=["data", "subprocessors", "security", "jurisdiction"],
            ),
        }

    def resolve_template(self, contract_type: str) -> ContractTemplate:
        key = contract_type.lower()
        return self.templates.get(key, self.templates["msa"])


TEMPLATE_REPOSITORY = TemplateRepository()
