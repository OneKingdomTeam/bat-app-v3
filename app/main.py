from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from app.exception.web import NonHTMXRequestException, RedirectToLoginException, non_htmx_request_exception_handler, redirect_to_login_exception_handler
from pathlib import Path

from app.config import FORCE_HTTPS_PATHS_ENV

from app.service.user import add_default_user
from app.service.question import add_default_questions

from app.web.public import router as public_router
from app.web.dashboard.dashboard import router as dashboard_router
from app.web.dashboard.users import router as dashboard_users_router
from app.web.dashboard.questions import router as dashboard_questions_router
from app.web.dashboard.assessments import router as dashboard_assessments_router
from app.web.dashboard.reports import router3 as dashboard_reports_router

from app.web.app import router as app_root_router
from app.web.app.assessments import router as app_assessments_router
from app.web.app.reports import router as app_reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    add_default_user()
    add_default_questions()

    yield


# Main app to start
app = FastAPI(lifespan=lifespan)

class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Force request.scheme to 'https'
        request.scope["scheme"] = "https"
        return await call_next(request)

if FORCE_HTTPS_PATHS_ENV:
    app.add_middleware(HTTPSRedirectMiddleware)


app.add_exception_handler(NonHTMXRequestException, non_htmx_request_exception_handler)
app.add_exception_handler(RedirectToLoginException, redirect_to_login_exception_handler)

# Mount static files directories
static_dir = Path(__file__).resolve().parent
app.mount("/js", StaticFiles(directory=static_dir / "static" / "js"), name="js")
app.mount("/css", StaticFiles(directory=static_dir / "static" / "css"), name="css")
app.mount("/images", StaticFiles(directory=static_dir / "static" / "images"), name="images")

# Routers

# Dashboard routers
app.include_router(public_router)
app.include_router(dashboard_router, prefix="/dashboard")
app.include_router(dashboard_users_router, prefix="/dashboard/users")
app.include_router(dashboard_questions_router, prefix="/dashboard/questions")
app.include_router(dashboard_assessments_router, prefix="/dashboard/assessments")
app.include_router(dashboard_reports_router, prefix="/dashboard/reports")

# App routers
app.include_router(app_root_router, prefix="/app")
app.include_router(app_assessments_router, prefix="/app/assessments")
app.include_router(app_reports_router, prefix="/app/reports")
