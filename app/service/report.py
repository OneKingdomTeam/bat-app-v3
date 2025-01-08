from app.data import resport as data
from app.model.report import Report
from app.model.user import User
from app.exception.service import EndpointDataMismatch, Unauthorized


# -------------------------------
#   CRUD
# -------------------------------

def get_all(current_user: User) -> list[Report]:

    if not current_user.can_manage_reports():
        raise Unauthorized(msg="You cannot manage reports.")

    return data.get_all_reports()


def get_report(report_id: str, current_user: User) -> Report:

    if not current_user.can_manage_reports():
        raise Unauthorized(msg="You cannot manage reports.")

    return data.get_report(report_id=report_id)


def update_report(report_id: str, report: Report, current_user: User) -> Report:

    if not current_user.can_manage_reports():
        raise Unauthorized(msg="You cannot manage reports.")

    if not report_id == report.report_id:
        raise EndpointDataMismatch(msg="Provided report object doesn't match endpoint ID.")

    return data.update_report(report=report)


def delete_report(report_id: str, current_user: User) -> Report:

    if not current_user.can_manage_reports():
        raise Unauthorized(msg="You cannot manage reports.")

    return data.get_report(report_id=report_id)
