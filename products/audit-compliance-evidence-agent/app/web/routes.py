from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.web.view_models import dashboard_metrics, scopes_with_stats
from core.auth.session import clear_session_cookie, set_session_cookie
from core.auth.supabase_auth import DEMO_USERS, authenticate, get_user_from_token
from core.db.repository import STORE


router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/web/templates")


def current_user_from_request(request: Request):
    token = request.cookies.get("session_token")
    return get_user_from_token(token)


def redirect_if_anonymous(request: Request):
    user = current_user_from_request(request)
    if user is None:
        return None, RedirectResponse(url="/login", status_code=302)
    return user, None


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    user, redirect = redirect_if_anonymous(request)
    if redirect is not None:
        return redirect
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "metrics": dashboard_metrics(), "scopes": scopes_with_stats()})


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "demo_users": DEMO_USERS.values(), "error": None, "user": None})


@router.post("/login", response_class=HTMLResponse)
def login_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        user = authenticate(email, password)
    except PermissionError:
        return templates.TemplateResponse("login.html", {"request": request, "demo_users": DEMO_USERS.values(), "error": "Credenciales no validas.", "user": None}, status_code=401)
    response = RedirectResponse(url="/", status_code=302)
    set_session_cookie(response, user.user_id)
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    clear_session_cookie(response)
    return response


@router.get("/scopes", response_class=HTMLResponse)
def scopes_page(request: Request):
    user, redirect = redirect_if_anonymous(request)
    if redirect is not None:
        return redirect
    return templates.TemplateResponse("scopes.html", {"request": request, "user": user, "scopes": scopes_with_stats()})


@router.get("/scopes/{scope_id}", response_class=HTMLResponse)
def scope_detail(scope_id: str, request: Request):
    user, redirect = redirect_if_anonymous(request)
    if redirect is not None:
        return redirect
    scope = STORE.scopes.get(scope_id)
    controls = [item for item in STORE.controls.values() if item.scope_id == scope_id]
    evidence_items = [item for item in STORE.evidence.values() if item.scope_id == scope_id]
    findings = [item for item in STORE.findings.values() if item.scope_id == scope_id]
    gaps = [item for item in STORE.gaps.values() if item.scope_id == scope_id]
    remediations = [item for item in STORE.remediations.values() if item.scope_id == scope_id]
    return templates.TemplateResponse("scope_detail.html", {"request": request, "user": user, "scope": scope, "controls": controls, "evidence_items": evidence_items, "findings": findings, "gaps": gaps, "remediations": remediations})


@router.get("/controls", response_class=HTMLResponse)
def controls_page(request: Request):
    user, redirect = redirect_if_anonymous(request)
    if redirect is not None:
        return redirect
    return templates.TemplateResponse("controls.html", {"request": request, "user": user, "controls": list(STORE.controls.values())})


@router.get("/evidence", response_class=HTMLResponse)
def evidence_page(request: Request):
    user, redirect = redirect_if_anonymous(request)
    if redirect is not None:
        return redirect
    return templates.TemplateResponse("evidence.html", {"request": request, "user": user, "evidence_items": list(STORE.evidence.values())})


@router.get("/evidence/{evidence_id}", response_class=HTMLResponse)
def evidence_detail(evidence_id: str, request: Request):
    user, redirect = redirect_if_anonymous(request)
    if redirect is not None:
        return redirect
    evidence = STORE.evidence.get(evidence_id)
    mappings = [item for item in STORE.mappings.values() if item.evidence_id == evidence_id]
    return templates.TemplateResponse("evidence_detail.html", {"request": request, "user": user, "evidence": evidence, "mappings": mappings})


@router.get("/gaps", response_class=HTMLResponse)
def gaps_page(request: Request):
    user, redirect = redirect_if_anonymous(request)
    if redirect is not None:
        return redirect
    return templates.TemplateResponse("gaps.html", {"request": request, "user": user, "gaps": list(STORE.gaps.values())})


@router.get("/findings", response_class=HTMLResponse)
def findings_page(request: Request):
    user, redirect = redirect_if_anonymous(request)
    if redirect is not None:
        return redirect
    return templates.TemplateResponse("findings.html", {"request": request, "user": user, "findings": list(STORE.findings.values())})


@router.get("/remediations", response_class=HTMLResponse)
def remediations_page(request: Request):
    user, redirect = redirect_if_anonymous(request)
    if redirect is not None:
        return redirect
    return templates.TemplateResponse("remediations.html", {"request": request, "user": user, "remediations": list(STORE.remediations.values())})


@router.get("/packages", response_class=HTMLResponse)
def packages_page(request: Request):
    user, redirect = redirect_if_anonymous(request)
    if redirect is not None:
        return redirect
    return templates.TemplateResponse("packages.html", {"request": request, "user": user, "packages": list(STORE.packages.values())})
