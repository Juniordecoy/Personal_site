from flask import Flask, render_template, redirect, url_for, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length

import smtplib
import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-key")

class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(max=4000)])
    submit = SubmitField("Send Message")

@app.route("/", methods=["GET","POST"])
def home():
    return render_template('index.html')

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/work")
def work():
    return render_template("work.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        email = form.email.data.strip()
        message = form.message.data.strip()

        gmail_user = os.environ.get("GMAIL_USER")
        email_pw = os.environ.get("EMAIL_PW")

        print("Email check:", gmail_user)
        print("Password check:", bool(email_pw))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as connection:
                connection.ehlo()
                connection.starttls()  # required for Gmail on port 587
                connection.ehlo()
                connection.login(user=gmail_user, password=email_pw)
                connection.sendmail(
                    from_addr=gmail_user,
                    to_addrs=gmail_user,
                    msg=f"Subject: New Contact Message from {name}\n\nEmail: {email}\n\nMessage:\n{message}"
                )
            flash("Thanks! Your message has been sent.", "success")
            return redirect(url_for("contact"))
        except Exception as e:
            app.logger.exception("Email send failed")
            flash("Sorry, something went wrong. Please try again or email us directly.", "error")

    return render_template("contact.html", form=form)

@app.route("/testbase")
def test_base():
    return render_template("test_index.html")

@app.route("/flash-test")
def flash_test():
    from flask import flash, redirect, url_for
    flash("This is a success message", "success")
    flash("This is an error message", "error")
    return redirect(url_for("home"))

@app.route("/under-construction")
def under_construction():
    return render_template('under_construction.html')

@app.route("/elements.html")
def elements():
    return render_template('elements.html')

if __name__ == '__main__':
    app.run(debug=True)#, host="0.0.0.0")