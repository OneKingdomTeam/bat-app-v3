from fastapi import APIRouter, Request, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse
from app.exception.database import RecordNotFound, UsernameOrEmailNotUnique
from app.exception.service import Unauthorized
from app.model.user import User, UserCreate
from app.template.init import jinja
from app.service.auth import user_htmx_dep

import app.service.user as service


router = APIRouter()

# -------------------------------------
# User management
# -------------------------------------

@router.get("", response_class=HTMLResponse, name="dashboard_users_page")
def get_users(request: Request, current_user: User = Depends(user_htmx_dep)):

    users = service.get_all(current_user)

    context = {
            "request": request,
            "title":"Users",
            "description":"List of users and their details.",
            "current_user": current_user,
            "users": users,
            }

    template_response = jinja.TemplateResponse(
            name="dashboard/users.html",
            context=context
            )

    return template_response


@router.get("/add", response_class=HTMLResponse, name="dashboard_user_add_page")
async def add_user(request: Request, current_user: User = Depends(user_htmx_dep)):

    context = {
            "request": request,
            "title":"Add User",
            "description":"BAT App dashboard interface",
            "available_roles": current_user.can_grant_roles()
            }

    template_response = jinja.TemplateResponse(
            name="dashboard/user-add.html",
            context=context
            )

    return template_response


@router.post("/add", response_class=HTMLResponse)
async def add_user_post(request: Request,  new_user: UserCreate,  current_user: User = Depends(user_htmx_dep)):

    context = {
            "request": request,
            "title":"Add User",
            "description":"BAT App dashboard interface",
            "available_roles": current_user.can_grant_roles(),
            }

    status_code: int = 201

    try:
        created_user: User = service.create(new_user, current_user)
        context["notification"] = 1
        context["notification_type"] = "success"
        context["notification_content"] = f"User {created_user.username} created!"
    except Unauthorized as e:
        context["notification"] = 1
        context["notification_type"] = "danger"
        context["notification_content"] = e.msg
        status_code = 401
    except UsernameOrEmailNotUnique as e:
        context["notification"] = 1
        context["notification_type"] = "warning"
        context["notification_content"] = e.msg
        status_code = 403


    template_response = jinja.TemplateResponse(
            name="dashboard/user-add.html",
            context=context,
            status_code=status_code
            )

    return template_response


@router.get("/{id}", response_class=HTMLResponse, name="dashboard_user_edit_page")
async def edit_user(id: str, request: Request, current_user: User = Depends(user_htmx_dep)):


    try:
        user_for_edit: User = service.get(id=id, current_user=current_user)
    except RecordNotFound as e:
        raise HTTPException(status_code=404, detail=e.msg)
    except Unauthorized as e:
        raise HTTPException(status_code=403, detail=e.msg)

    context = {
            "request": request,
            "title":f"Edit user: {user_for_edit.username}",
            "description":f"Edit details of the {user_for_edit.username}",
            "user_for_edit":user_for_edit,
            "available_roles": current_user.can_grant_roles()
            }

    template_response = jinja.TemplateResponse(
            name="dashboard/user-edit.html",
            context=context
            )

    return template_response


@router.put("/{uuid}", response_class=HTMLResponse)
async def update_user(uuid: str, updated_user: UserCreate, request: Request, current_user: User = Depends(user_htmx_dep)):

    return ""

    try:
        edited_user: User = service.update(uuid, updated_user, current_user)
    except RecordNotFound as e:
        raise HTTPException(status_code=404, detail=e.msg)
    except Unauthorized as e:
        raise HTTPException(status_code=403, detail=e.msg)
    except EndpointDataMismatch as e:
        raise HTTPException(status_code=403, detail=e.msg)
    except UsernameOrEmailNotUnique as e:
        raise HTTPException(status_code=400, detail=e.msg)

    menu  = get_menu(current_user=current_user, request=request)

    context = {
            "request": request,
            "title":f"Edit user: {edited_user.username}",
            "description":f"Edit details of the {edited_user.username}",
            "menu": menu,
            "user_for_edit":edited_user,
            "successful_update": True,
            "available_roles": current_user.can_grant_roles()
            }

    template_response = templates.TemplateResponse(
            name="dashboard-user-edit.html",
            context=context
            )

    return template_response


@router.delete("/{uuid}", response_class=HTMLResponse)
async def delete_user(uuid: str, response: Response, current_user: User = Depends(user_htmx_dep)):

    return ""

    try:
        deleted_user: DeletedUser = service.delete(uuid, current_user)
    except RecordNotFound as e:
        raise HTTPException(status_code=404, detail=e.msg)
    except Unauthorized as e:
        raise HTTPException(status_code=403, detail=e.msg)

    response.headers["HX-Retarget"] = "closest tr"
    response.headers["HX-Reswap"] = "outerHTML"
    response.status_code = 202
    response.body = b''

    return response
