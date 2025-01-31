from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

def format_timedelta(seconds):
    """Formats total seconds into HH:MM:SS format, even if exceeding 24 hours."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{int(hours):02}:{int(minutes):02}:{int(secs):02}"

def calculate_working_hours(df):
    df['Log Date'] = pd.to_datetime(df['Log Date'], format="%d/%m/%Y %H:%M:%S", errors='coerce')
    df = df.dropna()
    df['Date'] = df['Log Date'].dt.date

    total_seconds_worked = 0
    total_policy_seconds_worked = 0

    results = []

    for date, group in df.groupby('Date'):
        group = group.sort_values(by='Log Date')
        punch_in_time = group.iloc[0]['Log Date']
        punch_out_time = group.iloc[-1]['Log Date']

        hours_worked_seconds = (punch_out_time - punch_in_time).total_seconds()
        total_seconds_worked += hours_worked_seconds

        policy_cutoff_time = datetime.combine(punch_out_time.date(), datetime.strptime("17:30:00", "%H:%M:%S").time())
        policy_punch_out = min(punch_out_time, policy_cutoff_time)
        policy_worked_seconds = (policy_punch_out - punch_in_time).total_seconds()
        total_policy_seconds_worked += max(policy_worked_seconds, 0)

        results.append({
            "Date": date,
            "Punch In": punch_in_time.time(),
            "Punch Out": punch_out_time.time(),
            "Hours Worked (HH:MM:SS)": format_timedelta(hours_worked_seconds),
            "Policy Duration (HH:MM:SS)": format_timedelta(policy_worked_seconds),
        })

    results_df = pd.DataFrame(results)

    total_hours_hhmmss = format_timedelta(total_seconds_worked)
    total_policy_hours_hhmmss = format_timedelta(total_policy_seconds_worked)

    total_hours_decimal = round(total_seconds_worked / 3600, 2)
    total_policy_hours_decimal = round(total_policy_seconds_worked / 3600, 2)

    return results_df, total_hours_decimal, total_hours_hhmmss, total_policy_hours_decimal, total_policy_hours_hhmmss

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_data = request.form['input_data']

        data = []
        lines = input_data.strip().split("\n")
        header = ["Emp_nmbr", "Log Date", "Device id"]

        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                emp_number = parts[0]
                log_date = " ".join(parts[1:3])
                device_id = parts[-1]
                data.append([emp_number, log_date, device_id])

        if data:
            df = pd.DataFrame(data, columns=header)
            df['Emp_nmbr'] = pd.to_numeric(df['Emp_nmbr'], errors='coerce')

            results_df, total_hours_decimal, total_hours_hhmmss, total_policy_hours_decimal, total_policy_hours_hhmmss = calculate_working_hours(df)

            return render_template(
                'index.html',
                results=results_df.to_html(classes='table table-striped'),
                total_hours_decimal=total_hours_decimal,
                total_hours_hhmmss=total_hours_hhmmss,
                total_policy_hours_decimal=total_policy_hours_decimal,
                total_policy_hours_hhmmss=total_policy_hours_hhmmss
            )
        else:
            return render_template('index.html', error="No valid data entered.")
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
