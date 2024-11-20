from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

def calculate_working_hours(df):
    # Convert 'Log Date' to datetime
    df['Log Date'] = pd.to_datetime(df['Log Date'])
    
    # Extract the date and time separately
    df['Date'] = df['Log Date'].dt.date
    df['Time'] = df['Log Date'].dt.time

    # Group by Date to find punch-in and punch-out times
    results = []
    for date, group in df.groupby('Date'):
        # Sorting times to identify first (punch-in) and last (punch-out) of the day
        group = group.sort_values(by='Log Date')
        punch_in_time = group.iloc[0]['Log Date']
        punch_out_time = group.iloc[-1]['Log Date']
        
        # Calculate hours worked (in decimal)
        hours_worked_seconds = (punch_out_time - punch_in_time).total_seconds()
        hours_worked = hours_worked_seconds / 3600
        
        # Convert hours worked to HH:MM format
        hours_rounded = timedelta(seconds=hours_worked_seconds)
        hours_minutes = str(hours_rounded)  # 'HH:MM:SS' format
        hours_mm = hours_minutes.split(":")[:2]  # We only need hours and minutes
        
        results.append({
            "Date": date,
            "Punch In": punch_in_time.time(),
            "Punch Out": punch_out_time.time(),
            "Hours Worked (HH:MM)": f"{hours_mm[0]}:{hours_mm[1]}",
            "Hours Worked (Decimal)": hours_worked  # Keep the decimal hours for total calculation
        })

    # Create a DataFrame for results
    results_df = pd.DataFrame(results)
    total_hours = results_df["Hours Worked (Decimal)"].sum()

    return results_df, total_hours

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the data input from the user
        input_data = request.form['input_data']
        
        # Parse input data into DataFrame
        data = []
        lines = input_data.strip().split("\n")
        
        # Automatically set the header
        header = ["Emp_nmbr", "Log Date", "Device id"]
        for line in lines:
            parts = line.split("\t")
            if len(parts) == len(header):
                data.append(parts)
        
        # Check if data is not empty before creating a DataFrame
        if data:
            df = pd.DataFrame(data, columns=header)
            df['Emp_nmbr'] = df['Emp_nmbr'].astype(int)  # Convert Employee number to integer if necessary
            
            # Calculate working hours
            results_df, total_hours = calculate_working_hours(df)
            return render_template('index.html', results=results_df.to_html(classes='table table-striped'), total_hours=total_hours)
        else:
            return render_template('index.html', error="No valid data entered.")
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
