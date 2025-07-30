import os
import pytest
from requests import patch

from dotenv import load_dotenv
from unittest.mock import patch, MagicMock

from src.scheduler import Scheduler
from src.exeptions import APIConnectionError, InvalidDataError

load_dotenv()
API_URL = os.getenv('API_TEST_TASK')


def test_get_busy_slots(real_scheduler):
    """Test for getting busy slots"""
    assert real_scheduler.get_busy_slots("2025-02-15") == [('17:30', '20:00'), ('09:00', '12:00')]


def test_get_free_slots(real_scheduler):
    """Test for getting free slots"""
    assert real_scheduler.get_free_slots("2024-10-10") == []


def test_is_available(real_scheduler):
    """Test for checking availability"""
    assert real_scheduler.is_available("2025-02-15", "10:00", "10:30") is False


def test_real_is_available(real_scheduler):
    """Test for checking slot availability with real API"""
    free_slots = real_scheduler.get_free_slots("2025-02-15")
    if free_slots:
        free_start, free_end = free_slots[0]
        test_end = real_scheduler._minutes_to_time(
            (real_scheduler._time_to_minutes(free_start) +
             real_scheduler._time_to_minutes(free_end)) // 2
        )
        assert real_scheduler.is_available("2025-02-15", free_start, test_end) is True

    assert real_scheduler.is_available("2100-01-01", "10:00", "11:00") is False

def test_real_find_slot_for_duration(real_scheduler):
    """Test for finding a slot by duration with real API"""
    slot = real_scheduler.find_slot_for_duration(60)
    if slot is not None:
        date, start, end = slot
        assert real_scheduler.is_available(date, start, end) is True
        duration = (real_scheduler._time_to_minutes(end) -
                    real_scheduler._time_to_minutes(start))
        assert duration >= 60

def test_real_api_errors():
    """Test for API error handling"""
    with pytest.raises(APIConnectionError):
        Scheduler(url="https://lol-kek.com")

    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with pytest.raises(InvalidDataError):
            Scheduler(url=API_URL)