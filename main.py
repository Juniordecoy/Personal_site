from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length

import smtplib
import os

from ai_control_helpers import (
    load_agents, load_system_state, load_events, load_agent_locations, load_tools_registry,
    load_review_queue, load_tasks
)

from email_agent_helpers import load_email_agent_config, load_email_tools, load_email_agent_workflow

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
    return render_template("test_base.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password", "").strip()

        if password == os.environ.get("AI_DASHBOARD_PASSWORD", "test123"):
            session["ai_logged_in"] = True
            return redirect(url_for("ai_dashboard"))

        flash("Incorrect password. Please try again.", "error")

    return render_template("login.html")


@app.route("/ai-dashboard")
def ai_dashboard():
    if not session.get("ai_logged_in"):
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    agents = load_agents()
    agent_locations = load_agent_locations()
    system_state = load_system_state()
    events = load_events()
    tools = load_tools_registry()
    email_tools = load_email_tools()
    email_workflow = load_email_agent_workflow()
    review_queue = load_review_queue()
    tasks = load_tasks()
    available_tools = [tool for tool in tools if tool.get("status") in ["available", "planned"]]

    return render_template(
        "ai_dashboard.html",
        agents=agents,
        system_state=system_state,
        events=events,
        agent_locations=agent_locations,
        tools=tools,
        available_tools=available_tools,
        review_queue=review_queue,
        email_tools=email_tools,
        email_workflow=email_workflow,
        tasks=tasks
    )

@app.route("/logout")
def logout():
    session.pop("ai_logged_in", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)#, host="0.0.0.0")