from fastapi import HTTPException, Request, Response
from app.template.init import jinja

class NonHTMXRequestException(HTTPException):
    def __init__(self, detail: str = "Unauthorized - Non HTMX Request"):
        super().__init__(status_code=401, detail=detail)

async def non_htmx_request_exception_handler(request: Request, exc: Exception) -> Response:
    context = {
            "request": request,
            "title":"Loading...",
            "description":"Loading the page. Please wait.",
            "redirect_to": request.url,
            }

    return jinja.TemplateResponse(
            name="non-htmx-to-htmx.html",
            context=context
            )

class RedirectToLoginException(HTTPException):

    def __init__(self, detail: str = "Unauthorized, probalby expired session or not loged in."):
        super().__init__(status_code=401, detail=detail)

async def redirect_to_login_exception_handler(request: Request, exc: Exception) -> Response:

    login_url = request.url_for("login_page")
    redirect_target = f"{login_url}?expired_session=1"

    response = Response()
    response.headers["HX-Redirect"] = redirect_target

    return response
