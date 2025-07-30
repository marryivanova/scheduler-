import os
import pytest

from dotenv import load_dotenv
from src.scheduler import Scheduler


load_dotenv()
API_URL = os.getenv('API_TEST_TASK')


@pytest.fixture(scope="module")
def real_scheduler():
    """Fixture creates an instance of Scheduler with a real API"""
    return Scheduler(url=API_URL)