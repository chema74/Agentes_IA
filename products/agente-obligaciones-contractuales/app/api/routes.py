from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile

from services.workflows.contract_workflow import analyze_contract_file

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    checklist_json: str | None = Form(None),
) -> dict:
    payload = await file.read()
    result = analyze_contract_file(
        filename=file.filename or "uploaded-file",
        content=payload,
        suffix=Path(file.filename or "").suffix.lower(),
        checklist_json=checklist_json,
    )
    return result.model_dump(mode="json")
