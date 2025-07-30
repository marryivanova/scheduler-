import json
import requests
from dataclasses import asdict
from typing import List, Tuple, Optional

from src.shema import SchedulerResponse, Day, Timeslot
from src.exeptions import APIConnectionError, InvalidDataError, SchedulerError


class Scheduler:
    def __init__(self, url):
        self.url = url
        self.data = self._fetch_data()

    def _fetch_data(self) -> SchedulerResponse:
        """Fetch schedule data from API.

        Returns:
            SchedulerResponse: Object containing schedule data.

        Raises:
            APIConnectionError: If failed to connect to API.
            InvalidDataError: If data is invalid.
            SchedulerError: Other scheduler-related errors.
        """
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            json_data = response.json()

            days = [Day(**day) for day in json_data.get("days", [])]
            timeslots = [Timeslot(**slot) for slot in json_data.get("timeslots", [])]

            return SchedulerResponse(days=days, timeslots=timeslots)

        except requests.exceptions.Timeout:
            raise APIConnectionError("Server response timeout exceeded")

        except requests.exceptions.ConnectionError:
            raise APIConnectionError("Failed to connect to server")

        except requests.exceptions.HTTPError as e:
            raise APIConnectionError(f"HTTP error: {e.response.status_code}")

        except (ValueError, KeyError, TypeError) as e:
            raise InvalidDataError(f"Invalid server data: {str(e)}")

        except Exception as e:
            raise SchedulerError(f"Unknown error: {str(e)}")

    def to_json(self) -> str:
        """Convert schedule data to JSON string."""
        return json.dumps(asdict(self.data))

    def _get_day_schedule(self, date: str) -> Day:
        """Get day object by specified date."""
        return next((day for day in self.data.days if day.date == date), None)

    def _get_day_timeslots(self, date: str) -> List[Tuple[str, str]]:
        """Get list of occupied time slots for specified date."""
        day = self._get_day_schedule(date)
        if day is None:
            return []

        return [
            (slot.start, slot.end)
            for slot in self.data.timeslots
            if slot.day_id == day.id
        ]

    @staticmethod
    def _time_to_minutes(time_str) -> int:
        """Convert time in HH:MM format to minutes"""
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes

    @staticmethod
    def _minutes_to_time(minutes) -> str:
        """Convert minutes to time in HH:MM format"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"

    def get_busy_slots(self, date) -> List[Tuple[str, str]]:
        """Get all occupied slots for specified date"""
        return self._get_day_timeslots(date)

    def get_free_slots(self, date: str) -> List[Tuple[str, str]]:
        """Get all free slots for specified date."""
        day = self._get_day_schedule(date)
        if not day:
            return []

        work_start = self._time_to_minutes(day.start)
        work_end = self._time_to_minutes(day.end)
        busy_slots = self._get_day_timeslots(date)

        busy_minutes = sorted(
            (self._time_to_minutes(start), self._time_to_minutes(end))
            for start, end in busy_slots
        )

        free_slots: List[Tuple[str, str]] = []
        prev_end = work_start

        for start, end in busy_minutes:
            if start > prev_end:
                free_slots.append((
                    self._minutes_to_time(prev_end),
                    self._minutes_to_time(start)
                ))
            prev_end = max(prev_end, end)

        if prev_end < work_end:
            free_slots.append((
                self._minutes_to_time(prev_end),
                self._minutes_to_time(work_end)
            ))

        return free_slots

    def is_available(self, date: str, start_time: str, end_time: str) -> bool:
        """Check availability of a time slot.

        Args:
            date: Date as string
            start_time: Start time as string (HH:MM)
            end_time: End time as string (HH:MM)

        Returns:
            True if slot is available, otherwise False
        """
        day = self._get_day_schedule(date)
        if not day:
            return False

        if start_time < day.start or end_time > day.end:
            return False

        req_start = self._time_to_minutes(start_time)
        req_end = self._time_to_minutes(end_time)

        for busy_start, busy_end in self._get_day_timeslots(date):
            bs = self._time_to_minutes(busy_start)
            be = self._time_to_minutes(busy_end)
            if req_start < be and req_end > bs:
                return False

        return True

    def find_slot_for_duration(self, duration_minutes: int) -> Optional[Tuple[str, str, str]]:
        """Find first available free slot for specified duration."""
        for day in sorted(self.data.days, key=lambda x: x.date):
            for start, end in self.get_free_slots(day.date):
                start_min = self._time_to_minutes(start)
                end_min = self._time_to_minutes(end)

                if end_min - start_min >= duration_minutes:
                    end_time = self._minutes_to_time(start_min + duration_minutes)
                    return (day.date, start, end_time)

        return None