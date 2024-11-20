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

    total_seconds_worked = 0

    # Group by Date to find punch-in and punch-out times
    results = []
    for date, group in df.groupby('Date'):
        # Sorting times to identify first (punch-in) and last (punch-out) of the day
        group = group.sort_values(by='Log Date')
        punch_in_time = group.iloc[0]['Log Date']
        punch_out_time = group.iloc[-1]['Log Date']
        
        # Calculate hours worked in seconds
        hours_worked_seconds = (punch_out_time - punch_in_time).total_seconds()
        total_seconds_worked += hours_worked_seconds
        
        # Convert hours worked to HH:MM:SS format
        hours_worked_timedelta = timedelta(seconds=hours_worked_seconds)
        hours_mm_ss = str(hours_worked_timedelta)  # Format: 'HH:MM:SS'
        
        results.append({
            "Date": date,
            "Punch In": punch_in_time.time(),
            "Punch Out": punch_out_time.time(),
            "Hours Worked (HH:MM:SS)": hours_mm_ss,
        })

    # Create a DataFrame for results
    results_df = pd.DataFrame(results)
    
    # Convert total seconds worked to HH:MM:SS without days
    hours = total_seconds_worked // 3600
    minutes = (total_seconds_worked % 3600) // 60
    seconds = int(total_seconds_worked % 60)
    total_hours_hhmmss = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    # Convert total seconds to hours (decimal)
    total_hours_decimal = total_seconds_worked / 3600

    return results_df, total_hours_decimal, total_hours_hhmmss



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
            results_df, total_hours_decimal, total_hours_hhmmss = calculate_working_hours(df)
            return render_template(
                'index.html',
                results=results_df.to_html(classes='table table-striped'),
                total_hours_decimal=total_hours_decimal,
                total_hours_hhmmss=total_hours_hhmmss
            )
        else:
            return render_template('index.html', error="No valid data entered.")
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
