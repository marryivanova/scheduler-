import os
import pytest
import requests
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock


from src.scheduler import Scheduler
from src.exeptions import APIConnectionError

load_dotenv()
API_URL = os.getenv('API_TEST_TASK')


def test_api_response_structure():
    response = requests.get(API_URL)
    response.raise_for_status()

    data = response.json()
    days = data["days"]
    timeslots = data["timeslots"]

    assert days, "Days list is empty"
    assert timeslots, "Timeslots list is empty"

    day_fields = {"id", "date", "start", "end"}
    timeslot_fields = {"id", "day_id", "start", "end"}

    assert day_fields.issubset(days[0]), "Missing day fields"
    assert timeslot_fields.issubset(timeslots[0]), "Missing timeslot fields"


@pytest.fixture
def mock_api_data():
    return {
        "days": [
            {"id": 1, "date": "2025-02-15", "start": "09:00", "end": "21:00"},
            {"id": 2, "date": "2025-02-16", "start": "08:00", "end": "22:00"},
            {"id": 3, "date": "2025-02-17", "start": "09:00", "end": "18:00"},
            {"id": 4, "date": "2025-02-18", "start": "10:00", "end": "18:00"},
            {"id": 5, "date": "2025-02-19", "start": "09:00", "end": "18:00"}
        ],
        "timeslots": [
            {"id": 1, "day_id": 1, "start": "17:30", "end": "20:00"},
            {"id": 2, "day_id": 1, "start": "09:00", "end": "12:00"},
            {"id": 3, "day_id": 2, "start": "14:30", "end": "18:00"},
            {"id": 4, "day_id": 2, "start": "09:30", "end": "11:00"},
            {"id": 5, "day_id": 3, "start": "12:30", "end": "18:00"},
            {"id": 6, "day_id": 4, "start": "10:00", "end": "11:00"},
            {"id": 7, "day_id": 4, "start": "11:30", "end": "14:00"},
            {"id": 8, "day_id": 4, "start": "14:00", "end": "16:00"},
            {"id": 9, "day_id": 4, "start": "17:00", "end": "18:00"}
        ]
    }


@pytest.fixture
def mock_scheduler(mock_api_data):
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_api_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        scheduler = Scheduler(url=API_URL)
        yield scheduler


def test_get_busy_slots(mock_scheduler):
    busy_slots = mock_scheduler.get_busy_slots("2025-02-15")
    assert len(busy_slots) == 2
    assert ("09:00", "12:00") in busy_slots
    assert ("17:30", "20:00") in busy_slots

    busy_slots = mock_scheduler.get_busy_slots("2025-02-18")
    assert len(busy_slots) == 4
    assert ("10:00", "11:00") in busy_slots
    assert ("11:30", "14:00") in busy_slots
    assert ("14:00", "16:00") in busy_slots
    assert ("17:00", "18:00") in busy_slots

    busy_slots = mock_scheduler.get_busy_slots("2025-01-01")
    assert len(busy_slots) == 0


def test_get_free_slots(mock_scheduler):
    free_slots = mock_scheduler.get_free_slots("2025-02-15")
    assert len(free_slots) == 2
    assert ("12:00", "17:30") in free_slots
    assert ("20:00", "21:00") in free_slots

    free_slots = mock_scheduler.get_free_slots("2025-02-16")
    assert len(free_slots) == 3
    assert ("08:00", "09:30") in free_slots
    assert ("11:00", "14:30") in free_slots
    assert ("18:00", "22:00") in free_slots

    free_slots = mock_scheduler.get_free_slots("2025-02-19")
    assert len(free_slots) == 1
    assert ("09:00", "18:00") in free_slots


def test_is_available(mock_scheduler):
    assert mock_scheduler.is_available("2025-02-15", "12:00", "17:30") is True
    assert mock_scheduler.is_available("2025-02-16", "11:00", "14:00") is True
    assert mock_scheduler.is_available("2025-02-19", "10:00", "12:00") is True

    assert mock_scheduler.is_available("2025-02-15", "11:00", "13:00") is False
    assert mock_scheduler.is_available("2025-02-18", "13:30", "15:00") is False

    assert mock_scheduler.is_available("2025-02-15", "08:00", "09:00") is False
    assert mock_scheduler.is_available("2025-02-15", "21:00", "22:00") is False


def test_find_slot_for_duration(mock_scheduler):
    slot = mock_scheduler.find_slot_for_duration(60)
    assert slot == ("2025-02-15", "12:00", "13:00")

    slot = mock_scheduler.find_slot_for_duration(180)
    assert slot == ("2025-02-15", "12:00", "15:00")

    slot = mock_scheduler.find_slot_for_duration(480)
    assert slot == ("2025-02-19", "09:00", "17:00")

    slot = mock_scheduler.find_slot_for_duration(1440)
    assert slot is None



def test_api_error_handling():
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        with pytest.raises(APIConnectionError):
            Scheduler(url=API_URL)