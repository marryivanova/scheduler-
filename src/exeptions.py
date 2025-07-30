class SchedulerError(Exception):
    """Base exception for all scheduler errors."""
    pass


class APIConnectionError(SchedulerError):
    """API connection error."""
    pass


class InvalidDataError(SchedulerError):
    """Invalid data from API."""
    pass