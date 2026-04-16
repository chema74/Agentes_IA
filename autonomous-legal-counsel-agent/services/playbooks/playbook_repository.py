from __future__ import annotations


class PlaybookRepository:
    def rules(self) -> dict:
        return {
            "liability": {"forbidden": ["unlimited liability"], "fallback": "Cap to approved policy."},
            "jurisdiction": {"forbidden": ["Delaware exclusive", "Singapore exclusive"], "fallback": "EU venue only."},
            "data_transfer": {"forbidden": ["unrestricted transfer outside EU"], "fallback": "SCC or EU-only transfer."},
            "confidentiality": {"forbidden": [], "fallback": "Mutual confidentiality with standard carve-outs."},
        }


PLAYBOOK_REPOSITORY = PlaybookRepository()
