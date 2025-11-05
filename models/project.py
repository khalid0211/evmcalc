
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Project:
    project_id: str
    project_name: str
    department: str
    bac: float
    ac: float
    plan_start_date: date
    plan_finish_date: date
    data_date: date
    ev: Optional[float] = None
    pv: Optional[float] = None
    curve: Optional[str] = None
    beta: Optional[float] = None
    alpha: Optional[float] = None
    inflation_rate: Optional[float] = None
