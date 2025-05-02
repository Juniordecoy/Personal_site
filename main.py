from flask import Flask, render_template, redirect, url_for,request
from flask_bootstrap import Bootstrap5
import smtplib
import datetime as dt

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL

import os

app = Flask(__name__)
# app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap5(app)

my_email = "junior@changingform.com"
email_pw = "qnrazjcibafzzwgg"

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

@app.route("/under-construction")
def under_construction():
    return render_template('under_construction.html')

@app.route("/generic")
def generic():
    return render_template('generic.html')

@app.route("/elements.html")
def elements():
    return render_template('elements.html')

if __name__ == '__main__':
    app.run(debug=True)