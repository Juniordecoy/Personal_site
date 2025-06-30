from flask import Flask, render_template, redirect, url_for, request, send_file
from flask_bootstrap import Bootstrap5
import smtplib
import datetime as dt
import pandas as pd
import os
import io

import csv

import matplotlib
matplotlib.use('Agg')  # This disables GUI usage (important for Flask)
import matplotlib.pyplot as plt

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL

app = Flask(__name__)
Bootstrap5(app)

my_email = "junior@changingform.com"
email_pw = os.environ.get('EMAIL_PW')

task_log = []

@app.route("/", methods=["GET","POST"])
def home():
    if request.method == 'POST':
        data = request.form
        now = dt.datetime.now()
        print(now)
        print(data['name'])
        print(data['email'])
        print(data['message'])
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=my_email, password=email_pw)
            connection.sendmail(
                from_addr=my_email,
                to_addrs=my_email,
                msg=f"Subject:Changing Form Website Message\n\nFrom - {data['name']},\n\n{data['message']}"
            )
        return render_template('index.html')
    return render_template('index.html')

@app.route("/renders")
def renders():
    return render_template('3d-rendering.html')

@app.route("/2d-plans")
def two_d_plans():
    return render_template('2d-plans.html')

@app.route("/project-list")
def project_list():
    return render_template('project_list.html')

@app.route("/data-dashboard", methods=["GET", "POST"])
def data_dashboard():
    stats_table = None
    filename = None
    graph_url = None
    schema_table = None
    issues = None

    if request.method == "POST":
        file = request.files.get('file')
        if file and file.filename.endswith(".csv"):
            filename = file.filename
            df = pd.read_csv(file)

            # Data cleaning insights
            issues = {
                "Total Missing Values": int(df.isnull().sum().sum()),
                "Duplicate Rows": int(df.duplicated().sum()),
                "Rows with All Nulls": int((df.isnull().all(axis=1)).sum()),
                "Total Rows": len(df),
                "Total Columns": len(df.columns)
            }

            # Schema / column info
            column_info = pd.DataFrame({
                "Column": df.columns,
                "Data Type": df.dtypes.astype(str),
                "Missing Values": df.isnull().sum().values
            })
            schema_table = column_info.to_html(classes='alt', border=0, index=False)

            # Save stats table
            stats_table = df.describe(include='all').to_html(classes='alt', border=0)

            # Save the summary as downloadable CSV
            df.describe(include='all').to_csv("static/temp_uploaded.csv")

            # Generate and save a histogram
            plt.clf()
            df.hist(figsize=(10, 8))
            plt.tight_layout()
            plt.savefig("static/graph.png")
            graph_url = "static/graph.png"

    return render_template('data_dashboard.html', stats_table=stats_table, filename=filename,
        graph_url=graph_url, schema_table=schema_table, issues=issues)

@app.route("/download-graph-data")
def download_graph_data():
    path = "static/temp_uploaded.csv"
    response = send_file(path, as_attachment=True)
    # os.remove(path)  # Uncomment to delete after download
    return response

@app.route("/time-tracker", methods=["GET", "POST"])
def time_tracker():
    if request.method == "POST":
        task = request.form.get("task").capitalize()
        duration = request.form.get("duration")

        if task and duration:
            task_log.append({
                "task": task,
                "duration": int(duration)
            })
    total_time = sum(item["duration"] for item in task_log)

    return render_template("time_tracker.html", task_log=task_log, total_time=total_time)

@app.route("/download-tasks")
def download_tasks():
    # Step 1: Write to a text buffer
    csv_text = io.StringIO()
    writer = csv.writer(csv_text)
    writer.writerow(["Task", "Duration (minutes)"])
    for item in task_log:
        writer.writerow([item["task"], item["duration"]])

    # Step 2: Convert the text to bytes
    mem = io.BytesIO()
    mem.write(csv_text.getvalue().encode('utf-8'))
    mem.seek(0)

    # Step 3: Return as downloadable file
    return send_file(
        mem,
        mimetype="text/csv",
        as_attachment=True,
        download_name="task_log.csv"
    )

@app.route("/resume")
def resume():
    return render_template('resume.html')

@app.route("/under-construction")
def under_construction():
    return render_template('under_construction.html')

@app.route("/elements.html")
def elements():
    return render_template('elements.html')

if __name__ == '__main__':
    app.run(debug=True)