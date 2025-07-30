import os
import typer
from typing import Union
from dotenv import load_dotenv

from src.helper.custom_logging import get_logger
from src.scheduler import Scheduler

logger = get_logger(__name__)
logger.propagate = False

load_dotenv()
API_URL = os.getenv('API_TEST_TASK')

app = typer.Typer()

def display_menu() -> None:
    """Display the interactive menu options."""
    typer.echo("\n" + "="*40)
    typer.echo("SCHEDULER SYSTEM MENU")
    typer.echo("="*40)
    typer.echo("1. View busy time slots for a date")
    typer.echo("2. View free time slots for a date")
    typer.echo("3. Check time slot availability")
    typer.echo("4. Find first available slot for duration")
    typer.echo("5. Exit")
    typer.echo("="*40)

def get_date_input(prompt: str = "Enter date (YYYY-MM-DD): ") -> str:
    """Get and validate date input from user."""
    while True:
        date = typer.prompt(prompt)
        if date.lower() == 'exit':
            return date
        return date

def get_time_input(prompt: str = "Enter time (HH:MM): ") -> str:
    """Get and validate time input from user."""
    while True:
        time = typer.prompt(prompt)
        if time.lower() == 'exit':
            return time
        if len(time) == 5 and time[2] == ':' and time[:2].isdigit() and time[3:].isdigit():
            return time
        typer.echo("Invalid time format. Please use HH:MM format (e.g., 09:30)")

def get_duration_input() -> Union[str, int]:
    """Get and validate duration input in minutes."""
    while True:
        duration = typer.prompt("Enter duration in minutes")
        if duration.lower() == 'exit':
            return duration
        try:
            return int(duration)
        except ValueError:
            typer.echo("Please enter a valid number of minutes")

@app.command()
def main():
    scheduler = Scheduler(API_URL)

    typer.echo("\nWelcome to the Scheduler System!")
    typer.echo("Type 'exit' at any prompt to return to menu\n")

    while True:
        display_menu()
        choice = typer.prompt("Enter your choice (1-5)", type=int)

        if choice == 1:
            date = get_date_input()
            if date.lower() == 'exit':
                continue
            busy_slots = scheduler.get_busy_slots(date)
            typer.echo(f"\nBusy time slots for {date}:")
            for slot in busy_slots:
                typer.echo(f"- {slot[0]} to {slot[1]}")

        elif choice == 2:
            date = get_date_input()
            if date.lower() == 'exit':
                continue
            free_slots = scheduler.get_free_slots(date)
            typer.echo(f"\nFree time slots for {date}:")
            for slot in free_slots:
                typer.echo(f"- {slot[0]} to {slot[1]}")

        elif choice == 3:
            date = get_date_input()
            if date.lower() == 'exit':
                continue
            typer.echo("\nEnter time slot to check:")
            start_time = get_time_input("Start time (HH:MM): ")
            if start_time.lower() == 'exit':
                continue
            end_time = get_time_input("End time (HH:MM): ")
            if end_time.lower() == 'exit':
                continue

            is_available = scheduler.is_available(date, start_time, end_time)
            status = "AVAILABLE" if is_available else "NOT AVAILABLE"
            typer.echo(f"\nTime slot {start_time}-{end_time} on {date} is {status}")

        elif choice == 4:
            duration = get_duration_input()
            if isinstance(duration, str) and duration.lower() == 'exit':
                continue

            slot = scheduler.find_slot_for_duration(duration)
            if slot:
                typer.echo(f"\nFirst available {duration}-minute slot:")
                typer.echo(f"Date: {slot[0]}, Time: {slot[1]}-{slot[2]}")
            else:
                typer.echo(f"\nNo available {duration}-minute slots found")

        elif choice == 5:
            typer.echo("Exiting the Scheduler System. Goodbye!")
            raise typer.Exit()

        else:
            typer.echo("Invalid choice. Please enter a number between 1 and 5")

        typer.pause("\nPress Enter to continue...")

if __name__ == "__main__":
    app()