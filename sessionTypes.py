# Mapping of ACC session type codes (shorthand) to full session names
session_type_map = {
    "FP": "Free Practice",
    "Q": "Qualifying",
    "R": "Race",
    "WU": "Warm-up",
    "FL": "Formation Lap",
    "IL": "In-lap",
    "OL": "Out-lap",
    "SC": "Safety Car",
    "CD": "Cool-down Lap"
}

# Example function to get the full session name from the shorthand code
def get_session_type_name(session_code):
    return session_type_map.get(session_code, "Unknown Session Type")

# Example usage with your data
#full_session_type = get_session_type_name(session_code)
