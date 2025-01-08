from fastapi import APIRouter, Depends, Request

from app.model.report import Report
from app.service import report as service

from app.model.user import User
from app.template.init import jinja
from fastapi.responses import HTMLResponse
from app.service.auth import user_htmx_dep


router = APIRouter()



@router.get("", response_class=HTMLResponse, name="dashboard_reports_page")
def get_questions(request: Request, current_user: User = Depends(user_htmx_dep)):

    reports: list[Report] = service.get_all(current_user=current_user)
    
    context = {
            "request": request,
            "title":"Reports",
            "description":"List of all available reports.",
            "current_user": current_user,
            "reports": reports
            }

    response = jinja.TemplateResponse(
            context=context,
            name="dashboard/reports.html"
            )

    return response


@router.get("/create", response_class=HTMLResponse, name="dashboard_report_create_page")
def get_report_create(request: Request, current_user: User = Depends(user_htmx_dep)):

    return


@router.post("/create", response_class=HTMLResponse)
def post_report_create(request: Request, current_user: User = Depends(user_htmx_dep)):

    return


@router.get("/edit/{report_id}", response_class=HTMLResponse, name="dashboard_report_edit_page")
def get_report_edit(request: Request, report_id: str, current_user: User = Depends(user_htmx_dep)):

    return


@router.post("/edit/{report_id}", response_class=HTMLResponse)
def post_report_edit(request: Request, report_id: str, report: Report, current_user: User = Depends(user_htmx_dep)):

    return


