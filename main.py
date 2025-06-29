from flask import Flask, render_template, redirect, url_for, request, send_file
from flask_bootstrap import Bootstrap5
import smtplib
import datetime as dt
import pandas as pd
import os
from io import BytesIO

import matplotlib
matplotlib.use('Agg')  # This disables GUI usage (important for Flask)
import matplotlib.pyplot as plt

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL

import os

app = Flask(__name__)
Bootstrap5(app)

my_email = "junior@changingform.com"
email_pw = os.environ.get('EMAIL_PW')


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