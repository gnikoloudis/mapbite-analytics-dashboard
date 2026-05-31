import os
from datetime import date

# Get the directory where tracker.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct the full path to the tracker file
COUNTER_FILE = os.path.join(BASE_DIR, "api_usage_tracker.txt")

def check_and_increment_tracker(daily_max_limit):
    """
    Checks if the application run limits have been exhausted for the current day.
    Returns a tuple: (is_under_limit: bool, current_usage: int)
    """
    today = str(date.today())
    
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            lines = f.readlines()
            if lines:
                saved_date, saved_count = lines[0].strip().split(",")
                saved_count = int(saved_count)
                
                if saved_date == today:
                    if saved_count >= daily_max_limit:
                        return False, saved_count
                    return True, saved_count
    
    return True, 0

def increment_counter_file(current_count):
    """Increments the local tracking variable register inside the text file."""
    today = str(date.today())
    with open(COUNTER_FILE, "w") as f:
        f.write(f"{today},{current_count + 1}")