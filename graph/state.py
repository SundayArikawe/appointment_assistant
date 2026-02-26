from typing import TypedDict, Optional, List
from datetime import datetime
import uuid


class AppointmentState(TypedDict, total=False):
    run_id: str
    timestamp: str
    user_name: str
    user_input: str

    intent: Optional[str]
    department: Optional[str]
    requested_date: Optional[str]

    risk_flag: bool
    missing_info: bool
    status: str

    draft_response: Optional[str]
    final_response: Optional[str]

    pending_update: Optional[dict]

    path_trace: List[str]


def initialize_state(user_input: str, user_name: str) -> AppointmentState:
    return AppointmentState(
        run_id=str(uuid.uuid4()),
        timestamp=str(datetime.utcnow()),
        user_name=user_name,
        user_input=user_input,
        intent=None,
        department=None,
        requested_date=None,
        risk_flag=False,
        missing_info=False,
        status="IN_PROGRESS",
        draft_response=None,
        final_response=None,
        pending_update=None,
        path_trace=[],
    )