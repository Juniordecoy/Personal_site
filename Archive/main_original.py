from flask import Flask, render_template, redirect, url_for, request, send_file
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL

import sqlite3
import smtplib
import datetime as dt
import pandas as pd
import os
import io

import csv

import matplotlib
matplotlib.use('Agg')  # This disables GUI usage (important for Flask)
import matplotlib.pyplot as plt

app = Flask(__name__)
Bootstrap5(app)

my_email = "junior@changingform.com"
email_pw = os.environ.get('EMAIL_PW')

task_log = []

def init_guestbook():
    conn = sqlite3.connect("guestbook.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

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

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/testbase")
def test_base():
    return render_template("test_index.html")


@app.route("/renders")
def renders():
    return render_template('3d-rendering.html')

@app.route("/2d-plans")
def two_d_plans():
    return render_template('2d-plans.html')

@app.route("/project-list")
def project_list():
    return render_template('project_list.html')

@app.route("/weather-log", methods=["GET", "POST"])
def weather_log():
    weather_data = None

    if request.method == "POST":
        city = request.form.get("city").strip().title()
        # API call & database logic will go here later
        weather_data = {"city": city}  # just placeholder for now

    return render_template("weather_log.html", weather_data=weather_data)

@app.route("/guestbook", methods=["GET", "POST"])
def guestbook():
    if request.method == "POST":
        name = request.form.get("name").strip()
        message = request.form.get("message").strip()
        timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

        conn = sqlite3.connect("guestbook.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO entries (name, message, timestamp) VALUES (?, ?, ?)",
                       (name, message, timestamp))
        conn.commit()
        conn.close()
        return redirect(url_for("guestbook"))  # Refresh to avoid duplicate posts

    # Check if there is a filter
    search_query = request.args.get("search", "").strip()
    sort_by = request.args.get("sort", "newest")  # default is newest

    base_query = "SELECT id, name, message, timestamp FROM entries"
    params = []

    if search_query:
        base_query += " WHERE name LIKE ?"
        params.append(f"%{search_query}%")

    # Sorting logic
    if sort_by == "oldest":
        base_query += " ORDER BY id ASC"
    elif sort_by == "a-z":
        base_query += " ORDER BY name ASC"
    elif sort_by == "z-a":
        base_query += " ORDER BY name DESC"
    else:
        base_query += " ORDER BY id DESC"  # default: newest

    conn = sqlite3.connect("guestbook.db")
    cursor = conn.cursor()
    cursor.execute(base_query, params)
    entries = cursor.fetchall()
    conn.close()

    return render_template("guestbook.html", entries=entries, search_query=search_query, sort_by=sort_by)

@app.route("/download-guestbook")
def download_guestbook():
    conn = sqlite3.connect("guestbook.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, message, timestamp FROM entries ORDER BY id DESC")
    entries = cursor.fetchall()
    conn.close()

    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(["Name", "Message", "Timestamp"])
    writer.writerows(entries)
    si.seek(0)

    return send_file(
        io.BytesIO(si.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="guestbook_entries.csv"
    )

@app.route("/delete-entry/<int:entry_id>", methods=["POST"])
def delete_entry(entry_id):
    conn = sqlite3.connect("guestbook.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('guestbook'))

@app.route("/delete-all-guestbook", methods=["POST"])
def delete_all_guestbook():
    conn = sqlite3.connect("guestbook.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM entries")
    conn.commit()
    conn.close()
    return redirect(url_for("guestbook"))

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

@app.route("/reset-tasks", methods=["POST"])
def reset_tasks():
    task_log.clear()
    return redirect(url_for('time_tracker'))

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
    init_guestbook()
    app.run(debug=True)