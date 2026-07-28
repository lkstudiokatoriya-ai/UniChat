from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import mysql.connector

# ===========================
# Flask Configuration
# ===========================
app = Flask(__name__)

app.secret_key = "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY"

app.permanent_session_lifetime = timedelta(days=7)

# ===========================
# MySQL Configuration
# ===========================
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "polytechnic_hub"
}

def get_db():
    return mysql.connector.connect(**db_config)

# ===========================
# Home Page
# ===========================
@app.route("/")
def home():
    return render_template("index.html")

# ===========================
# Login Page
# ===========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session.permanent = True

            session["user_id"] = user["id"]
            session["name"] = user["name"]

            return redirect("/dashboard")

        return "Invalid Email or Password"

    return render_template("login.html")

# ===========================
# Dashboard
# ===========================
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        name=session["name"]
    )

# ===========================
# Logout
# ===========================
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# ===========================
# API Status
# ===========================
@app.route("/api/status")
def status():

    return jsonify({
        "status": "running",
        "project": "POLYTECHNIC HUB"
    })

# ===========================
# Run Server
# ===========================
if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
