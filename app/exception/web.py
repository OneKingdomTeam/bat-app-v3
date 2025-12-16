from fastapi import HTTPException, Request, Response
from fastapi.responses import RedirectResponse
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
    """
    Unified redirect handler that works for BOTH standard HTTP requests and HTMX requests.

    - For HTMX requests: Returns 200 OK with HX-Redirect header (full page reload)
    - For standard requests: Returns 303 redirect with Location header

    HTMX sends 'HX-Request: true' header, which we use to detect HTMX requests.
    Note: HTMX ignores response headers on 3xx status codes, so we must return 200.
    """

    login_url = request.url_for("login_page")

    # Capture current URL as 'next' parameter for post-login redirect
    current_url = str(request.url.path)
    if request.url.query:
        current_url += f"?{request.url.query}"

    # Build redirect URL with 'next' parameter
    redirect_target = f"{login_url}?next={current_url}&expired_session=1"

    # Check if this is an HTMX request
    # HTMX sends 'HX-Request: true' header with all HTMX-initiated requests
    is_htmx_request = request.headers.get("HX-Request") == "true"

    if is_htmx_request:
        # HTMX request: Return 200 OK with HX-Redirect header
        # Note: HTMX ignores response headers on 3xx status codes,
        # so we MUST return 200 for HX-Redirect to work
        response = Response(status_code=200)
        response.headers["HX-Redirect"] = redirect_target
        return response
    else:
        # Standard HTTP request: Return 303 redirect
        return RedirectResponse(url=redirect_target, status_code=303)
