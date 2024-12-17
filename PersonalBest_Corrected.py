import json
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from carModels import getCarString
from sessionTypes import get_session_type_name

# translate 1/0 for weather to icon
def get_weather_icon_for_table(is_wet):
    return "🌧️ Wet" if is_wet else "🌤️ Dry"

# Function to format time from milliseconds
def format_time(ms):
    if ms == 2147483647 or ms <= 0:  # Placeholder for "no lap recorded"
        return "N/A"
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    fraction = ms % 1000
    return f"{minutes}:{seconds:02}.{fraction:03}"

# Define the root directory where the "config" folder is located
root_folder = '../config/'

# Recursively find JSON files in "results" subdirectories
json_files = []  # This will store the full paths of JSON files

# Walk through the directory structure
for dirpath, dirnames, filenames in os.walk(root_folder):
    if 'results' in dirpath:  # Only include directories with "results" in their path
        # Filter and add only JSON files (i.e., files with a .json extension)
        json_files.extend([os.path.join(dirpath, file) for file in filenames if file.endswith('.json')])

# Prepare lists for the summary and session details
personal_bests = []

# Iterate through each file to process the data
for file_path in json_files:
    # Load JSON data
    with open(file_path, "r", encoding="utf-16-le") as f:
        data = json.load(f)

    # Extract session info
    session_date = file_path.split(os.sep)[-1].split('_')[0]  # Assuming date is part of the filename

    session_type = get_session_type_name(data["sessionType"])
    track_name = data["trackName"]
    is_wet = data["sessionResult"]["isWetSession"]
    leaderboard = data["sessionResult"]["leaderBoardLines"]

    # Convert the date from 'YYMMDD' to 'DD-MM-YYYY'
    session_date = datetime.strptime(session_date, "%y%m%d").strftime("%d-%m-%Y")

    # Collect personal best lap information
    for entry in leaderboard:
        driver = entry["currentDriver"]
        car = entry["car"]
        timing = entry["timing"]
        best_lap = timing["bestLap"]

        if best_lap != 2147483647 and best_lap > 0:
            # Format the best lap time here before appending
            best_lap_time = format_time(best_lap)
            splits = timing["bestSplits"]
            sector1 = format_time(splits[0]) if len(splits) > 0 else "N/A"
            sector2 = format_time(splits[1]) if len(splits) > 1 else "N/A"
            sector3 = format_time(splits[2]) if len(splits) > 2 else "N/A"
        else:
            best_lap_time = "N/A"
            sector1 = sector2 = sector3 = "N/A"

        personal_bests.append({
            "Driver": f"{driver['firstName']} {driver['lastName']}",
            "Track": track_name,
            "Session Type": session_type,
            "Car": getCarString(car["carModel"]),  # car["carModel"],
            "Date": session_date,
            "Was Wet": get_weather_icon_for_table(is_wet),
            "Best Lap Time": best_lap_time,
            "Sector 1": sector1,
            "Sector 2": sector2,
            "Sector 3": sector3
        })

# Convert to DataFrame for processing
personal_bests_df = pd.DataFrame(personal_bests)

# Group by Driver, Track, and Car to find the fastest lap
fastest_laps = (
    personal_bests_df.loc[personal_bests_df["Best Lap Time"] != "N/A"]  # Exclude "N/A" laps
    .groupby(["Driver", "Track", "Car"], as_index=False)
    .agg({
        "Date": "first",  # Keep one example date
        "Session Type": "first",  # Keep one example session type
        "Was Wet": "first",  # Keep one example wet/dry condition
        "Best Lap Time": "min",  # Keep the minimum best lap time
        "Sector 1": "first",  # Keep corresponding sectors
        "Sector 2": "first",
        "Sector 3": "first"
    })
)

# Rename "Was Wet" column to "Weather"
fastest_laps.rename(columns={"Was Wet": "Weather"}, inplace=True)

# Display in Streamlit
st.set_page_config(layout="wide")
st.title("Personal Bests: Fastest Laps by Driver, Circuit, and Car")

st.dataframe(fastest_laps, use_container_width=True)
