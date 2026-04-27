from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_health_and_evaluate_smoke():
    client = TestClient(app)
    health = client.get("/api/health")
    assert health.status_code == 200

    payload = {
        "student_id": "stu-api",
        "objective": {
            "id": "obj-api",
            "course_id": "course-001",
            "title": "Ensayo breve",
            "description": "Argumentar con evidencia.",
            "rubric_criteria": ["Argumentacion", "Proceso"],
            "expected_evidence_patterns": ["borradores", "revision"],
            "difficulty_level": "medium"
        },
        "source_type": "lms",
        "activity_type": "essay",
        "submission_id": "sub-api",
        "artifact_ref": "artifact-api",
        "content": "Texto breve con una sola version final y sin revision visible.",
        "draft_count": 1,
        "time_spent_estimate": 0.2
    }
    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "recomendacion_final" in body
