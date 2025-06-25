from datetime import datetime
import pytz
from utils.firebase_db import load_user_profile

def get_user_local_time(user_id, token=None):
    # Load timezone from user profile
    profile = load_user_profile(user_id, token)
    tz_str = profile.get("timezone", "US/Central")  # Default to Central if missing
    try:
        timezone = pytz.timezone(tz_str)
    except pytz.UnknownTimeZoneError:
        timezone = pytz.timezone("US/Central")
    
    return datetime.now(timezone)
