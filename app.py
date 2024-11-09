import pandas as pd
from datetime import datetime
import sys

def calculate_working_hours(df):
    # Convert 'Log Date' to datetime
    df['Log Date'] = pd.to_datetime(df['Log Date'])
    
    # Extract the date and time separately
    df['Date'] = df['Log Date'].dt.date
    df['Time'] = df['Log Date'].dt.time

    # Group by Date to find in/out times
    results = []
    for date, group in df.groupby('Date'):
        # Sorting times to identify first (log-in) and last (log-out) of the day
        group = group.sort_values(by='Log Date')
        log_in_time = group.iloc[0]['Log Date']
        log_out_time = group.iloc[-1]['Log Date']
        
        # Calculate hours worked
        hours_worked = (log_out_time - log_in_time).total_seconds() / 3600
        
        results.append({"Date": date, "Log In": log_in_time.time(), "Log Out": log_out_time.time(), "Hours Worked": hours_worked})

    # Create a DataFrame for results
    results_df = pd.DataFrame(results)
    total_hours = results_df["Hours Worked"].sum()

    return results_df, total_hours

def parse_input():
    # Read input as a block
    print("Paste your table input below (end with an empty line):")
    data = []
    is_header = True
    while True:
        line = sys.stdin.readline().strip()
        if line == "":
            break
        if is_header:
            # Skip the header
            is_header = False
            continue
        parts = line.split("\t")
        if len(parts) == 3:
            data.append(parts)

    # Create DataFrame from parsed data
    df = pd.DataFrame(data, columns=["Emp_nmbr", "Log Date", "Device id"])
    df['Emp_nmbr'] = df['Emp_nmbr'].astype(int)  # Convert Employee number to integer
    return df

# Get input and process
logs_df = parse_input()
if not logs_df.empty:
    results_df, total_hours = calculate_working_hours(logs_df)
    print("\nDaily Work Hours:")
    print(results_df)
    print(f"\nTotal Working Hours in the Week: {total_hours:.2f} hours")
else:
    print("No data entered.")
