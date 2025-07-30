from dataclasses import dataclass
from typing import List

@dataclass
class Timeslot:
    id: int
    day_id: int
    start: str
    end: str

@dataclass
class Day:
    id: int
    date: str
    start: str
    end: str

@dataclass
class SchedulerResponse:
    days: List[Day]
    timeslots: List[Timeslot]